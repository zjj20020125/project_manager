<template>
  <div class="project-status-subtasks-detail">
    <div class="header-section">
      <h2>{{ status }} 项目子任务详情</h2>
      <div class="header-actions">
        <el-dropdown trigger="click" style="margin-right: 10px;">
          <el-button type="primary" :loading="exportLoading">
            导出数据<i class="el-icon-arrow-down el-icon--right"></i>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="exportCurrentData">
                导出当前页面
              </el-dropdown-item>
              <el-dropdown-item @click="exportAllData">
                导出全部数据
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <button @click="goBack" class="btn btn-primary">返回</button>
      </div>
    </div>



    <!-- 项目状态子任务列表 -->
    <el-card class="task-list-card">
      <template #header>
        <div class="card-header">
          <span>{{ status }} 项目子任务列表</span>
          <div class="filter-section">
            <el-select 
              v-model="statusFilter" 
              placeholder="按状态筛选" 
              style="width: 150px; margin-right: 10px;"
              @change="fetchSubtasks"
            >
              <el-option label="全部" value=""></el-option>
              <el-option label="未开始" value="未开始"></el-option>
              <el-option label="进行中" value="进行中"></el-option>
              <el-option label="已完成" value="已完成"></el-option>
              <el-option label="已验收" value="已验收"></el-option>
            </el-select>
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜索任务名称或负责人" 
              style="width: 200px;"
              @input="handleSearch"
            ></el-input>
          </div>
        </div>
      </template>

      <el-table 
        :data="filteredTasks" 
        v-loading="loading"
        style="width: 100%"
        stripe
        border
        height="500"
      >
        <el-table-column prop="taskName" label="任务名称" min-width="200">
          <template #default="scope">
            <span class="task-name">{{ scope.row.taskName }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="projectName" label="所属项目" width="150">
          <template #default="scope">
            <span class="project-name">{{ scope.row.projectName }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="wbsNo" label="WBS编码" width="100">
          <template #default="scope">
            <el-tag type="info">{{ scope.row.wbsNo }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="owner" label="负责人" width="120">
          <template #default="scope">
            <span class="owner-name">{{ scope.row.owner }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="planStart" label="计划开始" width="120">
          <template #default="scope">
            <span>{{ formatDate(scope.row.planStart) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="planEnd" label="计划结束" width="120">
          <template #default="scope">
            <span>{{ formatDate(scope.row.planEnd) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="actualStart" label="实际开始" width="120">
          <template #default="scope">
            <span>{{ formatDate(scope.row.actual_start_date) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="actualEnd" label="实际结束" width="120">
          <template #default="scope">
            <span>{{ formatDate(scope.row.actual_end_date) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="progress" label="进度" width="100">
          <template #default="scope">
            <el-progress 
              :percentage="parseFloat(scope.row.progress)" 
              :color="getProgressColor(parseFloat(scope.row.progress))"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalTasks"
        >
        </el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElCard, ElTable, ElTableColumn, ElTag, ElProgress, ElPagination, ElSelect, ElOption, ElInput, ElMessage, ElMessageBox, ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { projectApi } from '../api/index.js'
import * as XLSX from 'xlsx'

const router = useRouter()
const route = useRoute()

// Element Plus 服务组件安全调用包装函数
const safeElMessage = (message, options = {}) => {
  try {
    return ElMessage(message, options);
  } catch (error) {
    console.warn('ElMessage 调用失败:', error);
    return null;
  }
};

// 从路由参数获取状态
const status = ref(route.params.status || '')

// 导出状态
const exportLoading = ref(false)

// 状态映射函数：将前端显示的状态映射到数据库中的实际状态
const mapStatusToDb = (displayStatus) => {
  switch(displayStatus) {
    case '未开始':
      return '未开始';  // 数据库中可能没有这个状态，但可以尝试
    case '进行中':
      return '进行中';  // 数据库中可能没有这个状态，但可以尝试
    case '已完成':
      return '完成';  // 映射到数据库中的'完成'
    case '已结项':
      return '完成';  // 已结项通常意味着任务完成
    case '已验收':
      return '完成';  // 已验收通常意味着任务完成
    default:
      return displayStatus;  // 如果没有匹配项，返回原始状态
  }
}

// 数据状态
const loading = ref(false)
const subtasks = ref([])
const filteredTasks = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalTasks = ref(0)
const statusFilter = ref('')
const searchKeyword = ref('')

// 统计数据
const subtaskStats = ref({
  totalSubtasks: 0,
  completedSubtasks: 0,
  pendingSubtasks: 0
})

// 数据格式转换函数
const convertTaskData = (task) => {
  return {
    taskName: task.task_name || '',
    projectName: task.project_name || '',
    wbsNo: task.wbs_code || '',
    taskType: task.task_type || '子任务',  // 如果没有task_type字段，默认为'子任务'
    owner: task.task_owner || '',
    status: task.task_status || '',
    planStart: task.planned_start_date || '',
    planEnd: task.planned_end_date || '',
    actual_start_date: task.actual_start_date || '',
    actual_end_date: task.actual_end_date || '',
    progress: task.progress || 0,
    created_at: task.created_at || '',
    taskId: task.task_id || ''
  };
};

// 获取项目状态子任务数据
const fetchSubtasks = async () => {
  console.log('=== 开始获取子任务数据 ===');
  console.log('请求状态:', status.value);
  
  loading.value = true;
  
  try {
    // 显示加载提示
    let loadingMsg;
    try {
      loadingMsg = safeElMessageInfo(`正在加载${status.value}项目子任务数据...`, {
        duration: 0
      });
    } catch (e) {
      console.warn('加载消息创建失败:', e);
    }
    
    // 根据项目状态获取对应的任务数据
    // 使用状态映射以匹配数据库中的实际状态
    const mappedStatus = mapStatusToDb(status.value);
    console.log('原始状态:', status.value);
    console.log('映射后的状态:', mappedStatus);
    
    // 尝试从localStorage获取缓存数据
    const cachedData = localStorage.getItem('projectTasksData');
    const cachedStatus = localStorage.getItem('clickedStatus');
    
    let response;
    
    if (cachedData && cachedStatus === status.value) {
      // 使用缓存数据
      console.log('✅ 使用缓存的数据');
      try {
        response = JSON.parse(cachedData);
        console.log('缓存数据解析成功，条数:', response.length);
        // 清除缓存数据
        localStorage.removeItem('projectTasksData');
        localStorage.removeItem('clickedStatus');
        console.log('已清除缓存数据');
      } catch (parseError) {
        console.error('❌ 缓存数据解析失败:', parseError);
        throw new Error('缓存数据格式错误');
      }
    } else {
      // 从API获取最新数据
      console.log('🔄 从API获取最新数据');
      console.log('调用API方法: getTasksByProjectStatusTasks');
      console.log('API参数:', mappedStatus);
      
      try {
        response = await projectApi.getTasksByProjectStatusTasks(mappedStatus);
        console.log('✅ API调用成功');
        console.log('API返回数据:', response);
        console.log('返回数据类型:', typeof response);
        console.log('返回数据长度:', response?.length || 0);
      } catch (apiError) {
        console.error('❌ API调用失败:', apiError);
        console.error('错误详情:', {
          message: apiError.message,
          response: apiError.response,
          status: apiError.response?.status
        });
        throw new Error(`API调用失败: ${apiError.message}`);
      }
    }
    
    // 验证响应数据
    if (!response) {
      console.warn('⚠️ 响应数据为空');
      response = [];
    }
    
    if (!Array.isArray(response)) {
      console.error('❌ 响应数据不是数组格式:', typeof response);
      console.log('响应数据内容:', response);
      throw new Error('数据格式错误：期望数组格式');
    }
    
    console.log('开始转换数据格式，原始数据条数:', response.length);
    
    // 转换数据格式以匹配前端表格字段
    const convertedResponse = response.map(convertTaskData);
    console.log('✅ 数据转换完成');
    console.log('转换后的数据条数:', convertedResponse.length);
    console.log('第一条数据示例:', convertedResponse[0]);
    
    // 设置数据
    subtasks.value = convertedResponse || [];
    filteredTasks.value = subtasks.value;
    totalTasks.value = subtasks.value.length;
    
    console.log('📊 数据设置完成:', {
      subtasks: subtasks.value.length,
      filteredTasks: filteredTasks.value.length,
      totalTasks: totalTasks.value
    });
    
    // 计算统计信息
    calculateStats(subtasks.value);
    
    // 关闭加载提示
    loadingMsg.close();
    
    // 显示成功消息
    if (subtasks.value.length > 0) {
      ElMessage.success(`✅ 成功加载 ${subtasks.value.length} 条${status.value}项目子任务数据`);
    } else {
      ElMessage.info(`ℹ️ ${status.value}项目暂无子任务数据`);
      console.log('ℹ️ 没有找到匹配的数据');
    }
    
  } catch (error) {
    console.error(`❌ 获取${status.value}项目子任务失败:`, error);
    console.error('错误堆栈:', error.stack);
    
    // 关闭可能存在的加载提示
    try {
      ElMessage.closeAll();
    } catch (e) {
      // 忽略关闭消息的错误
    }
    
    safeElMessageError(`获取${status.value}项目子任务数据失败：${error.message}`);
  } finally {
    loading.value = false;
    console.log('=== 数据获取流程结束 ===\n');
  }
}

// 计算统计信息
const calculateStats = (tasksData) => {
  const allSubtasks = tasksData || [];
  
  const total = allSubtasks.length
  // 根据数据库中的实际状态值进行统计
  const completed = allSubtasks.filter(task => task.status === '完成' || task.status === '延期完成').length  // 完成 + 延期完成 = 已完成子任务
  const pending = allSubtasks.filter(task => task.status === '异常').length  // 异常 = 待完成子任务
  
  subtaskStats.value = {
    totalSubtasks: total,
    completedSubtasks: completed,
    pendingSubtasks: pending
  }
  
  // 同时更新当前页面显示的数据
  subtasks.value = allSubtasks
  filteredTasks.value = allSubtasks.slice(
    (currentPage.value - 1) * pageSize.value,
    currentPage.value * pageSize.value
  )
  totalTasks.value = allSubtasks.length
}

// 获取所有子任务数据（保留此方法供分页使用）
const fetchAllSubtasks = async () => {
  try {
    // 根据项目状态获取对应的任务数据
    // 使用状态映射以匹配数据库中的实际状态
    const mappedStatus = mapStatusToDb(status.value)
    const response = await projectApi.getTasksByProjectStatusTasks(mappedStatus)
    // 转换数据格式以匹配前端表格字段
    return response.map(convertTaskData) || [];
  } catch (error) {
    console.error(`获取所有${status.value}项目子任务失败:`, error)
    return [];
  }
}

// 根据状态获取标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case '未开始':
      return 'info'
    case '进行中':
      return 'warning'
    case '完成':
      return 'success'
    case '延期完成':
      return 'danger'
    case '异常':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取进度条颜色
const getProgressColor = (progress) => {
  if (progress < 30) return '#F56C6C'  // 红色
  if (progress < 70) return '#E6A23C'  // 黄色
  return '#67C23A'  // 绿色
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return date.toISOString().split('T')[0]
}

// 返回上一页
const goBack = () => {
  router.push({ name: 'HomePage' })
}

// 导出全部数据
const exportAllData = async () => {
  try {
    if (subtasks.value.length === 0) {
      safeElMessageWarning('当前没有可导出的数据')
      return
    }
    
    // 询问用户确认
    await ElMessageBox.confirm(
      `确定要导出全部 ${subtasks.value.length} 条${status.value}项目子任务数据吗？`,
      '导出确认',
      {
        confirmButtonText: '确定导出',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    exportLoading.value = true
    
    // 导出全部数据（使用所有已加载的数据）
    // 这里可以根据实际需求选择不同的导出策略：
    // 1. 导出当前页面显示的数据
    // 2. 导出所有已加载的数据
    // 3. 重新从API获取所有数据再导出
    
    let exportData = subtasks.value;
    
    // 如果需要重新获取所有数据（忽略当前筛选和分页）
    // 可以在这里添加重新获取数据的逻辑
    
    // 创建Excel文件
    const worksheet = XLSX.utils.json_to_sheet(exportData.map(task => ({
      '任务名称': task.taskName,
      '所属项目': task.projectName,
      'WBS编码': task.wbsNo,
      '负责人': task.owner,
      '状态': task.status,
      '计划开始时间': formatDate(task.planStart),
      '计划结束时间': formatDate(task.planEnd),
      '实际开始时间': formatDate(task.actual_start_date),
      '实际结束时间': formatDate(task.actual_end_date),
      '进度': task.progress + '%',
      '创建时间': formatDate(task.created_at)
    })));
    
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, '项目子任务数据');
    
    // 生成文件
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${status.value}项目子任务_全部数据_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    safeElMessageSuccess(`成功导出 ${exportData.length} 条${status.value}项目子任务数据`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导出失败:', error)
      safeElMessageError('导出失败: ' + (error.message || '未知错误'))
    }
  } finally {
    exportLoading.value = false
  }
}

// 导出当前页面数据（保持原有功能）
const exportCurrentData = async () => {
  try {
    if (filteredTasks.value.length === 0) {
      safeElMessageWarning('当前没有可导出的数据')
      return
    }
    
    // 询问用户确认
    await ElMessageBox.confirm(
      `确定要导出当前显示的 ${filteredTasks.value.length} 条${status.value}项目子任务数据吗？`,
      '导出确认',
      {
        confirmButtonText: '确定导出',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    exportLoading.value = true
    
    // 创建Excel文件
    const worksheet = XLSX.utils.json_to_sheet(filteredTasks.value.map(task => ({
      '任务名称': task.taskName,
      '所属项目': task.projectName,
      'WBS编码': task.wbsNo,
      '负责人': task.owner,
      '状态': task.status,
      '计划开始时间': formatDate(task.planStart),
      '计划结束时间': formatDate(task.planEnd),
      '实际开始时间': formatDate(task.actual_start_date),
      '实际结束时间': formatDate(task.actual_end_date),
      '进度': task.progress + '%',
      '创建时间': formatDate(task.created_at)
    })));
    
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, '项目子任务数据');
    
    // 生成文件
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${status.value}项目子任务_当前页面_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    safeElMessageSuccess(`成功导出 ${filteredTasks.value.length} 条${status.value}项目子任务数据`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导出失败:', error)
      safeElMessageError('导出失败: ' + (error.message || '未知错误'))
    }
  } finally {
    exportLoading.value = false
  }
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchSubtasks()
}

// 处理当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchSubtasks()
}

// 处理搜索
const handleSearch = () => {
  let result = subtasks.value
  
  // 按状态筛选
  if (statusFilter.value) {
    result = result.filter(task => task.status === statusFilter.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(task => 
      task.taskName.toLowerCase().includes(keyword) || 
      task.owner.toLowerCase().includes(keyword) ||
      task.projectName.toLowerCase().includes(keyword)
    )
  }
  
  filteredTasks.value = result
  totalTasks.value = result.length
}

// 监听路由参数变化
const watchRouteParams = () => {
  const newStatus = route.params.status || '';
  if (newStatus !== status.value) {
    status.value = newStatus;
    console.log('路由参数变化，新状态:', status.value);
    if (status.value) {
      fetchSubtasks();
    }
  }
};

// 页面加载时获取数据
onMounted(() => {
  console.log('=== ProjectStatusSubtasksDetailView mounted ===');
  console.log('route params:', route.params);
  console.log('route query:', route.query);
  console.log('初始status.value:', status.value);
  
  // 检查localStorage中的缓存数据
  const cachedData = localStorage.getItem('projectTasksData');
  const cachedStatus = localStorage.getItem('clickedStatus');
  console.log('缓存数据:', { cachedData: !!cachedData, cachedStatus });
  
  if (cachedData) {
    try {
      const parsedData = JSON.parse(cachedData);
      console.log('缓存的数据内容:', parsedData);
    } catch (e) {
      console.error('解析缓存数据失败:', e);
    }
  }
  
  if (status.value) {
    console.log(`准备加载${status.value}项目子任务数据`);
    // 显示加载提示
    safeElMessage(`正在加载${status.value}项目子任务数据...`, {
      duration: 2000
    });
    fetchSubtasks();
  } else {
    console.error('❌ 未提供项目状态参数');
    console.log('可用的路由参数:', Object.keys(route.params));
    ElMessage.warning('未识别到项目状态参数，请从首页重新点击进入');
  }
});

// 监听路由变化
watch(() => route.params.status, (newStatus) => {
  if (newStatus) {
    watchRouteParams();
  }
});
</script>

<style scoped>
.project-status-subtasks-detail {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.header-section h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.btn {
  padding: 8px 16px;
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn:hover {
  opacity: 0.9;
}



.task-list-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  display: flex;
  gap: 10px;
}

.task-name {
  font-weight: 500;
  color: #303133;
}

.project-name {
  color: #606266;
}

.owner-name {
  color: #409EFF;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-cards {
    flex-direction: column;
  }
  
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .filter-section {
    width: 100%;
  }
}
</style>