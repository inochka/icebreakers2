from backend.calc.navigator import Navigator,IceCondition,Grade
from backend.calc.base_graph import BaseGraph
from backend.calc.vessel import Vessel,IceBreaker
from backend.calc.context import Context
from backend.models import VesselPath, IcebreakerPath, PathEvent
from backend.calc.navigator import Navigator
from fastapi.encoders import jsonable_encoder

class Computer:
    base:BaseGraph
    ice_cond:IceCondition
    def __init__(self,base,ice_cond):
        self.base = base
        self.ice_cond = ice_cond

    def optimal_timesheet(self, context): #-> tuple(Grade, list[VesselPath], list[IcebreakerPath]):
        nav = Navigator()
        grade, paths = nav.rough_estimate(self.base,self.ice_cond,context)
        vesselPaths = list(paths.values())

        return grade, vesselPaths, None