
from pydantic import BaseModel, field_validator
from typing import List, Optional
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

class IcebreakerPath(CustomBaseModel):
    icebreaker_id: int
    start_date: datetime
    source: int
    source_name: str
    min_ice_condition: Optional[float] = None  # худшие ледовые условия на маршруте
    waybill: List[PathEvent]   # описание пути


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