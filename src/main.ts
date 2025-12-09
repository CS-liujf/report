import { createApp } from 'vue'
import App from './App.vue'
import svgIcon from "@/components/SvgIcon/SvgIcon.vue"
import 'virtual:svg-icons-register'

createApp(App).component('SvgIcon',svgIcon).mount('#app')
