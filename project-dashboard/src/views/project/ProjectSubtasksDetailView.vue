<template>
  <el-container style="min-height: 100vh;">
    <!-- 顶部导航栏 -->
    <el-header style="background: #409EFF; padding: 0; color: white; display: flex; align-items: center;">
      <div style="max-width: 1200px; margin: 0 auto; width: 100%; display: flex; justify-content: center; align-items: center; position: relative;">
        <div style="position: absolute; left: 0;">
          <el-button @click="goBack" type="primary" plain style="margin-right: 20px;">
            <i class="el-icon-arrow-left"></i> 返回
          </el-button>
        </div>
        <div style="text-align: center; flex-grow: 1; margin: 0 20px;">
          <h2 style="margin: 0; font-size: 20px;">{{ projectName || '项目' }} - 子任务详情</h2>
        </div>
        <div style="color: white; font-size: 16px; position: absolute; right: 0;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </el-header>

    <el-main style="padding: 20px; display: flex; justify-content: center;">
      <div style="max-width: 1200px; width: 100%;">
        <!-- 项目信息卡片 -->
        <el-card shadow="hover" style="margin-bottom: 20px;" v-if="projectInfo && Object.keys(projectInfo).length > 0">
          <div slot="header" class="card-header">
            <span>项目基本信息</span>
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEditProject"
              style="float: right;"
            >
              修改项目信息
            </el-button>
          </div>
          <el-descriptions :column="3" border v-if="projectInfo && Object.keys(projectInfo).length > 0">
            <el-descriptions-item label="项目编号">{{ projectInfo.project_id || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="项目经理">{{ projectInfo.project_manager || '未指定' }}</el-descriptions-item>
            <el-descriptions-item label="项目状态">
              <el-tag :type="getStatusTagType(projectInfo.project_status)">
                {{ projectInfo.project_status || '未设定' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="计划开始时间">{{ projectInfo.planned_start_date || '未设定' }}</el-descriptions-item>
            <el-descriptions-item label="计划结束时间">{{ projectInfo.planned_end_date || '未设定' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ projectInfo.created_at || '未记录' }}</el-descriptions-item>
            <el-descriptions-item label="实际开始时间">{{ projectInfo.actual_start_date || '未开始' }}</el-descriptions-item>
            <el-descriptions-item label="实际结束时间">{{ projectInfo.actual_end_date || '未完成' }}</el-descriptions-item>
            <el-descriptions-item label="项目分类">
              <el-tag :type="getCategoryTagType(projectInfo.category)">
                {{ projectInfo.category || '未分类' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <div v-else style="text-align: center; padding: 20px;">
            未找到项目信息
          </div>
        </el-card>

       

        <!-- 项目子任务列表 -->
        <el-card shadow="hover">
          <div slot="header" class="card-header">{{ projectName || '项目' }} - 子任务列表</div>
          <el-table 
            :data="subtasksData" 
            border 
            style="width: 100%" 
            v-loading="loading"
            v-if="subtasksData && subtasksData.length > 0"
            fit
            :header-cell-style="{ textAlign: 'center', background: '#f5f7fa' }"
            :cell-style="{ textAlign: 'center', verticalAlign: 'middle' }"
          >
            <el-table-column prop="task_name" label="任务名称" min-width="200" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.task_name || scope.row.taskName || '未命名任务' }}
              </template>
            </el-table-column>
            <el-table-column prop="wbs_code" label="WBS编码" width="120" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.wbs_code || scope.row.wbsNo || 'N/A' }}
              </template>
            </el-table-column>
            <el-table-column prop="task_owner" label="任务负责人" width="120" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.task_owner || scope.row.owner || '未指定' }}
              </template>
            </el-table-column>
            <el-table-column prop="planned_start_date" label="计划开始时间" width="150" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.planned_start_date || scope.row.planStart || '未设定' }}
              </template>
            </el-table-column>
            <el-table-column prop="planned_end_date" label="计划结束时间" width="150" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.planned_end_date || scope.row.planEnd || '未设定' }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_start_date" label="实际开始时间" width="150" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.actual_start_date || scope.row.actualStart || '未开始' }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_end_date" label="实际结束时间" width="150" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.actual_end_date || scope.row.actualEnd || '未完成' }}
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="任务进度" width="120" align="center" header-align="center">
              <template #default="scope">
                <el-progress :percentage="Number(scope.row.progress?.toString().replace('%','') || 0)" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="task_status" label="任务状态" width="120" align="center" header-align="center">
              <template #default="scope">
                <!-- 使用动态计算的状态，而不是数据库的状态 -->
                <el-tag :type="getTaskStatusTagType(calculateTaskStatus(scope.row))">
                  {{ calculateTaskStatus(scope.row) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center" header-align="center" fixed="right">
              <template #default="scope">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleEdit(scope.row)"
                >
                  修改
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-else style="text-align: center; padding: 50px; color: #999;">
            暂无子任务数据
          </div>
        </el-card>
      </div>
    </el-main>

    <!-- 编辑任务对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      title="修改任务信息" 
      width="600px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form 
        ref="editFormRef" 
        :model="editForm" 
        label-width="120px"
        :rules="{
          task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
          task_owner: [{ required: true, message: '请输入任务负责人', trigger: 'blur' }]
        }"
      >
        <el-form-item label="任务 ID">
          <el-input v-model="editForm.task_id" disabled></el-input>
        </el-form-item>
        
        <el-form-item label="任务名称" required>
          <el-input v-model="editForm.task_name" placeholder="请输入任务名称"></el-input>
        </el-form-item>
        
        <el-form-item label="WBS 编码">
          <el-input v-model="editForm.wbs_code" placeholder="请输入 WBS 编码"></el-input>
        </el-form-item>
        
        <el-form-item label="任务负责人" required>
          <el-input v-model="editForm.task_owner" placeholder="请输入任务负责人"></el-input>
        </el-form-item>
        
        <el-form-item label="计划开始时间">
          <el-date-picker
            v-model="editForm.planned_start_date"
            type="date"
            placeholder="选择计划开始时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="计划结束时间">
          <el-date-picker
            v-model="editForm.planned_end_date"
            type="date"
            placeholder="选择计划结束时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="实际开始时间">
          <el-date-picker
            v-model="editForm.actual_start_date"
            type="date"
            placeholder="选择实际开始时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="实际结束时间">
          <el-date-picker
            v-model="editForm.actual_end_date"
            type="date"
            placeholder="选择实际结束时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="任务进度 (%)">
          <el-input-number 
            v-model="editForm.progress" 
            :min="0" 
            :max="100" 
            :step="5"
            style="width: 100%;"
          ></el-input-number>
        </el-form-item>
        
        <el-form-item label="任务状态">
          <el-select v-model="editForm.task_status" placeholder="请选择任务状态" style="width: 100%;">
            <el-option label="未开始" value="未开始"></el-option>
            <el-option label="进行中" value="进行中"></el-option>
            <el-option label="已完成" value="已完成"></el-option>
            <el-option label="已验收" value="已验收"></el-option>
            <el-option label="异常" value="异常"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="修改说明">
          <el-input 
            v-model="editForm.remarks_for_modification" 
            type="textarea" 
            :rows="3"
            placeholder="请输入修改说明（选填）"
          ></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmEdit" 
            :loading="editLoading"
          >
            确认修改
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑项目信息对话框 -->
    <el-dialog 
      v-model="editProjectDialogVisible" 
      title="修改项目信息" 
      width="600px"
      :close-on-click-modal="false"
      @close="handleEditProjectDialogClose"
    >
      <el-form 
        ref="editProjectFormRef" 
        :model="editProjectForm" 
        label-width="120px"
      >
        <el-form-item label="项目编号">
          <el-input v-model="editProjectForm.project_id" disabled></el-input>
        </el-form-item>
        
        <el-form-item label="项目名称" required>
          <el-input v-model="editProjectForm.project_name" placeholder="请输入项目名称"></el-input>
        </el-form-item>
        
        <el-form-item label="项目经理">
          <el-input v-model="editProjectForm.project_manager" placeholder="请输入项目经理姓名"></el-input>
        </el-form-item>
        
        <el-form-item label="计划开始时间">
          <el-date-picker
            v-model="editProjectForm.planned_start_date"
            type="date"
            placeholder="选择计划开始时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="计划结束时间">
          <el-date-picker
            v-model="editProjectForm.planned_end_date"
            type="date"
            placeholder="选择计划结束时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="实际开始时间">
          <el-date-picker
            v-model="editProjectForm.actual_start_date"
            type="date"
            placeholder="选择实际开始时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="实际结束时间">
          <el-date-picker
            v-model="editProjectForm.actual_end_date"
            type="date"
            placeholder="选择实际结束时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="项目分类">
          <el-select v-model="editProjectForm.category" placeholder="请选择项目分类" style="width: 100%;">
            <el-option label="未开始" value="未开始"></el-option>
            <el-option label="进行中" value="进行中"></el-option>
            <el-option label="已结项" value="已结项"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="修改说明">
          <el-input 
            v-model="editProjectForm.remarks_for_modification" 
            type="textarea" 
            :rows="3"
            placeholder="请输入修改说明（选填）"
          ></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editProjectDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmEditProject" 
            :loading="editProjectLoading"
          >
            确认修改
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElContainer, ElHeader, ElMain, ElCard, ElButton, ElTable, ElTableColumn, ElTag, ElProgress, ElDescriptions, ElDescriptionsItem, vLoading, ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber, ElSelect, ElOption, ElDatePicker, ElMessage, ElMessageBox } from 'element-plus'
import { projectApi } from '@/api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 状态变量
const projectName = ref('')
const projectId = ref('')
const currentTime = ref('')
const loading = ref(false)
const subtasksData = ref([])
const projectInfo = ref({})

