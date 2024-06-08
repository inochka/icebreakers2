import {tModal} from "../types.ts";

export namespace Store {
    export type Id = 'Store'

    export interface State {
        openModal: boolean
        typeModal: tModal | null
    }

    export interface Actions {
    }
}
