from enum import Enum
import math
import datetime as dt

vessels_data = {1:{"name":"ДЮК II","ice_class":"Arc 5","speed":15,"source":11,"source_name":"Новый порт","target":41,"target_name":"Рейд Мурманска","start_date":"01.03.2022"},
2:{"name":"САРМАТ","ice_class":"Arc 4","speed":15,"source":25,"source_name":"Сабетта","target":29,"target_name":"Архангельск","start_date":"02.03.2022"},
3:{"name":"EDUARD TOLL","ice_class":"Arc 7","speed":15,"source":25,"source_name":"Сабетта","target":41,"target_name":"Рейд Мурманска","start_date":"04.03.2022"},
4:{"name":"GEORGIY USHAKOV","ice_class":"Arc 7","speed":15,"source":4,"source_name":"Штокман","target":27,"target_name":"Пролив Лонга","start_date":"07.03.2022"},
5:{"name":"RUDOLF SAMOYLOVICH","ice_class":"Arc 7","speed":15,"source":11,"source_name":"Новый порт","target":24,"target_name":"устье Лены","start_date":"08.03.2022"},
6:{"name":"VLADIMIR VORONIN","ice_class":"Arc 7","speed":15,"source":25,"source_name":"Сабетта","target":27,"target_name":"Пролив Лонга","start_date":"12.03.2022"},
7:{"name":"NIKOLAY YEVGENOV","ice_class":"Arc 7","speed":14,"source":35,"source_name":"Терминал Утренний","target":27,"target_name":"Пролив Лонга","start_date":"13.03.2022"},
8:{"name":"CHRISTOPHE DE MARGERIE","ice_class":"Arc 7","speed":14,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"07.03.2022"},
9:{"name":"BORIS VILKITSKY","ice_class":"Arc 7","speed":19,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"07.03.2022"},
10:{"name":"АРКТИКА-2","ice_class":"Arc 5","speed":19,"source":35,"source_name":"Терминал Утренний","target":24,"target_name":"устье Лены","start_date":"15.03.2022"},
11:{"name":"ИНЖЕНЕР ВЕШНЯКОВ","ice_class":"Arc 5","speed":19,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"09.03.2022"},
12:{"name":"ТАМБЕЙ","ice_class":"Arc 4","speed":19,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"16.03.2022"},
13:{"name":"ШТУРМАН АЛЬБАНОВ","ice_class":"Arc 7","speed":19,"source":4,"source_name":"Штокман","target":1,"target_name":"Дудинка","start_date":"26.03.2022"},
14:{"name":"НИКИФОР БЕГИЧЕВ","ice_class":"Arc 4","speed":16,"source":11,"source_name":"Новый порт","target":5,"target_name":"Окно в Европу","start_date":"10.03.2022"},
15:{"name":"НОРИЛЬСКИЙ НИКЕЛЬ","ice_class":"Arc 7","speed":14,"source":16,"source_name":"Мыс Желания","target":24,"target_name":"устье Лены","start_date":"13.03.2022"},
16:{"name":"АЙС ИГЛ","ice_class":"Arc 5","speed":14,"source":11,"source_name":"Новый порт","target":4,"target_name":"Штокман","start_date":"24.03.2022"},
17:{"name":"ШТУРМАН КОШЕЛЕВ","ice_class":"Arc 7","speed":15,"source":27,"source_name":"Пролив Лонга","target":25,"target_name":"Сабетта","start_date":"04.03.2022"},
18:{"name":"ШТУРМАН ЩЕРБИНИН","ice_class":"Arc 7","speed":15,"source":6,"source_name":"Победа месторождение","target":5,"target_name":"Окно в Европу","start_date":"19.03.2022"},
19:{"name":"ШТУРМАН СКУРАТОВ","ice_class":"Arc 7","speed":15,"source":35,"source_name":"Терминал Утренний","target":24,"target_name":"устье Лены","start_date":"19.03.2022"},
20:{"name":"ИОГАНН МАХМАСТАЛЬ","ice_class":"Arc 5","speed":14,"source":11,"source_name":"Новый порт","target":5,"target_name":"Окно в Европу","start_date":"17.03.2022"},
21:{"name":"BORIS SOKOLOV","ice_class":"Arc 7","speed":14,"source":29,"source_name":"Архангельск","target":1,"target_name":"Дудинка","start_date":"24.03.2022"},
22:{"name":"ИНЖЕНЕР ТРУБИН","ice_class":"Arc 5","speed":12,"source":24,"source_name":"устье Лены","target":11,"target_name":"Новый порт","start_date":"08.03.2022"},
23:{"name":"БАРЕНЦ","ice_class":"Arc 4","speed":16,"source":28,"source_name":"Восточно-Сибирское 1","target":41,"target_name":"Рейд Мурманска","start_date":"20.03.2022"},
24:{"name":"ПОЛАР КИНГ","ice_class":"Arc 5","speed":16,"source":28,"source_name":"Восточно-Сибирское 3","target":29,"target_name":"Архангельск","start_date":"16.03.2022"},
25:{"name":"МЫС ДЕЖНЕВА","ice_class":"Arc 4","speed":16,"source":6,"source_name":"Победа месторождение","target":1,"target_name":"Дудинка","start_date":"01.04.2022"},
26:{"name":"СЕВМОРПУТЬ","ice_class":"Arc 5","speed":14,"source":4,"source_name":"Штокман","target":1,"target_name":"Дудинка","start_date":"08.04.2022"},
27:{"name":"ГРИГОРИЙ ШЕЛИХОВ","ice_class":"Arc 4","speed":14,"source":11,"source_name":"Новый порт","target":24,"target_name":"устье Лены","start_date":"10.04.2022"},
28:{"name":"УРАРТУ","ice_class":"Arc 4","speed":18,"source":29,"source_name":"Архангельск","target":24,"target_name":"устье Лены","start_date":"07.04.2022"},
29:{"name":"ФЕСКО ПАРИС","ice_class":"Arc 4","speed":18,"source":35,"source_name":"Терминал Утренний","target":27,"target_name":"Пролив Лонга","start_date":"15.04.2022"},
30:{"name":"ПРОГРЕСС","ice_class":"Arc 4","speed":18,"source":4,"source_name":"Штокман","target":35,"target_name":"Терминал УТренний","start_date":"16.04.2022"},
31:{"name":"МИХАИЛ БРИТНЕВ","ice_class":"Arc 4","speed":18,"source":41,"source_name":"Рейд Мурманска","target":11,"target_name":"Новый порт","start_date":"16.04.2022"},
32:{"name":"САБЕТТА","ice_class":"Arc 4","speed":16,"source":44,"source_name":"Индига","target":6,"target_name":"Победа Месторождение","start_date":"16.04.2022"},
33:{"name":"ГЕОРГИЙ УШАКОВ","ice_class":"Arc 4","speed":16,"source":27,"source_name":"Пролив Лонга","target":4,"target_name":"Штокман","start_date":"06.04.2022"},
34:{"name":"СЕВЕРНЫЙ ПРОЕКТ","ice_class":"Arc 4","speed":16,"source":25,"source_name":"Сабетта","target":5,"target_name":"Окно в Европу","start_date":"20.04.2022"},
35:{"name":"НИКОЛАЙ ЧУДОТВОРЕЦ","ice_class":"NO","speed":16,"source":25,"source_name":"Сабетта","target":5,"target_name":"Окно в Европу","start_date":"23.04.2022"},
36:{"name":"БЕРИНГ","ice_class":"Arc 4","speed":16,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"22.04.2022"},
37:{"name":"ТОЛБУХИН","ice_class":"Arc 4","speed":16,"source":41,"source_name":"Рейд Мурманска","target":1,"target_name":"Дудинка","start_date":"23.04.2022"},
38:{"name":"ЯМАЛ КРЕЧЕТ","ice_class":"Arc 4","speed":16,"source":4,"source_name":"Штокман","target":11,"target_name":"Новый порт","start_date":"25.04.2022"},
39:{"name":"CLEAN VISION","ice_class":"Arc 4","speed":14,"source":4,"source_name":"Штокман","target":24,"target_name":"устье Лены","start_date":"27.04.2022"},
40:{"name":"YAMAL SPIRIT","ice_class":"NO","speed":14,"source":25,"source_name":"Сабетта","target":29,"target_name":"Архангельск","start_date":"27.04.2022"},
41:{"name":"ТИКСИ","ice_class":"Arc 4","speed":16,"source":11,"source_name":"Новый порт","target":5,"target_name":"Окно в Европу","start_date":"25.04.2022"},
42:{"name":"ТАЙБОЛА","ice_class":"Arc 4","speed":16,"source":41,"source_name":"Рейд Мурманска","target":11,"target_name":"Новый порт","start_date":"30.04.2022"}}

