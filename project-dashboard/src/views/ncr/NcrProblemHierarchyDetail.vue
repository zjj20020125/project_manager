<template>
  <div class="ncr-problem-hierarchy-detail-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <el-page-header @back="goBack" :title="levelTitle" />
      <h2>{{ hierarchyName }} - 详情</h2>
      <p>该{{ levelText }}共包含 <strong>{{ totalCount }}</strong> 条 NCR 记录</p>
    </div>

    <!-- 筛选区域 -->
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

    <!-- 数据列表区域 -->
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
      
      <!-- 调试信息 -->
      <div v-if="ncrList.length > 0" style="margin-bottom: 10px; padding: 10px; background: #f0f9ff; border-left: 4px solid #409EFF;">
        <h4 style="margin: 0 0 10px 0;">📊 数据统计</h4>
        <p style="margin: 5px 0;">✅ 加载记录数：<strong>{{ ncrList.length }}</strong></p>
        <p style="margin: 5px 0;">✅ 总记录数：<strong>{{ totalCount }}</strong></p>
        <p style="margin: 5px 0;">🔍 当前层级：<strong>{{ levelText }} - {{ hierarchyName }}</strong></p>
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
      
      <!-- 数据表格 -->
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
import { ref, onMounted, reactive, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { projectApi } from '../../api/index.js';
import { ElMessage } from 'element-plus';

export default {
  name: 'NcrProblemHierarchyDetail',
  setup() {
   const route = useRoute();
   const router= useRouter();
    
    // 响应式数据
   const hierarchyName = ref('');  // 层级名称（如：设计问题）
   const level = ref('');          // 层级类型（wtdx/wtfl/wtflxfn）
   const count = ref(0);           // 数量
   const ncrList = ref([]);        // NCR 列表
   const totalCount = ref(0);      // 总数
   const loading = ref(false);     // 加载状态
   const currentPage = ref(1);     // 当前页码
   const pageSize = ref(20);       // 每页数量
   const tableColumns = ref([]);   // 动态表格列配置
    
    // 层级文本映射
   const levelTextMap = {
      'wtdx': '问题导向',
      'wtfl': '问题分类',
      'wtflxfn': '问题细分'
    };
    
    // 层级标题映射
   const levelTitleMap = {
      'wtdx': '问题导向详情',
      'wtfl': '问题分类详情',
      'wtflxfn': '问题细分详情'
    };
    
    // 计算属性
   const levelText = computed(() => levelTextMap[level.value] || '未知层级');
   const levelTitle = computed(() => levelTitleMap[level.value] || '问题层级详情');
    
    // 筛选表单
   const filterForm = reactive({
      status: '',
      priority: ''
    });

    // 动态生成表格列配置
   const generateTableColumns = (firstRecord) => {
      if (!firstRecord) return;
      
     const columnsConfig = {
        // 基础字段
        'process_no': { prop: 'process_no', label: '编号', width: 120, showOverflowTooltip: true },
        'defective_product_name': { prop: 'defective_product_name', label: '缺陷产品名称', minWidth: 150, showOverflowTooltip: true },
        'fsjd': { prop: 'fsjd', label: '发生阶段', width: 120 },
        'dqjd': { prop: 'dqjd', label: '当前节点', width: 120 },
        'wczz': { prop: 'wczz', label: '责任主体', minWidth: 120, showOverflowTooltip: true },
        
        // 问题相关字段（优先显示）
        'wtdx': { prop: 'wtdx', label: '问题导向', width: 140, showOverflowTooltip: true },
        'wtfl': { prop: 'wtfl', label: '问题分类', width: 140, showOverflowTooltip: true },
        'wtflxfn': { prop: 'wtflxfn', label: '问题细分', width: 140, showOverflowTooltip: true },
        'problem_category': { prop: 'problem_category', label: '问题类别', width: 140, showOverflowTooltip: true },
        
        // 状态和优先级
        'status': { prop: 'status', label: '状态', width: 100 },
        'review_level': { prop: 'review_level', label: '评审等级', width: 100 },
        'priority': { prop: 'priority', label: '优先级', width: 100 },
        
        // 日期字段
        'create_date': { prop: 'create_date', label: '创建日期', width: 120 },
        'occur_date': { prop: 'occur_date', label: '发生日期', width: 120 },
        
        // 其他字段
        'description': { prop: 'description', label: '问题描述', minWidth: 200, showOverflowTooltip: true },
        'measure': { prop: 'measure', label: '处理措施', minWidth: 200, showOverflowTooltip: true }
      };
      
      // 获取所有字段名
     const allFields = Object.keys(firstRecord);
      
      // 按优先级排序：固定配置字段优先，其他字段追加到后面
     const configuredFields = [];
     const otherFields = [];
      
      // 先添加有配置的字段
      Object.keys(columnsConfig).forEach(key => {
        if (allFields.includes(key)) {
         configuredFields.push({ ...columnsConfig[key] });
        }
      });
      
      // 添加未配置的其他字段
      allFields.forEach(field => {
        if (!columnsConfig[field]) {
          otherFields.push({
            prop: field,
            label: field,
            minWidth: 120,
            showOverflowTooltip: true,
            hidden: true  // 默认隐藏其他字段
          });
        }
      });
      
      // 合并并赋值
      tableColumns.value = [...configuredFields, ...otherFields];
      
     console.log('📋 生成的表格列配置:', tableColumns.value);
    };

    // 初始化数据
   const fetchData = async () => {
      loading.value = true;
      try {
        // 从路由参数获取层级信息
        level.value = route.params.level || '';
        // URL解码，处理特殊字符
        hierarchyName.value = decodeURIComponent(route.params.name || '');
       count.value = parseInt(route.params.count) || 0;
        
        if (!level.value || !hierarchyName.value) {
          ElMessage.warning('层级信息不完整');
          loading.value = false;
         return;
        }
        
       console.log('🔍 请求问题层级详情:', {
          '层级类型': level.value,
          '层级名称': hierarchyName.value,
          '数量': count.value,
          '当前页码': currentPage.value,
          '每页数量': pageSize.value
        });
        
        // 构建 API 请求参数
       const params = {
          level: level.value,
          name: hierarchyName.value,
          status: filterForm.status,
          priority: filterForm.priority,
          page: currentPage.value,
          limit: pageSize.value
        };
        
       console.log('📡 发送 API 请求参数:', params);
        
        // 调用后端 API 获取数据
        // TODO: 需要后端实现对应的 API 接口
       const response = await projectApi.getNcrByProblemHierarchy(params).catch(err => {
         console.error('❌ 问题层级 API 失败:', err);
         return [];
        });
        
       console.log('📥 接收到 API 响应:', response);
        
        // 处理响应数据
        if (response) {
          if (Array.isArray(response)) {
           console.log('✅ API 直接返回数组');
            ncrList.value = response || [];
            totalCount.value = response.length;
          } else if (response.data !== undefined) {
           console.log('✅ API 返回标准格式 {data, total}');
            
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
            '记录数': ncrList.value.length,
            '总数': totalCount.value
          });
        }
        
      } catch (error) {
       console.error('❌ 加载问题层级详情失败:', error);
        ElMessage.error('加载数据失败，请稍后重试');
      } finally {
        loading.value = false;
      }
    };

    // 分页事件
   const handleSizeChange = (val) => {
      pageSize.value = val;
      currentPage.value = 1;
      fetchData();
    };

   const handleCurrentChange = (val) => {
      currentPage.value = val;
      fetchData();
    };

    // 查询和重置
   const onQuery = () => {
      currentPage.value = 1;
      fetchData();
    };

   const resetFilter = () => {
      filterForm.status = '';
      filterForm.priority = '';
      onQuery();
    };

    // 行点击事件
   const handleRowClick = (row) => {
     console.log('🖱️ 点击行:', row);
    };

    // 查看详情
   const viewDetail = (row) => {
      if (!row.process_no) {
        ElMessage.warning('缺少流程编号');
       return;
      }
      
      ElMessage.success({
        message: `正在跳转到【${row.process_no}】详情...`,
        type: 'success',
        duration: 1500
      });
      
      // TODO: 跳转到具体的 NCR 详情页
      // router.push({
      //   name: 'NcrDetail',
      //   params: { processNo: row.process_no }
      // });
    };

    // 返回上一页
   const goBack = () => {
      router.back();
    };

    // 标签类型方法
   const getStatusTagType = (status) => {
     const statusMap = {
        '已完成': 'success',
        '待处理': 'warning',
        '处理中': 'primary',
        '待审核': 'danger'
      };
     return statusMap[status] || 'info';
    };

    // 生命周期钩子
    onMounted(() => {
      fetchData();
    });

   return {
      // 数据
      hierarchyName,
      level,
     count,
      ncrList,
      totalCount,
      loading,
      currentPage,
      pageSize,
      tableColumns,
      filterForm,
      levelText,
      levelTitle,
      
      // 方法
      handleSizeChange,
      handleCurrentChange,
      onQuery,
     resetFilter,
      handleRowClick,
      viewDetail,
      goBack,
      getStatusTagType
    };
  }
};
</script>

<style scoped>
.ncr-problem-hierarchy-detail-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.header-section {
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  color: white;
}

.header-section h2 {
  margin: 10px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-section p {
  margin: 5px 0;
  font-size: 14px;
  opacity: 0.9;
}

.filter-section {
  margin-bottom: 20px;
}

.data-section {
  min-height: 500px;
}

.pagination-right {
  float: right;
}

.clearfix::after {
  content: "";
  display: table;
  clear: both;
}

:deep(.el-page-header__title) {
  color: white;
  font-size: 16px;
}

:deep(.el-page-header__content) {
  color: rgba(255, 255, 255, 0.9);
}
</style>
