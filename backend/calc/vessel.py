from enum import Enum
import math
import datetime as dt

vessels = {1:{"name":"ДЮК II","ice_class":"Arc 5","move_class":"4-6","speed":15,"source":11,"source_name":"Новый порт","target":41,"target_name":"Рейд Мурманска","start_date":"01.03.2022 00:00"},
2:{"name":"САРМАТ","ice_class":"Arc 4","move_class":"4-6","speed":15,"source":25,"source_name":"Сабетта","target":29,"target_name":"Архангельск","start_date":"02.03.2022 00:00"},
3:{"name":"EDUARD TOLL","ice_class":"Arc 7","move_class":"7","speed":15,"source":25,"source_name":"Сабетта","target":41,"target_name":"Рейд Мурманска","start_date":"04.03.2022 00:00"},
4:{"name":"GEORGIY USHAKOV","ice_class":"Arc 7","move_class":"7","speed":15,"source":4,"source_name":"Штокман","target":27,"target_name":"Пролив Лонга","start_date":"07.03.2022 00:00"},
5:{"name":"RUDOLF SAMOYLOVICH","ice_class":"Arc 7","move_class":"7","speed":15,"source":11,"source_name":"Новый порт","target":24,"target_name":"устье Лены","start_date":"08.03.2022 00:00"},
6:{"name":"VLADIMIR VORONIN","ice_class":"Arc 7","move_class":"7","speed":15,"source":25,"source_name":"Сабетта","target":27,"target_name":"Пролив Лонга","start_date":"12.03.2022 00:00"},
7:{"name":"NIKOLAY YEVGENOV","ice_class":"Arc 7","move_class":"7","speed":14,"source":35,"source_name":"Терминал Утренний","target":27,"target_name":"Пролив Лонга","start_date":"13.03.2022 00:00"},
8:{"name":"CHRISTOPHE DE MARGERIE","ice_class":"Arc 7","move_class":"7","speed":14,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"07.03.2022 00:00"},
9:{"name":"BORIS VILKITSKY","ice_class":"Arc 7","move_class":"7","speed":19,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"07.03.2022 00:00"},
10:{"name":"АРКТИКА-2","ice_class":"Arc 5","move_class":"4-6","speed":19,"source":35,"source_name":"Терминал Утренний","target":24,"target_name":"устье Лены","start_date":"15.03.2022 00:00"},
11:{"name":"ИНЖЕНЕР ВЕШНЯКОВ","ice_class":"Arc 5","move_class":"4-6","speed":19,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"09.03.2022 00:00"},
12:{"name":"ТАМБЕЙ","ice_class":"Arc 4","move_class":"4-6","speed":19,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"16.03.2022 00:00"},
13:{"name":"ШТУРМАН АЛЬБАНОВ","ice_class":"Arc 7","move_class":"7","speed":19,"source":4,"source_name":"Штокман","target":1,"target_name":"Дудинка","start_date":"26.03.2022 00:00"},
14:{"name":"НИКИФОР БЕГИЧЕВ","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":11,"source_name":"Новый порт","target":5,"target_name":"Окно в Европу","start_date":"10.03.2022 00:00"},
15:{"name":"НОРИЛЬСКИЙ НИКЕЛЬ","ice_class":"Arc 7","move_class":"7","speed":14,"source":16,"source_name":"Мыс Желания","target":24,"target_name":"устье Лены","start_date":"13.03.2022 00:00"},
16:{"name":"АЙС ИГЛ","ice_class":"Arc 5","move_class":"4-6","speed":14,"source":11,"source_name":"Новый порт","target":4,"target_name":"Штокман","start_date":"24.03.2022 00:00"},
17:{"name":"ШТУРМАН КОШЕЛЕВ","ice_class":"Arc 7","move_class":"7","speed":15,"source":27,"source_name":"Пролив Лонга","target":25,"target_name":"Сабетта","start_date":"04.03.2022 00:00"},
18:{"name":"ШТУРМАН ЩЕРБИНИН","ice_class":"Arc 7","move_class":"7","speed":15,"source":6,"source_name":"Победа месторождение","target":5,"target_name":"Окно в Европу","start_date":"19.03.2022 00:00"},
19:{"name":"ШТУРМАН СКУРАТОВ","ice_class":"Arc 7","move_class":"7","speed":15,"source":35,"source_name":"Терминал Утренний","target":24,"target_name":"устье Лены","start_date":"19.03.2022 00:00"},
20:{"name":"ИОГАНН МАХМАСТАЛЬ","ice_class":"Arc 5","move_class":"4-6","speed":14,"source":11,"source_name":"Новый порт","target":5,"target_name":"Окно в Европу","start_date":"17.03.2022 00:00"},
21:{"name":"BORIS SOKOLOV","ice_class":"Arc 7","move_class":"7","speed":14,"source":29,"source_name":"Архангельск","target":1,"target_name":"Дудинка","start_date":"24.03.2022 00:00"},
22:{"name":"ИНЖЕНЕР ТРУБИН","ice_class":"Arc 5","move_class":"4-6","speed":12,"source":24,"source_name":"устье Лены","target":11,"target_name":"Новый порт","start_date":"08.03.2022 00:00"},
23:{"name":"БАРЕНЦ","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":28,"source_name":"Восточно-Сибирское 1","target":41,"target_name":"Рейд Мурманска","start_date":"20.03.2022 00:00"},
24:{"name":"ПОЛАР КИНГ","ice_class":"Arc 5","move_class":"4-6","speed":16,"source":28,"source_name":"Восточно-Сибирское 3","target":29,"target_name":"Архангельск","start_date":"16.03.2022 00:00"},
25:{"name":"МЫС ДЕЖНЕВА","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":6,"source_name":"Победа месторождение","target":1,"target_name":"Дудинка","start_date":"01.04.2022 00:00"},
26:{"name":"СЕВМОРПУТЬ","ice_class":"Arc 5","move_class":"4-6","speed":14,"source":4,"source_name":"Штокман","target":1,"target_name":"Дудинка","start_date":"08.04.2022 00:00"},
27:{"name":"ГРИГОРИЙ ШЕЛИХОВ","ice_class":"Arc 4","move_class":"4-6","speed":14,"source":11,"source_name":"Новый порт","target":24,"target_name":"устье Лены","start_date":"10.04.2022 00:00"},
28:{"name":"УРАРТУ","ice_class":"Arc 4","move_class":"4-6","speed":18,"source":29,"source_name":"Архангельск","target":24,"target_name":"устье Лены","start_date":"07.04.2022 00:00"},
29:{"name":"ФЕСКО ПАРИС","ice_class":"Arc 4","move_class":"4-6","speed":18,"source":35,"source_name":"Терминал Утренний","target":27,"target_name":"Пролив Лонга","start_date":"15.04.2022 00:00"},
30:{"name":"ПРОГРЕСС","ice_class":"Arc 4","move_class":"4-6","speed":18,"source":4,"source_name":"Штокман","target":35,"target_name":"Терминал УТренний","start_date":"16.04.2022 00:00"},
31:{"name":"МИХАИЛ БРИТНЕВ","ice_class":"Arc 4","move_class":"4-6","speed":18,"source":41,"source_name":"Рейд Мурманска","target":11,"target_name":"Новый порт","start_date":"16.04.2022 00:00"},
32:{"name":"САБЕТТА","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":44,"source_name":"Индига","target":6,"target_name":"Победа Месторождение","start_date":"16.04.2022 00:00"},
33:{"name":"ГЕОРГИЙ УШАКОВ","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":27,"source_name":"Пролив Лонга","target":4,"target_name":"Штокман","start_date":"06.04.2022 00:00"},
34:{"name":"СЕВЕРНЫЙ ПРОЕКТ","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":25,"source_name":"Сабетта","target":5,"target_name":"Окно в Европу","start_date":"20.04.2022 00:00"},
35:{"name":"НИКОЛАЙ ЧУДОТВОРЕЦ","ice_class":"NO","move_class":"0-3","speed":16,"source":25,"source_name":"Сабетта","target":5,"target_name":"Окно в Европу","start_date":"23.04.2022 00:00"},
36:{"name":"БЕРИНГ","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":5,"source_name":"Окно в Европу","target":35,"target_name":"Терминал Утренний","start_date":"22.04.2022 00:00"},
37:{"name":"ТОЛБУХИН","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":41,"source_name":"Рейд Мурманска","target":1,"target_name":"Дудинка","start_date":"23.04.2022 00:00"},
38:{"name":"ЯМАЛ КРЕЧЕТ","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":4,"source_name":"Штокман","target":11,"target_name":"Новый порт","start_date":"25.04.2022 00:00"},
39:{"name":"CLEAN VISION","ice_class":"Arc 4","move_class":"4-6","speed":14,"source":4,"source_name":"Штокман","target":24,"target_name":"устье Лены","start_date":"27.04.2022 00:00"},
40:{"name":"YAMAL SPIRIT","ice_class":"NO","move_class":"0-3","speed":14,"source":25,"source_name":"Сабетта","target":29,"target_name":"Архангельск","start_date":"27.04.2022 00:00"},
41:{"name":"ТИКСИ","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":11,"source_name":"Новый порт","target":5,"target_name":"Окно в Европу","start_date":"25.04.2022 00:00"},
42:{"name":"ТАЙБОЛА","ice_class":"Arc 4","move_class":"4-6","speed":16,"source":41,"source_name":"Рейд Мурманска","target":11,"target_name":"Новый порт","start_date":"30.04.2022 00:00"},
43:{"name":"50 лет Победы","ice_class":"Arc 9","move_class":"9_a","speed":22,"source":27,"source_name":"Пролив Лонга","start_date":"27.02.2022 00:00"},
44:{"name":"Ямал","ice_class":"Arc 9","move_class":"9_a","speed":21,"source":41,"source_name":"Рейд Мурманска","start_date":"27.02.2022 00:00"},
45:{"name":"Таймыр","ice_class":"Arc 9","move_class":"9_b","speed":18.5,"source":16,"source_name":"Мыс Желания","start_date":"27.02.2022 00:00"},
46:{"name":"Вайгач","ice_class":"Arc 9","move_class":"9_b","speed":18.5,"source":6,"source_name":"Победа месторождение","start_date":"27.02.2022 00:00"}}


