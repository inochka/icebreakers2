from backend.calc.base_graph import BaseGraph
from backend.calc.ice_cond import IceCondition
from backend.calc.navigator import Navigator
from backend.calc.context import Context, Grade
from backend.models import Caravan, VesselPath, IcebreakerPath
from queue import PriorityQueue
from vessel import Vessel,IceBreaker
from time import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

class Computer:
    base:BaseGraph
    ice_cond:IceCondition
    context: Context
    navigator: Navigator

    planing_horizon: timedelta = timedelta(days=7)

    def __init__(self, base, ice_cond, context):
        self.base = base
        self.ice_cond = ice_cond
        self.navigator = Navigator(base=base, ice_cond=ice_cond, context=context)

    def init_app(self):
        pass

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

    def estimate_caravan_profit(self, caravan: Caravan) -> Grade:
        pass


    def compute_optimal_track_for_caravan(self, caravan: Caravan) -> (List[VesselPath], IcebreakerPath, Grade):
        pass

    def optimal_timesheet_for_planing_horizon(self, vessels: List[Vessel], icebreakers: List[IceBreaker]) -> \
            (List[VesselPath], List[IcebreakerPath], List[IceBreaker]):
        """
            Распределение судов по ледоколам внутри окна планирования
        """

        vessels_queue = PriorityQueue()
        icebreakers_paths_from_current_pos = {icebreaker.idx: self.navigator.calc_shortest_path(icebreaker)
                                              for icebreaker in icebreakers}

        icebreakers_vessels_distribution = {icebreaker.idx: [] for icebreaker in icebreakers}
        # [icebreaker_id, [vessels_ids]]

        for v in vessels:
            vessels_queue.put((self.navigator.priority[v.idx], v))

        while vessels_queue.not_empty:
            v = vessels_queue.get()[1]

            icebreaker_times_to_v = {idx: all_paths.paths[v.source].total_time_hours
                                     for idx, all_paths in icebreakers_paths_from_current_pos.items()}

            opt_icebreaker_id = min(icebreaker_times_to_v, key=icebreaker_times_to_v.get)






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