// 编辑对话框相关
const editDialogVisible = ref(false)
const editFormRef = ref(null)
const editForm = ref({
  task_id: '',
  task_name: '',
  wbs_code: '',
  task_owner: '',
  planned_start_date: '',
  planned_end_date: '',
  actual_start_date: '',
  actual_end_date: '',
  progress: 0,
  task_status: ''
})
const editLoading = ref(false)

// 编辑项目对话框相关
const editProjectDialogVisible = ref(false)
const editProjectFormRef = ref(null)
const editProjectForm = ref({
  project_id: '',
  project_name: '',
  project_manager: '',
  planned_start_date: '',
  planned_end_date: '',
  actual_start_date: '',
  actual_end_date: '',
  category: '',
  remarks_for_modification: ''
})
const editProjectLoading = ref(false)

// ECharts实例
let ganttChart = null
const ganttRef = ref(null)

// 在onMounted中初始化数据
onMounted(() => {
  // 从路由参数获取项目信息
  projectId.value = route.params.projectId
  projectName.value = route.query.projectName || '项目'
  
  // 更新当前时间
  updateTime()
  // 每秒更新一次时间
  setInterval(updateTime, 1000)
  
  // 获取子任务数据
  fetchSubtasksData()
  
  window.addEventListener('resize', resizeCharts)
})

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

