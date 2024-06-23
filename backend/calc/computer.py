import logging
import math
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path
from time import time
from typing import List, Any, Optional, DefaultDict
from tqdm import tqdm
from fastapi.encoders import jsonable_encoder
from collections import defaultdict
import numpy as np
import itertools
from uuid import uuid1
from backend.calc.base_graph import BaseGraph
from backend.calc.context import Context
from backend.calc.ice_cond import IceCondition
from backend.calc.navigator import Navigator
from backend.calc.vessel import Vessel, IceBreaker
from backend.config import backend_base_dir
from backend.constants import PathEventsType
from backend.crud.crud_types import (TemplatesCRUD, VesselPathCRUD, IcebreakerPathCRUD,
                                     CaravanCRUD, GradeCRUD)
from backend.models import Caravan, VesselPath, SimpleVesselPath, AllSimpleVesselPath, PathEvent, \
    CaravanConfiguration, Grade

logger = logging.getLogger(__name__)
from backend.models import IcebreakerPath


class Computer:
    base: BaseGraph
    ice_cond: IceCondition
    context: Context
    navigator: Navigator

    max_ships_per_icebreaker: int = 3
    max_T: timedelta = timedelta(days=90) # максимальное забегание вперед
    p_norm: float

    time_estimate_gate: int = 5
    estimator_samle_size = 100

    # почему-то выгоднее просто локально жадничать, чем ставить горизонт планирования ощутимо больше, чем шаг
    planing_horizon: timedelta = timedelta(days=7)  # насколько мы вперед знаем расписание #timedelta(days=7)
    planing_step: timedelta = timedelta(days=3)  # дискретность шага планирования
    # beta - какое-то характерное время ожидания, alpha - вероятность, что придется вести одним ледоколом
    # / характерное число судов в проводке
    # solo_stuck_time = beta * planing_horizon.hours + alpha * time_with_best_icebreaker
    # TODO: пересчитать solo_stuck_time исходя из нач и кон точек маршрута
    solo_stuck_time: float = 14 * 24 # вклад во время в часах, предполагая, что судно придется вести отдельным ледоколом #1e6
    icebreaker_time_fee: float = 3.  # насколько время ледокола дороже времени обычного судна
    typical_vessel_waiting_time: float = 3 * 24  # характерное допустимое время ожидания судна в порту

    def __init__(self, context: Context | None = None):
        file_path = backend_base_dir / "input_files/IntegrVelocity.xlsx"
        base = BaseGraph()
        ice_cond = IceCondition(file_path, base.graph)

        if not context:
            full_template_name = "full"
            templates_crud = TemplatesCRUD()
            context = Context(templates_crud.get(full_template_name))

        self.base = base
        self.ice_cond = ice_cond
        self.navigator = Navigator(base=base, ice_cond=ice_cond, context=context)
        self.context = context

    def init_app(self, recalculate_loaded: bool = True):

        full_template_name = "full"
        templates_crud = TemplatesCRUD()
        vessel_paths_crud = VesselPathCRUD()
        icebreaker_paths_crud = IcebreakerPathCRUD()
        grade_crud = GradeCRUD()
        caravan_crud = CaravanCRUD()

        if recalculate_loaded:
            # считаем реальные оценки
            context = Context(templates_crud.get(full_template_name))
            self.context = context
            real_vessel_paths, real_icebreaker_paths, real_grade, caravans = self.optimal_timesheet()
            vessel_paths_crud.post_or_put_list(real_vessel_paths)
            icebreaker_paths_crud.post_or_put_list(real_icebreaker_paths)
            grade_crud.post(real_grade)
            caravan_crud.post_or_put_list(caravans)

            # считаем самостоятельные оценки
            context = Context(templates_crud.get("solo"))
            self.context = context
            self.navigator.context = context
            solo_nav_grade, solo_vessel_paths = self.navigator.rough_estimate()
            vessel_paths_crud.post_or_put_list(solo_vessel_paths.values())

            # считаем лучшие оценки
            context = Context(templates_crud.get("best"))
            self.context = context
            self.navigator.context = context
            best_nav_grade, best_vessel_paths = self.navigator.rough_estimate(with_best_icebreaker=True)
            vessel_paths_crud.post_or_put_list(best_vessel_paths.values())

    def generate_distributions(self, n_icebrs: int, ships: List[int]):
        def distribute(remaining_ships, current_distribution):
            distributions.append([list(group) for group in current_distribution])
            if not remaining_ships:
                return
            for i in range(n_icebrs):
                if len(current_distribution[i]) < self.max_ships_per_icebreaker:
                    new_distribution = [list(group) for group in current_distribution]
                    new_distribution[i].append(remaining_ships[0])
                    distribute(remaining_ships[1:], new_distribution)

        distributions = []
        distribute(ships, [[] for _ in range(n_icebrs)])
        return distributions

    @staticmethod
    def all_subsets_up_to_k_elements(s, k):
        subsets = []
        for i in range(1, k + 1):
            subsets.extend(itertools.combinations(s, i))
        return subsets


    def merge_icebreakers_paths(self, paths_old: List[IcebreakerPath], paths_new: List[IcebreakerPath]):
        """
        Метод для слияния 2 путей ледокола, мерджит waybill
        """
        if not paths_old:
            return paths_new

        old_path_dict = {path.icebreaker_id: path for path in paths_old}
        new_path_dict = {path.icebreaker_id: path for path in paths_new}

        # TODO: поправить сдвиги time_line
        for idx in new_path_dict:
            if idx in old_path_dict:
                old_path_dict[idx] = IcebreakerPath(
                    start_date=old_path_dict[idx].start_date,
                    end_date=new_path_dict[idx].end_date,
                    source=new_path_dict[idx].source, # меняем точку старта на конец последнего каравана, то есть сурс для обновленного ледокола
                    # TODO: понять, нет ли тут опечатки с сурсами. нового же нужно, разве нет??
                    source_name=old_path_dict[idx].source_name,
                    waybill=old_path_dict[idx].waybill + new_path_dict[idx].waybill,
                    path_line=old_path_dict[idx].path_line + new_path_dict[idx].path_line,
                    template_name=self.context.template_name,
                    icebreaker_id=idx,
                    time_line=old_path_dict[idx].time_line + new_path_dict[idx].time_line
                )
            else:
                old_path_dict[idx] = new_path_dict[idx]

        return list(old_path_dict.values())

    def calculate_total_paths_grade(self, vessels: List[VesselPath]) -> Grade:
        total_time = sum(vessel.total_time_hours for vessel in vessels if vessel.success)
        total_waiting_time = sum(vessel.total_waiting_time_hours for vessel in vessels if vessel.success)
        max_waiting_time = max(vessel.total_waiting_time_hours for vessel in vessels if vessel.success)
        stuck_vessels = sum(1 for vessel in vessels if not vessel.success)
        best_possible = sum( min(self.navigator.solo_move_ways[v.vessel_id].total_time_hours,self.navigator.ice_move_ways[v.vessel_id].total_time_hours )for v in vessels     )
        return Grade(template_name=self.context.template_name, 
                     total_time=total_time, 
                     best_possible_time=best_possible,
                     total_waiting_time=total_waiting_time,
                     max_waiting_time=max_waiting_time,
                     stuck_vessels=stuck_vessels)

    @staticmethod
    def update_list_of_objects(old_list: List[Any], updated_values: List[Any], id_field: str) -> List[Any]:
        old_dict = {getattr(obj, id_field): obj for obj in old_list}
        updated_dict = {getattr(obj, id_field): obj for obj in updated_values}

        for idx, obj in updated_dict.items():
            old_dict[idx] = obj

        return list(old_dict.values())


    def estimate_solo_move(self, vessel_ids: List[int]) -> float:
        if not vessel_ids:
            return 0

        solo_movement_times = [self.navigator.solo_move_ways[idx].total_time_hours for idx in vessel_ids]
        # TODO: подумать над правильным штрафом за простой на данном этапе
        best_ib_movement_times = [self.navigator.ice_move_ways[idx].total_time_hours + self.solo_stuck_time +
                                  ((self.current_time - self.context.vessels[idx].start_date).days * 24) ** 2 / self.typical_vessel_waiting_time
                                  for idx in vessel_ids]
        return sum(solo_time if solo_time < math.inf else best_ib_time for solo_time, best_ib_time
                   in zip(solo_movement_times, best_ib_movement_times))

    @staticmethod
    def non_intersecting_permutations_with_empty_indices(sets, k):
        def are_disjoint(indices_combination):
            seen = set()
            for index in indices_combination:
                if index != -1:
                    s = sets[index]
                    if seen.intersection(s):
                        return False
                    seen.update(s)
            return True

        indices = list(range(len(sets)))
        indices_with_empty = indices + [-1] * k

        all_permutations = set()
        for permutation in itertools.permutations(indices_with_empty, k):
            if are_disjoint(permutation):
                all_permutations.add(permutation)

        return list(all_permutations)

    def find_admissible_starts_ends(self, vessel_ids: List[int]) -> (List[int], List[int]):
        if not vessel_ids:
            return [[], []]

        admissible_vertices_from_starts = [self.navigator.reachable_vertices_from_start[v] for v in vessel_ids]
        possible_caravan_starts = list(reduce(set.intersection, map(set, admissible_vertices_from_starts)))

        admissible_vertices_from_ends = [self.navigator.reachable_vertices_from_end[v] for v in vessel_ids]
        possible_caravan_ends = list(reduce(set.intersection, map(set, admissible_vertices_from_ends)))

        # предполагая, что караван собирается и расходится в одной точке
        if not possible_caravan_starts or not possible_caravan_ends:
            return [[], []]

        return possible_caravan_starts, possible_caravan_ends

    # TODO: передавать караван
    def find_best_caravans(self, vessel_ids: List[int], icebreaker_path_times_to_all: AllSimpleVesselPath,
                                icebreaker: IceBreaker, rough: bool = False) -> Caravan | None:
        if not vessel_ids:
            return None

        vessels_obj = {idx: self.context.vessels[idx] for idx in vessel_ids}
        n_vessels = len(vessel_ids)

        possible_caravan_starts, possible_caravan_ends = self.find_admissible_starts_ends(vessel_ids)

        best_caravan = Caravan(
            uuid=str(uuid1()),
            total_time_hours = math.inf,
            icebreaker_move_time = math.inf
        )

        # сохраняем и передаем список всех возможныз караванов с лучшим временем,мб с какой-то погрешностью!
        #best_caravans = [best_caravan]
        best_time = best_caravan.total_time_hours

        for a in possible_caravan_starts:
            for b in possible_caravan_ends:
                if a == b:
                    continue

                # грубо оцениваем, забивая на время ожидания
                if self.navigator.best_icebreaker_paths_times[a][b] * n_vessels + sum(
                        self.navigator.path_from_all[idx].paths[b].total_time_hours
                        + self.navigator.path_to_all[idx].paths[a].total_time_hours for idx in
                        vessel_ids) >= best_caravan.total_time_hours:
                    continue

                # считаем затраты на то, чтобы все суда собрались в точке старта
                caravan_start_time = max([timedelta(hours=self.navigator.path_to_all[idx].paths[a].total_time_hours)
                                          + vessels_obj[idx].start_date for idx in vessel_ids])

                caravan_start_time = max(caravan_start_time, icebreaker.start_date +
                                         timedelta(hours=icebreaker_path_times_to_all.paths[a].total_time_hours))

                total_move_time = sum(
                    [(caravan_start_time - vessel.start_date).days for vessel in vessels_obj.values()])
                total_move_time = total_move_time * 24

                total_move_time += sum(
                    [self.navigator.path_from_all[idx].paths[b].total_time_hours for idx in vessel_ids])

                # оцениваем время проводки, грубо, посредством идеального ледокола
                # но еще учитываем, что это время движутся еще и остальные суда
                if rough:
                    time_in_caravan = self.navigator.best_icebreaker_paths_times[a][b]
                else:
                    # отсиваем очевидно-плохие пути еще дополнительно
                    if total_move_time + self.navigator.best_icebreaker_paths_times[a][b] > best_caravan.total_time_hours:
                        continue  # увеличение скорости перебора примерно в 10 раз дает

                    time_in_caravan = max([self.navigator.calc_shortest_path(v, source_node = a, target_node = b,
                                                                             start_time = caravan_start_time,
                                                                             icebreaker = icebreaker).total_time_hours
                                           for v in vessels_obj.values()])

                total_move_time += n_vessels * time_in_caravan

                # TODO: поменять на честные ледоколы
                #total_move_time += self.navigator.best_icebreaker_paths_times[icebreaker.source][a]
                icebreaker_time_fee = time_in_caravan + (caravan_start_time - icebreaker.start_date).days * 24

                if best_time > total_move_time:
                    best_caravan = Caravan(
                        uuid=str(uuid1()),
                        total_time_hours = total_move_time, icebreaker_time_fee = icebreaker_time_fee, start_node = a,
                        end_node = b, vessel_ids = vessel_ids, icebreaker_id = icebreaker.idx, start_time = caravan_start_time
                    )
                    """
                    # оставляем только попадающие в новые ворота
                    best_caravans = [c for c in best_caravans if abs(c.total_time_hours - total_move_time) < self.time_estimate_gate]
                elif total_move_time < self.time_estimate_gate + best_time:
                    # иначе, добавляем также все попадающее в ворота
                    best_caravans.append(
                        Caravan(
                            total_time_hours=total_move_time, icebreaker_time_fee=icebreaker_time_fee, start_node=a,
                            end_node=b, vessel_ids=vessel_ids, icebreaker_id=icebreaker.idx,
                            start_time=caravan_start_time
                        )
                    )"""

        return best_caravan if best_caravan.total_time_hours < math.inf else None


    def estimate_possible_caravans(self, vessel_ids: List[int], icebreaker_ids: List[int]):
        """
        Функция, возвращающая возможные / околооптимальные конфигурации караванов
        """
        logger.info(f"Estimating possible caravans for vessels {vessel_ids} and icebreakers {icebreaker_ids}")
        paths = {idx: self.navigator.calc_shortest_path(self.context.icebreakers[idx]) for idx in icebreaker_ids}
        # TODO: взять эти пути из кэша, учесть, что там разные ледовые данные / в другом месте брать не из кэша

        subsets = self.all_subsets_up_to_k_elements(vessel_ids, self.max_ships_per_icebreaker)
        suitable_subsets = [s for s in subsets if self.find_admissible_starts_ends(s) != [[], []]]

        logger.info(f"Found {len(suitable_subsets)} suitable subsets!")
        distributions = self.non_intersecting_permutations_with_empty_indices(suitable_subsets, len(icebreaker_ids))

        caravans_hashed: DefaultDict[int, DefaultDict[int, Caravan | None]] = defaultdict(lambda: defaultdict())
        # точный расчет времени движения каравана с данным ледоколом и списком судов
        logger.info(f"Creating computatinal cache...")
        for l in tqdm(range(len(suitable_subsets))):
            for idx in icebreaker_ids:
                caravan_vessels = suitable_subsets[l]
                caravan = self.find_best_caravans(caravan_vessels, paths[idx], self.context.icebreakers[idx],
                                                  rough=False)
                if sum(self.navigator.solo_move_ways[v_id].total_time_hours for v_id in caravan_vessels) < caravan.total_time_hours:
                    for idxx in icebreaker_ids:
                        caravans_hashed[l][idxx] = None
                    break
                else:
                    caravans_hashed[l][idx] = caravan


        logger.info(f"Obtained {len(distributions)} possible caravan configurations!")
        caravans_configurations = []
        for j in tqdm(range(len(distributions))):
            distr = distributions[j]
            caravans = [caravans_hashed[distr[i]][idx] for i, idx in enumerate(icebreaker_ids) if distr[i] >= 0]

            if None in caravans:
                continue
            caravans_vessels_ids = [suitable_subsets[distr[i]] for i, idx in enumerate(icebreaker_ids) if distr[i] >= 0]
            if caravans_vessels_ids:
                caravans_vessels_ids = reduce(set.union, map(set, caravans_vessels_ids))

            outside_caravan_vessels_ids = list(set(vessel_ids).difference(caravans_vessels_ids))
            caravan_vessels_move_time = sum(caravan.total_time_hours for caravan in caravans)
            icebreakers_time_fee = sum(caravan.icebreaker_time_fee for caravan in caravans)

            solo_move_time_for_caravan_vessels = self.estimate_solo_move(list(caravans_vessels_ids))
            solo_move_time_outside_caravan_vessels = self.estimate_solo_move(outside_caravan_vessels_ids)

            # считаем выгодность каравана. Пытаемся оценивать вклад в полное время, которое она даст в перспективе,
            # с учетом судов, которые придется тащить отдельно

            caravans_configurations.append(
                CaravanConfiguration(caravans=caravans, solo_vessel_ids=outside_caravan_vessels_ids,
                                     total_time_hours=caravan_vessels_move_time + solo_move_time_outside_caravan_vessels,
                                     configuration_grade=solo_move_time_for_caravan_vessels - caravan_vessels_move_time,
                                     icebreakers_time_fee = icebreakers_time_fee
                                     #configuration_grade=solo_move_time_for_caravan_vessels - caravan_vessels_move_time
                                     )
            )

        return caravans_configurations

    def grade_caravans_configuration(self, conf: CaravanConfiguration):
        # то есть, вначале минимизируем число застрявших, и среди них выбираем конфигурацию
        # с мин вр дввиежния и простоя ледоколов
        # тут возникает много одинаковых конфигураций, поэтому нужно побольше критериев взять
        total_used_vessels_num = len(conf.solo_vessel_ids) + sum([len(caravan.vessel_ids) for caravan in conf.caravans])
        return  -conf.total_time_hours, total_used_vessels_num, -conf.icebreakers_time_fee, conf.configuration_grade

    def optimal_timesheet_for_planing_horizon(self, vessels: List[Vessel], icebreakers: List[IceBreaker]) \
            -> (List[VesselPath], List[IcebreakerPath], List[IceBreaker], List[Caravan]):
        """
            Распределение судов по ледоколам внутри окна планирования
        """

        logger.info(f"Making horizon timetable for icebreakers {jsonable_encoder(icebreakers)} and "
                    f"vessels {jsonable_encoder(vessels)}")

        vessel_ids = [v.idx for v in vessels]
        icebreaker_ids = [v.idx for v in icebreakers]
        caravans_configurations = self.estimate_possible_caravans(vessel_ids=vessel_ids, icebreaker_ids=icebreaker_ids)

        if not caravans_configurations:
            return [], [], [], []

        conf = max(caravans_configurations, key=self.grade_caravans_configuration)
        logger.info(f"Found best caravan configuration: {jsonable_encoder(conf)}")
        # выбираем лучшую возможную конфигурацию, их не очень много оказывается на практике

        vessel_paths, icebreaker_paths = self.convert_caravan_conf_to_ship_paths(conf)

        used_icebreaker_ids = [caravan.icebreaker_id for caravan in conf.caravans if caravan.vessel_ids]
        updated_icebreakers = []

        icebreakers_dict = {ib.idx: ib for ib in icebreakers}

        for idx, icebreaker_path in icebreaker_paths.items():
            if idx not in used_icebreaker_ids:
                continue

            updated_ib: IceBreaker = icebreakers_dict[idx]
            updated_ib.source = icebreaker_path.waybill[-1].point
            # TODO: подумать, мб как-то двигать ледокол к след неделе
            updated_ib.start_date = icebreaker_path.waybill[-1].dt
            updated_ib.source_name = self.base.graph.nodes[updated_ib.source]["point_name"]
            updated_icebreakers.append(updated_ib)

        return list(vessel_paths.values()), list(icebreaker_paths.values()), updated_icebreakers, conf.caravans

    def convert_caravan_conf_to_ship_paths(self, caravan_conf: CaravanConfiguration) -> (
    List[VesselPath], List[IcebreakerPath]):
        # формируем пути для ледоколов

        icebreaker_paths = {}
        vessel_paths = {}

        # обрабатываем самостоятелньо движущиеся суда
        for idx in caravan_conf.solo_vessel_ids:
            vessel_paths[idx] = self.navigator.solo_move_ways[idx]

        for caravan in caravan_conf.caravans:

            icebreaker = self.context.icebreakers[caravan.icebreaker_id]

            # считаем ледокол
            if icebreaker.source != caravan.start_node:
                icebreaker_simple_path_before = self.navigator.calc_shortest_path(icebreaker,
                                                                                  source_node=icebreaker.source,
                                                                                  target_node=caravan.start_node,
                                                                                  start_time=icebreaker.start_date)

                waiting_time = 0
                end_type = PathEventsType.formation
                ib_arrival_date = icebreaker.start_date + timedelta(hours=icebreaker_simple_path_before.total_time_hours)
                if ib_arrival_date < caravan.start_time:
                    waiting_time = (caravan.start_time - ib_arrival_date).days * 24
                    end_type = PathEventsType.wait

                icebreaker_waybill_before = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_before,
                                                                                          icebreaker.start_date,
                                                                                          icebreaker.source,
                                                                                          PathEventsType.move,
                                                                                          PathEventsType.move,
                                                                                          end_type
                                                                                          )

            else:
                icebreaker_waybill_before = []
                icebreaker_simple_path_before = SimpleVesselPath()
                ib_arrival_date = icebreaker.start_date

            icebreaker_simple_path_in = self.navigator.calc_shortest_path(icebreaker,
                                                                          source_node=caravan.start_node,
                                                                          target_node=caravan.end_node,
                                                                          start_time=caravan.start_time)

            caravan_end_time = caravan.start_time + timedelta(hours=icebreaker_simple_path_in.total_time_hours)

            # движение в караване
            icebreaker_waybill_in = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_in,
                                                                                  caravan.start_time,
                                                                                  caravan.start_node,
                                                                                  PathEventsType.formation,
                                                                                  PathEventsType.formation,
                                                                                  PathEventsType.wait
                                                                                  )

            icebreaker_paths[caravan.icebreaker_id] = IcebreakerPath(
                start_date=icebreaker.start_date,
                end_date=caravan_end_time,
                source=icebreaker.source,
                source_name=self.base.graph.nodes[icebreaker.source]["point_name"],
                waybill=icebreaker_waybill_before + icebreaker_waybill_in,
                path_line=icebreaker_simple_path_before.path_line + icebreaker_simple_path_in.path_line,
                template_name=self.context.template_name,
                icebreaker_id=caravan.icebreaker_id,
                time_line=icebreaker_simple_path_before.time_line + icebreaker_simple_path_in.time_line
            )

            # считаем суда
            for idx in caravan.vessel_ids:
                v = self.context.vessels[idx]
                # движение до каравана
                waiting_time = 0
                if caravan.start_node != v.source: # формирование каравана в море
                    simple_path_before = self.navigator.path_to_all[idx].paths[caravan.start_node]
                    time_before = simple_path_before.total_time_hours
                    # TODO: учесть, что путь тоже меняется тогда, или делать ожидание в море
                    vessel_caravan_start_arrival_date = v.start_date + timedelta(hours=time_before) if time_before != math.inf else None

                    # судно дожидается в море
                    waybill_before = self.navigator.convert_simple_path_to_waybill(simple_path_before, v.start_date,
                                                                                   v.source, 
                                                                                   PathEventsType.move,
                                                                                   PathEventsType.move,
                                                                                   PathEventsType.wait)
                    if vessel_caravan_start_arrival_date < caravan.start_time:
                        waiting_time = (caravan.start_time - vessel_caravan_start_arrival_date).days * 24
                    else:
                        waybill_before.pop () #удаляем последний wait    
                else: #caravan.start_node == v.source формирование в порту
                    if caravan.start_time > v.start_date:
                        waybill_before = [PathEvent(event=PathEventsType.wait, point=v.source, dt=v.start_date)]
                        waiting_time = (caravan.start_time - v.start_date).days * 24
                        simple_path_before = SimpleVesselPath(total_time_hours=waiting_time, path_line=[v.source],
                                                              time_line=[0])
                    else:
                        waybill_before=[]
                        time_before = 0 # чтобы не париться с округлением и проч
                        simple_path_before = SimpleVesselPath()

                if caravan.end_node == v.target:
                    end_type = PathEventsType.fin
                else:
                    end_type = PathEventsType.wait

                # движение в караване
                waybill_in = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_in,
                                                                           caravan.start_time,
                                                                           caravan.start_node,
                                                                           PathEventsType.formation,
                                                                           PathEventsType.formation,
                                                                           end_type)

                if end_type != PathEventsType.fin:
                    simple_path_after = self.navigator.calc_shortest_path(v, source_node=caravan.end_node,
                                                                          target_node=v.target,
                                                                          start_time=caravan_end_time)

                    waybill_after = self.navigator.convert_simple_path_to_waybill(simple_path_after, caravan_end_time,
                                                                                caravan.end_node, 
                                                                                PathEventsType.move,
                                                                                PathEventsType.move,
                                                                                PathEventsType.fin)
                    vessel_end_date = caravan_end_time + timedelta(hours=simple_path_after.total_time_hours)
                else:
                    waybill_after = []
                    simple_path_after = SimpleVesselPath()
                    vessel_end_date = caravan_end_time

                # TODO: проверить, не проебаны ли смежные ребра
                total_time_hours = (simple_path_before.total_time_hours + icebreaker_simple_path_in.total_time_hours
                                    + simple_path_after.total_time_hours)

                vessel_paths[idx] = VesselPath(
                    total_time_hours=total_time_hours,
                    total_waiting_time_hours = waiting_time,
                    start_date=v.start_date,
                    end_date=vessel_end_date,
                    source=v.source,
                    source_name=self.base.graph.nodes[v.source]["point_name"],
                    target=v.target,
                    target_name=self.base.graph.nodes[v.target]["point_name"],
                    success=True,  # мы не брали суда в караван, если они не смогут дойти
                    waybill=waybill_before + waybill_in + waybill_after,
                    path_line=simple_path_before.path_line + icebreaker_simple_path_in.path_line + simple_path_after.path_line,
                    template_name=self.context.template_name,
                    vessel_id=idx,
                    caravan_id=str(caravan.uuid),
                    time_line=simple_path_before.time_line + icebreaker_simple_path_in.time_line + simple_path_after.time_line
                )

        return vessel_paths, icebreaker_paths

    def get_possible_vessels(self, time_from: datetime, time_to: datetime) -> List[Vessel]:
        # нестрогое неравентсво, чтобы не терять точно ничего, повторения отдельно отсеем
        return list(filter(lambda v: (v.start_date <= time_to) and (v.start_date >= time_from),
                           list(self.context.vessels.values())))

    def get_possible_icebreakers(self, icebreakers: List[IceBreaker],
                                 time_to: datetime) -> List[IceBreaker]:
        return list(filter(lambda v: v.start_date < time_to, icebreakers))

    def optimal_timesheet(self) -> (List[VesselPath], List[IcebreakerPath], Grade, List[Caravan]):
