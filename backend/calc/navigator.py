from datetime import datetime, timedelta
import math
from collections import defaultdict
from tqdm import tqdm
import numpy as np

from backend.calc.base_graph import BaseGraph
from backend.calc.vessel import AbstractVessel, Vessel, IceBreaker
from queue import PriorityQueue
from backend.calc.context import Context
from backend.constants import PathEventsType
from backend.utils import add_hours
from backend.models import PathEvent, Grade
from backend.calc.ice_cond import IceCondition
from backend.models import VesselPath, SimpleVesselPath, AllSimpleVesselPath
from typing import List, Dict, DefaultDict
import logging

logger = logging.getLogger(__name__)

class Navigator:

    # сохраненные результаты расчетов

    solo_move_grade: Grade  # верхняя оценка времени для заявок, самостоятельная проводка
    solo_move_ways: Dict[int, VesselPath] | None = None  # список кратчайших путей при самостоятельном движении
    ice_move_grade: Grade  # нижняя оценка времени для заявок, проводка идеальным ледоколом
    ice_move_ways: Dict[int, VesselPath] | None = None  # список кратчайших путей при движении с ледоколом
    priority: Dict[int, float] | None = None  # приоритет проводки self_move_paths - ice_move_paths

    path_to_all: Dict[int, AllSimpleVesselPath] | None = None # кратчайшее расстояние от точек старта
                                                                  # до каждой вершины,ключ - vessel_id

    reachable_vertices_from_start: Dict[int, List[int]] | None = None  # список достижимых вершин для данного судна,
                                                                       # из точки старта, ключ - vessel_id

    reachable_vertices_from_end: Dict[int, List[int]] | None = None  # список достижимых вершин для данного судна,
                                                                       # ключ - vessel_id

    path_from_all: Dict[int, AllSimpleVesselPath] | None = None
    estimate_path_time = timedelta(days=14)

    icebreakers_shortest_paths: DefaultDict[int, DefaultDict[int, Dict[int, SimpleVesselPath]]] # ледокол - судно - идентификатор конца пути

    # TODO: просчитать отдельно для всех ледоколов
    best_icebreaker_paths_times: np.ndarray  # матрица оптимальных времен между вершинами

    base: BaseGraph
    ice_cond: IceCondition
    context: Context


    def __init__(self,  base: BaseGraph, context: Context, ice_cond: IceCondition):
        """Сохраняет результаты расчетов для дальнейшего использования"""

        self.base = base
        self.ice_cond = ice_cond
        self.context = context

        self.solo_move_grade, self.solo_move_ways = self.rough_estimate()
        self.ice_move_grade, self.ice_move_ways = self.rough_estimate(with_best_icebreaker=True)

        self.priority = {}

        for k, sm in self.solo_move_ways.items():
            self.priority[k] = sm.total_time_hours - self.ice_move_ways[k].total_time_hours

        # считаем пути во все точки из начала
        self.path_to_all = {}
        self.reachable_vertices_from_start = {}
        for k, v in self.context.vessels.items():
            paths = self.calc_shortest_path(v)
            self.path_to_all[k] = paths

            self.reachable_vertices_from_start[k] = [node for node, simple_v_path in paths.paths.items()
                                                     if simple_v_path.total_time_hours < math.inf]

        # считаем пути из всех точек в конец

        self.path_from_all = {}
        self.reachable_vertices_from_end = {}
        for k, v in self.context.vessels.items():
            # обращаем направление стрелы времени , чтобы использовать тот же алгоритм
            paths = self.calc_shortest_path(v, source_node=v.target, time_orientation = -1,
                                            start_time= v.start_date + self.estimate_path_time)
            self.path_from_all[k] = paths

            self.reachable_vertices_from_end[k] = [node for node, simple_v_path in paths.paths.items()
                                                     if simple_v_path.total_time_hours < math.inf]


        # считаем все.. пред можно убрать, наверное
        self.icebreakers_shortest_paths = defaultdict(lambda: defaultdict(dict))
        logger.info(f"Calculating icebreakers paths from all to all...")
        for idx, icebreaker in tqdm(self.context.icebreakers.items()):
            for a in self.base.graph:
                for b in self.base.graph:
                    if a == b:
                        self.icebreakers_shortest_paths[idx][a][b] = SimpleVesselPath()
                        continue

                    self.icebreakers_shortest_paths[idx][a][b] = self.calc_shortest_path(icebreaker,
                                                                                         source_node=a, target_node=b)

        # считаем оптимальные времена с оптимальным ледоколом для дальнейшего откидывания нехороших вариантов
        ice_breaker = self.get_best_ice_breaker()
        n_vertices = len(self.base.graph.nodes)

        best_icebreaker_paths_times = np.zeros((n_vertices, n_vertices))
        for n in self.base.graph:
            all_paths = self.calc_shortest_path(ice_breaker, use_best_ice_condition=True)
            for m, simple_path in all_paths.paths.items():
                best_icebreaker_paths_times[n][m] = simple_path.total_time_hours
                best_icebreaker_paths_times[m][n] = simple_path.total_time_hours

        self.best_icebreaker_paths_times = best_icebreaker_paths_times
        # TODO: может, проще уже для всех ледоколов честно просчитать, их не сильно много?


    def get_best_ice_breaker(self):
        best_speed = 0
        min_move_pen_19_15 = 1
        min_move_pen_14_10 = 1
        for k, i in self.context.icebreakers.items():
            if i.speed > best_speed:
                best_speed = i.speed
            if i.move_pen_19_15 < min_move_pen_19_15:
                min_move_pen_19_15 = i.move_pen_19_15
            if i.move_pen_14_10 < min_move_pen_14_10:
                min_move_pen_14_10 = i.move_pen_14_10

        return IceBreaker(
            name = "Ямал",
            ice_class = "Arc 9",
            speed = best_speed,
            move_pen_19_15 = min_move_pen_19_15,
            move_pen_14_10 = min_move_pen_14_10,
            source = 41,
            source_name = "Рейд Мурманска",
            start_date = "27.02.2022",
            idx = 0
        )


    @staticmethod
    def unfold_path(n, source_node, node_prev, node_time):
        path = [n]
        time = [node_time[n]]
        i = n
        while node_prev[i] != source_node:
            path.insert(0, node_prev[i])
            time.insert(0, node_time[node_prev[i]])
            i = node_prev[i]
        path.insert(0, source_node)
        time.insert(0, 0)
        return path, time

    def shift_waybill(self, waybill: List[PathEvent], time_shift: timedelta):
        shifted_waybill = []
        for path_event in waybill:
            shifted_waybill.append(PathEvent(event=path_event.event, point=path_event.point,
                                             dt=path_event.dt+time_shift))

        return shifted_waybill
            
    def convert_simple_path_to_waybill(self, simple_path: SimpleVesselPath, start_time: datetime, source: int,
                                       start_type: PathEventsType,
                                       move_type:PathEventsType,
                                       end_type: PathEventsType
                                       ):
        time = simple_path.total_time_hours
        # TODO min_ice_condition сделать функцию расчета худших ледовых условий на маршруте, или пока выпилить
        # TODO speed сделать метод на графе для расчета длины маршрута чтобы посчитать среднюю скорость
        if time == math.inf:
            path_event = PathEvent(event=PathEventsType.stuck, point=source, dt=start_time)
            waybill = [path_event]
        else:
            waybill = []
            next_event_time = start_time

            for i, n in enumerate(simple_path.path_line):
                if n == simple_path.path_line[-1]:
                    waybill.append(PathEvent(event=end_type, point=n, dt=next_event_time))
                else:
                    waybill.append(PathEvent(event=move_type, point=n, dt=next_event_time))
                    next_event_time = add_hours(start_time, simple_path.time_line[i + 1])

            if waybill:
                waybill[0].event = start_type

        return waybill


    def calc_shortest_path(self, vessel: AbstractVessel, start_time: datetime | None = None,
                           time_orientation: int = +1, use_best_ice_condition: bool = False,
                           source_node: int | None = None, target_node=None, icebreaker: IceBreaker = None):
        """
        base - опорный граф
        ice_cond - ледовые условия
        vessel - судно для расчета
        start_time - время начала движения
        source_node - пункт отправки
        target_node - пункт назначения (указывается при расчете пути до конкретной точки)
        icebreaker - ледокол (указывается при расчете движения под проводкой)

        возвращает список конечных вершин с длиной маршрута в часах до каждой и маршрутом в виде (время маршрута, список вершин, список времен достижения)
        {1:(45,[5,2,6,1],[0,1,2,3]),2:{...},...}
        если задан пункт назначения вернет (45,[5,2,6,1],[0,1,2,3])
        """
        node_time = {}  # время достижения вершины по кратчайшему пути
        node_prev = {}  # из какой вершины попали по кратчайшему пути

        if start_time is None:
            start_time = vessel.start_date

        if source_node is None:
            source_node = vessel.source

        for n in self.base.graph:
            node_time[n] = math.inf
        node_time[source_node] = 0
        next_nodes = PriorityQueue()
        next_nodes.put((0, source_node))
        seen = []
        while not next_nodes.empty() and not ((target_node is not None) and (target_node in seen)):
            current_node = next_nodes.get()[1]
            seen.append(current_node)
            for n in self.base.graph.neighbors(current_node):
                length = self.base.graph.get_edge_data(current_node, n)["length"]
                if not use_best_ice_condition:
                    ice_cond_time = start_time + time_orientation * timedelta(hours=node_time[current_node])
                    ice = self.ice_cond.condition(current_node, n, ice_cond_time)
                else:
                    ice = self.ice_cond.best_condition(current_node, n)

                if icebreaker:
                    if not hasattr(vessel, "calc_time_with_icebreaker"):
                        logger.info(f"Something wrong with call calc_time_with_icebreaker_method")
                        new_time = node_time[current_node] + vessel.calc_time(length, ice)
                    else:
                        new_time = node_time[current_node] + vessel.calc_time_with_icebreaker(length, ice, icebreaker)
                else:
                    new_time = node_time[current_node] + vessel.calc_time(length, ice)

                if node_time[n] > new_time:
                    node_time[n] = new_time
                    node_prev[n] = current_node
                    next_nodes.put((new_time, n))

        if target_node is not None:
            if node_time[target_node] < math.inf:
                path, time = self.unfold_path(target_node, source_node, node_prev, node_time)
            else:
                path = []
                time = []
            return SimpleVesselPath(total_time_hours=node_time[target_node], path_line=path, time_line=time) #(node_time[target_node], path, time)
        else:
            simple_paths = {}
            for n in node_time:
                if n != source_node:
                    if node_time[n] < math.inf:
                        path, time = self.unfold_path(n, source_node, node_prev, node_time)
                    else:
                        path = []
                        time = []
                    simple_paths[n] = SimpleVesselPath(total_time_hours=node_time[n], path_line=path, time_line=time) #(node_time[n], path, time)

            # TODO: првоерить, не отъебывает ли
            simple_paths[source_node] = SimpleVesselPath(total_time_hours=0, path_line=[], time_line=[])
            all_paths = AllSimpleVesselPath(node=source_node, paths=simple_paths)
            return all_paths

    def rough_estimate(self, with_best_icebreaker=False) -> (Grade, List[VesselPath]):
        """Приближенная оценка, возвращает общую оценку самостоятельного движения или движения под проводкой и маршруты Возвращает объект Grade и описания маршрутов виде структуры в виде словаря с ключами = идентификатор судна
        {4: {'start_date': datetime.datetime(2022, 3, 7, 0, 0),
        'end_date': datetime.datetime(2022, 4, 16, 8, 7, 57, 477552),
        'total_hours': 4.6,
        'source': 4,
        'source_name': 'Штокман',
        'target': 27,
        'target_name': 'пролив Лонга',
        'success': True,
        'path_line': [4, 21, 16, 20, 19, 8, 12, 42, 30, 28, 27],
        'waybill': [(<PathEventsType.move: 'move'>, 4, datetime.datetime(2022, 3, 7, 0, 0)), (<PathEventsType.move: 'move'>, 21, datetime.datetime(2022, 3, 12, 12, 4, 1, 293600)), (<PathEventsType.move: 'move'>, 16, datetime.datetime(2022, 3, 20, 16, 39, 34, 805440)), (<PathEventsType.move: 'move'>, 20, datetime.datetime(2022, 4, 5, 11, 10, 6, 169280)), (<PathEventsType.move: 'move'>, 19, datetime.datetime(2022, 4, 22, 7, 52, 49, 536336)), (<PathEventsType.move: 'move'>, 8, datetime.datetime(2022, 5, 10, 1, 45, 41, 206048)), (<PathEventsType.move: 'move'>, 12, datetime.datetime(2022, 5, 30, 1, 47, 5, 784400)), (<PathEventsType.move: 'move'>, 42, datetime.datetime(2022, 6, 25, 8, 49, 15, 524352)), (<PathEventsType.move: 'move'>, 30, datetime.datetime(2022, 7, 24, 21, 21, 51, 954704)), (<PathEventsType.move: 'move'>, 28, datetime.datetime(2022, 8, 29, 2, 58, 52, 704416)), (<PathEventsType.fin: 'fin'>, 27, datetime.datetime(2022, 10, 8, 11, 6, 50, 181968))]}}"""
        grade = Grade()
        res = {}
        if with_best_icebreaker:  # создаем идеальный ледокол для нижней оценки
            best_icebreaker = self.get_best_ice_breaker()

        for k, v in self.context.vessels.items():
            if with_best_icebreaker:
                simple_path = self.calc_shortest_path(v, target_node=v.target, icebreaker = best_icebreaker)
            else:
                simple_path = self.calc_shortest_path(v, target_node=v.target)

            time = simple_path.total_time_hours
            grade.total_time = grade.total_time + time
            end_date = add_hours(v.start_date, time) if time != math.inf else None
            # TODO min_ice_condition сделать функцию расчета худших ледовых условий на маршруте, или пока выпилить
            # TODO speed сделать метод на графе для расчета длины маршрута чтобы посчитать среднюю скорость
            if time == math.inf:
                grade.stuck_vessels = grade.stuck_vessels + 1
                path_event = PathEvent(event=PathEventsType.stuck, point=v.source, dt=v.start_date)
                waybill = [path_event]
            else:
                waybill = []
                next_event_time = v.start_date

                for i, n in enumerate(simple_path.path_line):
                    if n == v.target:
                        waybill.append(PathEvent(event=PathEventsType.fin, point=n, dt=next_event_time))
                    else:
                        waybill.append(PathEvent(event=PathEventsType.move, point=n, dt=next_event_time))
                        next_event_time = add_hours(next_event_time, simple_path.time_line[i + 1])

            res[k] = VesselPath(
                total_time_hours = time,
                start_date = v.start_date,
                end_date = end_date,
                source = v.source,
                source_name = self.base.graph.nodes[v.source]["point_name"],
                target = v.target,
                target_name = self.base.graph.nodes[v.target]["point_name"],
                success = time < math.inf,
                waybill = waybill,
                path_line = simple_path.path_line,
                template_name = self.context.template_name,
                vessel_id = k,
                time_line = simple_path.time_line
            )

        return grade, res

