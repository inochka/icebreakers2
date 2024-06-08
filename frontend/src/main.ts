import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import {createPinia} from 'pinia'
import vClickOutside from "click-outside-vue3";

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
    .use(vClickOutside)
    .mount('#app')