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

class AlgoType(Enum):
    default = "default"
    best = "best"  # с лучшим ледоколом
    solo = "solo"  # самостоятельно


icebreake1_params = {"waybill": [
            {
                "event": "move",
                "point": 4,
                "dt": "2022-03-07T00:00:00"
            },
            {
                "event": "move",
                "point": 21,
                "dt": "2022-03-07T19:48:36.194040"
            },
            {
                "event": "move",
                "point": 16,
                "dt": "2022-03-09T01:17:56.220816"
            },
            {
                "event": "move",
                "point": 20,
                "dt": "2022-03-12T04:16:00.710592"
            },
            {
                "event": "move",
                "point": 19,
                "dt": "2022-03-16T09:26:17.203584"
            },
            {
                "event": "move",
                "point": 8,
                "dt": "2022-03-20T19:54:05.772240"
            },
            {
                "event": "move",
                "point": 12,
                "dt": "2022-03-25T14:29:11.277192"
            },
            {
                "event": "move",
                "point": 40,
                "dt": "2022-03-31T11:10:14.428064"
            },
            {
                "event": "move",
                "point": 42,
                "dt": "2022-04-06T18:00:06.046120"
            },
            {
                "event": "move",
                "point": 30,
                "dt": "2022-04-13T12:27:31.667736"
            },
            {
                "event": "move",
                "point": 18,
                "dt": "2022-04-22T07:23:25.965872"
            },
            {
                "event": "fin",
                "point": 27,
                "dt": "2022-05-04T09:43:12.923208"
            }
        ],
        "start_date": "2022-03-07T00:00:00",
        "end_date": "2022-03-19T02:19:46.957336",
        "source": 4,
        "source_name": "Штокман",
        "target": 27,
        "target_name": "пролив Лонга",
        "min_ice_condition": None,
        "speed": None,
        "icebreaker_id": 1,
        "template_name": "full",
        "path_line": [
            4,
            21,
            16,
            20,
            19,
            8,
            12,
            40,
            42,
            30,
            18,
            27
        ]}

icebreake2_params = {
        "waybill": [
            {
                "event": "move",
                "point": 16,
                "dt": "2022-03-13T00:00:00"
            },
            {
                "event": "move",
                "point": 20,
                "dt": "2022-03-15T00:43:39.067500"
            },
            {
                "event": "move",
                "point": 19,
                "dt": "2022-03-18T05:31:48.138446"
            },
            {
                "event": "move",
                "point": 8,
                "dt": "2022-03-21T16:00:10.147603"
            },
            {
                "event": "move",
                "point": 12,
                "dt": "2022-03-25T11:10:37.445649"
            },
            {
                "event": "fin",
                "point": 24,
                "dt": "2022-03-30T11:39:58.685795"
            }
        ],
        "start_date": "2022-03-13T00:00:00",
        "end_date": "2022-03-18T00:29:21.240146",
        "source": 16,
        "source_name": "Мыс Желания",
        "target": 24,
        "target_name": "устье Лены",
        "speed": None,
        "icebreaker_id": 2,
        "template_name": "full",
        "path_line": [
            16,
            20,
            19,
            8,
            12,
            24
        ]
    }