class MoveType(Enum):
    CLEAN = 0 #Самостоятельное движение
    ICE = 1 #Движение под проводкой
    NOT = 2 #Движение запрещено

"""Режимы движения судов в зависимости от ледового класса"""
move_table = {
            "0-3": #No ice class, Ice1-Ice3
              {"21-20":{'move_type':MoveType.CLEAN,'slowdown':0}, #TODO уточнить когда переход
               "19-15":{'move_type':MoveType.ICE,'slowdown':0},
               "14-10":{'move_type':MoveType.NOT,'slowdown':1}
               },
            "4-6": #Arc4-Arc6
              {"21-20":{'move_type':MoveType.CLEAN,'slowdown':0},
               "19-15":{'move_type':MoveType.ICE,'slowdown':0.2},
               "14-10":{'move_type':MoveType.ICE,'slowdown':0.3}
               },
            "7": #Arc4-Arc6
              {"21-20":{'move_type':MoveType.CLEAN,'slowdown':0},
               "19-15":{'move_type':MoveType.CLEAN,'slowdown':0.4},
               "14-10":{'move_type':MoveType.ICE,'slowdown':0.85} #TODO уточнить
               },
            "9_a": #Arc9 50 лет Победы, Ямал 
              {"21-20":{'move_type':MoveType.CLEAN,'slowdown':0},
               "19-15":{'move_type':MoveType.CLEAN,'slowdown':0.1}, #TODO уточнить
               "14-10":{'move_type':MoveType.CLEAN,'slowdown':0.25} #TODO уточнить
               },
            "9_b": #Arc9 Вайгач, Таймыр
              {"21-20":{'move_type':MoveType.CLEAN,'slowdown':0},
               "19-15":{'move_type':MoveType.CLEAN,'slowdown':0.1},
               "14-10":{'move_type':MoveType.CLEAN,'slowdown':0.25} #TODO уточнить
               },             
            }

