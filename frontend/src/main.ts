import {createApp} from 'vue'
import './style.scss'
import App from './App.vue'
import {createPinia} from 'pinia'
import vClickOutside from "click-outside-vue3";
import ganttastic from '@infectoone/vue-ganttastic'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
    .use(vClickOutside)
    .use(ganttastic)
    .mount('#app')