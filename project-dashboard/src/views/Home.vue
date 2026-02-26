<template>
  <div class="home-page" style="min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; padding: 20px;">
    <div class="container" style="text-align: center; background: white; border-radius: 20px; padding: 60px 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 800px; width: 100%;">
      <h1 style="font-size: 36px; color: #333; margin-bottom: 20px; font-weight: bold;">结构件事业部管理系统</h1>
      <p style="font-size: 18px; color: #666; margin-bottom: 50px;">请选择您要访问的管理模块</p>
      
      <div class="button-group" style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;">
        <!-- 项目管理按钮 -->
        <div class="button-card" style="text-align: center; transition: transform 0.3s ease;">
          <div @click="goToProjectManagement" 
               class="nav-button" 
               style="background: linear-gradient(135deg, #409EFF 0%, #4d9eff 100%); color: white; padding: 30px; border-radius: 15px; cursor: pointer; box-shadow: 0 10px 20px rgba(64, 158, 255, 0.3); width: 220px; height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: all 0.3s ease; border: none;">
            <div style="font-size: 60px; margin-bottom: 20px;">📊</div>
            <h3 style="font-size: 22px; margin: 10px 0 5px 0; color: white; font-weight: 600;">项目管理</h3>
            <p style="font-size: 14px; color: rgba(255,255,255,0.9); margin: 0;">Project Management</p>
          </div>
        </div>
        
        <!-- NCR管理按钮 -->
        <div class="button-card" style="text-align: center; transition: transform 0.3s ease;">
          <div @click="goToNcrManagement" 
               class="nav-button" 
               style="background: linear-gradient(135deg, #67C23A 0%, #81c784 100%); color: white; padding: 30px; border-radius: 15px; cursor: pointer; box-shadow: 0 10px 20px rgba(103, 194, 58, 0.3); width: 220px; height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: all 0.3s ease; border: none;">
            <div style="font-size: 60px; margin-bottom: 20px;">📋</div>
            <h3 style="font-size: 22px; margin: 10px 0 5px 0; color: white; font-weight: 600;">NCR管理</h3>
            <p style="font-size: 14px; color: rgba(255,255,255,0.9); margin: 0;">NCR Management</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 跳转到项目管理页面
const goToProjectManagement = async () => {
  try {
    // 添加跳转提示
    ElMessage.info('正在跳转到项目管理界面...')
    // 使用路由跳转到项目管理主页
    await router.push('/homepage')
  } catch (error) {
    console.error('跳转到项目管理页面失败:', error)
    ElMessage.error('跳转失败，请稍后重试')
  }
}

// 跳转到NCR管理页面
const goToNcrManagement = async () => {
  try {
    // 添加跳转提示
    ElMessage.info('正在跳转到NCR管理界面...')
    // 使用路由跳转到增强版NCR仪表盘
    await router.push('/ncr-enhanced')
  } catch (error) {
    console.error('跳转到NCR管理页面失败:', error)
    ElMessage.error('跳转失败，请稍后重试')
  }
}
</script>

<style scoped>
.nav-button:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.nav-button:active {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.15);
}

.button-card:hover {
  transform: scale(1.05);
  transition: transform 0.3s ease;
}

/* 添加按钮点击效果 */
.nav-button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 添加渐变动画效果 */
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.nav-button:hover {
  animation: gradientShift 3s ease infinite;
  background-size: 200% 200%;
}
</style>