#определяем начало диапазона - это минимум из всех заявок
        min_time = min([v.start_date for v in self.context.vessels.values()])
#определяем правую границу диапазона, это дата последней заявки + max_T
        # нужно, чтобы последние тоже успели дойти
        max_time = max([v.start_date for v in self.context.vessels.values()]) + self.max_T

        self.current_time = min_time
        icebreakers = self.context.icebreakers.values() #список ледоколов
        icebreaker_paths = [] #

        logger.info(f"Computing optimal timesheet for context {self.context.to_dict()}")

        result_vessels_paths = []
        caravans = []
        #possible_vessels = self.context.vessels.values() #суда доступные на очередном шаге
        possible_vessels = []
        stucked_vessels = []
        new_vessel_paths = []
        used_wessels = []

        while self.current_time < max_time:

            if len(self.context.vessels) == len(used_wessels):
                break  # выходим, так как все уже посчитали

            possible_vessels = self.get_possible_vessels(self.current_time, self.current_time + self.planing_horizon) #выбираем все доступные суда из диапазона
            possible_vessels += stucked_vessels #добавляем застаканные с прошлого шага
            possible_vessels = list(set(possible_vessels).difference(set(used_wessels))) #удаляем уже проведенные

            logger.info(f"Current Time: {self.current_time}, Planning Horizon: {self.planing_horizon}")
            logger.info(f"Used Vessels Count: {len(used_wessels)}, Used Vessels IDs: {[v.idx for v in used_wessels]}")
            logger.info(f"Possible Vessels Count: {len(possible_vessels)}, Possible Vessels IDs: {[v.idx for v in possible_vessels]}")
            logger.info(f"Currently Stucked Vessels Count: {len(stucked_vessels)}, Currently Stucked Vessels IDs: {[v.idx for v in stucked_vessels]}")

            possible_icebreakers = self.get_possible_icebreakers(icebreakers, #фильтрует все доступные ледоколы оканчивающие проводки до окончания очередного шага
                                                                 self.current_time + self.planing_horizon)
            self.current_time += self.planing_step #сдвигаем время вперед
            new_step = self.optimal_timesheet_for_planing_horizon(vessels=possible_vessels, icebreakers=possible_icebreakers)
            if new_step == ([], [], [], []):
                continue
            new_vessel_paths, new_icebreaker_paths, updated_possible_icebreakers, new_caravans = new_step

            stucked_vessel_ids = [vessel_path.vessel_id for vessel_path in new_vessel_paths if not vessel_path.success]
            unstucked_new_vessel_paths = [vessel_path for vessel_path in new_vessel_paths if vessel_path.success]
            stucked_vessels = [self.context.vessels[idx] for idx in stucked_vessel_ids]
            used_wessels += [self.context.vessels[vessel_path.vessel_id] for vessel_path in unstucked_new_vessel_paths]

            icebreakers = self.update_list_of_objects(icebreakers, updated_possible_icebreakers, id_field="idx")
            result_vessels_paths += unstucked_new_vessel_paths
            icebreaker_paths = self.merge_icebreakers_paths(icebreaker_paths, new_icebreaker_paths)
            caravans += new_caravans

            logger.info(f"Used Vessels Count: {len(used_wessels)}, Used Vessels IDs: {[v.idx for v in used_wessels]}")

            logger.info(
                f"Stucked Vessels Count: {len(stucked_vessels)}, Stucked Vessels IDs: {[v.idx for v in stucked_vessels]}")

        finally_stucked_vessel_paths = [vp for vp in new_vessel_paths if not vp.success]
        logger.info(f"Finally stucked vessels: {finally_stucked_vessel_paths}")
        result_vessels_paths += finally_stucked_vessel_paths

        grade = self.calculate_total_paths_grade(result_vessels_paths)
        # TODO: довозвращать караваны

        for caravan in caravans:
            caravan.template_name = self.context.template_name

        return result_vessels_paths, icebreaker_paths, grade, caravans


if __name__ == "__main__":
    start = time()
    print('===============')
    base = BaseGraph()
    backend_base_dir = Path(__file__).parent
    file_path = backend_base_dir / "input_files/IntegrVelocity.xlsx"
    base = BaseGraph()
    base.set_base_values()
    ice_cond = IceCondition(file_path, base.graph)
    context = Context()
    context.load_from_template('test_1')
    comp = Computer(base, ice_cond, context)
    comp.optimal_timesheet()
    fin = time()
    print('============' + str(fin - start))
