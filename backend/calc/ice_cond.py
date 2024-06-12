import logging
from datetime import datetime
from pathlib import Path
from typing import List
from networkx import Graph
import geopandas as gpd
import numpy as np
import pandas as pd
from dateutil import parser
from scipy.interpolate import LinearNDInterpolator
import matplotlib.pyplot as plt
from backend.calc.base_graph import BaseGraph

logger = logging.getLogger(__name__)

class IceCondition:

    """Хранение данных о ледовой обстановке"""

    dfs: dict[datetime, pd.DataFrame]
    interpolators: dict[datetime, LinearNDInterpolator]

    def __init__(self, file_path: Path | str):
        self.dfs = self.read_file(file_path)
        interpolators = {}
        for dt, df in self.dfs.items():
          interpolators[dt] =  self.make_interpolator(df)
        self.interpolators = interpolators

    def obtain_condition_for_edge(self, u: np.ndarray, v: np.ndarray, dt: datetime)->float:
        """
        u_x, u_y, v_x, v_y - координаты начальной и конечной точки ребра
        t - время (берем ближайшее к нему время прогноза)
        """

        assert u.shape == (2,)
        assert v.shape == (2,)

        forecast_date = self.find_appropriate_conditions_date(list(self.interpolators.keys()), dt)

        n_points = 10
        points = [u + (v - u) * i / 5 for i in range(n_points)]

        coords_y = [u[1] + (v - u)[1] * i / n_points for i in range(n_points)]
        coords_x = [u[0] + (v - u)[0] * np.sin(coords_y[i] / 180 * np.pi) * i / n_points for i in range(n_points)]

        points =np.array(list(zip(coords_x, coords_y)))

        # берем просто среднее ледовое условие, по n_points точкам на данном отрезке
        return np.mean(self.interpolators[forecast_date](points))

    def obtain_condition_for_graph(self, graph: Graph, dt: datetime):
        """
        Обрабатывает целый граф, используя свойства ребер с долготой и широтой.
        graph: граф из networkx с ребрами, содержащими координаты
        dt: время (берем ближайшее к нему время прогноза)
        """

        forecast_date = self.find_appropriate_conditions_date(list(self.interpolators.keys()), dt)

        n_points = 10
        all_points = []
        edge_indices = []

        # Обход всех ребер в графе
        for u, v, data in graph.edges(data=True):
            u_coords = np.array([graph.nodes[u]['lon'], graph.nodes[u]['lat']])
            v_coords = np.array([graph.nodes[v]['lon'], graph.nodes[v]['lat']])

            coords_y = np.linspace(u_coords[1], v_coords[1], n_points)
            coords_x = np.linspace(u_coords[0], v_coords[0], n_points)

            # исправляем расстояния на геометрические для лучшей интерполяции
            coords_x = coords_x * np.sin(coords_y / 180 * np.pi)

            points = np.column_stack((coords_x, coords_y))
            all_points.append(points)
            edge_indices.append((u, v))

        all_points = np.vstack(all_points)

        # Выполняем интерполяцию для всех точек разом
        ice_conditions = self.interpolators[forecast_date](all_points)

        # Присваиваем средние значения ледовых условий для каждого ребра
        for i, (u, v) in enumerate(edge_indices):
            start_idx = i * n_points
            end_idx = (i + 1) * n_points
            graph[u][v]['ice_condition'] = np.mean(ice_conditions[start_idx:end_idx])

        return graph


    @staticmethod
    def find_appropriate_conditions_date(conditions_dates: List[datetime], dt: datetime):
        return  min(conditions_dates, key=lambda sub: abs(sub - dt))

    @staticmethod
    def convert_str_to_datetime(datestr: str) -> datetime:
        return parser.parse(datestr)

    def condition(self, base_node_u, base_node_v, time_n: datetime)->float:
        """Возвращает ледовые условия для ребра u-v на момент времени time_n"""
        return base_node_u + base_node_v + time_n  #TODO тут должна быть логика расчета по ледовым данным

    def read_file(self, file_path: str | Path):
        logger.info(f"Reading ice conditions file...")
        xls = pd.ExcelFile(file_path)
        latitudes = pd.read_excel(xls, sheet_name=xls.sheet_names[1])
        longitudes = pd.read_excel(xls, sheet_name=xls.sheet_names[0])

        shape1 = latitudes.values.shape
        shape2 = longitudes.values.shape

        assert shape2 == shape1

        lat_flat = latitudes.values.flatten()
        lon_flat = longitudes.values.flatten()

        dfs = {}

        for sheet_name in xls.sheet_names[2:]:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            assert df.values.shape == shape1
            data_flat = df.values.flatten()

            data_df = pd.DataFrame({
                'latitude': lat_flat,
                'longitude': lon_flat,
                'ice_condition': data_flat
                #'geometry': points,
            })

            dfs[self.convert_str_to_datetime(sheet_name)] = data_df

        dfs = dict(sorted(dfs.items()))

        return dfs

    def make_interpolator(self, data: pd.DataFrame, target_col: str = "ice_condition") -> LinearNDInterpolator:
        logger.info(f"Interpolating ice data...")
        # все слои перегоняем от 0 до 360, частички потребляют именно такой вид
        # в тепловой карте потом назад возвращаем, если нужно

        data_shifted_left = data.assign(longitude=data["longitude"] - 360)[data["longitude"] >= -90]
        data_shifted_right = data.assign(longitude=data["longitude"] + 360)[data["longitude"] < 90]
        data = pd.concat([data, data_shifted_left, data_shifted_right], ignore_index=True)

        coords_y = data["latitude"].values
        coords_x = data["longitude"].values * np.sin(data["latitude"].values / 180 * np.pi)
        coords = np.array(tuple(zip(coords_x, coords_y)))

        interpolator = LinearNDInterpolator(coords, data[target_col].values, fill_value=0, rescale=True)

        return interpolator

    def plot_ice_condition_with_edge(self, u, v, dt):

        forecast_date = self.find_appropriate_conditions_date(list(self.interpolators.keys()), dt)
        df = self.dfs[forecast_date]
        df = df[df.ice_condition > 0]
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.longitude, df.latitude)
        )

        # Переход к системе координат WGS84 (широта-долгота)
        gdf.set_crs(epsg=4326, inplace=True)

        # Построение тепловой карты
        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        gdf.plot(column='ice_condition', cmap='coolwarm', legend=True, ax=ax, markersize=5)

        ax.plot([u[0], v[0]], [u[1], v[1]], color='black', linewidth=2, label='Path Line')

        ax.set_title('Ice Condition Heatmap')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.show()


file_path = "../input_files/IntegrVelocity.xlsx"
ice_cond = IceCondition(file_path)
u = np.array([70, 80])
v = np.array([75, 68])
dt = datetime(year=2020, month=3, day=1)
print(ice_cond.obtain_condition_for_edge(u, v, dt))
ice_cond.plot_ice_condition_with_edge(u,v,dt)
graph = BaseGraph()
graph.set_base_values()
new_graph = ice_cond.obtain_condition_for_graph(graph.graph, dt)
print(new_graph)