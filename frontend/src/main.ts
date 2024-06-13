import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import {createPinia} from 'pinia'
import vClickOutside from "click-outside-vue3";
import ganttastic from '@infectoone/vue-ganttastic'
import "vue3-openlayers/styles.css";
import OpenLayersMap from "vue3-openlayers";

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
    .use(vClickOutside)
    .use(ganttastic)
    .use(OpenLayersMap)
    .mount('#app')