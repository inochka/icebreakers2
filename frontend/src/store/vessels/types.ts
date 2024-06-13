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
        getVessels(): () => Promise<void>
        getIcebreakers(): () => Promise<void>
        getPath(): (id: any) => Promise<void>
        getBaseEdges(): () => Promise<void>
        getBaseNodes(): () => Promise<void>
    }
}