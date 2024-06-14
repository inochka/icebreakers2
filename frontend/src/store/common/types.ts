import {IVessel, tModal, TypeSidebar} from "../../types.ts";

export namespace CommonStore {
    export type Id = 'CommonStore'

    export interface State {
        openModal: boolean
        typeModal: tModal | null
        modalInfo: IVessel | null

        showGraph: boolean

        typeSidebar: TypeSidebar

        isLoading: boolean
    }
}