// 返回上一页
const goBack = () => {
  router.go(-1)  // 返回上一页
}

// 处理编辑
const handleEdit = (row) => {
  console.log('编辑任务:', row)
  
  // 填充表单数据
  editForm.value = {
    task_id: row.task_id || '',
    task_name: row.task_name || row.taskName || '',
    wbs_code: row.wbs_code || row.wbsNo || '',
    task_owner: row.task_owner || row.owner || '',
    planned_start_date: row.planned_start_date || row.planStart || '',
    planned_end_date: row.planned_end_date || row.planEnd || '',
    actual_start_date: row.actual_start_date || row.actualStart || '',
    actual_end_date: row.actual_end_date || row.actualEnd || '',
    progress: parseFloat(row.progress?.toString().replace('%','') || 0),
    task_status: row.task_status || row.status || ''
  }
  
  editDialogVisible.value = true
}

// 确认修改
const confirmEdit = async () => {
  if (!editFormRef.value) {
    console.error('❌ 表单引用不存在')
    ElMessage.error('表单初始化失败，请刷新页面')
    return
  }
  
  try {
    // 先进行表单验证
    await editFormRef.value.validate()
    console.log('✅ 表单验证通过')
    
    editLoading.value = true
    
    // 检查 task_id 是否存在
    if (!editForm.value.task_id) {
      console.error('❌ 任务 ID 为空', editForm.value)
      ElMessage.error('任务 ID 丢失，请重新打开编辑对话框')
      editLoading.value = false
      return
    }
    
    // 准备修改数据 - 确保日期格式正确
    const modifyData = {
      task_name: editForm.value.task_name,
      wbs_code: editForm.value.wbs_code,
      task_owner: editForm.value.task_owner,
      planned_start_date: editForm.value.planned_start_date || null,
      planned_end_date: editForm.value.planned_end_date || null,
      actual_start_date: editForm.value.actual_start_date || null,
      actual_end_date: editForm.value.actual_end_date || null,
      progress: Number(editForm.value.progress) || 0,
      task_status: editForm.value.task_status || '未开始',
      modifier_name: '当前用户', // TODO: 从用户会话中获取实际用户名
      remarks_for_modification: editForm.value.remarks_for_modification || '修改任务信息'
    }
    
    console.log('📝 提交修改数据:', JSON.stringify(modifyData, null, 2))
    console.log('🆔 任务 ID:', editForm.value.task_id)
    
    // 调用后端 API 更新任务数据
    const response = await projectApi.updateTask(editForm.value.task_id, modifyData)
    
    console.log('✅ API 响应:', response)
    
    if (response.success) {
      ElMessage.success('任务修改成功')
      editDialogVisible.value = false
      
      // 重新加载子任务数据和项目信息
      await fetchSubtasksData()
      
      // 显示提示消息，说明项目状态已自动更新
      ElMessage.info('项目状态已根据最新数据自动更新')
    } else {
      console.error('❌ 修改失败，服务器返回 success=false', response)
      throw new Error(response.message || '修改失败')
    }
    
  } catch (error) {
    console.error('❌ 修改任务失败:', error)
    console.error('错误堆栈:', error.stack)
    
    // 过滤掉正常的验证取消错误
    if (error.message !== 'validate' && !error.toString().includes('validate')) {
      let errorMsg = '修改任务失败'
      
      if (error.response) {
        // 服务器返回了错误响应
        console.error('📡 HTTP 错误响应:', error.response.status, error.response.data)
        errorMsg = error.response.data?.detail || error.response.data?.message || errorMsg
      } else if (error.message) {
        errorMsg = error.message
      }
      
      ElMessage.error(errorMsg)
    } else {
      console.log('ℹ️ 表单验证未通过，已取消提交')
    }
  } finally {
    editLoading.value = false
  }
}

