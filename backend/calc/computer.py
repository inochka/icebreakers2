from backend.calc.navigator import Navigator,IceCondition,Grade
from base_graph import BaseGraph
from vessel import Vessel,IceBreaker
from context import Context
from backend.models import VesselPath, IcebreakerPath, PathEvent
from navigator import Navigator

class Computer:
    base:BaseGraph
    ice_cond:IceCondition
    def __init__(self,base,ice_cond):
        self.base = base
        self.ice_cond = ice_cond

    def optimal_timesheet(self, context): #-> tuple(Grade, list[ShipPath], list[IcebreakerPath]):
        nav = Navigator()
        grade,paths = nav.rough_estimate(self.base,self.ice_cond,context)
        vesselPaths = []
        for vid, path in paths.items():
            model = VesselPath(**path)
            model.vessel_id = vid
            vesselPaths.append(model)
        return grade, vesselPaths, None