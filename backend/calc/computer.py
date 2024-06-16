from backend.calc.base_graph import BaseGraph
from backend.calc.ice_cond import IceCondition
from backend.calc.navigator import Navigator
from backend.calc.context import Context
from backend.models import Caravan
from queue import PriorityQueue
from vessel import Vessel,IceBreaker
from time import time

class Computer:
    base:BaseGraph
    ice_cond:IceCondition
    context: Context
    navigator: Navigator
    def __init__(self, base, ice_cond, context):
        self.base = base
        self.ice_cond = ice_cond
        self.navigator = Navigator(base=base, ice_cond=ice_cond, context=context)

    def init_app(self):
        pass

    def estimate_caravan_track(self, caravan: Caravan):
        pass

    def find_best_track_for_caravan(self, caravan: Caravan):
        pass

    def optimal_timesheet(self): #-> tuple(Grade, list[VesselPath], list[IcebreakerPath]):
        nav = Navigator(self.base, self.context, self.ice_cond)
        ready_vessels = PriorityQueue()
        #self.priority.put((sm.total_hours - self.ice_move_ways[k].total_hours, k))

        current_time =  next(iter(self.context.vessels)).start_date
        for i,v in self.context.vessels.items():
             current_time = min(current_time,v.start_date)
        print(current_time)


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



