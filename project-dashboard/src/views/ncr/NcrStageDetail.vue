<template>
  <div class="ncr-stage-detail-container">
    <div class="header-section">
      <el-page-header @back="goBack" content="NCR阶段详情" />
      <h2>{{ stageName }} 阶段详情</h2>
      <p>该阶段共包含 {{ totalCount }} 条NCR记录</p>
    </div>

    <el-card class="filter-section" shadow="never">
      <el-form :inline="true" :model="filterForm" class="demo-form-inline">
        <el-form-item label="状态筛选">
          <el-select v-model="filterForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="待处理"></el-option>
            <el-option label="处理中" value="处理中"></el-option>
            <el-option label="已完成" value="已完成"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="优先级筛选">
          <el-select v-model="filterForm.priority" placeholder="请选择优先级" clearable>
            <el-option label="高" value="高"></el-option>
            <el-option label="中" value="中"></el-option>
            <el-option label="低" value="低"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onQuery">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="data-section" shadow="never">
      <div slot="header" class="clearfix">
        <span>数据列表</span>
        <el-pagination
          class="pagination-right"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalCount">
        </el-pagination>
      </div>
      
      <!-- 调试信息：显示 API 返回的原始数据 -->
      <div v-if="ncrList.length > 0" style="margin-bottom: 10px; padding: 10px; background: #f0f9ff; border-left: 4px solid #409EFF;">
        <h4 style="margin: 0 0 10px 0;">📊 数据统计</h4>
        <p style="margin: 5px 0;">✅ 加载记录数：<strong>{{ ncrList.length }}</strong></p>
        <p style="margin: 5px 0;">✅ 总记录数：<strong>{{ totalCount }}</strong></p>
        <p style="margin: 5px 0;">🔍 当前阶段：<strong>{{ stageName }}</strong></p>
        <details style="margin-top: 10px;">
          <summary style="cursor: pointer; color: #409EFF;">🔬 查看第一条数据的完整结构（点击展开）</summary>
          <pre style="background: #fff; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px; margin-top: 5px;">{{ JSON.stringify(ncrList[0], null, 2) }}</pre>
        </details>
        <details style="margin-top: 10px;">
          <summary style="cursor: pointer; color: #409EFF;">📋 查看所有字段名（点击展开）</summary>
          <div style="background: #fff; padding: 10px; border-radius: 4px; margin-top: 5px;">
            <span v-for="(key, index) in Object.keys(ncrList[0])" :key="index" style="display: inline-block; background: #ecf5ff; padding: 4px 8px; margin: 2px; border-radius: 3px; font-size: 12px;">
              {{ key }}
            </span>
          </div>
        </details>
      </div>
      
      <el-table 
        :data="ncrList" 
        v-loading="loading"
        style="width: 100%"
        border
        @row-click="handleRowClick"
        highlight-current-row>
        <!-- 动态生成表格列 -->
        <template v-for="(column, index) in tableColumns" :key="column.prop">
          <el-table-column 
            :prop="column.prop" 
            :label="column.label" 
            :width="column.width" 
            :min-width="column.minWidth"
            :align="column.align || 'center'"
            :show-overflow-tooltip="column.showOverflowTooltip"
            v-if="!column.hidden">
            <template #default="scope" v-if="column.prop === 'status'">
              <el-tag :type="getStatusTagType(scope.row[column.prop])">
                {{ scope.row[column.prop] }}
              </el-tag>
            </template>
          </el-table-column>
        </template>
        <!-- 操作列 -->
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="scope">
            <el-button size="mini" type="primary" @click.stop="viewDetail(scope.row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { projectApi } from '../../api/index.js';
import { ElMessage } from 'element-plus';

