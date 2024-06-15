from backend.calc.base_graph import BaseGraph
from backend.calc.ice_cond import IceCondition
from backend.calc.navigator import Navigator
from backend.calc.context import Context
from backend.models import Caravan


class Computer:
    base:BaseGraph
    ice_cond:IceCondition
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

    def optimal_timesheet(self, context): #-> tuple(Grade, list[VesselPath], list[IcebreakerPath]):
        #nav = Navigator(self.base, self.ice_cond)
        #grade, paths = nav.rough_estimate()
        #vesselPaths = list(paths.values())
        #return grade, vesselPaths, None
        pass





