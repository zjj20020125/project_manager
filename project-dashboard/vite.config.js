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
        target: 'http://127.0.0.1:8001', // 使用127.0.0.1替代localhost
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        secure: false // 允许HTTP请求
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