// 处理对话框关闭
const handleDialogClose = () => {
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
}

// 处理编辑项目
const handleEditProject = () => {
  console.log('=== 开始编辑项目 ===')
  console.log('当前 projectInfo:', projectInfo.value)
  console.log('projectInfo 是否为空:', !projectInfo.value || Object.keys(projectInfo.value).length === 0)
  
  if (!projectInfo.value || Object.keys(projectInfo.value).length === 0) {
    ElMessage.warning('项目信息尚未加载，请稍后再试')
    return
  }
  
  // 填充表单数据
  editProjectForm.value = {
    project_id: projectInfo.value.project_id || '',
    project_name: projectInfo.value.project_name || '',
    project_manager: projectInfo.value.project_manager || '',
    planned_start_date: projectInfo.value.planned_start_date || '',
    planned_end_date: projectInfo.value.planned_end_date || '',
    actual_start_date: projectInfo.value.actual_start_date || '',
    actual_end_date: projectInfo.value.actual_end_date || '',
    category: projectInfo.value.category || '',
    remarks_for_modification: ''
  }
  
  console.log('填充后的表单数据:', editProjectForm.value)
  editProjectDialogVisible.value = true
}

// 确认修改项目
const confirmEditProject = async () => {
  if (!editProjectFormRef.value) {
    console.error('❌ 项目表单引用不存在')
    ElMessage.error('表单初始化失败，请刷新页面')
    return
  }
  
  try {
    // 先进行表单验证
    await editProjectFormRef.value.validate()
    console.log('✅ 项目表单验证通过')
    
    editProjectLoading.value = true
    
    // 检查 project_id 是否存在
    if (!editProjectForm.value.project_id) {
      console.error('❌ 项目ID 为空', editProjectForm.value)
      ElMessage.error('项目ID 丢失，请重新打开编辑对话框')
      editProjectLoading.value = false
      return
    }
    
    // 准备修改数据 - 确保日期格式正确
    const modifyData = {
      project_name: editProjectForm.value.project_name,
      project_manager: editProjectForm.value.project_manager || null,
      planned_start_date: editProjectForm.value.planned_start_date || null,
      planned_end_date: editProjectForm.value.planned_end_date || null,
      actual_start_date: editProjectForm.value.actual_start_date || null,
      actual_end_date: editProjectForm.value.actual_end_date || null,
      category: editProjectForm.value.category || null,
      modifier_name: '当前用户', // TODO: 从用户会话中获取实际用户名
      remarks_for_modification: editProjectForm.value.remarks_for_modification || '修改项目信息'
    }
    
    console.log('📝 提交修改数据:', JSON.stringify(modifyData, null, 2))
    console.log('🆔 项目ID:', editProjectForm.value.project_id)
    
    // 调用后端 API 更新项目数据
    const response = await projectApi.updateProject(editProjectForm.value.project_id, modifyData)
    
    console.log('✅ API 响应:', response)
    
    if (response.success || response.message) {
      ElMessage.success('项目信息修改成功')
      editProjectDialogVisible.value = false
      
      // 重新加载项目信息和子任务数据
      await fetchSubtasksData()
      
      // 显示提示消息
      ElMessage.info('项目状态已根据最新数据自动更新')
    } else {
      console.error('❌ 修改失败，服务器返回 success=false', response)
      throw new Error(response.message || '修改失败')
    }
    
  } catch (error) {
    console.error('❌ 修改项目失败:', error)
    console.error('错误堆栈:', error.stack)
    
    // 过滤掉正常的验证取消错误
    if (error.message !== 'validate' && !error.toString().includes('validate')) {
      let errorMsg = '修改项目失败'
      
      if (error.response) {
        // 服务器返回了错误响应
        console.error('📡 HTTP 错误响应:', error.response.status, error.response.data)
        
        // 特殊处理：如果没有提供有效字段，给出更友好的提示
        if (error.response.data?.detail?.includes('没有提供有效的更新字段')) {
          errorMsg = '未检测到任何修改，请至少修改一个字段后再保存'
        } else if (error.response.data?.detail?.includes('项目更新失败')) {
          errorMsg = '项目数据未发生变化，请修改其他字段或检查是否与原数据完全一致'
        } else {
          errorMsg = error.response.data?.detail || errorMsg
        }
      } else if (error.message) {
        errorMsg = error.message
      }
      
      ElMessage.error(errorMsg)
    } else {
      console.log('ℹ️ 表单验证未通过，已取消提交')
    }
  } finally {
    editProjectLoading.value = false
  }
}

