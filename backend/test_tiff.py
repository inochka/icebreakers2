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
from backend.config import recalculate_loaded, tiffs_dir
from backend.utils import replace_inf_nan
from fastapi.middleware.cors import CORSMiddleware
import json
from time import time
from backend.calc.navigator import Grade
from xarray import DataArray

start = time()

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rioxarray
from geocube.api.core import make_geocube
from pathlib import Path

def make_geotiffs_for_ice_conditions(self):
    self.gtiffs_paths = {}
 
    for dt, df in self.dfs.items():
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

        out_grid = make_geocube(
            vector_data=gdf,
            measurements=["ice_condition"],
            resolution=(-0.1, 0.1),
        )

        filename = dt.strftime("%Y_%m_%d") + ".tif"

        ice_condition = out_grid["ice_condition"].values

        # Создание массива цветов на основе значений ice_condition
        rgb_array = np.zeros((ice_condition.shape[0], ice_condition.shape[1], 3), dtype=np.uint8)

        rgb_array[(ice_condition < 10)] = [165, 42, 42]   # Коричневый
        rgb_array[(ice_condition >= 10) & (ice_condition < 14.5)] = [255, 0, 0]   # Красный
        rgb_array[(ice_condition >= 14.5) & (ice_condition < 19.5)] = [255, 255, 0] # Желтый
        rgb_array[(ice_condition >= 19.5)] = [0, 128, 0]  # Зеленый

        # Создание DataArray для записи в GeoTIFF
        rgb_dataarray = xr.DataArray(
            rgb_array,
            dims=("y", "x", "band"),
            coords={"y": out_grid.y, "x": out_grid.x, "band": [1, 2, 3]},
        )

        # Добавление CRS и запись в GeoTIFF
        rgb_dataarray.rio.write_crs(out_grid.rio.crs, inplace=True)
        rgb_dataarray.rio.to_raster(tiffs_dir / filename)

        # Сохранение цветовой карты отдельно
        fig, ax = plt.subplots()
        cmap = plt.cm.colors.ListedColormap(['brown', 'red', 'yellow', 'green'])
        norm = plt.cm.colors.BoundaryNorm([0, 10, 14.5, 19.5, ice_condition.max()], cmap.N)
        cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
        cbar.set_label('Ice Condition')
        plt.savefig(tiffs_dir / (dt.strftime("%Y_%m_%d") + "_colormap.png"))
        plt.close(fig)

        self.gtiffs_paths[dt] = tiffs_dir / filename



comp = Computer()
comp.init_app(recalculate_loaded=False)

comp.ice_cond.make_geotiffs_for_ice_conditions_draft()
