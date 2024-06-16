from enum import Enum
import math
from datetime import datetime
from backend.utils import parse_dates
from backend.models import VesselModel, IcebreakerModel, CustomBaseModel


class AbstractVessel:
    idx: int
    api_class: type(CustomBaseModel)
    name: str  # Наименование судна
    ice_class: str  # Ледовый класс, допустимые значения "NO","Arc 1","Arc 2","Arc 3", "Arc 4","Arc 5","Arc 7","Arc 9"
    speed: float  # скорость в узлах по чистой воде
    source: int  # Пункт начала плавания, номер вершины в маршрутном графе
    start_date: datetime
    move_pen_19_15: float  # штраф при самостоятельном движении, если запрещено то 1
    move_pen_14_10: float  # штраф при самостоятельном под проводкой, если запрещено то 1

    def calc_time(self, length, ice_cond_val):
        """
        Расчет времени прохождения ребра длиной length в условиях ice_cond_val
        """
        return calc_time(length, self.speed, self.move_pen_19_15, self.move_pen_14_10, ice_cond_val)

    @classmethod
    def make_model_from_dict_entry(cls, id: int, attrs: dict):
        return cls.api_class(id=id, **attrs)


class IceBreaker(AbstractVessel):
    api_class = IcebreakerModel

    def __init__(self, idx: int, name: str, ice_class: str, speed: float, move_pen_19_15: float,
                 move_pen_14_10: float, source: int, source_name: str, start_date: str, **kwargs):
        """
        Инициализация экземпляра IceBreaker с использованием явных аргументов.
        {"name":"Ямал","ice_class":"Arc 9","speed":21,"move_pen_19_15":0.15, "move_pen_14_10":0.35,"source":41,"source_name":"Рейд Мурманска","start_date":"27.02.2022"}

        """
        self.idx = idx
        self.name = name
        self.ice_class = ice_class
        self.speed = speed
        self.source = source
        self.move_pen_19_15 = move_pen_19_15
        self.move_pen_14_10 = move_pen_14_10
        self.start_date = parse_dates(start_date)
        self.source_name = source_name

    def calc_time(self, length, ice_cond_val):
        """
        Расчет времени прохождения ребра длиной length в условиях ice_cond_val
        """
        # определяем тяжесть ледовых условий
        if ice_cond_val >= 19.5:
            speed = self.speed
        elif ice_cond_val >= 14.5:
            # правки по итогам встречи с оргами
            speed = ice_cond_val * (1-self.move_pen_19_15)
        elif ice_cond_val >= 10: #10:
            speed = ice_cond_val * (1-self.move_pen_14_10)
        else:
            return math.inf
        return length / speed


class Vessel(AbstractVessel):
    api_class = VesselModel
    # id
    target: int  # Пункт окончания плавания, номер вершины в маршрутном графе
    move_pen_19_15_ice: float  # штраф при движении под проводкой, если запрещено то 1
    move_pen_14_10_ice: float  # штраф при движении под проводкой, если запрещено то 1

    def __init__(self, idx: int, name: str, ice_class: str, speed: float, source: int, source_name: str,
                 target: int, target_name: str, start_date: str):
        """
        Инициализация экземпляра Vessel с использованием явных аргументов.
         {"name":"CLEAN VISION","ice_class":"Arc 4","speed":14,"source":4,"source_name":"Штокман","target":24,"target_name":"устье Лены","start_date":"27.04.2022"},

        """
        self.idx = idx
        self.name = name
        self.ice_class = ice_class
        self.speed = speed
        self.source = source
        self.target = target
        self.start_date = parse_dates(start_date)
        self.source_name = source_name
        self.target_name = target_name
        self.set_move_pen()

    def calc_time_with_icebreaker(self, length, ice_cond_val, icebreaker: IceBreaker):
        """
        Расчет времени прохождения ребра длиной length в условиях ice_cond_val ледокольной проводкой
        """
        if icebreaker:
            self_time = calc_time(length, self.speed, self.move_pen_19_15_ice, self.move_pen_14_10_ice, ice_cond_val)
            icebreaker_time = icebreaker.calc_time(length, ice_cond_val)
            return max(self_time, icebreaker_time)
        else:
            return super().calc_time(length, ice_cond_val)

    def set_move_pen(self):
        """
        Рассчитывает штрафы на движение по ледовому классу
        """
        if self.ice_class in ["NO", "Arc 1", "Arc 2", "Arc 3"]:
            self.move_pen_19_15 = 1
            self.move_pen_19_15_ice = 0.5
            self.move_pen_14_10 = 1
            self.move_pen_14_10_ice = 1
        elif self.ice_class in ["Arc 4", "Arc 5", "Arc 6"]:
            self.move_pen_19_15 = 1
            self.move_pen_19_15_ice = 0.2
            self.move_pen_14_10 = 1
            self.move_pen_14_10_ice = 0.3
        elif self.ice_class in ["Arc 7"]:
            self.move_pen_19_15 = 0.4
            self.move_pen_19_15_ice = 0
            self.move_pen_14_10 = 1
            self.move_pen_14_10_ice = 0.2
        elif self.ice_class in ["Arc 9"]:
            raise ValueError("Для Arc 9 нужно использовать отдельный конструктор IceBreaker ")
        else:
            raise ValueError("Неизвестное значение ледового класса: " + str(self.ice_class))


def calc_time(length, speed, move_pen_19_15, move_pen_14_10, ice_cond_val):
    """
    Рассчитывает время прохождения ребра в часах Если для данного льда самостоятельное движение невозможно возвращается бесконечность math.inf
    length - расстояние в морских милях
    speed - скорость в узлах (морских миль в час) по чистой воде
    move_pen_19_15 - штраф по льду 19-15
    move_pen_14_10 - штраф по льду 14-10
    ice_cond_val - ледовые условия на маршруте
    """
    assert (length > 0)
    assert (speed > 0)
    # определяем тяжесть ледовых условий
    if ice_cond_val >= 19.5:
        move_pen = 0
    elif ice_cond_val >= 14.5:
        move_pen = move_pen_19_15
    elif ice_cond_val >= 3: #10:
        move_pen = move_pen_14_10
    else:
        move_pen = 1
    if move_pen == 1:
        return math.inf
    return length / (speed * (1 - move_pen))