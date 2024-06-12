from enum import Enum
import math
from datetime import datetime
from backend.utils import parse_dates
from backend.models import VesselModel, IcebreakerModel, CustomBaseModel

class AbstractVessel:
    #id
    api_class: type(CustomBaseModel)
    name:str # Наименование судна
    ice_class:str #Ледовый класс, допустимые значения "NO","Arc 1","Arc 2","Arc 3", "Arc 4","Arc 5","Arc 7","Arc 9"
    speed:float #скорость в узлах по чистой воде
    source:int #Пункт начала плавания, номер вершины в маршрутном графе
    start_date:datetime
    move_pen_19_15: float #штраф при самостоятельном движении, если запрещено то 1
    move_pen_14_10: float  #штраф при самостоятельном под проводкой, если запрещено то 1 
    def calc_time(self,length,ice_cond_val):
        """
        Расчет времени прохождения ребра длиной length в условиях ice_cond_val
        """
        return calc_time(length, self.speed, self.move_pen_19_15, self.move_pen_14_10, ice_cond_val )

    @classmethod
    def make_model_from_dict_entry(cls, id: int, attrs: dict):
        return cls.api_class(id=id, **attrs)
    
class IceBreaker(AbstractVessel):

    api_class = IcebreakerModel

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
        self.start_date = parse_dates(data["start_date"])

class Vessel(AbstractVessel):

    api_class = VesselModel
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
        self.start_date = parse_dates(data["start_date"])
        self.set_move_pen()



    def calc_time(self,length,ice_cond_val, icebreaker:IceBreaker):
        """
        Расчет времени прохождения ребра длиной length в условиях ice_cond_val ледокольной проводкой
        """
        self_time = super().calc_time(length, ice_cond_val )
        if icebreaker:  
            icebreaker_time = icebreaker.calc_time(length,ice_cond_val)
            return max(self_time,icebreaker_time)
        else:
            return self_time
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
            self.move_pen_19_15_ice = 0
            self.move_pen_14_10 = 0.85
            self.move_pen_14_10_ice = 0.2        
        elif self.ice_class in ["Arc 9"]:
            raise ValueError ("Для Arc 9 нужно использовать отдельный конструктор IceBreaker ")
        else:
            raise ValueError ("Неизвестное значение ледового класса: "+str(self.ice_class))

def calc_time(length, speed, move_pen_19_15, move_pen_14_10, ice_cond_val ):
    """
    Рассчитывает время прохождения ребра в часах Если для данного льда самостоятельное движение невозможно возвращается бесконечность math.inf
    length - расстояние в морских милях
    speed - скорость в узлах (морских миль в час) по чистой воде
    move_pen_19_15 - штраф по льду 19-15
    move_pen_14_10 - штраф по льду 14-10
    ice_cond_val - ледовые условия на маршруте
    """
    assert(length>0)
    assert(speed>0)
    #определяем тяжесть ледовых условий
    if ice_cond_val >= 19.5:
        move_pen = 0
    elif ice_cond_val >= 14.5:
        move_pen = move_pen_19_15
    elif ice_cond_val >=10: 
        move_pen = move_pen_14_10 
    else: 
        move_pen = 1
    if move_pen == 1:
        return math.inf
    return length/(speed*(1-move_pen))