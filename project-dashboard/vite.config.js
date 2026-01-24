import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8001', // 后端API地址 - 修改为实际后端端口
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