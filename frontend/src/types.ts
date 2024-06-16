export enum tModal {
    VESSEL = 'vessel',
    ICEBREAKER = 'icebreaker',
    GANTT = 'gantt',
    DELETE = 'delete',
    CREATE_TEMPLATE = 'createTemplate'
}

export enum tTypeWay {
    MOVE = 'move',
    WAIT = 'wait',
    FORMATION = 'formation',
    FIN = 'fin',
    STUCK = 'stuck'
}

export interface IVessel {
    id: number
    name: string
    ice_class: string
    speed: number
    source: number
    source_name: string
    target: number
    target_name: string
    start_date: string
}

export interface IIcebreaker {
    id: number
    name: string
    ice_class: string
    speed: number
    speed_penalty_19_15: number
    speed_penalty_14_10: number
    source: number
    source_name: string
    start_date: string
}

export interface IWaybill {
    event: tTypeWay
    point: number
    dt: string
}

export interface IPath {
    vessel_id: number
    type: typeTransport
    start_date: string
    end_date: string
    source: number
    source_name: string
    target: number
    target_name: string
    success: boolean
    min_ice_condition?: number
    speed: number
    waybill?: IWaybill[],
    path_line?: []
}

export interface IBaseNode {
    id: number
    lat: number
    lon: number
    point_name: string
    rep_id: number
}

export interface IBaseEdge {
    id: number,
    start_point_id: number
    end_point_id: number
    length: number
    rep_id: number
    status: number
}

export enum typeTransport {
    VESSELS = 'vessels',
    ICEBREAKERS = 'icebreakers',
}

export type Select = {
    value: string
    label: string
}

export enum TypeSidebar {
    TEMPLATES = 'templates',
    LAYERS = 'layers',
}

export interface ITemplate {
    name: string
    description: string
    vessels: number[]
    icebreakers: number[]
    algorythm: string
}

export type PathArgs = {
    vessel_id?: number
    icebreaker_id?: number
    template_name: string
}

export enum TypeLayersForMap {
    POINT = 'point',
    PATH = 'path'
}
