import networkx as nx
import math
"""
length - расстояние по прямой в морских милях
rep_id - обозначение на картинке
"""

base_nodes = [(0,{"lat":73.1, "lon" : 80,"point_name" : "Бухта Север и Диксон", "rep_id":1010}),
(1,{"lat":69.4, "lon" : 86.15,"point_name" : "Дудинка", "rep_id":1007}),
(2,{"lat":69.9, "lon" : 44.6,"point_name" : "кромка льда на Западе", "rep_id":2002}),
(3,{"lat":69.15, "lon" : 57.68,"point_name" : "Варандей-Приразломное", "rep_id":1015}),
(4,{"lat":73, "lon" : 44,"point_name" : "Штокман", "rep_id":1012}),
(5,{"lat":71.5, "lon" : 22,"point_name" : "Окно в Европу", "rep_id":2001}),
(6,{"lat":74.6, "lon" : 63.9,"point_name" : "Победа месторождение", "rep_id":1011}),
(7,{"lat":76.4, "lon" : 86.4,"point_name" : "Карское - 3 (центр)", "rep_id":2008}),
(8,{"lat":77.6, "lon" : 107.7,"point_name" : "пролив Вилькицкого - 3", "rep_id":2013}),
(9,{"lat":74.9, "lon" : 116.7,"point_name" : "Лаптевых - 4 (юг)", "rep_id":2018}),
(10,{"lat":73.1, "lon" : 72.7,"point_name" : "Вход в Обскую губу", "rep_id":2009}),
(11,{"lat":68.5, "lon" : 73.7,"point_name" : "Новый порт", "rep_id":1004}),
(12,{"lat":76.75, "lon" : 116,"point_name" : "Лаптевых - 1 (центр)", "rep_id":2015}),
(13,{"lat":74, "lon" : 76.7,"point_name" : "Карское - 1 (сбор каравана)", "rep_id":2006}),
(14,{"lat":72.35, "lon" : 79.6,"point_name" : "Лескинское м-е", "rep_id":1014}),
(15,{"lat":70.3, "lon" : 57.8,"point_name" : "Карские ворота", "rep_id":2005}),
(16,{"lat":77.3, "lon" : 67.7,"point_name" : "Мыс Желания", "rep_id":2003}),
(17,{"lat":71.74, "lon" : 184.7,"point_name" : "остров Врангеля", "rep_id":2026}),
(18,{"lat":70.7, "lon" : 170.5,"point_name" : "Восточно-Сибирское - 1 (восток)", "rep_id":2023}),
(19,{"lat":77.8, "lon" : 104.1,"point_name" : "пролив Вилькицкого - восток", "rep_id":2012}),
(20,{"lat":77.7, "lon" : 99.5,"point_name" : "пролив Вилькицкого - запад", "rep_id":2011}),
(21,{"lat":76.2, "lon" : 58.3,"point_name" : "около Новой Земли", "rep_id":2004}),
(22,{"lat":74.4, "lon" : 139,"point_name" : "Пролив Санникова - 1", "rep_id":2020}),
(23,{"lat":74.3, "lon" : 146.7,"point_name" : "Пролив Санникова - 2", "rep_id":2021}),
(24,{"lat":74, "lon" : 128.1,"point_name" : "устье Лены", "rep_id":2019}),
(25,{"lat":71.3, "lon" : 72.15,"point_name" : "Сабетта", "rep_id":1003}),
(26,{"lat":69.1, "lon" : 169.4,"point_name" : "мыс.Наглёйнын", "rep_id":1009}),
(27,{"lat":69.9, "lon" : 179,"point_name" : "пролив Лонга", "rep_id":2027}),
(28,{"lat":73.5, "lon" : 169.9,"point_name" : "Восточно-Сибирское - 3 (север)", "rep_id":2025}),
(29,{"lat":64.95, "lon" : 40.05,"point_name" : "Архангельск", "rep_id":1002}),
(30,{"lat":75.9, "lon" : 152.6,"point_name" : "Лаптевых - 3 (восток)", "rep_id":2017}),
(31,{"lat":68.37, "lon" : 54.6,"point_name" : "МОТ Печора", "rep_id":1017}),
(32,{"lat":73.7, "lon" : 109.26,"point_name" : "Хатангский залив", "rep_id":1008}),
(33,{"lat":72, "lon" : 159.5,"point_name" : "Восточно-Сибирское - 2 (запад)", "rep_id":2024}),
(34,{"lat":72.4, "lon" : 65.6,"point_name" : "Ленинградское-Русановское", "rep_id":1013}),
(35,{"lat":71, "lon" : 73.73,"point_name" : "терминал Утренний", "rep_id":1005}),
(36,{"lat":76.5, "lon" : 97.6,"point_name" : "Таймырский залив", "rep_id":2010}),
(37,{"lat":64.2, "lon" : 188.2,"point_name" : "Берингово", "rep_id":2029}),
(38,{"lat":60.7, "lon" : 175.3,"point_name" : "кромка льда на Востоке", "rep_id":2030}),
(39,{"lat":69.75, "lon" : 169.9,"point_name" : "Рейд Певек", "rep_id":1006}),
(40,{"lat":75.5, "lon" : 131.5,"point_name" : "Лаптевых - 2 (центр)", "rep_id":2016}),
(41,{"lat":69.5, "lon" : 33.75,"point_name" : "Рейд Мурманска", "rep_id":1001}),
(42,{"lat":76.7, "lon" : 140.8,"point_name" : "остров Котельный", "rep_id":2022}),
(43,{"lat":74.8, "lon" : 84.2,"point_name" : "Карское - 2 (прибрежный)", "rep_id":2007}),
(44,{"lat":67.58, "lon" : 47.82,"point_name" : "Индига", "rep_id":1016}),
(45,{"lat":65.9, "lon" : 190.65,"point_name" : "Берингов пролив", "rep_id":2028}),
(46,{"lat":55.7, "lon" : 164.25,"point_name" : "Окно в Азию", "rep_id":2031})]


