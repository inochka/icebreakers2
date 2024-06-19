import logging
import math
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path
from time import time
from typing import List, Any, Optional
from tqdm import tqdm
from fastapi.encoders import jsonable_encoder
import numpy as np
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
    CaravanConfiguration, Grade, IcebreakerPath

logger = logging.getLogger(__name__)

class Computer:
    max_ships_per_icebreaker: int = 3
    max_T: timedelta = timedelta(days=90)
    planing_horizon: timedelta = timedelta(days=14)
    planing_step: timedelta = timedelta(days=3)
    solo_stuck_time: float = 14 * 24
    icebreaker_time_fee: float = 3.0
    estimator_sample_size = 100

    def __init__(self, context: Optional[Context] = None):
        file_path = backend_base_dir / "input_files/IntegrVelocity.xlsx"
        self.base = BaseGraph()
        self.ice_cond = IceCondition(file_path, self.base.graph)
        self.context = context or Context(TemplatesCRUD().get("full"))
        self.navigator = Navigator(base=self.base, ice_cond=self.ice_cond, context=self.context)

    def init_app(self, recalculate_loaded: bool = True):
        templates_crud = TemplatesCRUD()
        vessel_paths_crud = VesselPathCRUD()
        icebreaker_paths_crud = IcebreakerPathCRUD()
        grade_crud = GradeCRUD()
        caravan_crud = CaravanCRUD()

        if recalculate_loaded:
            context = Context(templates_crud.get("full"))
            self.context = context
            real_vessel_paths, real_icebreaker_paths, real_grade, caravans = self.optimal_timesheet()
            vessel_paths_crud.post_or_put_list(real_vessel_paths)
            icebreaker_paths_crud.post_or_put_list(real_icebreaker_paths)
            grade_crud.post(real_grade)
            caravan_crud.post_or_put_list(caravans)

            context = Context(templates_crud.get("solo"))
            self.context = context
            solo_nav_grade, solo_vessel_paths = self.navigator.rough_estimate()
            vessel_paths_crud.post_or_put_list(solo_vessel_paths.values())

            context = Context(templates_crud.get("best"))
            self.context = context
            best_nav_grade, best_vessel_paths = self.navigator.rough_estimate(with_best_icebreaker=True)
            vessel_paths_crud.post_or_put_list(best_vessel_paths.values())

    def generate_distributions(self, n_icebrs: int, ships: List[int]):
        def distribute(remaining_ships, current_distribution):
            if not remaining_ships:
                distributions.append([list(group) for group in current_distribution])
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
        if not paths_old:
            return paths_new

        old_path_dict = {path.icebreaker_id: path for path in paths_old}
        new_path_dict = {path.icebreaker_id: path for path in paths_new}

        for idx, new_path in new_path_dict.items():
            if idx in old_path_dict:
                old_path = old_path_dict[idx]
                old_path.waybill += new_path.waybill
                old_path.path_line += new_path.path_line
                old_path.time_line += new_path.time_line
                old_path.end_date = new_path.end_date
            else:
                old_path_dict[idx] = new_path

        return list(old_path_dict.values())

    def calculate_total_paths_grade(self, vessels: List[VesselPath]) -> Grade:
        total_time = sum(vessel.total_time_hours for vessel in vessels if vessel.success)
        stuck_vessels = sum(1 for vessel in vessels if not vessel.success)
        return Grade(template_name=self.context.template_name, total_time=total_time, stuck_vessels=stuck_vessels)

    @staticmethod
    def update_list_of_objects(old_list: List[Any], updated_values: List[Any], id_field: str) -> List[Any]:
        old_dict = {getattr(obj, id_field): obj for obj in old_list}
        updated_dict = {getattr(obj, id_field): obj for obj in updated_values}
        old_dict.update(updated_dict)
        return list(old_dict.values())

    def estimate_solo_move(self, vessel_ids: List[int]) -> float:
        if not vessel_ids:
            return 0

        solo_movement_times = [self.navigator.solo_move_ways[idx].total_time_hours for idx in vessel_ids]
        best_ib_movement_times = [1.5 * self.navigator.ice_move_ways[idx].total_time_hours + self.solo_stuck_time for idx in vessel_ids]
        return sum(min(solo_time, best_ib_time) for solo_time, best_ib_time in zip(solo_movement_times, best_ib_movement_times))

    def estimate_caravan_profit(self, vessel_ids: List[int], icebreaker_path_times_to_all: AllSimpleVesselPath, icebreaker: IceBreaker, rough: bool = True) -> Optional[Caravan]:
        if not vessel_ids:
            return None

        vessels_obj = {idx: self.context.vessels[idx] for idx in vessel_ids}
        n_vessels = len(vessel_ids)

        admissible_vertices_from_starts = [self.navigator.reachable_vertices_from_start[v] for v in vessel_ids]
        possible_caravan_starts = list(reduce(set.intersection, map(set, admissible_vertices_from_starts)))

        admissible_vertices_from_ends = [self.navigator.reachable_vertices_from_end[v] for v in vessel_ids]
        possible_caravan_ends = list(reduce(set.intersection, map(set, admissible_vertices_from_ends)))

        if not possible_caravan_starts or not possible_caravan_ends:
            return None

        best_caravan = Caravan(total_time_hours=math.inf, icebreaker_time_fee=math.inf)

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

                caravan_start_time = max(timedelta(hours=self.navigator.path_to_all[idx].paths[a].total_time_hours) + vessels_obj[idx].start_date for idx in vessel_ids)
                caravan_start_time = max(caravan_start_time, icebreaker.start_date + timedelta(hours=icebreaker_path_times_to_all.paths[a].total_time_hours))

                total_move_time = sum((caravan_start_time - vessel.start_date).total_seconds() / 3600 for vessel in vessels_obj.values())
                total_move_time += sum(self.navigator.path_from_all[idx].paths[b].total_time_hours for idx in vessel_ids)

                if rough:
                    time_in_caravan = self.navigator.best_icebreaker_paths_times[a][b]
                else:
                    time_in_caravan = max(self.navigator.calc_shortest_path(v, source_node=a, target_node=b,
                                                                            start_time=caravan_start_time,
                                                                            icebreaker=icebreaker).total_time_hours
                                          for v in vessels_obj.values())

                total_move_time += n_vessels * time_in_caravan
                icebreaker_time_fee = time_in_caravan + (caravan_start_time - icebreaker.start_date).total_seconds() / 3600

                if best_caravan.total_time_hours > total_move_time:
                    best_caravan = Caravan(total_time_hours=total_move_time, icebreaker_time_fee=icebreaker_time_fee, start_node=a, end_node=b, vessel_ids=vessel_ids, icebreaker_id=icebreaker.idx, start_time=caravan_start_time)
        # TODO: может, нужно все оптимумы возвращать, а не только один??
        return best_caravan if best_caravan.total_time_hours < math.inf else None

    def estimate_possible_caravans(self, vessel_ids: List[int], icebreaker_ids: List[int]):
        logger.info(f"Estimating possible caravans for vessels {vessel_ids} and icebreakers {icebreaker_ids}")
        paths = {idx: self.navigator.calc_shortest_path(self.context.icebreakers[idx]) for idx in icebreaker_ids}
        distributions = self.generate_distributions(len(icebreaker_ids), vessel_ids)

        logger.info(f"Found {len(distributions)} variants!")

        #indices = np.random.choice(len(distributions), self.estimator_sample_size, replace=False)

        


        suitable_distributions = []

        for distr in tqdm(distributions):
            form_caravan = True
            for i, icebreaker_id in enumerate(icebreaker_ids):
                icebreaker = self.context.icebreakers[icebreaker_id]
                caravan = self.estimate_caravan_profit(distr[i], paths[icebreaker_id], icebreaker, rough=False)
                if not caravan:
                    form_caravan = False
                    break
            if form_caravan:
                suitable_distributions.append(distr)

        logger.info(f"Obtained {len(suitable_distributions)} possible caravan configurations!")

        caravans_configurations = []
        for distr in tqdm(suitable_distributions):
            caravans = []
            form_caravan = True
            for i, icebreaker_id in enumerate(icebreaker_ids):
                icebreaker = self.context.icebreakers[icebreaker_id]
                caravan = self.estimate_caravan_profit(distr[i], paths[icebreaker_id], icebreaker, rough=False)
                if not caravan:
                    form_caravan = False
                    break
                caravans.append(caravan)

            if form_caravan:
                caravans_vessels_ids = reduce(set.union, map(set, distr)) if distr else set()
                solo_move_time_for_caravan_vessels = self.estimate_solo_move(list(caravans_vessels_ids))
                outside_caravan_vessels_ids = list(set(vessel_ids).difference(caravans_vessels_ids))
                caravan_vessels_move_time = sum(caravan.total_time_hours for caravan in caravans)
                icebreakers_time_fee = sum(caravan.icebreaker_time_fee for caravan in caravans)
                solo_move_time_outside_caravan_vessels = self.estimate_solo_move(outside_caravan_vessels_ids)

                caravans_configurations.append(
                    CaravanConfiguration(caravans=caravans, solo_vessel_ids=outside_caravan_vessels_ids, total_time_hours=caravan_vessels_move_time + solo_move_time_outside_caravan_vessels, configuration_grade=solo_move_time_for_caravan_vessels - caravan_vessels_move_time, icebreakers_time_fee=icebreakers_time_fee)
                )

        return caravans_configurations

    def grade_caravans_configuration(self, conf: CaravanConfiguration):
        total_used_vessels_num = len(conf.solo_vessel_ids) + sum(len(caravan.vessel_ids) for caravan in conf.caravans)
        return -conf.total_time_hours, total_used_vessels_num, -conf.icebreakers_time_fee, conf.configuration_grade

    def optimal_timesheet_for_planing_horizon(self, vessels: List[Vessel], icebreakers: List[IceBreaker]) -> (List[VesselPath], List[IcebreakerPath], List[IceBreaker], List[Caravan]):
        logger.info(f"Making horizon timetable for icebreakers {jsonable_encoder(icebreakers)} and vessels {jsonable_encoder(vessels)}")
        vessel_ids = [v.idx for v in vessels]
        icebreaker_ids = [v.idx for v in icebreakers]
        caravans_configurations = self.estimate_possible_caravans(vessel_ids=vessel_ids, icebreaker_ids=icebreaker_ids)

        if not caravans_configurations:
            return [], [], [], []

        conf = max(caravans_configurations, key=self.grade_caravans_configuration)
        logger.info(f"Found best caravan configuration: {jsonable_encoder(conf)}")

        vessel_paths, icebreaker_paths = self.convert_caravan_conf_to_ship_paths(conf)
        used_icebreaker_ids = [caravan.icebreaker_id for caravan in conf.caravans if caravan.vessel_ids]
        icebreakers_dict = {ib.idx: ib for ib in icebreakers}

        updated_icebreakers = [icebreakers_dict[idx] for idx, icebreaker_path in icebreaker_paths.items()
                               if idx in used_icebreaker_ids]

        for idx, icebreaker_path in icebreaker_paths.items():
            if idx not in used_icebreaker_ids:
                continue
            updated_ib = icebreakers_dict[idx]
            updated_ib.source = icebreaker_path.waybill[-1].point
            updated_ib.start_date = icebreaker_path.waybill[-1].dt
            updated_ib.source_name = self.base.graph.nodes[updated_ib.source]["point_name"]

        return list(vessel_paths.values()), list(icebreaker_paths.values()), updated_icebreakers, conf.caravans

    def convert_caravan_conf_to_ship_paths(self, caravan_conf: CaravanConfiguration) -> (List[VesselPath], List[IcebreakerPath]):
        icebreaker_paths = {}
        vessel_paths = {}

        for idx in caravan_conf.solo_vessel_ids:
            vessel_paths[idx] = self.navigator.solo_move_ways[idx]

        for caravan in caravan_conf.caravans:
            icebreaker = self.context.icebreakers[caravan.icebreaker_id]

            if icebreaker.source != caravan.start_node:
                icebreaker_simple_path_before = self.navigator.calc_shortest_path(icebreaker, source_node=icebreaker.source,
                                                                                  target_node=caravan.start_node,
                                                                                  start_time=icebreaker.start_date)
                ib_arrival_date = icebreaker.start_date + timedelta(hours=icebreaker_simple_path_before.total_time_hours)
                waiting_time = max(0, (caravan.start_time - ib_arrival_date).total_seconds() / 3600)
                icebreaker_waybill_before = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_before,
                                                                                          icebreaker.start_date,
                                                                                          icebreaker.source,
                                                                                          PathEventsType.wait if waiting_time > 0 else PathEventsType.formation)
            else:
                icebreaker_waybill_before = []
                icebreaker_simple_path_before = SimpleVesselPath()
                ib_arrival_date = icebreaker.start_date

            icebreaker_simple_path_in = self.navigator.calc_shortest_path(icebreaker, source_node=caravan.start_node, target_node=caravan.end_node, start_time=caravan.start_time)
            caravan_end_time = caravan.start_time + timedelta(hours=icebreaker_simple_path_in.total_time_hours)
            # TODO: перенести в расчет при оценке точной end_time в караван + туда же добавить маршруты
            icebreaker_waybill_in = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_in, caravan.start_time, caravan.start_node, PathEventsType.wait, PathEventsType.formation)

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

            for idx in caravan.vessel_ids:
                vessel = self.context.vessels[idx]
                if caravan.start_node != vessel.source:
                    simple_path_before = self.navigator.path_to_all[idx].paths[caravan.start_node]
                    time_before = simple_path_before.total_time_hours
                    vessel_caravan_start_arrival_date = vessel.start_date + timedelta(hours=time_before) if time_before != math.inf else None
                    waybill_before = self.navigator.convert_simple_path_to_waybill(simple_path_before, vessel.start_date, vessel.source, PathEventsType.formation)

                    if vessel_caravan_start_arrival_date < caravan.start_time:
                        waiting_time = (caravan.start_time - vessel_caravan_start_arrival_date).total_seconds() / 3600
                        waybill_before = ([PathEvent(event=PathEventsType.wait, point=vessel.source, dt=vessel.start_date)]
                                          + self.navigator.shift_waybill(waybill_before, timedelta(hours=waiting_time)))
                else:
                    waybill_before = []
                    time_before = 0
                    simple_path_before = SimpleVesselPath()

                end_type = PathEventsType.fin if caravan.end_node == vessel.target else PathEventsType.move
                waybill_in = self.navigator.convert_simple_path_to_waybill(icebreaker_simple_path_in, caravan.start_time, caravan.start_node, end_type, PathEventsType.formation)

                if end_type != PathEventsType.fin:
                    simple_path_after = self.navigator.calc_shortest_path(vessel, source_node=caravan.end_node, target_node=vessel.target, start_time=caravan_end_time)
                    waybill_after = self.navigator.convert_simple_path_to_waybill(simple_path_after, caravan_end_time, caravan.end_node, PathEventsType.fin)
                    vessel_end_date = caravan_end_time + timedelta(hours=simple_path_after.total_time_hours)
                else:
                    waybill_after = []
                    simple_path_after = SimpleVesselPath()
                    vessel_end_date = caravan_end_time

                total_time_hours = simple_path_before.total_time_hours + icebreaker_simple_path_in.total_time_hours + simple_path_after.total_time_hours

                vessel_paths[idx] = VesselPath(
                    total_time_hours=total_time_hours,
                    start_date=vessel.start_date,
                    end_date=vessel_end_date,
                    source=vessel.source,
                    source_name=self.base.graph.nodes[vessel.source]["point_name"],
                    target=vessel.target,
                    target_name=self.base.graph.nodes[vessel.target]["point_name"],
                    success=True,
                    waybill=waybill_before + waybill_in + waybill_after,
                    path_line=simple_path_before.path_line + icebreaker_simple_path_in.path_line + simple_path_after.path_line,
                    template_name=self.context.template_name,
                    vessel_id=idx,
                    time_line=simple_path_before.time_line + icebreaker_simple_path_in.time_line + simple_path_after.time_line
                )

        return vessel_paths, icebreaker_paths

    def get_possible_vessels(self, time_from: datetime, time_to: datetime) -> List[Vessel]:
        return [v for v in self.context.vessels.values() if time_from <= v.start_date <= time_to]

    def get_possible_icebreakers(self, icebreakers: List[IceBreaker], time_from: datetime, time_to: datetime) -> List[IceBreaker]:
        return [ib for ib in icebreakers if ib.start_date < time_to]

    def optimal_timesheet(self) -> (List[VesselPath], List[IcebreakerPath], Grade, List[Caravan]):
        min_time = min(v.start_date for v in self.context.vessels.values())
        max_time = max(v.start_date for v in self.context.vessels.values()) + self.max_T
        current_time = min_time
        icebreakers = list(self.context.icebreakers.values())
        icebreaker_paths = []

        logger.info(f"Computing optimal timesheet for context {self.context.to_dict()}")

        result_vessels_paths = []
        caravans = []
        stucked_vessels = []

        while current_time < max_time:
            if len(self.context.vessels) == len(result_vessels_paths):
                break

            vessels = list(set(self.get_possible_vessels(current_time, current_time + self.planing_horizon)).difference(set(result_vessels_paths))) + stucked_vessels
            logger.info(f"Current Time: {current_time}, Planning Horizon: {self.planing_horizon}")
            logger.info(f"Possible Vessels Count: {len(vessels)}, Vessels IDs: {[v.idx for v in vessels]}")
            current_time += self.planing_step

            possible_icebreakers = self.get_possible_icebreakers(icebreakers, current_time, current_time + self.planing_horizon)
            new_vessel_paths, new_icebreaker_paths, updated_possible_icebreakers, new_caravans = self.optimal_timesheet_for_planing_horizon(vessels=vessels, icebreakers=possible_icebreakers)

            if not new_vessel_paths:
                continue

            stucked_vessel_ids = [vessel_path.vessel_id for vessel_path in new_vessel_paths if not vessel_path.success]
            unstucked_new_vessel_paths = [vessel_path for vessel_path in new_vessel_paths if vessel_path.success]
            stucked_vessels = [self.context.vessels[idx] for idx in stucked_vessel_ids]

            icebreakers = self.update_list_of_objects(icebreakers, updated_possible_icebreakers, id_field="idx")
            result_vessels_paths += unstucked_new_vessel_paths
            icebreaker_paths = self.merge_icebreakers_paths(icebreaker_paths, new_icebreaker_paths)
            caravans += new_caravans

            logger.info(f"Used Vessels Count: {len(result_vessels_paths)}, Used Vessels IDs: {[v.vessel_id for v in result_vessels_paths if v.success]}")
            logger.info(f"Stucked Vessels Count: {len(stucked_vessels)}, Stucked Vessels IDs: {[v.idx for v in stucked_vessels]}")

        grade = self.calculate_total_paths_grade(result_vessels_paths)
        for caravan in caravans:
            caravan.template_name = self.context.template_name

        return result_vessels_paths, icebreaker_paths, grade, caravans

if __name__ == "__main__":
    start = time()
    print('===============')
    base = BaseGraph()
    backend_base_dir = Path(__file__).parent
    file_path = backend_base_dir / "input_files/IntegrVelocity.xlsx"
    base.set_base_values()
    ice_cond = IceCondition(file_path, base.graph)
    context = Context()
    context.load_from_template('test_1')
    comp = Computer(context)
    comp.optimal_timesheet()
    fin = time()
    print('============' + str(fin - start))
