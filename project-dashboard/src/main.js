import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import router from './router'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { initExtensionMonitoring } from '@/utils/extensionHandler'

const app = createApp(App)
app.use(router)
app.use(ElementPlus)

// 初始化扩展干扰监控
initExtensionMonitoring()

app.mount('#app')
