from datetime import datetime
import math
from base_graph import BaseGraph
from vessel import Vessel,IceBreaker
from queue import PriorityQueue
from context import Context,Grade
from backend.constants import PathEventsType
from backend.utils import add_hours

class IceCondition:
    """Хранение данных о ледовой обстановке"""
    def condition(self, base_node_u,base_node_v, time_n:datetime)->float:
        """Возвращает ледовые условия для ребра u-v на момент времени time_n"""
        return 16  #TODO тут должна быть логика расчета по ледовым данным



class Navigator:
    #сохраненные результаты расчетов
    self_move_grade:Grade  #верхняя оценка времени для заявок, самостоятельная проводка
    self_move_ways = {} #список кратчайших путей
    ice_move_grade:Grade = {} #нижняя оценка времени для заявок, проводка идеальным ледоколом
    ice_move_ways = {} #список кратчайших путей
    priority = {} #приоритет проводки self_move_paths - ice_move_paths
    path_to_all = {} #кратчайшее расстояние от точек старта до каждой вершины

    def calc_shortest_path(self,base:BaseGraph, ice_cond:IceCondition, vessel:Vessel ,time:datetime,source_node,target_node=None, icebreaker:IceBreaker = None):
        """
        base - опорный граф
        ice_cond - ледовые условия
        vessel - судно для расчета
        time - время начала движения
        source_node - пункт отправки
        target_node - пункт назначения (указывается при расчете пути до конкретной точки)
        icebreaker - ледокол (указывается при расчете движения под проводкой)

        возвращает список конечных вершин с длиной маршрута в часах до каждой и маршрутом в виде (время маршрута, список вершин, список времен достижения)
        {1:(45,[5,2,6,1],[0,1,2,3]),2:{...},...}
        если задан пункт назначения вернет (45,[5,2,6,1],[0,1,2,3])
        """
        node_time = {} #время достижения вершины по кратчайшему пути
        node_prev = {} #из какой вершины попали по кратчайшему пути
        for n in base.graph:
            node_time[n] = math.inf
        node_time[source_node] = 0
        next_nodes = PriorityQueue()
        next_nodes.put((0,source_node ))
        seen = []         
        while not next_nodes.empty() and not (target_node != None and target_node in seen):
            current_node = next_nodes.get()[1]
            seen.append(current_node)
            for n in base.graph.neighbors(current_node):
                length = base.graph.get_edge_data(current_node,n)["length"]
                ice = ice_cond.condition(current_node,n,node_time[current_node])
                new_time = node_time[current_node] + vessel.calc_time(length, ice, icebreaker)
                if node_time[n] > new_time:
                    node_time[n] = new_time
                    node_prev[n] = current_node
                    next_nodes.put((new_time,n))
        res = {}
        def calc_path(n,source_node,node_prev,node_time):
            path = [n]
            time = [node_time[n]]
            i = n
            while node_prev[i] != source_node:
                path.insert(0,node_prev[i])
                time.insert(0,node_time[node_prev[i]])
                i = node_prev[i]
            path.insert(0,source_node)
            time.insert(0,0)
            return path,time
        if target_node:
            if node_time[target_node] < math.inf:
                path,time = calc_path(target_node,source_node,node_prev,node_time)
            else:
                path = []
                time = []
            res = (node_time[target_node],path,time)
        else:
            for n in node_time:
                if n != source_node:
                    if node_time[n] < math.inf:
                        path,time = calc_path(n,source_node,node_prev,node_time)
                    else:
                        path = []
                        time = []
                    res[n] = (node_time[n],path,time)
        return res
    
    def rough_estimate(self, base:BaseGraph, ice_cond:IceCondition, context:Context, with_best_icebreaker = False):
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
        if with_best_icebreaker: # создаем идеальный ледокол для нижней оценки
            best_speed = 0
            min_move_pen_19_15 = 1
            min_move_pen_14_10 = 1
            for k,i in context.icebreakers.items():
                if i.speed > best_speed:
                    best_speed = i.speed
                if i.move_pen_19_15 < min_move_pen_19_15:
                    min_move_pen_19_15 = i.move_pen_19_15
                if i.move_pen_14_10 < min_move_pen_14_10:
                    min_move_pen_14_10 = i.move_pen_14_10
            best_icebreaker = IceBreaker()
            best_icebreaker.load_from({"name":"Ямал","ice_class":"Arc 9","speed":best_speed,"move_pen_19_15":min_move_pen_19_15, "move_pen_14_10":min_move_pen_14_10,"source":41,"source_name":"Рейд Мурманска","start_date":"27.02.2022"})

        for k,v in context.vessels.items():
            if with_best_icebreaker:
                time,path,timelist = self.calc_shortest_path(base,ice_cond,v, v.start_date, v.source, v.target, best_icebreaker)
            else:
                time,path,timelist = self.calc_shortest_path(base,ice_cond,v, v.start_date, v.source, v.target)
            grade.total_time = grade.total_time + time
            res[k] = {}
            res[k]['start_date'] = v.start_date
            if time == math.inf:
                res[k]['end_date'] = None
            else:
                res[k]['end_date'] = add_hours(v.start_date,time) 
            res[k]['total_hours'] = time
            res[k]['source'] = v.source
            res[k]['source_name'] = base.graph.nodes[v.source]["point_name"]
            res[k]['target'] = v.target
            res[k]['target_name'] = base.graph.nodes[v.target]["point_name"]
            res[k]['success'] = (time < math.inf) 
            #TODO min_ice_condition сделать функцию расчета худших ледовых условий на маршруте, или пока выпилить
            #TODO speed сделать метод на графе для расчета длины маршрута чтобы посчитать среднюю скорость
            res[k]['path_line'] = path
            if time == math.inf:
                grade.stuck_vessels = grade.stuck_vessels + 1
                waybill = [(PathEventsType.stuck,v.source,v.start_date)]
            else:
                waybill = []
                next_event_time = v.start_date
                for i,n in enumerate(path):
                    if n == v.target:
                        waybill.append((PathEventsType.fin,n,next_event_time))
                    else:
                        waybill.append((PathEventsType.move,n,next_event_time))
                        next_event_time = add_hours(next_event_time,timelist[i+1])
            res[k]['waybill'] = waybill
        return grade,res
    def all_vessels_path_from(self, base:BaseGraph, ice_cond:IceCondition, context:Context):
        """Для каждого судна вычисляет стоимость достижения каждой вершины при самостоятельном движении, возвращает словарь { номер судна: {каждая конечная вершина:(время в часах,[путь],[время на пути])}"""
        res = {}
        for k,v in context.vessels.items():
            paths = self.calc_shortest_path(base,ice_cond,v, v.start_date, v.source)
            res[k] = paths
        return res
    def create_calc_cache(self, base:BaseGraph, ice_cond:IceCondition, context:Context):
        """Сохраняет результаты расчетов для дальнейшего использования"""
        self.self_move_grade,self.self_move_ways = self.rough_estimate(base,ice_cond,context)
        self.ice_move_grade,self.ice_move_ways = self.rough_estimate(base,ice_cond,context,with_best_icebreaker=True)
        self.priority = {}
        for k,sm in self.self_move_ways.items():
            self.priority[k] = sm['total_hours'] - self.ice_move_ways[k]['total_hours']