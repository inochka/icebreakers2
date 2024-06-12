import networkx as nx
from datetime import datetime
import math
from base_graph import BaseGraph
from vessel import Vessel,IceBreaker
from queue import PriorityQueue
from context import Context
import matplotlib.pyplot as plt

class IceCondition:
    """Хранение данных о ледовой обстановке"""
    def condition(self, base_node_u,base_node_v, time_n:datetime)->float:
        """Возвращает ледовые условия для ребра u-v на момент времени time_n"""
        return base_node_u + base_node_v + time_n  #TODO тут должна быть логика расчета по ледовым данным

class Grade:
    """Оценка стоимости проводки"""
    stuck_vessels:int = 0 #количество судов не достигших точки назначения
    total_time:int = 0 #общее время всех судов на маршруте в часах (на считая ледоколов) в часах

class Navigator:
    def calc_shortest_path(self,base:BaseGraph, ice_cond:IceCondition, vessel:Vessel ,time:datetime,source_node,target_node=None, icebreaker:IceBreaker = None):
        """
        base - опорный граф
        ice_cond - ледовые условия
        vessel - судно для расчета
        time - время начала движения
        source_node - пункт отправки
        target_node - пункт назначения (указывается при расчете пути до конкретной точки)
        icebreaker - ледокол (указывается при расчете движения под проводкой)

        возвращает список конечных вершин с длиной маршрута в часах до каждой и маршрутом {1:(45,[5,2,6,1])}
        если задан пункт назначения вернет (45,[5,2,6,1])
        """
        node_time = {}
        node_prev = {}
        for n in base.graph:
            node_time[n] = math.inf
        node_time[source_node] = 0
        next_nodes = PriorityQueue()
        next_nodes.put((0,source_node ))
        seen = []            
        while not next_nodes.empty() and (target_node != None and target_node not in seen):
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
        def calc_path(n,source_node,node_prev):
            path = [n]
            i = n
            while node_prev[i] != source_node:
                path.insert(0,node_prev[i])
                i = node_prev[i]
            path.insert(0,source_node)
            return path
        if target_node:
            if node_time[target_node] < math.inf:
                path = calc_path(target_node,source_node,node_prev)
            else:
                path = []
            res = (node_time[target_node],path)
        else:
            for n in node_time:
                if n != source_node:
                    if node_time[n] < math.inf:
                        path = calc_path(n,source_node,node_prev)
                    else:
                        path = []
                    res[n] = (node_time[n],path)
        return res
    
    def calc_upper_grade(self, base:BaseGraph, ice_cond:IceCondition, context:Context):
        """Верхняя оценка, возвращает общую оценку проводки и маршруты"""
        grade = Grade()
        paths = {}
        for k,v in context.vessels.items():
            time,path = self.calc_shortest_path(base,ice_cond,v, v.start_date, v.source, v.target)
            grade.total_time = grade.total_time + time
            if time == math.inf:
                grade.stuck_vessels = grade.stuck_vessels + 1
            path[k] = path
        #TODO возврат результата    
