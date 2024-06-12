from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from backend.models import VesselModel, IcebreakerModel, BaseNode, BaseEdge, ShipPath, PostCalcPath, PostCalcPathIce
from backend.calc.base_graph import BaseGraph
from backend.data.vessels_data import vessels_data, icebreaker_data
from backend.calc.vessel import Vessel, IceBreaker

app = FastAPI()

@app.get("/get_base_nodes/", response_model=List[BaseNode])
async def get_nodes():
    graph = BaseGraph()
    graph.set_base_values()
    return JSONResponse(jsonable_encoder(graph.make_list_of_models_for_nodes()))

@app.get("/get_base_edges/", response_model=List[BaseNode])
async def get_edges():
    graph = BaseGraph()
    graph.set_base_values()
    return JSONResponse(jsonable_encoder(graph.make_list_of_models_for_edges()))

@app.get("/vessels/{vessel_id}", response_model = VesselModel | List[VesselModel])
async def get_vessel(id: int | None = None):

    if not id:
        vessels = [Vessel.make_model_from_dict_entry(id, vessels_data[id]) for id in vessels_data]
        return JSONResponse(jsonable_encoder(vessels))

    if id in vessels_data:
        return JSONResponse(jsonable_encoder(Vessel.make_model_from_dict_entry(id, vessels_data[id])))

    raise HTTPException(status_code=404, detail="Vessel not found")


@app.get("/icebreakers/{icebreaker_id}", response_model = IcebreakerModel | List[IcebreakerModel])
async def get_icebreaker(id: int | None = None):
    if not id:
        icebreakers = [IceBreaker.make_model_from_dict_entry(id, icebreaker_data[id]) for id in icebreaker_data]
        return JSONResponse(jsonable_encoder(icebreakers))

    if id in icebreaker_data:
        return JSONResponse(jsonable_encoder(IceBreaker.make_model_from_dict_entry(id, icebreaker_data[id])))

    raise HTTPException(status_code=404, detail="Vessel not found")


@app.post("/calculate_path", response_model=ShipPath)
async def calculate_path(calc: PostCalcPath):
    # Placeholder logic for path calculation
    pass

@app.post("/calculate_path_with_icebreaker", response_model=ShipPath)
async def calculate_path_with_icebreaker(calc: PostCalcPathIce):
    # Placeholder logic for path calculation with icebreaker
    pass


#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8003)