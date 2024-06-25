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

start = time()

comp = Computer()
comp.init_app(recalculate_loaded=False)

template_name = 'full'
template: Template =  TemplatesCRUD().get(template_name)
if not template:
    raise Exception("Template not found")

vessel_paths_crud = VesselPathCRUD()
icebreaker_paths_crud = IcebreakerPathCRUD()
grades_crud = GradeCRUD()
caravan_crud = CaravanCRUD()

fin = time()
preprocessing_time = fin-start

calc_time = []
total_time = []
total_time = []
total_waiting = []
max_waiting = []
stuck = []

#BEST = 4284 -> 4178 -> 3815
comp.planing_horizon = timedelta(days=7)
comp.planing_step = timedelta(days=3,hours=0)
comp.solo_stuck_time = 15.0 * 24 # вклад во время в часах, предполагая, что судно придется вести отдельным ледоколом #1e6
comp.icebreaker_time_fee = 3.  # насколько время ледокола дороже времени обычного судна
comp.typical_vessel_waiting_time = 3. * 24  # характерное допустимое время ожидания судна в порту

print('Template: '+ template_name)
print('Nodes: '+ str(len(comp.base.graph.nodes)))
print('Edges: '+ str(len(comp.base.graph.edges)))
print('max_ships_per_icebreaker: '+ str(comp.max_ships_per_icebreaker))
print('max_T: '+ str(comp.max_T))
print('planing_horizon: '+ str(comp.planing_horizon))
print('planing_step: '+ str(comp.planing_step))
print('solo_stuck_time: '+ str(comp.solo_stuck_time))
print('icebreaker_time_fee: '+ str(comp.icebreaker_time_fee))
print('typical_vessel_waiting_time: '+ str(comp.typical_vessel_waiting_time))

N = 10
for i in range(N):
    start = time()
    context = Context(template)
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
    print('planing_horizon: '+ str(comp.planing_horizon))
    print('planing_step: '+ str(comp.planing_step))
    print('solo_stuck_time: '+ str(comp.solo_stuck_time))
    print('icebreaker_time_fee: '+ str(comp.icebreaker_time_fee))
    print('typical_vessel_waiting_time: '+ str(comp.typical_vessel_waiting_time))
    print('----------------------------------')
    print('Preprocessing time (s):'+str(preprocessing_time))
    print('Iteration '+str(i))
    print('Calculation time (s): '+str(fin-start))
    print('Best possible time (h): '+str(real_grade.best_possible_time))
    print('Total time (h): '+str(real_grade.total_time))
    print('Total waiting time (h): '+str(real_grade.total_waiting_time))
    print('Max waiting time (h): '+str(real_grade.max_waiting_time))
    print('Stuck: '+str(real_grade.stuck_vessels))
    calc_time.append(fin-start)
    total_time.append(real_grade.total_time)
    total_waiting.append(real_grade.total_waiting_time)
    max_waiting.append(real_grade.max_waiting_time)
    stuck.append(real_grade.stuck_vessels)

print('------------------- Result:')
print('Best possible time (h):'+str(real_grade.best_possible_time))
print('Preprocessing time (s):'+str(preprocessing_time))
print('Calculation time (s): '+str(sum(calc_time) / len(calc_time)))
print('------------------- Average:')
print('Total time (h): '+str(sum(total_time) / len(total_time)))
print('Total waiting time (h): '+str(sum(total_waiting) / len(total_waiting)))
print('Max waiting time (h): '+str(sum(max_waiting) / len(max_waiting)))
print('Stuck: '+str(sum(stuck) / len(stuck)))
print('------------------- Min:')
print('Calculation time (s): '+str(min(calc_time)))
print('Total time (h): '+str(min(total_time)))
print('Total waiting time (h): '+str(min(total_waiting)))
print('Max waiting time (h): '+str(min(max_waiting)))
print('------------------- Max:')
print('Calculation time (s): '+str(max(calc_time)))
print('Total time (h): '+str(max(total_time)))
print('Total waiting time (h): '+str(max(total_waiting)))
print('Max waiting time (h): '+str(max(max_waiting)))
print('------------------ RAW:')
print('Calculation time (s): '+str(calc_time))
print('Total time (h): '+str(total_time))
print('Total waiting time (h): '+str(total_waiting))
print('Max waiting time (h): '+str(max_waiting))