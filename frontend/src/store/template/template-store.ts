import {defineStore} from "pinia";
import {TemplateStore} from "./types.ts";
import { requestApi } from "../request.api.ts";
import {toast, ToastOptions} from "vue3-toastify";

export const useTemplateStore = defineStore<
    TemplateStore.Id,
    TemplateStore.State,
    TemplateStore.Actions
>('TemplateStore', {
    state: (): TemplateStore.State => ({
        templates: [],
        selectTemplate: null,
        removingTemplate: null
    }),
    actions: {
        async getTemplates() {
            try {
                const {data} = await requestApi({
                    method: 'get',
                    url: '/template/',
                })

                this.templates = data
            } catch (e) {
                console.error(e)
            }
        },
        async createTemplate(params) {
            try {
                await requestApi({
                    method: 'post',
                    url: '/template/',
                    data: params
                })

                this.templates.push(params)

                toast("Шаблон успешно создан", {
                    type: 'success',
                } as ToastOptions);
            } catch (e) {
                console.error(e)
            }
        },
        async removeTemplate() {
            try {
                await requestApi({
                    method: 'delete',
                    url: '/template/',
                    params: {template_name: this.removingTemplate.name}
                })

                const templateIdx = this.templates.findIndex(({name}) => name === this.removingTemplate.name)
                this.templates.splice(templateIdx, 1)

                this.removingTemplate = null
            } catch (e) {
                console.error(e)
            }
        }
    }
})
