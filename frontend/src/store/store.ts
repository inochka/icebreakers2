import {defineStore} from "pinia";
import {Store} from "./types.ts";

export const useStore = defineStore<
    Store.Id,
    Store.State,
    Store.Actions
>('Store', {
    state: (): Store.State => ({
        openModal: false,
        typeModal: null
    }),

    actions: {},
})
