import math
from functools import reduce
from backend.calc.base_graph import BaseGraph
from backend.calc.ice_cond import IceCondition
from backend.calc.navigator import Navigator
from backend.calc.context import Context, Grade
from backend.models import Caravan, VesselPath, IcebreakerPath, SimpleVesselPath, AllSimpleVesselPath, CaravanConfiguration
from queue import PriorityQueue
from vessel import Vessel,IceBreaker
from time import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Computer:
    base:BaseGraph
    ice_cond:IceCondition
    context: Context
    navigator: Navigator

    planing_horizon: timedelta = timedelta(days=7)
    max_ships_per_icebreaker: int = 3
    solo_stuck_time: float = 1e6

    def __init__(self, base, ice_cond, context):
        self.base = base
        self.ice_cond = ice_cond
        self.navigator = Navigator(base=base, ice_cond=ice_cond, context=context)
        self.context = context

    def init_app(self):
        pass

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

        pass

    def calculate_total_paths_grade(self, vessels: List[VesselPath]) -> Grade:
        grade = Grade()
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
                                icebreaker: IceBreaker) -> (float, int, int):

        best_caravan_time = math.inf  # в часах
        a_best = None
        b_best = None

        if not vessel_ids:
            return 0, a_best, b_best

        vessels_obj = {idx: self.context.vessels[idx] for idx in vessel_ids}

        admissible_vertices_from_starts = [self.navigator.reachable_vertices_from_start[v] for v in vessel_ids]
        possible_caravan_starts = list(reduce(set.intersection, map(set, admissible_vertices_from_starts)))

        admissible_vertices_from_ends = [self.navigator.reachable_vertices_from_end[v] for v in vessel_ids]
        possible_caravan_ends = list(reduce(set.intersection, map(set, admissible_vertices_from_ends)))

        # предполагая, что караван собирается и расходится в одной точке
        if not possible_caravan_starts or not possible_caravan_ends:
            return best_caravan_time, a_best, b_best


        for a in possible_caravan_starts:
            for b in possible_caravan_ends:
                if a == b:
                    continue

                # считаем затраты на то, чтобы все суда собрались в точке старта
                caravan_start_time = max([timedelta(hours=self.navigator.path_to_all[idx].paths[a].total_time_hours)
                                    + vessels_obj[idx].start_date for idx in vessel_ids])

                caravan_start_time = max(caravan_start_time, icebreaker.start_date +
                                         timedelta(hours=icebreaker_path_times_to_all.paths[a].total_time_hours))

                total_move_time = sum([(caravan_start_time - vessel.start_date).seconds for vessel in vessels_obj.values()])
                total_move_time = total_move_time / 3600

                # оцениваем время проводки, грубо, посредством идеального ледокола

                total_move_time += self.navigator.best_icebreaker_paths_times[a][b]

                total_move_time += sum([self.navigator.path_from_all[idx].paths[b].total_time_hours for idx in vessel_ids])

                if best_caravan_time > total_move_time:
                    a_best = a
                    b_best = b
                    best_caravan_time = total_move_time

        return best_caravan_time, a_best, b_best

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
                t1, a, b = self.estimate_caravan_profit(distributions[j][i], paths[icebreaker_id], icebreaker)

                if t1 == math.inf:
                    form_caravan = False
                    break

                caravans.append(
                    Caravan(start_node=a, end_node=b, time_estimate=t1, vessel_ids=distributions[j][i],
                            icebreaker_id=icebreaker_id)
                )

                times.append(t1)

            if not form_caravan:
                continue

            caravans_vessels_ids = reduce(set.union, map(set, distributions[j]))
            solo_move_time_for_caravan_vessels = self.estimate_solo_move(list(caravans_vessels_ids))

            outside_caravan_vessels_ids = list(set(vessel_ids).difference(caravans_vessels_ids))

            caravan_vessels_move_time = sum(times)

            solo_move_time_outside_caravan_vessels = self.estimate_solo_move(outside_caravan_vessels_ids)

            # считаем выгодность каравана

            caravans_configurations.append(
                CaravanConfiguration(caravans=caravans, solo_vessel_ids=outside_caravan_vessels_ids,
                                     time_estimate=caravan_vessels_move_time + solo_move_time_outside_caravan_vessels,
                                     configuration_grade = solo_move_time_for_caravan_vessels - caravan_vessels_move_time
                                     )
            )

        return caravans_configurations


    def optimal_timesheet_for_planing_horizon(self, vessels: List[Vessel], icebreakers: List[IceBreaker]) \
            -> (List[VesselPath], List[IcebreakerPath], List[IceBreaker]):
        """
            Распределение судов по ледоколам внутри окна планирования
        """

        vessel_ids = [v.idx for v in vessels]
        icebreaker_ids = [v.idx for v in icebreakers]


        caravans_configuration = self.estimate_possible_caravans(vessel_ids=vessel_ids, icebreaker_ids=icebreaker_ids)

        best_conf = max(caravans_configuration, key=lambda model: model.configuration_grade)
        # TODO: добавить несколько первых и сравнить





    def get_possible_vessels(self, time_from: datetime, time_to: datetime) -> List[Vessel]:
        return list(filter(lambda v: (v.start_date < time_to) and (v.start_date >= time_from), self.context.vessels))

    def get_possible_icebreakers(self, icebreakers: List[IceBreaker], time_from: datetime,
                                 time_to: datetime) -> List[IceBreaker]:
        return list(filter(lambda v: v.start_date < time_to, icebreakers))

    def optimal_timesheet(self) -> (List[VesselPath], List[IcebreakerPath], Grade):

        min_time = min([v.start_date for v in self.context.vessels.values()])
        max_time = max([v.start_date for v in self.context.vessels.values()])

        current_time = min_time
        icebreakers = context.icebreakers.values()
        icebreaker_paths = []

        result_vessels_paths = []

        while current_time < max_time:
            vessels = self.get_possible_vessels(current_time, current_time+self.planing_horizon)
            possible_icebreakers = self.get_possible_icebreakers(icebreakers, current_time, current_time+self.planing_horizon)

            new_vessel_paths, new_icebreaker_paths, updated_possible_icebreakers =\
                self.optimal_timesheet_for_planing_horizon(vessels=vessels, icebreakers=possible_icebreakers)

            icebreakers = self.update_list_of_objects(icebreakers, updated_possible_icebreakers, id_field="idx")
            result_vessels_paths.append(new_vessel_paths)
            icebreaker_paths = self.merge_icebreakers_paths(icebreaker_paths, new_icebreaker_paths)

            current_time += self.planing_horizon

        grade = self.calculate_total_paths_grade(result_vessels_paths)

        return result_vessels_paths, icebreaker_paths, grade


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
    comp = Computer(base,ice_cond,context)
    comp.optimal_timesheet()
    fin = time()
    print('============'+str(fin-start))



