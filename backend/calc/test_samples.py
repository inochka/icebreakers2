from backend.calc.navigator import Navigator,IceCondition
from base_graph import BaseGraph
import matplotlib.pyplot as plt
from vessel import Vessel,IceBreaker
from backend.data.vessels_data import vessels_data, icebreaker_data

def set_g_base2(base): #задать базовый граф 2 вершины
    # определяем список узлов (ID узлов)
    nodes = [(0,{'test':0}), (1,{'test':0})]
    edges = [(0, 1),(1,0)]
    base.graph
    # добавляем информацию в объект графа
    base.graph.add_nodes_from(nodes)
    base.graph.add_edges_from(edges)


def set_g_base5(base): #задать базовый граф  с пятью вершинами
    # определяем список узлов (ID узлов)
    nodes = [0, 1, 2, 3, 4]
    edges = [(1, 2),(2,1), (1, 3),(3,1), (2, 3),(3,2), (2, 4),(4,2), (3, 0),(0,3),(4,0),(0,4),(1,0),(0,1)]
    base.graph
    # добавляем информацию в объект графа
    base.graph.add_nodes_from(nodes)
    base.graph.add_edges_from(edges)

def test_path():
    base = BaseGraph()
    base.set_base_values()
    vessel = Vessel()
    vessel.load_from(vessels_data[4])
    ice_cond = IceCondition()
    icebreaker = IceBreaker()
    icebreaker.load_from(icebreaker_data[1])
    nav = Navigator()
    paths = nav.calc_shortest_path(base,ice_cond,vessel, vessel.start_date,29,46)
    print(paths)
    base.draw_geo()
    base.draw_path(paths[46]["path"])
    plt.show()

if __name__ == "__main__":
    test_path()