// 处理编辑项目对话框关闭
const handleEditProjectDialogClose = () => {
  if (editProjectFormRef.value) {
    editProjectFormRef.value.resetFields()
  }
}

// 获取项目子任务数据
const fetchSubtasksData = async () => {
  loading.value = true
  try {
    console.log('正在获取项目ID:', projectId.value)
    console.log('正在获取项目名称:', route.query.projectName)
    
    // 使用项目标识符获取项目详细信息
    let projectIdentifier = null;
    
    // 优先使用路由参数中的项目ID，如果不存在则使用项目名称
    if (route.params.projectId) {
      projectIdentifier = route.params.projectId;
    } else if (route.query.projectName) {
      projectIdentifier = decodeURIComponent(route.query.projectName);
    }
    
    if (!projectIdentifier) {
      console.error('没有提供项目ID或项目名称');
      return;
    }
    
    // 获取项目详细信息
    const projectDetailResponse = await projectApi.getProjectsDetail()
    console.log('项目详细信息:', projectDetailResponse)
    
    let project = null;
    // 首先尝试根据项目ID查找
    if (projectId.value) {
      project = projectDetailResponse.find(p => String(p.project_id) === String(projectId.value));
    }
    
    // 如果通过ID未找到，尝试通过项目名称查找
    if (!project && route.query.projectName) {
      const queryProjectName = decodeURIComponent(route.query.projectName);
      project = projectDetailResponse.find(p => p.project_name === queryProjectName);
    }
    
    if (project) {
      projectInfo.value = project
      projectName.value = project.project_name
      document.title = `${projectName.value} - 子任务详情` // 更新页面标题
      console.log('找到项目信息:', project)
    } else {
      console.log('未找到项目，尝试使用第一个项目')
      // 如果找不到项目，使用第一个项目作为备选
      if (projectDetailResponse.length > 0) {
        const firstProject = projectDetailResponse[0]
        projectInfo.value = firstProject
        projectName.value = firstProject.project_name
        console.log('使用第一个项目信息:', firstProject)
      }
    }

    // 直接使用新API根据项目标识符获取子任务数据
    console.log('准备调用API，项目标识符:', projectIdentifier);
    try {
      const projectSubtasksResponse = await projectApi.getProjectSubtasks(projectIdentifier);
      console.log('项目子任务数据:', projectSubtasksResponse);
      
      // 标准化字段名，确保所有任务都有统一的字段结构
      const standardizedTasks = projectSubtasksResponse.map(task => {
        // 从任务对象中提取所有可能的字段名
        return {
          ...task,
          task_name: task.task_name || task.taskName || task.task_name || task.name || '未知任务',
          wbs_code: task.wbs_code || task.wbsNo || task.wbs_code || task.wbsCode || task.wbs_no || '',
          task_owner: task.task_owner || task.owner || task.task_owner || task.taskOwner || task.responsible || '未指定',
          planned_start_date: task.planned_start_date || task.planStart || task.planned_start_date || task.plan_start || task.plannedStart || '',
          planned_end_date: task.planned_end_date || task.planEnd || task.planned_end_date || task.plan_end || task.plannedEnd || '',
          actual_start_date: task.actual_start_date || task.actual_start_date || task.actualStart || task.actual_start || task['actual-start-time'] || '',
          actual_end_date: task.actual_end_date || task.actual_end_date || task.actualEnd || task.actual_end || task['actual-end-time'] || '',
          progress: (task.progress && typeof task.progress === 'string' && !task.progress.endsWith('%')) ? `${task.progress}%` : (task.progress || '0%'),
          task_status: task.task_status || task.status || task.task_status || task.taskStatus || task.Status || '未开始'
        };
      });
      
      console.log(`最终找到 ${standardizedTasks.length} 个任务属于项目 ${projectName.value}`);
      console.log('标准化后的任务数据:', standardizedTasks);
      subtasksData.value = standardizedTasks;
      
      // 初始化甘特图
      await initGanttChart();
    } catch (apiError) {
      console.error('API调用失败:', apiError);
      console.error('错误详情:', {
        message: apiError.message,
        response: apiError.response,
        request: apiError.request,
        config: apiError.config
      });
      
      // 显示用户友好的错误信息
      if (apiError.response) {
        console.error('HTTP错误状态:', apiError.response.status);
        console.error('HTTP错误数据:', apiError.response.data);
      }
      
      // 即使出错也要隐藏加载状态
      subtasksData.value = [];
    }
  } catch (error) {
    console.error('获取子任务数据失败:', error);
    console.error(error.stack);
    // 即使出错也要隐藏加载状态
    subtasksData.value = [];
  } finally {
    loading.value = false;
  }
}

