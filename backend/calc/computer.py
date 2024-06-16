from backend.calc.base_graph import BaseGraph
from backend.calc.navigator import IceCondition
from backend.calc.navigator import Navigator


class Computer:
    base:BaseGraph
    ice_cond:IceCondition
    def __init__(self,base,ice_cond):
        self.base = base
        self.ice_cond = ice_cond

    def init_app(self):
        pass

    def optimal_timesheet(self, context): #-> tuple(Grade, list[VesselPath], list[IcebreakerPath]):
        nav = Navigator()
        grade, paths = nav.rough_estimate(self.base,self.ice_cond,context)
        vesselPaths = list(paths.values())

        return grade, vesselPaths, None