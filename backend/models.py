
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict
from datetime import datetime
from backend.constants import IceClass, PathEventsType, AlgoType
from backend.utils import parse_dates
from fastapi.encoders import jsonable_encoder

class CustomBaseModel(BaseModel):
    class Config:
        extra = "ignore"

class VesselModel(CustomBaseModel):
    id: int  # суррогатный идентификатор заявки
    name: str  # Наименование судна
    ice_class: IceClass  # Ледовый класс
    speed: float  # скорость в узлах по чистой воде
    source: int  # Пункт начала плавания, номер вершины в маршрутном графе
    source_name: str  # название, определяется по номеру вершины
    target: int  # Пункт окончания плавания, номер вершины в маршрутном графе
    target_name: str  # название, определяется по номеру вершины
    start_date: datetime  # Дата начала плавания

    @field_validator("start_date", mode="before")
    @classmethod
    def parse_start_date(cls, raw_str: str) -> datetime:
        return parse_dates(raw_str)

class IcebreakerModel(CustomBaseModel):
    id: int  # суррогатный идентификатор ледокола
    name: str  # Наименование судна
    ice_class: IceClass  # константа
    speed: float  # скорость в узлах по чистой воде
    move_pen_19_15: float = 0.  # штраф при движении в условиях 19-15
    move_pen_14_10: float = 0.  # штраф при движении в условиях 14-10
    source: int  # Пункт начала плавания, номер вершины в маршрутном графе
    source_name: str  # Определяется по номеру вершины
    start_date: datetime  # Дата начала плавания

    @field_validator("start_date", mode="before")
    @classmethod
    def parse_start_date(cls, raw_str: str) -> datetime:
        return parse_dates(raw_str)

class BaseNode(CustomBaseModel):
    id: int = -1 # идентификатор вершины графа
    lat: float
    lon: float
    point_name: str
    rep_id: Optional[int] = None  # rep_id - обозначение на картинке, нет явного требования к использованию

class BaseEdge(CustomBaseModel):
    id: int # сурроготный ключ для фронта (если нужен, пока непонятно)
    start_point_id: int = -1  # начальная вершина
    end_point_id: int = -1  # конечная вершина
    length: float  # длина в морских милях
    rep_id: Optional[int] = None  # видимо игнорируем
    status: Optional[int] = None  # на сессии ответов на вопросы сказали что игнорируем

class PathEvent(CustomBaseModel):
    event: PathEventsType  # тип события (move, wait, formation, fin, stuck)
    point: int  # где произошло событие
    dt: datetime  # когда произошло событие

class SimpleVesselPath(CustomBaseModel):
    total_time_hours: float = 0
    path_line: List[int] = []
    time_line: List[float] = []

class AllSimpleVesselPath(CustomBaseModel):
    # все пути в/из вершину
    node: int # общая точка путей
    paths: Dict[int, SimpleVesselPath] = {} # ключ - номер вершины, из / в которой идут пути


class VesselPath(CustomBaseModel):
    waybill: List[PathEvent] = []  # описание пути
    total_time_hours: float
    start_date: datetime
    end_date: Optional[datetime] = None
    source: int
    source_name: str
    target: int
    target_name: str
    success: bool  # если false, значит маршрут непроходим без ледокольной проводки
    min_ice_condition: Optional[float] = None  # худшие ледовые условия на маршруте
    speed: Optional[float] = None  # средняя скорость на маршруте
    vessel_id: int = -1
    template_name: str = ""  # имя шаблона, если расчет происходит по нему
    path_line: List[int] = []
    time_line: List[float] = []


class IcebreakerPath(CustomBaseModel):
    waybill: List[PathEvent] = []  # описание пути
    start_date: datetime
    end_date: Optional[datetime] = None
    source: int
    source_name: str
    speed: Optional[float] = None  # средняя скорость на маршруте
    icebreaker_id: int = -1
    path_line: List[int] = []
    time_line: List[float] = []
    template_name: str = ""  # имя шаблона, если расчет происходит по нему


class PostCalcPath(CustomBaseModel):
    vessel_id: int  # идентификатор судна

class PostCalcPathIce(CustomBaseModel):
    vessel_id: int
    icebreaker_id: int
    formation_point: int  # точка начала проводки
    leave_point: int  # точка окончания проводки

class Template(CustomBaseModel):
    name: str
    description: str = ""
    vessels: List[int]
    icebreakers: List[int]
    algorythm: AlgoType

class AllVesselPaths(CustomBaseModel):
    name: str
    description: str = ""
    vessels: List[int]
    icebreakers: List[int]
    algorythm: AlgoType

class Caravan(CustomBaseModel):
    start_node: int | None = None
    end_node: int | None = None
    vessel_ids: List[int] = []
    icebreaker_id: int = -1
    time_estimate: float = 0
    start_time: datetime
    template_name: str = ""

class CaravanConfiguration(CustomBaseModel):
    caravans: List[Caravan]
    solo_vessel_ids: List[int]
    time_estimate: float
    configuration_grade: float


class Grade(CustomBaseModel):
    """Оценка стоимости проводки"""
    stuck_vessels:int = 0 #количество судов не достигших точки назначения
    total_time: float = 0 #общее время всех судов на маршруте в часах (на считая ледоколов) в часах
    template_name: str = ""