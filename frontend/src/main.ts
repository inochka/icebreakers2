import {createApp} from 'vue'
import './style.scss'
import App from './App.vue'
import {createPinia} from 'pinia'
// @ts-ignore
import vClickOutside from "click-outside-vue3";
import ganttastic from '@infectoone/vue-ganttastic'
import VueDatePicker from '@vuepic/vue-datepicker';
import {
    vTooltip,
    vClosePopper,
    Tooltip,
} from 'floating-vue'
import Vue3Toastify, { type ToastContainerOptions } from 'vue3-toastify';

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
    .use(vClickOutside)
    .use(ganttastic)
    .use(Vue3Toastify, {
        autoClose: 3000,
    } as ToastContainerOptions)
    .directive('tooltip', vTooltip)
    .directive('close-popper', vClosePopper)
    .component('VTooltip', Tooltip)
    .component('VueDatePicker', VueDatePicker)
    .mount('#app')