move_tbl = { "0-3": #No ice class, Ice1-Ice3": 
                   {"move_pen_19_15_clean":1,
                    "move_pen_19_15_clean":0.2,
                    "move_pen_14_10_clean":1,
                    "move_pen_14_10_clean":0.3
                    },
            "4-6": #Arc4-Arc6
                   {"move_pen_19_15_clean":1,
                    "move_pen_19_15_clean":0,
                    "move_pen_14_10_clean":1,
                    "move_pen_14_10_clean":1
                    },
             "7": #Arc4-Arc6
                    {"move_pen_19_15_clean":0.4,
                    "move_pen_19_15_clean":0.4,
                    "move_pen_14_10_clean":1,
                    "move_pen_14_10_clean":0.8
                    }
            } 

class AbstractVessel:
    #id
    name:str # Наименование судна
    ice_class:str #Ледовый класс, допустимые значения "NO","Arc 1","Arc 2","Arc 3", "Arc 4","Arc 5","Arc 7","Arc 9"
    speed:float #скорость в узлах по чистой воде
    source:int #Пункт начала плавания, номер вершины в маршрутном графе
    start_date:dt.date
    move_pen_19_15_clean: float #штраф при самостоятельном движении, если запрещено то 1
    move_pen_19_15_ice: float #штраф при движении под проводкой, если запрещено то 1
    move_pen_14_10_clean: float  #штраф при самостоятельном под проводкой, если запрещено то 1
    move_pen_14_10_ice: float   #штраф при движении под проводкой, если запрещено то 1  
    def __init__(self,name,ice_class,speed,source,start_date,move_pen_19_15_clean,move_pen_19_15_ice,move_pen_14_10_clean,move_pen_14_10_ice):
        self.name = name
        self.ice_class = ice_class
        self.speed = speed
        self.source = source
        self.start_date = start_date
        self.move_pen_19_15_clean = move_pen_19_15_clean
        self.move_pen_19_15_ice = move_pen_19_15_ice
        self.move_pen_14_10_clean = move_pen_14_10_clean
        self.move_pen_14_10_ice = move_pen_14_10_ice


