import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8001', // 本地后端服务（8001 端口）
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '') // 去掉/api 前缀
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