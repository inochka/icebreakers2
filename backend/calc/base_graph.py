import networkx as nx
import math
from backend.data.base_graph_data import base_edges, base_nodes
from backend.models import BaseNode, BaseEdge
from shapely.geometry import LineString, Point
from itertools import combinations
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

class BaseGraph:
    """
    Опорный граф
    """
    graph:nx.Graph

    ports = [1, 35, 4, 5, 6, 41, 11, 44, 16, 24, 25, 27, 28, 29]  # вершины, в которых расположены порты
    l0 = 100

# Треугольник на юге Обсуой Губы: Новый-порт (11) - Терминал утренний (35)  - Сабетта (25)
#

    new_ages =  [ (11,35, {"length" : 205.18, "id" : 0, "rep_id": 54, "status": 1, "new_age":True}), #380rv
                (11,25, {"length" : 232.18, "id" : 0, "rep_id": 54, "status": 1, "new_age":True}),
                (25,35, {"length" : 35.64, "id" : 0, "rep_id": 54, "status": 1, "new_age":True}),
                ]
    
    def __init__(self):
        self.graph = nx.Graph()
        self.set_base_values()
        self.graph = self.add_intersection_vertices(self.graph)
        self.graph.add_edges_from(self.new_ages)
        #self.graph = self.add_midpoints_and_connect_within_triangles(self.graph, self.l0)


           


    def draw(self):
        """Построить и отобразить опорный граф
        """
        #pos = nx.planar_layout(self.graph)
        nx.draw(self.graph, with_labels=True, font_weight="bold")
    
    def draw_path(self, path):
        pos = {}
        for n in self.graph:
            pos[n] = [ self.graph.nodes[n]["lon"] ,  self.graph.nodes[n]["lat"] ]
        print('edgelist ',self.get_nodes_from_path(path))
        nx.draw_networkx_edges(self.graph,pos,edgelist = self.get_nodes_from_path(path), width = 1.5, edge_color = "#880000")
       
    def get_nodes_from_path(self,path):
        "Преобразует [1,2,3] в [(1,2),(2,3)]"
        res = []
        for i in range(len(path)-1):
            res.append((path[i],path[i+1]))
        return res
    
    def draw_geo(self):
        """Отрисовать с учетом координат"""
        #{0: array([-1.,  0.]), 1: array([1., 0.])}
        pos = {}
        node_labels = {}
        for n in self.graph:
            pos[n] = [ self.graph.nodes[n]["lon"] ,  self.graph.nodes[n]["lat"] ]
            node_labels[n] =  ' (' + str(n) + ')' # self.graph.nodes[n]["point_name"] +

        edge = []
        edge_ice = []
        added_edges = []
        edge_labels = {}
        edge_labels_ice = {}
        added_edges_labels = {}
        for u,v,data in self.graph.edges.data():
            if data['status'] == 1:
                edge.append((u,v))
                edge_labels[(u,v)] = math.floor(data["length"])
            elif data['status'] == 2:
                edge_ice.append((u,v))
                edge_labels_ice[(u,v)] = math.floor(data["length"])
            else:
                added_edges.append((u,v))
                added_edges_labels[(u, v)] = 0 #math.floor(data["length"])
        
        #nx.draw(self.graph, pos, with_labels=False, font_weight="bold")
        nx.draw_networkx_nodes(self.graph,pos,node_size = 5, node_color='#EEEEEE')
        nx.draw_networkx_labels(self.graph, pos,labels =node_labels, font_size=8, font_color='#AAAAAA')
        nx.draw_networkx_edges(self.graph,pos,edgelist = edge, width = 0.1, edge_color = "#55ff55")
        nx.draw_networkx_edges(self.graph,pos,edgelist = edge_ice, width = 0.1, edge_color = "#5555ff")
        nx.draw_networkx_edges(self.graph, pos, edgelist=added_edges, width=0.1, edge_color="#ff5555")
        #nx.draw_networkx_edge_labels(self.graph,pos,edge_labels=edge_labels,font_size=5,font_color='#333333')
        #nx.draw_networkx_edge_labels(self.graph,pos, edge_labels=edge_labels_ice,font_size=5,font_color='#333333')
        #nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=added_edges_labels, font_size=5, font_color='#333333')

    def set_base_values(self):
        self.graph.add_nodes_from(base_nodes)
        self.graph.add_edges_from(base_edges)

    def make_list_of_models_for_nodes(self):
        node_models = []
        for node_id, attrs in self.graph.nodes(data=True):
            node_model = BaseNode(**attrs)
            node_model.id = node_id
            node_models.append(node_model)
        return node_models

    def make_list_of_models_for_edges(self):
        edge_models = []
        for (u, v, attrs) in self.graph.edges(data=True):
            try:
                edge_model = BaseEdge(**attrs)
            except:
                print(1)
            edge_model.start_point_id = u
            edge_model.end_point_id = v
            edge_models.append(edge_model)
        return edge_models

    def add_intersection_vertices(self, G):
        edges_to_add = []
        nodes_to_add = []
        intersections = {}
        edges_to_remove = set()
        last_edge_id = len(G.edges)

        for (u1, v1, data1), (u2, v2, data2) in combinations(G.edges(data=True), 2):
            line1 = LineString([(G.nodes[u1]['lon'], G.nodes[u1]['lat']), (G.nodes[v1]['lon'], G.nodes[v1]['lat'])])
            line2 = LineString([(G.nodes[u2]['lon'], G.nodes[u2]['lat']), (G.nodes[v2]['lon'], G.nodes[v2]['lat'])])

            if line1.intersects(line2):
                intersection_point = line1.intersection(line2)
                if intersection_point.geom_type == 'Point':
                    x, y = intersection_point.x, intersection_point.y

                    if intersection_point in list(line1.boundary.geoms) + list(line2.boundary.geoms):
                        continue

                    intersection_key = (round(x, 6), round(y, 6))
                    if intersection_key not in intersections:
                        new_node = len(G.nodes) + len(nodes_to_add)
                        nodes_to_add.append((new_node, {'lat': y, 'lon': x, "point_name": ""}))
                        intersections[intersection_key] = new_node

                    new_node = intersections[intersection_key]
                    for u, v, line, data in [(u1, v1, line1, data1), (u2, v2, line2, data2)]:
                        if G.has_edge(u, v) and not ((u, new_node) in edges_to_add or (new_node, v) in edges_to_add):
                            point_u = Point(G.nodes[u]['lon'], G.nodes[u]['lat'])
                            point_v = Point(G.nodes[v]['lon'], G.nodes[v]['lat'])
                            dist_u = point_u.distance(intersection_point)
                            dist_v = point_v.distance(intersection_point)
                            total_length = dist_u + dist_v

                            edges_to_add.append(
                                (u, new_node, {'id': G[u][v]['id'], 'length': dist_u / total_length * data['length'],
                                               "status": 3}))
                            edges_to_add.append(
                                (new_node, v, {'id': last_edge_id, 'length': dist_v / total_length * data['length'],
                                               "status": 3}))
                            edges_to_remove.add((u, v))

                            last_edge_id += 1

        for edge in edges_to_remove:
            if G.has_edge(*edge):
                G.remove_edge(*edge)

        G.add_nodes_from(nodes_to_add)
        G.add_edges_from(edges_to_add)

        # Проверяем граф на корректность
        if not nx.is_connected(G):
            logger.info(f"Warning: Base Graph is disconnected after adding intersection vertices")
        else:
            logger.info(f"Base Graph is connected after adding intersection vertices")

        return G

    def find_triangles(self, G):
        triangles = []
        for u in G.nodes():
            neighbors = list(G.neighbors(u))
            for v, w in combinations(neighbors, 2):
                if G.has_edge(v, w):
                    triangles.append((u, v, w))
        return triangles

    def add_midpoints_and_connect_within_triangles(self, G: nx.Graph, l0: float):
        edges_to_add = []
        nodes_to_add = []
        edges_to_remove = set()
        midpoint_mapping = {}
        last_edge_id = len(G.edges)

        # Находим все треугольники в исходном графе
        triangles = self.find_triangles(G)
        # Добавляем точки посередине длинных ребер
        for u, v, data in G.edges(data=True):
            if data['length'] > l0:
                midpoint_lon = (G.nodes[u]['lon'] + G.nodes[v]['lon']) / 2
                midpoint_lat = (G.nodes[u]['lat'] + G.nodes[v]['lat']) / 2
                new_node = len(G.nodes) + len(nodes_to_add)
                nodes_to_add.append((new_node, {'lat': midpoint_lat, 'lon': midpoint_lon, "point_name": ""}))
                edges_to_add.append((u, new_node, {'id': G[u][v]['id'], 'length': data['length'] / 2, "status": 3}))
                edges_to_add.append((new_node, v, {'id': last_edge_id , 'length': data['length'] / 2,
                                                   "status": 3}))

                last_edge_id += 1
                edges_to_remove.add((u, v))
                midpoint_mapping[(u, v)] = new_node
                midpoint_mapping[(v, u)] = new_node

        for edge in edges_to_remove:
            if G.has_edge(*edge):
                G.remove_edge(*edge)

        G.add_nodes_from(nodes_to_add)
        G.add_edges_from(edges_to_add)

        # Соединяем вершины на серединах ребер внутри треугольников
        for node, u, v in triangles:
            midpoints = []
            if (node, u) in midpoint_mapping:
                midpoints.append(midpoint_mapping[(node, u)])
            if (node, v) in midpoint_mapping:
                midpoints.append(midpoint_mapping[(node, v)])
            if (u, v) in midpoint_mapping:
                midpoints.append(midpoint_mapping[(u, v)])

            if len(midpoints) == 3:
                new_node1, new_node2, new_node3 = midpoints
                # Соединяем вершины внутри треугольника
                G.add_edge(new_node1, new_node2,
                           length=Point(G.nodes[new_node1]['lon'], G.nodes[new_node1]['lat']).distance(
                               Point(G.nodes[new_node2]['lon'], G.nodes[new_node2]['lat'])), status=3,
                           id=last_edge_id)
                G.add_edge(new_node2, new_node3,
                           length=Point(G.nodes[new_node2]['lon'], G.nodes[new_node2]['lat']).distance(
                               Point(G.nodes[new_node3]['lon'], G.nodes[new_node3]['lat'])), status=3,
                           id=last_edge_id + 1)
                G.add_edge(new_node3, new_node1,
                           length=Point(G.nodes[new_node3]['lon'], G.nodes[new_node3]['lat']).distance(
                               Point(G.nodes[new_node1]['lon'], G.nodes[new_node1]['lat'])), status=3,
                           id=last_edge_id + 2)
                last_edge_id += 3

        return G


#plt.figure(figsize=(20,10))

#base_graph = BaseGraph()
#base_graph.set_base_values()
#base_graph.draw_geo()
#plt.show()

#base_graph.graph = base_graph.add_intersection_vertices(base_graph.graph)
#base_graph.graph = base_graph.add_midpoints_and_connect_within_triangles(base_graph.graph, l0=150.)  # Укажите нужное значение l0
#base_graph.draw_geo()

#plt.show()