class Vessel(AbstractVessel):
    #id
    target:int #Пункт окончания плавания, номер вершины в маршрутном графе
    def __init__(self,name,ice_class,speed,source,start_date,target):
        self.target = target
        if ice_class in ["NO","Arc 1","Arc 2","Arc 3"]:
            move_pen_19_15_clean = 1
            move_pen_19_15_ice = 0
            move_pen_14_10_clean = 1
            move_pen_14_10_ice = 1
        elif ice_class in ["Arc 4","Arc 5","Arc 6"]:
            move_pen_19_15_clean = 1
            move_pen_19_15_ice = 0.2
            move_pen_14_10_clean = 1
            move_pen_14_10_ice = 0.3
        elif ice_class in ["Arc 7"]:
            move_pen_19_15_clean = 0.4
            move_pen_19_15_ice = 0.4
            move_pen_14_10_clean = 1
            move_pen_14_10_ice = 0.8            
        elif ice_class in ["Arc 9"]:
            raise ValueError ("Для Arc 9 нужно использовать отдельный конструктор IceBreaker ")
        else:
            raise ValueError ("Неизвестное значение ледового класса: "+str(ice_class))
        super().__init__(name,ice_class,speed,source,start_date,move_pen_19_15_clean,move_pen_19_15_ice,move_pen_14_10_clean,move_pen_14_10_ice)

class IceBreaker(AbstractVessel):
    pass #TODO

def calc_time(length, speed, move_class, ice_cond , icebreaker = False ):
    """
    Рассчитывает время прохождения ребра в часах Если для данного льда самостоятельное движение невозможно возвращается бесконечность math.inf
    length - расстояние в морских милях
    speed - скорость в узлах (морских миль в час) по чистой воде
    move_class - мореходные качества судна в зависимости от ледового класса "0-3","4-6","7","9_a","9_b"
    ice_cond - ледовые условия на маршруте
    icebreaker - расчет с учетом ледовой проводки
    """
    assert(length>0)
    assert(speed>0)
    assert(move_class in move_table)
    #определяем тяжесть ледовых условий
    if ice_cond >= 20:
        ice_cond_id = '21-20'
    elif ice_cond >=15:
        ice_cond_id = '19-15'
    elif ice_cond >=10: 
        ice_cond_id = '14-10' 
    else: 
        return math.inf
    #определяем режим движения в этих условиях для судна
    move_type = move_table[move_class][ice_cond_id]['move_type']
    #проверяем возможность движения
    if not ( move_type== MoveType.CLEAN or (move_type== MoveType.ICE and icebreaker ) ):
        return math.inf
    # определяем скорость движения с учетом поправки
    # TODO поправить таблицу и учесть ледокольную проводку
    slowdown = move_table[move_class][ice_cond_id]['slowdown']
    return length/(speed*(1-slowdown))