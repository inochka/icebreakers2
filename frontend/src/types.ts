export enum tModal {
    VESSEL = 'vessel',
    ICEBREAKER = 'icebreaker',
    GANTT = 'gantt'
}

export enum tTypeWay {
    MOVE = 'move', // самостоятельноe движение из точки
    WAIT = 'wait', // ожидание/простой
    FORMATION = 'formation', // проводка караваном
    FIN = 'fin' // прибытие
}

export interface IVessel {
    "id": number
    "name": string
    "ice_class": string
    "speed": number
    "source": number
    "source_name": string
    "target": number
    "target_name": string
    "start_date": string
}

export interface IIcebreaker {
    "id": number
    "name": string
    "ice_class": string
    "speed": number
    "speed_penalty_19_15": number
    "speed_penalty_14_10": number
    "source": number
    "source_name": string
    "start_date": string
}

export interface IWaybill {
    "event": tTypeWay
    "point": number //где произошло событие
    "time": string //когда произошло событие
}

export interface IPath {
    "id": number
    "type": typeTransport
    "start_date": string
    "end_date": string
    "source": number // Пункт начала плавания, номер вершины в маршрутном графе
    "source_name": string // название, определяется по номеру вершины
    "target": number //Пункт окончания плавания, номер вершины в маршрутном графе
    "target_name": string // название, определяется по номеру вершины
    "success": boolean // если false значит маршрут непроходим без ледокольной проводки и остальные параметры ниже отсутствуют
    "min_ice_condition"?: number //худшие ледовые условия на маршруте
    "speed": number //средняя скорость на маршруте
    "waybill"?: IWaybill[],
    "path_line"?: []
}

export interface IBaseNode {
    "id": number
    "lat": number
    "lon": number
    "point_name": string
    "rep_id": number
}

export interface IBaseEdge {
    "id": number, //сурроготный ключ для фронта (если нуженб пока непонятно)
    "start_point_id": number // начальная вершина
    "end_point_id": number	// конечная вершина
    "length": number // длина в морских милях
    "rep_id": number //видимо игнорируем
    "status": number
}

export enum typeTransport {
    "VESSELS" = 'vessels',
    'ICEBREAKERS' = 'icebreakers',
}

export type Select = {
    value: string
    label: string
}