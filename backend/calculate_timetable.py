from backend.calc.computer import Computer
from backend.calc.base_graph import BaseGraph
from backend.calc.ice_cond import IceCondition
from backend.calc.context import Context
from backend.calc.navigator import Navigator
from backend.config import backend_base_dir, recalculate_loaded
from backend.crud.crud_types import TemplatesCRUD, VesselPathCRUD

"""
Весь пайплайн вычисления / инициализация выислителя при старте приложения
"""

file_path = backend_base_dir / "input_files/IntegrVelocity.xlsx"
base = BaseGraph()
base.set_base_values()
ice_cond = IceCondition(file_path, base.graph)
computator = Computer(base, ice_cond)

full_template_name = "full"
templates_crud = TemplatesCRUD()
vessel_paths_crud = VesselPathCRUD()

context = Context()
nav = Navigator()

if recalculate_loaded:
    # считаем реальные оценки
    context.load_from_template_obj(templates_crud.get("full"))
    real_grade, real_vessel_paths, real_icebreaker_paths = computator.optimal_timesheet(context)
    vessel_paths_crud.post_or_put_list(real_vessel_paths)

    # считаем самостоятельные оценки
    context.load_from_template_obj(templates_crud.get("solo"))
    solo_nav_grade, solo_vessel_paths = nav.rough_estimate(base, ice_cond, context)
    vessel_paths_crud.post_or_put_list(solo_vessel_paths.values())

    # считаем лучшие оценки
    context.load_from_template_obj(templates_crud.get("best"))
    best_nav_grade, best_vessel_paths = nav.rough_estimate(base, ice_cond, context, with_best_icebreaker=True)
    vessel_paths_crud.post_or_put_list(best_vessel_paths.values())

