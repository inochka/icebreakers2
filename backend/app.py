from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Dict
from backend.models import (VesselModel, IcebreakerModel, BaseNode, BaseEdge, Template, IcebreakerPath,
                            VesselPath, PostCalcPath, PostCalcPathIce, Caravan)
from datetime import datetime
from backend.calc.base_graph import BaseGraph
from backend.data.vessels_data import vessels_data, icebreaker_data
from backend.calc.vessel import Vessel, IceBreaker
from backend.crud.crud_types import TemplatesCRUD, VesselPathCRUD, IcebreakerPathCRUD, GradeCRUD, CaravanCRUD
#from backend.calculate_timetable import computator, ice_cond
from backend.calc.context import Context
from backend.calc.computer import Computer
from backend.config import recalculate_loaded, tiffs_dir
from backend.utils import replace_inf_nan
from fastapi.middleware.cors import CORSMiddleware

import json
import os


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все адреса
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

comp = Computer()

@app.on_event('startup')
def init():
    comp.init_app(recalculate_loaded=recalculate_loaded)


@app.middleware("http")
async def replace_inf_middleware(request, call_next):
    response = await call_next(request)
    if response.media_type == "application/json":
        body = await response.body()
        content = json.loads(body)
        processed_content = replace_inf_nan(content)
        response = JSONResponse(content=processed_content)
    return response

@app.get("/get_base_nodes/", response_model=List[BaseNode])
async def get_nodes():
    graph = BaseGraph()
    return JSONResponse(jsonable_encoder(graph.make_list_of_models_for_nodes()))

@app.get("/get_base_edges/", response_model=List[BaseEdge])
async def get_edges():
    graph = BaseGraph()
    return JSONResponse(jsonable_encoder(graph.make_list_of_models_for_edges()))

@app.get("/vessels/", response_model = VesselModel | List[VesselModel])
async def get_vessel(id: int | None = None):

    if not id:
        vessels = [Vessel.make_model_from_dict_entry(id, vessels_data[id]) for id in vessels_data]
        return JSONResponse(jsonable_encoder(vessels))

    if id in vessels_data:
        return JSONResponse(jsonable_encoder(Vessel.make_model_from_dict_entry(id, vessels_data[id])))

    raise HTTPException(status_code=404, detail="Vessel not found")


@app.get("/icebreakers/", response_model = IcebreakerModel | List[IcebreakerModel])
async def get_icebreaker(id: int | None = None):
    if not id:
        icebreakers = [IceBreaker.make_model_from_dict_entry(id, icebreaker_data[id]) for id in icebreaker_data]
        return JSONResponse(jsonable_encoder(icebreakers))

    if id in icebreaker_data:
        return JSONResponse(jsonable_encoder(IceBreaker.make_model_from_dict_entry(id, icebreaker_data[id])))

    raise HTTPException(status_code=404, detail="Vessel not found")


@app.get("/template/", response_model=Template)
async def get_template(template_name: str = ""):
    """
    Получение шаблона по имени
    """
    crud = TemplatesCRUD()
    if template_name:
        item = crud.get(template_name)
        if not item:
            raise HTTPException(status_code=404, detail="Template not found")
        return JSONResponse(jsonable_encoder(item))
    else:
        return JSONResponse(jsonable_encoder(crud.get_all()))

@app.delete("/template/", response_model=Template)
async def delete_template(template_name: str):
    """
        Удаление шаблона
    """
    crud = TemplatesCRUD()
    item = crud.delete(template_name)
    if not item:
        raise HTTPException(status_code=404, detail="Template not found")
    return JSONResponse(jsonable_encoder(item))

@app.post("/template/", response_model=Template)
async def post_template(template: Template):
    """
        Публикация шаблона
    """
    crud = TemplatesCRUD()
    # TODO: добавить проверку на корректность идентификаторов ледоколов и судов, пока пох
    return JSONResponse(jsonable_encoder(crud.post(template)))