// 初始化甘特图
const initGanttChart = async () => {
  if (!ganttRef.value || !subtasksData.value || subtasksData.value.length === 0) {
    console.log('甘特图不需要初始化：没有数据或DOM元素')
    return
  }
  
  // 销毁之前的图表实例
  if (ganttChart) {
    ganttChart.dispose()
  }
  
  // 确保DOM元素已经渲染
  await nextTick()
  
  ganttChart = echarts.init(ganttRef.value)
  
  // 准备甘特图数据 - 任务只要有开始或结束日期之一即可显示
  const filteredTasks = subtasksData.value.filter(task => 
    task.planned_start_date || task.planned_end_date
  )
  
  if (filteredTasks.length === 0) {
    ganttChart.setOption({
      title: {
        text: '暂无任务数据',
        left: 'center',
        top: 'center'
      }
    })
    return
  }
  
  const processedData = []
  const validTasks = []
  
  filteredTasks.forEach(task => {
    // 尝试多个可能的日期字段名
    const startDateStr = task.planned_start_date || task.planStart;
    const endDateStr = task.planned_end_date || task.planEnd;
    
    // 尝试解析日期字符串
    let startDate, endDate;
    
    if (startDateStr) {
      startDate = new Date(startDateStr);
    }
    if (endDateStr) {
      endDate = new Date(endDateStr);
    }
    
    // 如果其中一个日期为空或无效，尝试用另一个日期代替
    if (!startDate && endDate) {
      startDate = endDate;
    } else if (startDate && !endDate) {
      endDate = startDate;
    } else if (!startDate && !endDate) {
      // 如果两个日期都无效，创建一个当前日期的点作为占位符
      const today = new Date();
      startDate = new Date(today);
      endDate = new Date(today);
      endDate.setDate(endDate.getDate() + 1); // 结束日期设为明天
      console.log('使用默认日期的任务', task.task_name || task.taskName || '未知任务');
    }
    
    // 检查日期是否有效
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      // 如果解析失败，使用当前日期
      const today = new Date();
      startDate = new Date(today);
      endDate = new Date(today);
      endDate.setDate(endDate.getDate() + 1);
      console.log('使用默认日期的任务（原日期无效）', task.task_name || task.taskName || '未知任务');
    }
    
    // 确保结束日期不早于开始日期，如果不符合则交换
    if (endDate < startDate) {
      console.log('日期顺序错误，已调整', task, startDateStr, endDateStr);
      [startDate, endDate] = [endDate, startDate]; // 交换日期
    }
    
    processedData.push({
      name: task.task_name || task.taskName || task.task_name || '未知任务',
      value: [startDate.getTime(), endDate.getTime()],
      itemStyle: {
        color: '#409EFF'
      }
    });
    validTasks.push(task);
  });
  
  if (processedData.length === 0) {
    ganttChart.setOption({
      title: {
        text: '没有有效数据可以显示',
        left: 'center',
        top: 'center'
      }
    })
    return
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const task = validTasks[params.dataIndex]
        if (!task) return ''
        const taskName = task.task_name || task.taskName || task.task_name || '未知任务'
        const taskOwner = task.task_owner || task.owner || '未知负责人'
        const plannedStartDate = task.planned_start_date || task.planStart || '未知'
        const plannedEndDate = task.planned_end_date || task.planEnd || '未知'
        const actualStartDate = task.actual_start_date || task.actualStartTime || '未开始'
        const actualEndDate = task.actual_end_date || task.actualEndTime || '未完成'
        
        return `
          <div>任务：${taskName}</div>
          <div>负责人：${taskOwner}</div>
          <div>计划时间：${plannedStartDate} ~ ${plannedEndDate}</div>
          <div>实际时间：${actualStartDate} ~ ${actualEndDate}</div>
        `
      }
    },
    grid: { left: '15%', right: '8%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'time',
      min: Math.min(...processedData.map(d => d.value[0])),
      max: Math.max(...processedData.map(d => d.value[1])),
      axisLabel: { 
        formatter: (val) => {
          const date = new Date(val)
          return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
        }
      }
    },
    yAxis: {
      type: 'category',
      data: validTasks.map(task => task.task_name || task.taskName || task.task_name || '未知任务'),
      axisLabel: { interval: 0, fontSize: 10 },
      inverse: true
    },
    series: [
      {
        name: '任务进度',
        type: 'bar',
        data: processedData,
        barWidth: 15,
        itemStyle: {
          color: '#409EFF',
          borderRadius: 4
        }
      }
    ]
  }
  
  ganttChart.setOption(option)
  
  // 为图表添加resize监听
  if (!ganttChart._resizeHandler) {
    ganttChart._resizeHandler = () => {
      ganttChart.resize()
    }
    window.addEventListener('resize', ganttChart._resizeHandler)
  }
}