"""
rep_id - обозначение на картинке
length - расстояние по прямой в морских милях
status - служебное поле 
(-1 - исключено из расчёта. 
0 - чистая вода. движение по прямой. 
1 - роутинг. ледокола нет. 
2 - роутинг. возможен ледокол)
"""
base_edges = [(44,15, {"length" : 270.0166416, "id" : 0, "rep_id": 54, "status": 1}),
(10,11, {"length" : 277.1898363, "id" : 1, "rep_id": 102, "status": 1}),
(18,39, {"length" : 58.39035132, "id" : 2, "rep_id": 108, "status": 2}),
(13,16, {"length" : 238.8589885, "id" : 3, "rep_id": 10, "status": 2}),
(10,13, {"length" : 86.93004916, "id" : 4, "rep_id": 8, "status": 2}),
(21,5, {"length" : 655.3557374, "id" : 5, "rep_id": 1, "status": 1}),
(4,5, {"length" : 410.5701116, "id" : 6, "rep_id": 114, "status": 1}),
(45,37, {"length" : 119.5634492, "id" : 7, "rep_id": 48, "status": 1}),
(13,7, {"length" : 206.8821279, "id" : 8, "rep_id": 15, "status": 2}),
(9,24, {"length" : 191.1526107, "id" : 9, "rep_id": 26, "status": 2}),
(27,18, {"length" : 178.645412, "id" : 10, "rep_id": 45, "status": 2}),
(28,33, {"length" : 205.7748943, "id" : 11, "rep_id": 40, "status": 2}),
(40,22, {"length" : 134.3049847, "id" : 12, "rep_id": 32, "status": 2}),
(42,30, {"length" : 174.3916815, "id" : 13, "rep_id": 35, "status": 2}),
(31,3, {"length" : 81.8159608, "id" : 14, "rep_id": 107, "status": 2}),
(0,43, {"length" : 123.6831421, "id" : 15, "rep_id": 13, "status": 2}),
(12,24, {"length" : 246.2458649, "id" : 16, "rep_id": 28, "status": 2}),
(12,42, {"length" : 339.778226, "id" : 17, "rep_id": 30, "status": 2}),
(15,2, {"length" : 270.5921169, "id" : 18, "rep_id": 5, "status": 1}),
(10,35, {"length" : 127.6546236, "id" : 19, "rep_id": 103, "status": 1}),
(9,32, {"length" : 140.7360068, "id" : 20, "rep_id": 105, "status": 2}),
(2,3, {"length" : 278.1227556, "id" : 21, "rep_id": 53, "status": 1}),
(0,1, {"length" : 251.8626597, "id" : 22, "rep_id": 104, "status": 1}),
(33,18, {"length" : 225.0238977, "id" : 23, "rep_id": 41, "status": 2}),
(40,42, {"length" : 152.2019466, "id" : 24, "rep_id": 31, "status": 2}),
(4,41, {"length" : 288.1919175, "id" : 25, "rep_id": 113, "status": 1}),
(8,12, {"length" : 121.8205679, "id" : 26, "rep_id": 24, "status": 2}),
(2,29, {"length" : 315.3047628, "id" : 27, "rep_id": 3, "status": 1}),
(15,3, {"length" : 69.16861273, "id" : 28, "rep_id": 55, "status": 1}),
(12,40, {"length" : 234.8941148, "id" : 29, "rep_id": 29, "status": 2}),
(19,8, {"length" : 47.63018916, "id" : 30, "rep_id": 23, "status": 2}),
(28,30, {"length" : 308.4151996, "id" : 31, "rep_id": 39, "status": 2}),
(13,0, {"length" : 77.9639623, "id" : 32, "rep_id": 12, "status": 2}),
(21,2, {"length" : 445.9281382, "id" : 33, "rep_id": 4, "status": 1}),
(30,18, {"length" : 436.2716913, "id" : 34, "rep_id": 38, "status": 2}),
(40,9, {"length" : 229.4577372, "id" : 35, "rep_id": 27, "status": 2}),
(21,4, {"length" : 297.1508085, "id" : 36, "rep_id": 2, "status": 1}),
(16,34, {"length" : 296.3206745, "id" : 37, "rep_id": 60, "status": 2}),
(45,17, {"length" : 373.6308274, "id" : 38, "rep_id": 46, "status": 2}),
(17,18, {"length" : 281.0870454, "id" : 39, "rep_id": 44, "status": 2}),
(18,26, {"length" : 98.81552937, "id" : 40, "rep_id": 109, "status": 2}),
(38,46, {"length" : 460.2848327, "id" : 41, "rep_id": 110, "status": 1}),
(30,33, {"length" : 260.5701136, "id" : 42, "rep_id": 37, "status": 2}),
(24,22, {"length" : 179.7422785, "id" : 43, "rep_id": 33, "status": 2}),
(10,16, {"length" : 263.6393465, "id" : 44, "rep_id": 9, "status": 2}),
(27,45, {"length" : 355.6231614, "id" : 45, "rep_id": 47, "status": 2}),
(7,36, {"length" : 157.6035239, "id" : 46, "rep_id": 19, "status": 2}),
(7,20, {"length" : 192.4522229, "id" : 47, "rep_id": 18, "status": 2}),
(34,13, {"length" : 215.0532376, "id" : 48, "rep_id": 61, "status": 2}),
(43,36, {"length" : 223.5714878, "id" : 49, "rep_id": 20, "status": 2}),
(6,7, {"length" : 352.936821, "id" : 50, "rep_id": 58, "status": 2}),
(10,25, {"length" : 108.6630553, "id" : 51, "rep_id": 101, "status": 1}),
(37,38, {"length" : 414.6912251, "id" : 52, "rep_id": 49, "status": 1}),
(13,15, {"length" : 410.4549185, "id" : 53, "rep_id": 7, "status": 2}),
(7,16, {"length" : 260.1771091, "id" : 54, "rep_id": 16, "status": 2}),
(6,16, {"length" : 171.4172136, "id" : 55, "rep_id": 57, "status": 2}),
(36,19, {"length" : 116.7439955, "id" : 56, "rep_id": 21, "status": 2}),
(33,23, {"length" : 261.600589, "id" : 57, "rep_id": 36, "status": 2}),
(20,16, {"length" : 409.3111575, "id" : 58, "rep_id": 17, "status": 2}),
(10,15, {"length" : 326.4328417, "id" : 59, "rep_id": 6, "status": 2}),
(34,15, {"length" : 195.7328443, "id" : 60, "rep_id": 59, "status": 2}),
(44,2, {"length" : 156.0644819, "id" : 61, "rep_id": 52, "status": 1}),
(14,0, {"length" : 45.6421557, "id" : 62, "rep_id": 106, "status": 1}),
(8,9, {"length" : 206.5979139, "id" : 63, "rep_id": 25, "status": 2}),
(2,5, {"length" : 456.2676239, "id" : 64, "rep_id": 111, "status": 1}),
(16,21, {"length" : 145.1826364, "id" : 65, "rep_id": 11, "status": 1}),
(27,28, {"length" : 275.6604549, "id" : 66, "rep_id": 42, "status": 2}),
(13,43, {"length" : 130.3081116, "id" : 67, "rep_id": 14, "status": 2}),
(19,20, {"length" : 58.95750201, "id" : 68, "rep_id": 22, "status": 2}),
(6,15, {"length" : 280.7806599, "id" : 69, "rep_id": 56, "status": 2}),
(2,41, {"length" : 227.2269304, "id" : 70, "rep_id": 112, "status": 1}),
(22,23, {"length" : 124.9092209, "id" : 71, "rep_id": 34, "status": 2}),
(17,28, {"length" : 285.0795135, "id" : 72, "rep_id": 43, "status": 2})]



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
