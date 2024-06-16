from backend.calc.navigator import Navigator,IceCondition,Grade
from base_graph import BaseGraph
import matplotlib.pyplot as plt
plt.ion() #macOS problem
from vessel import Vessel,IceBreaker
from backend.data.vessels_data import vessels_data, icebreaker_data
from context import Context
from time import time
from computer import Computer
from backend.config import backend_base_dir

file_path = backend_base_dir / "input_files/IntegrVelocity.xlsx"
base = BaseGraph()
base.set_base_values()
ice_cond = IceCondition(file_path, base.graph)
comp = Computer(base, ice_cond)

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
    vessel = Vessel(**vessels_data[4])
    ice_cond = IceCondition()
    icebreaker = IceBreaker(**icebreaker_data[1])
    nav = Navigator()
    paths = nav.calc_shortest_path(base,ice_cond,vessel, vessel.start_date,29,46)
    print(paths)
    base.draw_geo()
    base.draw_path(paths[1])
    plt.show()

def test_calc_upper_grade():
    base = BaseGraph()
    ice_cond = IceCondition()
    base.set_base_values()   
    context = Context()
    context.load_from_template('test_1')
    nav = Navigator()
    grade,paths = nav.rough_estimate(base,ice_cond,context)
    print("stuck_vessels: ")
    print(grade.stuck_vessels)
    print("total_time: ")
    print(grade.total_time)
    print("paths: ")
    print(paths)

def test_calc_lower_grade():
    base = BaseGraph()
    ice_cond = IceCondition()
    base.set_base_values()   
    context = Context()
    context.load_from_template('test_1')
    nav = Navigator()
    grade,paths = nav.rough_estimate(base,ice_cond,context,with_best_icebreaker=True)
    context.res_grade = grade
    context.res_vessels = paths
    ship_path = context.make_list_of_models_for_res_vessels()
    print(ship_path)


def test_calc_lower_grade():
    base = BaseGraph()
    ice_cond = IceCondition()
    base.set_base_values()   
    context = Context()
    context.load_from_template('test_1')
    nav = Navigator()
    grade,paths = nav.rough_estimate(base,ice_cond,context,with_best_icebreaker=True)
    print("stuck_vessels: ")
    print(grade.stuck_vessels)
    print("total_time: ")
    print(grade.total_time)
    print("paths: ")
    print(paths)

def test_all_vessels_path_from():
    base = BaseGraph()
    ice_cond = IceCondition()
    base.set_base_values()   
    context = Context()
    context.load_from_template('test_1')
    nav = Navigator()
    res = nav.all_vessels_path_from(base,ice_cond,context)
    print(res)

def test_create_calc_cache():
    base = BaseGraph()
    ice_cond = IceCondition()
    base.set_base_values()   
    context = Context()
    context.load_from_template('test_1')
    nav = Navigator()
    nav.create_calc_cache(base, ice_cond, context)
    print(nav.priority)    

def test_compute_optimal():
    context = Context()
    context.load_from_template('test_1')
    grade, vessel_paths, icebreaker_paths = comp.optimal_timesheet(context)
    print(vessel_paths)

if __name__ == "__main__":
    start = time()
    print('===============')
    test_compute_optimal()
    fin = time()
    print('============'+str(fin-start))


