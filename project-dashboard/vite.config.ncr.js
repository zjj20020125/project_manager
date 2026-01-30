import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// NCR管理界面专用配置
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '172.16.33.192',
    port: 3001,  // NCR管理界面使用端口3001
    open: false,
    proxy: {
      '/api': {
        target: 'http://172.16.33.192:8002', // NCR后端API地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    // 添加CSP头
    headers: {
      'Content-Security-Policy': "script-src 'self' 'unsafe-inline' 'unsafe-eval'; object-src 'none';"
    }
  },
  // 添加CSP配置以允许ECharts使用eval()
  appType: 'spa',
  optimizeDeps: {
    exclude: []
  }
})