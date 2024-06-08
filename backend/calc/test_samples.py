import navigator as nav
import base_graph as bg
import matplotlib.pyplot as plt


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



if __name__ == "__main__":
    base = bg.BaseGraph()
    #set_g_base5(base)
    base.set_base_values()
    ice = nav.IceCondition()
    calc = nav.CalcGraph(base,ice)
    # 29 - 16
    paths = nav.calc_shortest_path(base,ice,20,'9_a','02-02-2022',29,16,False)
    print(paths)
    base.draw_geo()
    plt.show()