@app.post("/calculation_request/", response_model=Dict[str, List[IcebreakerPath | VesselPath]])
async def post_calculation_request(template_name: str):
    """
    Заявка на расчет по шаблону template_name
    """
    template: Template =  TemplatesCRUD().get(template_name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")


    context = Context(template)
    vessel_paths_crud = VesselPathCRUD()
    icebreaker_paths_crud = IcebreakerPathCRUD()
    grades_crud = GradeCRUD()
    caravan_crud = CaravanCRUD()

    comp.context = context
    real_vessel_paths, real_icebreaker_paths, real_grade, caravans = comp.optimal_timesheet()

    vessel_paths_crud.post_or_put_list(real_vessel_paths)
    icebreaker_paths_crud.post_or_put_list(real_icebreaker_paths)
    grades_crud.post(real_grade)
    caravan_crud.post_or_put_list(caravans)

    return_dict = {
        "vessels": real_vessel_paths,
        "icebreakers": real_icebreaker_paths,
        "grade": real_grade,
        "caravans": caravans
    }

    return JSONResponse(replace_inf_nan(jsonable_encoder(return_dict)))

@app.get("/calculation_request/vessels/", response_model=List[VesselPath])
async def get_calculation_request_results(template_name: str, vessel_id: int | None = None):
    """
    Получение результатов расчета для судна vessel_id по шаблону template_name
    """
    template: Template =  TemplatesCRUD().get(template_name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    crud = VesselPathCRUD()

    filter_conds = {"template_name": template_name}

    if vessel_id:
        filter_conds["vessel_id"] = vessel_id

    return JSONResponse(replace_inf_nan(jsonable_encoder(crud.get_by_filter_conds(filter_conds))))


@app.get("/calculation_request/icebreakers/", response_model=List[IcebreakerModel])
async def get_calculation_request_results(template_name: str, icebreaker_id: int | None = None):
    """
    Получение результатов расчета для судна vessel_id по шаблону template_name
    """
    template: Template =  TemplatesCRUD().get(template_name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    crud = IcebreakerPathCRUD()

    filter_conds = {"template_name": template_name}

    if icebreaker_id:
        filter_conds["icebreaker_id"] = icebreaker_id

    return JSONResponse(replace_inf_nan(jsonable_encoder(crud.get_by_filter_conds(filter_conds))))


@app.post("/calculate_path_wo_icebreaker/", response_model=VesselPath)
async def calculate_path_wo_icebreaker(vessel_id: int | None = None):
    """
        Получение пути без ледокола для судна vessel_id
    """
    crud = VesselPathCRUD()
    filter_conds = {"template_name": "solo"}

    if vessel_id:
        filter_conds["vessel_id"] = vessel_id

    return JSONResponse(replace_inf_nan(jsonable_encoder(crud.get_by_filter_conds(filter_conds))))


@app.get("/calculate_path_with_icebreaker/", response_model=VesselPath)
async def calculate_path_with_icebreaker(vessel_id: int | None = None):
    """
        Получение пути с лучшим ледоколом для судна vessel_id
    """
    crud = VesselPathCRUD()
    filter_conds = {"template_name": "best"}

    if vessel_id:
        filter_conds["vessel_id"] = vessel_id

    return JSONResponse(replace_inf_nan(jsonable_encoder(crud.get_by_filter_conds(filter_conds))))

@app.get("/caravans/", response_model=Caravan)
async def get_caravans(template_name: str):
    caravan_crud = CaravanCRUD()
    filter_conds = {"template_name": template_name}
    return JSONResponse(replace_inf_nan(jsonable_encoder(caravan_crud.get_by_filter_conds(filter_conds))))

@app.get("/grade/", response_model=Caravan)
async def get_grades(template_name: str = ""):
    grades_crud = GradeCRUD()
    if not template_name:
        return JSONResponse(jsonable_encoder(grades_crud.get_all()))
    else:
        return JSONResponse(jsonable_encoder(grades_crud.get(template_name)))

# TODO: добавить пост алгоритма + добавить идентификатора в vesselpath

@app.get("/get_tiff")
async def get_tiff(dt: datetime):
    name = '2020_03_03.tif'
    if not os.path.isfile(tiffs_dir / name):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(tiffs_dir / name, media_type='image/tiff',filename=name)

#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8003)
# >T3an5DRGzg-9)q