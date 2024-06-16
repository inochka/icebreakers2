import {IBaseEdge, IBaseNode, IIcebreaker, IPath, IVessel, PathArgs} from "../../types.ts";

export namespace IceTransportStore {
    export type Id = 'IceTransportStore'

    export interface State {
        vessels: IVessel[]
        icebreakers: IIcebreaker[]

        allVessels: IVessel[]
        allIcebreakers: IIcebreaker[]

        paths: IPath[]

        baseNodes: IBaseNode[]
        baseEdges: IBaseEdge[]

        icebreakerPoints: number[]
        vesselPoints: number[]

        tiffDate: string
    }

    export interface Actions {
        getVessels(): (idVessel?: number) => Promise<void>
        getIcebreakers(): (id?: number) => Promise<void>
        getPath(): (args: PathArgs) => Promise<void>
        getBaseEdges(): () => Promise<void>
        getBaseNodes(): () => Promise<void>
        calculatePath(): (template: string) => Promise<void>
        getTiffDate(): (date: string) => Promise<void>
    }
}