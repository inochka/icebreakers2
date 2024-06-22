from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Dict
from backend.models import (VesselModel, IcebreakerModel, BaseNode, BaseEdge, Template, IcebreakerPath,
                            VesselPath, PostCalcPath, PostCalcPathIce, Caravan)
from datetime import datetime, timedelta
from backend.calc.base_graph import BaseGraph
from backend.data.vessels_data import vessels_data, icebreaker_data
from backend.calc.vessel import Vessel, IceBreaker
from backend.crud.crud_types import TemplatesCRUD, VesselPathCRUD, IcebreakerPathCRUD, GradeCRUD, CaravanCRUD
#from backend.calculate_timetable import computator, ice_cond
from backend.calc.context import Context
from backend.calc.computer import Computer
from backend.config import recalculate_loaded
from backend.utils import replace_inf_nan
from fastapi.middleware.cors import CORSMiddleware
import json
from time import time
from backend.calc.navigator import Grade

comp = Computer()
comp.init_app(recalculate_loaded=False)
start = time()
template_name = 'full'
template: Template =  TemplatesCRUD().get(template_name)
if not template:
    raise Exception("Template not found")
context = Context(template)
vessel_paths_crud = VesselPathCRUD()
icebreaker_paths_crud = IcebreakerPathCRUD()
grades_crud = GradeCRUD()
caravan_crud = CaravanCRUD()

comp.planing_horizon = timedelta(days=7)

print('Template: '+ template_name)
print('Nodes: '+ str(len(comp.base.graph.nodes)))
print('Edges: '+ str(len(comp.base.graph.edges)))
print('max_ships_per_icebreaker: '+ str(comp.max_ships_per_icebreaker))
print('max_T: '+ str(comp.max_T))
print('time_estimate_gate: '+ str(comp.time_estimate_gate))
print('planing_horizon: '+ str(comp.planing_horizon))
print('planing_step: '+ str(comp.planing_step))
print('solo_stuck_time: '+ str(comp.solo_stuck_time))
print('icebreaker_time_fee: '+ str(comp.icebreaker_time_fee))
print('typical_vessel_waiting_time: '+ str(comp.typical_vessel_waiting_time))

comp.context = context
real_vessel_paths, real_icebreaker_paths, real_grade, caravans = comp.optimal_timesheet()

vessel_paths_crud.post_or_put_list(real_vessel_paths)
icebreaker_paths_crud.post_or_put_list(real_icebreaker_paths)
grades_crud.post(real_grade)
caravan_crud.post_or_put_list(caravans)

fin = time()
print('=================================')
print('Template: '+ template_name)
print('Nodes: '+ str(len(comp.base.graph.nodes)))
print('Edges: '+ str(len(comp.base.graph.edges)))
print('max_ships_per_icebreaker: '+ str(comp.max_ships_per_icebreaker))
print('max_T: '+ str(comp.max_T))
print('time_estimate_gate: '+ str(comp.time_estimate_gate))
print('planing_horizon: '+ str(comp.planing_horizon))
print('planing_step: '+ str(comp.planing_step))
print('solo_stuck_time: '+ str(comp.solo_stuck_time))
print('icebreaker_time_fee: '+ str(comp.icebreaker_time_fee))
print('typical_vessel_waiting_time: '+ str(comp.typical_vessel_waiting_time))
print('----------------------------------')
print('Calculation time (s): '+str(fin-start))
print('Best possible time (h): '+str(real_grade.best_possible_time))
print('Total time (h): '+str(real_grade.total_time))
print('Stuck: '+str(real_grade.stuck_vessels))

