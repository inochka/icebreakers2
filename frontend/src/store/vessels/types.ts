import {IBaseEdge, IBaseNode, IIcebreaker, IPath, IVessel} from "../../types.ts";

export namespace VesselStore {
    export type Id = 'VesselStore'

    export interface State {
        vessels: IVessel[]
        icebreakers: IIcebreaker[]
        paths: IPath[]
        baseNodes: IBaseNode[]
        baseEdges: IBaseEdge[]
    }

    export interface Actions {
        getVessels(): () => void,
        getIcebreakers(): () => void,
        getPaths(): () => void
    }
}