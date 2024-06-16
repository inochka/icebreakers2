import { ITemplate } from "../../types"

export namespace TemplateStore {
    export type Id = 'TemplateStore'

    export interface State {
        templates: ITemplate[]
        selectTemplate: null | ITemplate
        removingTemplate: null | ITemplate
    }

    export interface Actions {
        getTemplates(): () => Promise<void>
        removeTemplate(): () => Promise<void>
        createTemplate(): (params: ITemplate) => Promise<void>
    }
}
