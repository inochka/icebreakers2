import {defineStore} from "pinia";
import {IceTransportStore} from "./types.ts";
import {PathArgs} from "../../types.ts";
import {requestApi} from "../request.api.ts";
import {DateTime} from "luxon";

export const useIceTransportStore = defineStore<
    IceTransportStore.Id,
    IceTransportStore.State,
    // @ts-ignore
    IceTransportStore.Actions
>('IceTransportStore', {
    state: (): IceTransportStore.State => ({
        vessels: [],
        icebreakers: [],

        allVessels: [],
        allIcebreakers: [],

        pathsVessels: [],
        pathsIcebreakers: [],

        baseNodes: [],
        baseEdges: [],

        icebreakerPoints: [],
        vesselPoints: [],

        tiffDate: ''
    }),

    actions: {
        async calculatePath(template_name: string) {
            try {
                await requestApi({
                    method: 'post',
                    url: '/calculation_request/',
                    params: {template_name},
                })
            } catch (e) {
                await this.calculatePath(template_name)
            }
        },
        async getVessels(id?: number) {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/vessels/',
                    params: {id},
                })

                if (id === undefined) {
                    this.allVessels = data
                } else {
                    this.vessels.push(data)
                }
            } catch (e) {
                console.error(e)
            }
        },
        async getIcebreakers(id?: number) {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/icebreakers/',
                    params: {id},
                })

                if (id === undefined) {
                    this.allIcebreakers = data
                } else {
                    this.icebreakers.push(data)
                }
            } catch (e) {
                console.error(e)
            }
        },
        async getBaseEdges() {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/get_base_edges/',
                })

                this.baseEdges = data
            } catch (e) {
                console.error(e)
            }
        },
        async getBaseNodes() {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/get_base_nodes/',
                })

                this.baseNodes = data
            } catch (e) {
                console.error(e)
            }
        },
        async getPathVessels({vessel_id, template_name}: PathArgs) {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/calculation_request/vessels/',
                    params: {vessel_id, template_name}
                })

                if (data[0]) this.pathsVessels.push(data[0])
            } catch (e) {
                console.error(e)
            }
        },
        async getPathIcebreakers({icebreaker_id, template_name}: PathArgs) {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/calculation_request/icebreakers/',
                    params: {icebreaker_id, template_name}
                })

                if (data[0]) this.pathsIcebreakers.push(data[0])
            } catch (e) {
                console.error(e)
            }
        },
        async getTiffDate(dt: string) {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/get_tiff_name/',
                    params: {dt}
                })

                this.tiffDate = DateTime.fromISO(data).toFormat('yyyy_MM_dd')
            } catch (e) {
                console.error(e)
            }
        }
    },
})
