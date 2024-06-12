from enum import Enum

class IceClass(Enum):
    NO = "NO"
    Arc1 = "Arc 1"
    Arc2 = "Arc 2"
    Arc3 = "Arc 3"
    Arc4 = "Arc 4"
    Arc5 = "Arc 5"
    Arc7 = "Arc 7"
    Arc9 = "Arc 9"

class PathEventsType(Enum):
    #(move, wait, formation, fin, stuck)
    move = "move"
    wait = "wait"
    formation = "formation"
    fin = "fin"
    stuck = "stuck"