icebreaker_data = {1:{"name":"50 лет Победы","ice_class":"Arc 9","speed":22,"move_pen_19_15":0.15, "move_pen_14_10":0.35,"source":27,"source_name":"Пролив Лонга","start_date":"27.02.2022"},
2:{"name":"Ямал","ice_class":"Arc 9","speed":21,"move_pen_19_15":0.15, "move_pen_14_10":0.35,"source":41,"source_name":"Рейд Мурманска","start_date":"27.02.2022"},
3:{"name":"Таймыр","ice_class":"Arc 9","speed":18.5,"move_pen_19_15":0.1, "move_pen_14_10":0.25,"source":16,"source_name":"Мыс Желания","start_date":"27.02.2022"},
4:{"name":"Вайгач","ice_class":"Arc 9","speed":18.5,"move_pen_19_15":0.1, "move_pen_14_10":0.25,"source":6,"source_name":"Победа месторождение","start_date":"27.02.2022"}}



class AbstractVessel:
    #id
    name:str # Наименование судна
    ice_class:str #Ледовый класс, допустимые значения "NO","Arc 1","Arc 2","Arc 3", "Arc 4","Arc 5","Arc 7","Arc 9"
    speed:float #скорость в узлах по чистой воде
    source:int #Пункт начала плавания, номер вершины в маршрутном графе
    start_date:dt.date
    move_pen_19_15: float #штраф при самостоятельном движении, если запрещено то 1
    move_pen_14_10: float  #штраф при самостоятельном под проводкой, если запрещено то 1 
    def calc_time(self,length,ice_cond):
        """
        Расчет времени прохождения ребра длиной length в условиях ice_cond
        """
        return calc_time(length, self.speed, self.move_pen_19_15, self.move_pen_14_10, ice_cond )
    
