import {defineStore} from "pinia";
import {CommonStore} from "./types.ts";
import {tModal} from "../../types.ts";

export const useCommonStore = defineStore<
    CommonStore.Id,
    CommonStore.State
>('CommonStore', {
    state: (): CommonStore.State => ({
        openModal: true,
        typeModal: tModal.GANTT,
        modalInfo: null,

        isLoading: false
    }),
})
