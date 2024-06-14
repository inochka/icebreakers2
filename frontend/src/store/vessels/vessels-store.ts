import {defineStore} from "pinia";
import {VesselStore} from "./types.ts";
import {path} from "../../mock/path.ts";
import axios from "axios";
import {AxiosRequestConfig, AxiosResponse} from "axios";
import {vessels} from "../../mock/vessels.json.ts";
import {icebreakers} from "../../mock/icebreakers.json.ts";
import {typeTransport} from "../../types.ts";

interface IFetchData<D> extends AxiosRequestConfig<D> {
    data?: D
}

const baseURL = import.meta.env.VITE_APP_BASE_URL

const requestApi = async ({method, url, params, data}: IFetchData<D>): Promise<AxiosResponse<D>> => {
    return await axios({
        baseURL,
        method,
        url,
        data,
        params,
    });
}

export const useVesselsStore = defineStore<
    VesselStore.Id,
    VesselStore.State,
    VesselStore.Actions
>('VesselStore', {
    state: (): VesselStore.State => ({
        vessels: [],
        icebreakers: [],
        paths: [],
        baseNodes: [],
        baseEdges: []
    }),

    actions: {
        async getVessels(id?: number) {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/vessels/',
                    // params: {id: 1},
                })

                if (!id) {
                    this.vessels = data
                } else {

                }
            } catch (e) {
                console.error(e)
                this.vessels = vessels
            }
        },
        async getIcebreakers(id?: number) {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/icebreakers/',
                    params: {id},
                })

                if (!id) {
                    this.icebreakers = data
                } else {

                }
            } catch (e) {
                console.error(e)
                this.icebreakers = icebreakers
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
        async getPath(vessel_id: number, type: typeTransport) {
            try {
                const {data} = await requestApi({
                    method: 'post',
                    url: '/calculate_path/',
                    data: {vessel_id}
                })

                this.paths.push({...data, id: vessel_id, type})
            } catch (e) {
                console.error(e)
                this.paths.push({...path[vessel_id], id: vessel_id, type})
            }
        }
    },
})
