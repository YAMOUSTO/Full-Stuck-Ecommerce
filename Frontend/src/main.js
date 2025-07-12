import './assets/main.css' 

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router' 
import Toast, { POSITION } from 'vue-toastification'
import 'vue-toastification/dist/index.css'

const options = {
    position: POSITION.TOP_RIGHT, // Where toasts appear
    timeout: 4000,                // 4 seconds
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false
};

const app = createApp(App)
const pinia = createPinia()

app.use(createPinia())
app.use(router)
app.use(Toast, options)
app.mount('#app')