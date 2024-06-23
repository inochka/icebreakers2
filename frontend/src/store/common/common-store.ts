import {defineStore} from "pinia";
import {CommonStore} from "./types.ts";
import {TypeSidebar} from "../../types.ts";
import {requestApi} from "../request.api.ts";

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

        grade: null
    }),

    actions: {
        async getGrade(template_name: string) {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/grade/',
                    params: {template_name},
                })

                this.grade = data
            } catch (e) {
                console.error(e)
            }
        }
    }
})
