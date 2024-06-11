import networkx as nx
import math
from backend.data.base_graph_data import base_edges, base_nodes
from backend.models import BaseNode, BaseEdge

class BaseGraph:
    """
    Опорный граф
    """
    def __init__(self):
        self.graph = nx.Graph()

    graph:nx.Graph
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
            node_labels[n] =  self.graph.nodes[n]["point_name"] + ' (' + str(n) + ')'  

        edge = []
        edge_ice = []
        edge_labels = {}
        edge_labels_ice = {}
        for u,v,data in self.graph.edges.data():
            if data['status'] == 1:
                edge.append((u,v))
                edge_labels[(u,v)] = math.floor(data["length"])
            else:
                edge_ice.append((u,v))
                edge_labels_ice[(u,v)] = math.floor(data["length"])
        
        #nx.draw(self.graph, pos, with_labels=True, font_weight="bold")
        nx.draw_networkx_nodes(self.graph,pos,node_size = 50, node_color='#EEEEEE')
        nx.draw_networkx_labels(self.graph, pos,labels =node_labels, font_size=8, font_color='#AAAAAA')
        nx.draw_networkx_edges(self.graph,pos,edgelist = edge, width = 1.0, edge_color = "#CCCCCC")
        nx.draw_networkx_edges(self.graph,pos,edgelist = edge_ice, width = 1.0, edge_color = "#333333")
        nx.draw_networkx_edge_labels(self.graph,pos,edge_labels=edge_labels,font_size=5,font_color='#333333')
        nx.draw_networkx_edge_labels(self.graph,pos,edge_labels=edge_labels_ice,font_size=5,font_color='#333333')


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
            edge_model = BaseEdge(**attrs)
            edge_model.start_point_id = u
            edge_model.end_point_id = v
            edge_models.append(edge_model)
        return edge_models