class IceBreaker(AbstractVessel):
    def load_from(self, data):
        """
        Загрузка из строки вида {"name":"Ямал","ice_class":"Arc 9","speed":21,"move_pen_19_15":0.15, "move_pen_14_10":0.35,"source":41,"source_name":"Рейд Мурманска","start_date":"27.02.2022"}
        """
        self.name = data["name"]
        self.ice_class = data["ice_class"]
        self.speed = data["speed"]
        self.source = data["source"]
        self.move_pen_19_15 = data["move_pen_19_15"]
        self.move_pen_14_10 = data["move_pen_14_10"]        
        self.start_date = dt.strptime(data["start_date"], '%d.%m.%Y')

class Vessel(AbstractVessel):
    #id
    target:int #Пункт окончания плавания, номер вершины в маршрутном графе
    move_pen_19_15_ice: float #штраф при движении под проводкой, если запрещено то 1
    move_pen_14_10_ice: float   #штраф при движении под проводкой, если запрещено то 1 
    def load_from(self, data):
        """
        Загрузка из строки вида {"name":"CLEAN VISION","ice_class":"Arc 4","speed":14,"source":4,"source_name":"Штокман","target":24,"target_name":"устье Лены","start_date":"27.04.2022"},
        """
        self.name = data["name"]
        self.ice_class = data["ice_class"]
        self.speed = data["speed"]
        self.source = data["source"]
        self.target = data["target"]
        self.start_date = dt.strptime(data["start_date"], '%d.%m.%Y')
        self.set_move_pen()

    def calc_time_ice(self,length,ice_cond, icebreaker:IceBreaker):
        """
        Расчет времени прохождения ребра длиной length в условиях ice_cond ледокольной проводкой
        """
        self_time = calc_time(length, self.speed, self.move_pen_19_15_ice, self.move_pen_14_10_ice, ice_cond )
        icbreaker_time = icebreaker.calc_time(length,ice_cond)
        return max(self_time,icbreaker_time)

    def set_move_pen(self):
        """
        Рассчитывает штрафы на движение по ледовому классу
        """    
        if self.ice_class in ["NO","Arc 1","Arc 2","Arc 3"]:
            self.move_pen_19_15 = 1
            self.move_pen_19_15_ice = 0
            self.move_pen_14_10 = 1
            self.move_pen_14_10_ice = 1
        elif self.ice_class in ["Arc 4","Arc 5","Arc 6"]:
            self.move_pen_19_15 = 1
            self.move_pen_19_15_ice = 0.2
            self.move_pen_14_10 = 1
            self.move_pen_14_10_ice = 0.3
        elif self.ice_class in ["Arc 7"]:
            self.move_pen_19_15 = 0.4
            self.move_pen_19_15_ice = 0.4
            self.move_pen_14_10 = 1
            self.move_pen_14_10_ice = 0.8        
        elif self.ice_class in ["Arc 9"]:
            raise ValueError ("Для Arc 9 нужно использовать отдельный конструктор IceBreaker ")
        else:
            raise ValueError ("Неизвестное значение ледового класса: "+str(self.ice_class))

def calc_time(length, speed, move_pen_19_15, move_pen_14_10, ice_cond ):
    """
    Рассчитывает время прохождения ребра в часах Если для данного льда самостоятельное движение невозможно возвращается бесконечность math.inf
    length - расстояние в морских милях
    speed - скорость в узлах (морских миль в час) по чистой воде
    move_pen_19_15 - штраф по льду 19-15
    move_pen_14_10 - штраф по льду 14-10
    ice_cond - ледовые условия на маршруте
    """
    assert(length>0)
    assert(speed>0)
    #определяем тяжесть ледовых условий
    if ice_cond >= 19.5:
        move_pen = 0
    elif ice_cond >= 14.5:
        move_pen = move_pen_19_15
    elif ice_cond >=10: 
        move_pen = move_pen_14_10 
    else: 
        move_pen = 1
    if move_pen == 1:
        return math.inf
    return length/(speed*(1-move_pen))