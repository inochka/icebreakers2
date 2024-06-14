import {defineStore} from "pinia";
import {CommonStore} from "./types.ts";
import {TypeSidebar} from "../../types.ts";

export const useCommonStore = defineStore<
    CommonStore.Id,
    CommonStore.State
>('CommonStore', {
    state: (): CommonStore.State => ({
        openModal: false,
        typeModal: null,
        modalInfo: null,

        typeSidebar: TypeSidebar.TEMPLATES,

        showGraph: true,

        isLoading: false,
    }),
})
