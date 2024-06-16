from backend.calc.base_graph import BaseGraph
from backend.calc.navigator import IceCondition
from backend.calc.navigator import Navigator
from backend.models import IcebreakerPath
from backend.constants import icebreake1_params, icebreake2_params


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

        icebreaker1_path = IcebreakerPath(**icebreake1_params)
        icebreaker1_path.template_name = context.template_name

        icebreaker2_path = IcebreakerPath(**icebreake2_params)
        icebreaker2_path.template_name = context.template_name

        return grade, vesselPaths, [icebreaker1_path, icebreaker2_path]