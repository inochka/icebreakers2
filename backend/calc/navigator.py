import networkx as nx
import base_graph as bg
import datetime as dt
import math
from queue import PriorityQueue
import vessel
import matplotlib.pyplot as plt

class IceCondition:
    """Хранение данных о ледовой обстановке"""
    def condition(self, base_node_u, base_node_v, time_n:dt.datetime)->float:
        """Возвращает ледовые условия для ребра u-v на момент времени time_n"""
        return base_node_u + base_node_v + time_n  #TODO тут должна быть логика расчета по ледовым данным


def calc_shortest_path(base:bg.BaseGraph, ice_cond:IceCondition, speed:float, move_class:str,time:dt.datetime,source_node,target_node=None, icebreaker = False):#TODO ice_cond: класс для хранения условий
    """возвращает список конечных вершин с длиной маршрута в часах до каждой и маршрутом {1:{"time":45.1,"path":[5,2,6,1]}}
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
            new_time = node_time[current_node] + vessel.calc_time(base.graph.get_edge_data(current_node,n)["length"],speed, move_class,ice_cond= ice_cond.condition(current_node,n,node_time[current_node]), icebreaker = icebreaker) #TODO запрос расчета ice_cond
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
        res[target_node] = {"time":node_time[target_node]}
        if res[target_node]["time"] < math.inf:
            path = calc_path(target_node,source_node,node_prev)
        else:
            path = []
        res[target_node]["path"] = path
    else:
        for n in node_time:
            if n != source_node:
                res[n] = {"time":node_time[n]}
                if res[n]["time"] < math.inf:
                    path = calc_path(n,source_node,node_prev)
                else:
                    path = []
                res[n]["path"] = path
    return res




if __name__ == "__main__":
    base = bg.BaseGraph()
    #set_g_base5(base)
    base.set_base_values()
    # 29 - 16
    paths = calc_shortest_path(base,None,20,'9_a','02-02-2022',5,46,False)
    print(paths)
    base.draw_geo()
    base.draw_path(paths[46]["path"])
    plt.show()