export default {
  name: 'NcrStageDetail',
  setup() {
    const route = useRoute();
    const router = useRouter();
    
    // 响应式数据
    const stageName = ref('');
    const ncrList = ref([]);
    const totalCount = ref(0);
    const loading = ref(false);
    const currentPage = ref(1);
    const pageSize = ref(20);
    const tableColumns = ref([]); // 动态表格列配置
    
    // 筛选表单
    const filterForm = reactive({
      status: '',
      priority: ''
    });

    // 初始化数据
    const fetchData = async () => {
      loading.value = true;
      try {
        // 从路由参数获取阶段名称
        stageName.value = route.params.stage || '';
            
        if (!stageName.value) {
          ElMessage.warning('未指定阶段名称');
          loading.value = false;
          return;
        }
            
        console.log('🔍 请求阶段详情:', {
          阶段名称:stageName.value,
          完整路由参数:route.params,
          当前页码:currentPage.value,
          每页数量:pageSize.value
        });
            
        // 获取 NCR 数据
        const params = {
          stage: stageName.value,
          status: filterForm.status,
          priority: filterForm.priority,
          page: currentPage.value,
          limit: pageSize.value
        };
            
        console.log('📡 发送 API 请求参数:', params);
            
        // 使用 NCR API 获取数据
        const response = await projectApi.getNcrByStage(params);
        
        console.log('📥 接收到 API 响应:', response);
            
        // 分析响应数据结构
        console.log('🔍 响应数据类型:', typeof response);
        console.log('🔍 是否为数组:', Array.isArray(response));
        console.log('🔍 响应对象的所有键:', Object.keys(response || {}));
        
        if (response) {
          // 检查是否是 {data: [], total: 0} 格式
          if (Array.isArray(response)) {
            console.log('✅ API 直接返回数组');
            ncrList.value = response || [];
            totalCount.value = response.length;
          } else if (response.data !== undefined) {
            console.log('✅ API 返回标准格式 {data, total}');
            console.log('📋 data 字段类型:', typeof response.data);
            console.log('📋 data 数组长度:', response.data?.length);
            console.log('📋 total 字段值:', response.total);
            
            if (Array.isArray(response.data) && response.data.length > 0) {
              console.log('🔬 第一条数据的结构:');
              console.log('  - 完整数据:', response.data[0]);
              console.log('  - 所有字段名:', Object.keys(response.data[0]));
              
              // 动态生成表格列配置
              generateTableColumns(response.data[0]);
            }
            
            ncrList.value = response.data || [];
            totalCount.value = response.total || 0;
          } else {
            console.warn('⚠️ API 返回未知格式:', response);
            ncrList.value = [];
            totalCount.value = 0;
          }
          
          console.log('✅ 数据加载完成:', {
            记录数:ncrList.value.length,
            总数:totalCount.value,
            第一条数据:ncrList.value[0]
          });
              
          if (totalCount.value === 0) {
            ElMessage.info({
              message: `【${stageName.value}】阶段暂无 NCR 记录`,
              type: 'info',
              duration: 3000
            });
          } else {
            ElMessage.success({
              message: `找到 ${totalCount.value} 条【${stageName.value}】阶段的 NCR 记录`,
              type: 'success',
              duration: 2000
            });
          }
        }
      } catch (error) {
        console.error('❌ 获取 NCR 数据失败:', error);
        console.error('错误详情:', {
          错误消息:error.message,
          错误堆栈:error.stack,
          响应数据:error.response?.data
        });
        ElMessage.error('获取数据失败，请稍后重试');
      } finally {
        loading.value = false;
      }
    };

    // 获取状态标签类型
    const getStatusTagType = (status) => {
      switch (status) {
        case '待处理':
          return 'warning';
        case '处理中':
          return 'primary';
        case '已完成':
          return 'success';
        default:
          return 'info';
      }
    };

    // 获取优先级标签类型
    const getPriorityTagType = (priority) => {
      switch (priority) {
        case '高':
        case '一级':
          return 'danger';
        case '中':
        case '二级':
          return 'warning';
        case '低':
          return 'success';
        default:
          return 'info';
      }
    };

    // 动态生成表格列配置
    const generateTableColumns = (firstRow) => {
      if (!firstRow) return;
      
      const columns = [];
      const fieldMap = {
        // 常用字段映射（字段名：中文标签）
        'ch': '图号',
        'xmh': '项目号',
        'bhgpmc': '不合格品名称',
        'cpbh': '产品编号',
        'fsjd': '发生阶段',
        'sl': '数量',
        'sscx': '所属产线',
        'dqjd': '当前阶段',
        'wczz': '完成职责',
        'cjr': '创建人',
        'cjrq': '创建日期',
        'fsrq': '发生日期',
        'cjbm': '创建部门',
        'fsbm': '发生部门',
        'zrbm': '责任部门',
        'wtfl': '问题分类',
        'wlbm': '物料编码',
        'th': '图号',
        'sscpmc': '所属产品名称',
        'zlry': '质量人员'
      };
      
      // 遍历第一行数据的所有字段
      Object.keys(firstRow).forEach(field => {
        const value = firstRow[field];
        
        // 跳过空值、null、undefined、纯空格的字段
        if (value === null || value === undefined || 
            (typeof value === 'string' && value.trim() === '') ||
            field === 'id') { // 跳过 id 字段
          return;
        }
        
        // 根据字段名生成中文标签
        let label = fieldMap[field] || field.toUpperCase();
        
        // 设置列宽
        let width = 120;
        let minWidth = null;
        
        // 特殊字段处理
        if (field === 'bhgpmc' || field === 'cpbhgztms' || field === 'bz') {
          minWidth = 150;
          width = null;
        } else if (field === 'ch' || field === 'th' || field === 'xmh') {
          width = 150;
        } else if (field === 'sl' || field === 'wlbm') {
          width = 100;
        }
        
        columns.push({
          prop: field,
          label: label,
          width: width,
          minWidth: minWidth,
          align: 'center',
          showOverflowTooltip: true,
          hidden: false
        });
      });
      
      tableColumns.value = columns;
      console.log('✅ 动态生成的表格列:', columns.length, '列');
      console.log('📋 列配置:', columns);
    };
    
    // 查询
    const onQuery = () => {
      currentPage.value = 1;
      fetchData();
    };

    // 重置筛选
    const resetFilter = () => {
      filterForm.status = '';
      filterForm.priority = '';
      currentPage.value = 1;
      fetchData();
    };

    // 页码改变
    const handleCurrentChange = (page) => {
      currentPage.value = page;
      fetchData();
    };

    // 页面大小改变
    const handleSizeChange = (size) => {
      pageSize.value = size;
      currentPage.value = 1;
      fetchData();
    };

    // 行点击事件
    const handleRowClick = (row) => {
      // 点击行时可以选择操作，这里暂时不做任何操作
      console.log('Row clicked:', row);
    };

    // 查看详情
    const viewDetail = (row) => {
      router.push({
        name: 'NcrItemDetail',
        params: { processNo: row.process_no }
      });
    };

    // 返回上一页
    const goBack = () => {
      // 使用 router.back() 返回浏览器历史记录的上一个页面
      // 这样可以从 NcrStageDetail 返回到 NcrEnhancedDashboard
      router.back();
    };

    onMounted(() => {
      fetchData();
    });

    return {
      stageName,
      ncrList,
      totalCount,
      loading,
      currentPage,
      pageSize,
      tableColumns,
      filterForm,
      getStatusTagType,
      getPriorityTagType,
      generateTableColumns,
      onQuery,
      resetFilter,
      handleCurrentChange,
      handleSizeChange,
      handleRowClick,
      viewDetail,
      goBack
    };
  }
};
</script>

<style scoped>
.ncr-stage-detail-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header-section {
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-section h2 {
  margin: 10px 0;
  color: #303133;
}

.filter-section {
  margin-bottom: 20px;
}

.demo-form-inline {
  display: flex;
  align-items: center;
}

.data-section {
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.clearfix {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-right {
  float: right;
}
</style>
