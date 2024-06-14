import {createApp} from 'vue'
import './style.scss'
import App from './App.vue'
import {createPinia} from 'pinia'
import vClickOutside from "click-outside-vue3";
import ganttastic from '@infectoone/vue-ganttastic'
import VueDatePicker from '@vuepic/vue-datepicker';

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
    .use(vClickOutside)
    .use(ganttastic)
    .component('VueDatePicker', VueDatePicker)
    .mount('#app')