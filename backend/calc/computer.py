import logging
import math
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path
from time import time
from typing import List, Any

from fastapi.encoders import jsonable_encoder

from backend.calc.base_graph import BaseGraph
from backend.calc.context import Context
from backend.calc.ice_cond import IceCondition
from backend.calc.navigator import Navigator
from backend.calc.vessel import Vessel, IceBreaker
from backend.config import backend_base_dir
from backend.constants import PathEventsType
from backend.crud.crud_types import (TemplatesCRUD, VesselPathCRUD, IcebreakerPathCRUD,
                                     CaravanCRUD, GradeCRUD)
from backend.models import Caravan, VesselPath, SimpleVesselPath, AllSimpleVesselPath, \
    CaravanConfiguration, Grade

logger = logging.getLogger(__name__)
from backend.models import IcebreakerPath


class Computer:
    base: BaseGraph
    ice_cond: IceCondition
    context: Context
    navigator: Navigator

    planing_horizon: timedelta = timedelta(days=14) #timedelta(days=7)
    max_ships_per_icebreaker: int = 3
    solo_stuck_time: float = 1e6

    def __init__(self, context: Context | None = None):
        file_path = backend_base_dir / "input_files/IntegrVelocity.xlsx"
        base = BaseGraph()
        base.set_base_values()
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
            solo_nav_grade, solo_vessel_paths = self.navigator.rough_estimate()
            vessel_paths_crud.post_or_put_list(solo_vessel_paths.values())

            # считаем лучшие оценки
            context = Context(templates_crud.get("best"))
            self.context = context
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
                    source=old_path_dict[idx].source,
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
        grade = Grade(template_name=self.context.template_name)
        for vessel in vessels:
            if vessel.success:
                grade.total_time += vessel.total_time_hours
            else:
                grade.stuck_vessels += 1

        return grade

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

        return sum([min(self.navigator.solo_move_ways[idx].total_time_hours, self.solo_stuck_time)
                    for idx in vessel_ids])

    def estimate_caravan_profit(self, vessel_ids: List[int], icebreaker_path_times_to_all: AllSimpleVesselPath,
                                icebreaker: IceBreaker) -> (float, int, int, datetime):

        best_caravan_time = math.inf  # в часах
        a_best = None
        b_best = None
        caravan_start_time = None

        if not vessel_ids:
            return 0, a_best, b_best, caravan_start_time

        vessels_obj = {idx: self.context.vessels[idx] for idx in vessel_ids}

        admissible_vertices_from_starts = [self.navigator.reachable_vertices_from_start[v] for v in vessel_ids]
        possible_caravan_starts = list(reduce(set.intersection, map(set, admissible_vertices_from_starts)))

        admissible_vertices_from_ends = [self.navigator.reachable_vertices_from_end[v] for v in vessel_ids]
        possible_caravan_ends = list(reduce(set.intersection, map(set, admissible_vertices_from_ends)))

        # предполагая, что караван собирается и расходится в одной точке
        if not possible_caravan_starts or not possible_caravan_ends:
            return best_caravan_time, a_best, b_best, caravan_start_time

        for a in possible_caravan_starts:
            for b in possible_caravan_ends:
                if a == b:
                    continue

                # считаем затраты на то, чтобы все суда собрались в точке старта
                caravan_start_time = max([timedelta(hours=self.navigator.path_to_all[idx].paths[a].total_time_hours)
                                          + vessels_obj[idx].start_date for idx in vessel_ids])

                caravan_start_time = max(caravan_start_time, icebreaker.start_date +
                                         timedelta(hours=icebreaker_path_times_to_all.paths[a].total_time_hours))

                total_move_time = sum(
                    [(caravan_start_time - vessel.start_date).seconds for vessel in vessels_obj.values()])
                total_move_time = total_move_time / 3600

                # оцениваем время проводки, грубо, посредством идеального ледокола

                total_move_time += self.navigator.best_icebreaker_paths_times[a][b]

                total_move_time += sum(
                    [self.navigator.path_from_all[idx].paths[b].total_time_hours for idx in vessel_ids])

                if best_caravan_time > total_move_time:
                    a_best = a
                    b_best = b
                    best_caravan_time = total_move_time

        return best_caravan_time, a_best, b_best, caravan_start_time

    def estimate_possible_caravans(self, vessel_ids: List[int], icebreaker_ids: List[int]):
        logger.info(f"Estimating possible caravans for vessels {vessel_ids} and icebreakers {icebreaker_ids}")
        paths = {idx: self.navigator.calc_shortest_path(self.context.icebreakers[idx]) for idx in icebreaker_ids}
        distributions = self.generate_distributions(len(icebreaker_ids), vessel_ids)

        logger.info(f"Found {len(distributions)} variants!")

        caravans_configurations = []

        for j in range(len(distributions)):
            times = []
            caravans = []
            form_caravan = True
            for i in range(len(icebreaker_ids)):
                icebreaker_id = icebreaker_ids[i]
                icebreaker = self.context.icebreakers[icebreaker_id]
                t1, a, b, caravan_start_time = self.estimate_caravan_profit(distributions[j][i], paths[icebreaker_id],
                                                                            icebreaker)

                if (t1 == math.inf) or (t1 == 0) or (a is None) or (b is None):
                    form_caravan = False
                    break

                caravans.append(
                    Caravan(start_node=a, end_node=b, time_estimate=t1, vessel_ids=distributions[j][i],
                            icebreaker_id=icebreaker_id, start_time=caravan_start_time)
                )

                times.append(t1)

            if not form_caravan:
                continue

            if distributions[j]:
                caravans_vessels_ids = reduce(set.union, map(set, distributions[j]))
            else:
                caravans_vessels_ids = []

            solo_move_time_for_caravan_vessels = self.estimate_solo_move(list(caravans_vessels_ids))

            outside_caravan_vessels_ids = list(set(vessel_ids).difference(caravans_vessels_ids))

            caravan_vessels_move_time = sum(times)

            solo_move_time_outside_caravan_vessels = self.estimate_solo_move(outside_caravan_vessels_ids)

            # считаем выгодность каравана

            caravans_configurations.append(
                CaravanConfiguration(caravans=caravans, solo_vessel_ids=outside_caravan_vessels_ids,
                                     time_estimate=caravan_vessels_move_time + solo_move_time_outside_caravan_vessels,
                                     configuration_grade=solo_move_time_for_caravan_vessels - caravan_vessels_move_time
                                     )
            )

        return caravans_configurations

    def optimal_timesheet_for_planing_horizon(self, vessels: List[Vessel], icebreakers: List[IceBreaker]) \
            -> (List[VesselPath], List[IcebreakerPath], List[IceBreaker], List[Caravan]):
        """
            Распределение судов по ледоколам внутри окна планирования
        """

        logger.info(f"Making horizon timetable for icebreakers {jsonable_encoder(icebreakers)} and "
                    f"vessels {jsonable_encoder(vessels)}")

        vessel_ids = [v.idx for v in vessels]
        icebreaker_ids = [v.idx for v in icebreakers]
        caravans_configuration = self.estimate_possible_caravans(vessel_ids=vessel_ids, icebreaker_ids=icebreaker_ids)

        best_conf: CaravanConfiguration = max(caravans_configuration, key=lambda model: model.configuration_grade)
        # TODO: добавить несколько первых и сравнить

        vessel_paths, icebreaker_paths = self.convert_caravan_conf_to_ship_paths(best_conf)

        used_icebreaker_ids = [caravan.icebreaker_id for caravan in best_conf.caravans if caravan.vessel_ids]
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

        return list(vessel_paths.values()), list(icebreaker_paths.values()), updated_icebreakers, best_conf.caravans

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
                end_date = icebreaker.start_date + timedelta(hours=icebreaker_simple_path_before.total_time_hours)
                if end_date < caravan.start_time:
                    waiting_time = (caravan.start_time - end_date).seconds / 3600
                    end_type = PathEventsType.wait

                icebreaker_waybill_before = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_before,
                                                                                          icebreaker.start_date,
                                                                                          icebreaker.source,
                                                                                          end_type)

            else:
                icebreaker_waybill_before = []
                icebreaker_simple_path_before = SimpleVesselPath()



            icebreaker_simple_path_in = self.navigator.calc_shortest_path(icebreaker,
                                                                          source_node=caravan.start_node,
                                                                          target_node=caravan.end_node,
                                                                          start_time=caravan.start_time)

            caravan_end_time = caravan.start_time + timedelta(hours=icebreaker_simple_path_in.total_time_hours)

            # движение в караване
            icebreaker_waybill_in = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_in,
                                                                                  caravan.start_time,
                                                                                  caravan.start_node,
                                                                                  PathEventsType.wait,
                                                                                  PathEventsType.formation
                                                                                  )

            icebreaker_paths[caravan.icebreaker_id] = IcebreakerPath(
                start_date=icebreaker.start_date,
                end_date=end_date,
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

                # обрабатываем случай сборки каравана в порту
                if caravan.start_node != v.source:
                    simple_path_before = self.navigator.path_to_all[idx].paths[caravan.start_node]
                    time_before = simple_path_before.total_time_hours
                    end_date = v.start_date + timedelta(hours=time_before) if time_before != math.inf else None

                    waiting_time = 0
                    end_type = PathEventsType.formation
                    if end_date < caravan.start_time:
                        waiting_time = (caravan.start_time - end_date).seconds / 3600
                        end_type = PathEventsType.wait

                    waybill_before = self.navigator.convert_simple_path_to_waybill(simple_path_before, v.start_date,
                                                                                   v.source, end_type)
                else:
                    waybill_before = []
                    simple_path_before = SimpleVesselPath()

                if caravan.end_node == v.target:
                    end_type = PathEventsType.fin
                else:
                    end_type = PathEventsType.move

                # движение в караване
                waybill_in = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_in,
                                                                           caravan.start_time,
                                                                           caravan.start_node, end_type,
                                                                           PathEventsType.formation)

                if end_type != PathEventsType.fin:
                    simple_path_after = self.navigator.calc_shortest_path(v, source_node=caravan.end_node,
                                                                          target_node=v.target,
                                                                          start_time=caravan_end_time)

                    waybill_after = self.navigator.convert_simple_path_to_waybill(simple_path_after, caravan_end_time,
                                                                                  caravan.end_node, PathEventsType.fin)
                else:
                    waybill_after = []
                    simple_path_after = SimpleVesselPath()

                # TODO: проверить, не проебаны ли смежные ребра
                total_time_hours = (simple_path_before.total_time_hours + icebreaker_simple_path_in.total_time_hours
                                    + simple_path_after.total_time_hours)

                vessel_paths[idx] = VesselPath(
                    total_time_hours=total_time_hours,
                    start_date=v.start_date,
                    end_date=end_date,
                    source=v.source,
                    source_name=self.base.graph.nodes[v.source]["point_name"],
                    target=v.target,
                    target_name=self.base.graph.nodes[v.target]["point_name"],
                    success=True,  # мы не брали суда в караван, если они не смогут дойти
                    waybill=waybill_before + waybill_in + waybill_after,
                    path_line=simple_path_before.path_line + icebreaker_simple_path_in.path_line + simple_path_after.path_line,
                    template_name=self.context.template_name,
                    vessel_id=idx,
                    time_line=simple_path_before.time_line + icebreaker_simple_path_in.time_line + simple_path_after.time_line
                )

        return vessel_paths, icebreaker_paths

    def get_possible_vessels(self, time_from: datetime, time_to: datetime) -> List[Vessel]:
        return list(filter(lambda v: (v.start_date < time_to) and (v.start_date >= time_from),
                           list(self.context.vessels.values())))

    def get_possible_icebreakers(self, icebreakers: List[IceBreaker], time_from: datetime,
                                 time_to: datetime) -> List[IceBreaker]:
        return list(filter(lambda v: v.start_date < time_to, icebreakers))

    def optimal_timesheet(self) -> (List[VesselPath], List[IcebreakerPath], Grade, List[Caravan]):

        min_time = min([v.start_date for v in self.context.vessels.values()])
        max_time = max([v.start_date for v in self.context.vessels.values()])

        current_time = min_time
        icebreakers = self.context.icebreakers.values()
        icebreaker_paths = []

        logger.info(f"Computing optimal timesheet for context {self.context.to_dict()}")

        result_vessels_paths = []
        caravans = []

        while current_time < max_time:
            vessels = self.get_possible_vessels(current_time, current_time + self.planing_horizon)
            possible_icebreakers = self.get_possible_icebreakers(icebreakers, current_time,
                                                                 current_time + self.planing_horizon)

            new_vessel_paths, new_icebreaker_paths, updated_possible_icebreakers, new_caravans = \
                self.optimal_timesheet_for_planing_horizon(vessels=vessels, icebreakers=possible_icebreakers)

            icebreakers = self.update_list_of_objects(icebreakers, updated_possible_icebreakers, id_field="idx")
            result_vessels_paths += new_vessel_paths
            icebreaker_paths = self.merge_icebreakers_paths(icebreaker_paths, new_icebreaker_paths)
            caravans += new_caravans
            current_time += self.planing_horizon

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
