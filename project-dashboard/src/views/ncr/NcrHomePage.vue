<template>
  <div class="ncr-home">
    <el-container style="min-height: 100vh; padding-top: 120px;">
      <!-- 标题栏 -->
      <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #409EFF 0%, #4d9eff 100%); padding: 30px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);"> 
        <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: center; align-items: center; position: relative;">
          <div style="text-align: center;">
            <h1 style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">NCR管理</h1>
            <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">NCR流程管理</p>
          </div>
          <div style="color: white; font-size: 18px; position: absolute; right: 0;">
            <div>{{ currentTime }}</div>
          </div>
        </div>
      </div>

      <!-- 顶部导航 -->
      <el-header style="background: #fff; border-bottom: 1px solid #eee; padding: 0 20px; flex-shrink: 0; max-width: 1200px; margin: 0 auto; width: 100%;">
        <el-menu :default-active="activeMenu" mode="horizontal" background-color="#fff" text-color="#333" active-text-color="#67C23A" @select="handleMenuSelect">
          <el-menu-item index="1">项目管理</el-menu-item>
          <el-menu-item index="2">NCR管理</el-menu-item>
        </el-menu>
      </el-header>

      <el-main style="padding: 20px 0; display: flex; justify-content: center;">
        <div style="max-width: 1200px; width: 100%; padding: 0 20px;">
          <!-- NCR流程图表 -->
          <el-card shadow="hover" margin-bottom="20px" style="margin-top: 20px;">
            <NcrFlowChart />
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElContainer, ElHeader, ElMain, ElCard, ElMenu, ElMenuItem } from 'element-plus'
import { useRouter } from 'vue-router'
import NcrFlowChart from './NcrFlowChart.vue'
import 'element-plus/dist/index.css'

const router = useRouter()

// 当前显示的视图
const currentView = ref('ncr')

// 当前时间状态
const currentTime = ref('')

// 更新当前时间
const updateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 导航激活项
const activeMenu = ref('2')

// 处理菜单选择
const handleMenuSelect = (index) => {
  if (index === '1') {
    router.push('/home')  // 跳转到项目管理首页
  } else {
    currentView.value = 'ncr'
    activeMenu.value = '2'
  }
}

// 挂载时初始化
onMounted(() => {
  // 更新当前时间
  updateTime()
  // 每秒更新一次时间
  setInterval(updateTime, 1000)
})
</script>