// 动态计算任务状态
const calculateTaskStatus = (task) => {
  const now = new Date()
  const currentDate = now.toISOString().split('T')[0] // 格式：YYYY-MM-DD
  
  const plannedStart = task.planned_start_date || task.planStart
  const plannedEnd = task.planned_end_date || task.planEnd
  const actualStart = task.actual_start_date || task.actualStart
  const actualEnd = task.actual_end_date || task.actualEnd
  
  // 情况 1: 已完成的任务 (有实际开始和结束时间)
  if (actualStart && actualEnd) {
    if (plannedStart && plannedEnd) {
      // 检查是否按时完成
      if (actualStart >= plannedStart && actualStart <= plannedEnd &&
          actualEnd >= plannedStart && actualEnd <= plannedEnd) {
        return '按时完成'
      } else if (actualEnd > plannedEnd) {
        return '延期完成'
      } else {
        return '完成'
      }
    } else {
      return '已完成'
    }
  }
  
  // 情况 2: 进行中的任务 (有实际开始时间，没有实际结束时间)
  if (actualStart && !actualEnd) {
    if (plannedStart && plannedEnd) {
      // 实际开始在计划范围内
      if (actualStart >= plannedStart && actualStart <= plannedEnd) {
        // 检查当前日期是否超过计划结束时间
        if (currentDate > plannedEnd) {
          return '异常' // 超期进行中
        } else {
          return '进行中'
        }
      }
      // 实际开始早于计划开始
      else if (actualStart < plannedStart) {
        if (currentDate > plannedEnd) {
          return '异常' // 提前开始但超期
        } else {
          return '进行中'
        }
      }
      // 实际开始晚于计划结束
      else if (actualStart > plannedEnd) {
        return '异常'
      }
    }
    // 没有计划时间，但有实际开始
    return '进行中'
  }
  
  // 情况 3: 未启动的任务 (没有实际开始和结束时间)
  if (!actualStart && !actualEnd) {
    if (plannedStart && plannedEnd) {
      // 当前日期在计划开始前
      if (currentDate < plannedStart) {
        return '未开始'
      }
      // 当前日期应该在计划范围内
      else if (currentDate >= plannedStart && currentDate <= plannedEnd) {
        return '异常' // 应该开始但未开始
      }
      // 当前日期超过计划结束时间
      else if (currentDate > plannedEnd) {
        return '异常' // 已经超期还未开始
      }
    } else if (plannedStart && currentDate < plannedStart) {
      return '未开始'
    } else {
      return '未开始'
    }
  }
  
  // 其他异常情况
  return '异常'
}

// 获取任务状态标签类型
const getTaskStatusTagType = (status) => {
  switch (status) {
    case '未开始':
      return 'warning'
    case '进行中':
      return 'info'
    case '已完成':
      return 'success'
    case '已验收':
      return 'primary'
    case '按时完成':
      return 'success'
    case '延期完成':
      return 'danger'
    case '完成':
      return 'success'
    case '异常':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取项目状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case '未开始':
      return 'warning'
    case '进行中':
      return 'info'
    case '已完成':
      return 'success'
    case '已验收':
      return 'primary'
    default:
      return 'info'
  }
}

// 获取项目分类标签类型
const getCategoryTagType = (category) => {
  switch (category) {
    case '未开始':
      return 'warning'
    case '进行中':
      return 'info'
    case '已结项':
      return 'success'
    default:
      return 'info'
  }
}

// 监听窗口resize事件
const resizeCharts = () => {
  ganttChart?.resize()
}

// 确保使用nextTick

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  // 销毁图表实例
  if (ganttChart) {
    ganttChart.dispose()
  }
})
</script>

<style scoped>
.card-header {
  font-weight: 600;
  font-size: 14px;
  padding-bottom: 8px;
}
.gantt-container {
  width: 100%;
  height: 500px;
}
</style>