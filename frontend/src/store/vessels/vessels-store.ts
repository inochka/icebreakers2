import {defineStore} from "pinia";
import {VesselStore} from "./types.ts";
import {vessels} from "../../mock/vessels.ts";
import {icebreakers} from "../../mock/icebreakers.ts";
import {path} from "../../mock/path.ts";
import {baseNode} from "../../mock/base_node.ts";
import {baseEdge} from "../../mock/base_edge.ts";

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
        async getVessels() {
            try {
                this.vessels = vessels
            } catch (e) {
                console.error(e)
            }
        },
        async getIcebreakers() {
            try {
                this.icebreakers = icebreakers
            } catch (e) {
                console.error(e)
            }
        },
        async getPaths() {
            try {
                this.paths = path
                this.baseNodes = baseNode
                this.baseEdges = baseEdge
            } catch (e) {
                console.error(e)
            }
        }
    },
})
