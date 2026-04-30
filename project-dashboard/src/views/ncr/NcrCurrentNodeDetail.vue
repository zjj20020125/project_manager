<template>
  <div class="ncr-current-node-detail-container">
    <div class="header-section">
      <el-page-header @back="goBack" content="当前节点详情" />
      <h2>当前节点详情</h2>
      <p>该节点共包含 {{ totalCount }} 条 NCR 记录</p>
    </div>

    <!-- 节点统计信息卡片 -->
    <el-card class="stats-section" shadow="never" v-if="nodeStats && nodeStats.length > 0">
      <template #header>
        <div class="card-header">
          <span>📊 节点统计</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8" v-for="(stat, index) in nodeStats" :key="index">
          <el-statistic :title="stat.nodeName" :value="stat.count">
            <template #suffix>条</template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>

    <!-- 调试信息 -->
    <el-alert
      v-if="ncrList.length > 0"
      title="📋 数据加载成功"
      type="success"
      :closable="false"
      style="margin-bottom: 15px;"
    >
      <template #default>
        <div style="margin-top: 10px;">
          <p style="margin: 5px 0;">✅ 加载记录数：<strong>{{ ncrList.length }}</strong></p>
          <p style="margin: 5px 0;">✅ 总记录数：<strong>{{ totalCount }}</strong></p>
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
      </template>
    </el-alert>

    <!-- 数据表格 -->
    <el-card class="data-section" shadow="never">
      <template #header>
        <div class="card-header">
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
      </template>
      
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
  name: 'NcrCurrentNodeDetail',
  setup() {
    const route = useRoute();
    const router = useRouter();
    
    // 响应式数据
    const ncrList = ref([]);
    const totalCount = ref(0);
    const nodeStats = ref([]);
    const loading = ref(false);
    const currentPage = ref(1);
    const pageSize = ref(20);
    const tableColumns = ref([]); // 动态表格列配置
    
    // 从路由参数获取当前节点信息
    const currentNodes = ref([]);
    
    // 初始化数据
    const fetchData = async () => {
      loading.value = true;
      try {
        // 从路由参数获取当前节点信息
        const nodesParam = route.params.currentNodes;
        
        if (!nodesParam) {
          ElMessage.error('缺少当前节点参数');
          loading.value = false;
          return;
        }
        
        // 解析节点参数（支持多个节点，使用逗号分隔）
        currentNodes.value = Array.isArray(nodesParam) 
          ? nodesParam 
          : nodesParam.split(',').map(node => node.trim()).filter(node => node);
        
        if (currentNodes.value.length === 0) {
          ElMessage.warning('未指定当前节点');
          loading.value = false;
          return;
        }
        
        console.log('🔍 请求当前节点详情:', {
          节点列表: currentNodes.value,
          完整路由参数: route.params,
          当前页码: currentPage.value,
          每页数量: pageSize.value
        });
        
        // 调用 API 获取数据
        const response = await projectApi.getNcrCurrentNodeDetail({
          currentNodes: currentNodes.value
        });
        
        console.log('📥 接收到 API 响应:', response);
        
        // 分析响应数据结构
        if (response) {
          if (response.data !== undefined) {
            console.log('✅ API 返回标准格式 {data, total, nodeStats}');
            console.log('📋 data 字段类型:', typeof response.data);
            console.log('📋 data 数组长度:', response.data?.length);
            console.log('📋 total 字段值:', response.total);
            console.log('📋 nodeStats 字段值:', response.nodeStats);
            
            if (Array.isArray(response.data) && response.data.length > 0) {
              console.log('🔬 第一条数据的结构:');
              console.log('  - 完整数据:', response.data[0]);
              console.log('  - 所有字段名:', Object.keys(response.data[0]));
              
              // 动态生成表格列配置
              generateTableColumns(response.data[0]);
            }
            
            ncrList.value = response.data || [];
            totalCount.value = response.total || 0;
            nodeStats.value = response.nodeStats || [];
            
            console.log('✅ 数据加载完成:', {
              记录数: ncrList.value.length,
              总数: totalCount.value,
              节点统计: nodeStats.value
            });
            
            if (totalCount.value === 0) {
              ElMessage.info({
                message: `当前节点暂无 NCR 记录`,
                type: 'info',
                duration: 3000
              });
            } else {
              ElMessage.success({
                message: `找到 ${totalCount.value} 条当前节点的 NCR 记录`,
                type: 'success',
                duration: 2000
              });
            }
          } else {
            console.warn('⚠️ API 返回未知格式:', response);
            ncrList.value = [];
            totalCount.value = 0;
            nodeStats.value = [];
          }
        }
      } catch (error) {
        console.error('❌ 获取当前节点详情失败:', error);
        console.error('错误详情:', {
          错误消息: error.message,
          错误堆栈: error.stack,
          响应数据: error.response?.data
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
        'zlry': '质量人员',
        'process_no': '流程编号',
        'project_no': '项目编号',
        'defective_product_name': '不合格品名称',
        'product_no': '产品编号',
        'occurrence_department': '发生部门',
        'responsibility_department': '责任部门',
        'creator': '创建人',
        'create_date': '创建日期',
        'occurrence_date': '发生日期',
        'quantity': '数量',
        'review_level': '评审级别',
        'problem_category': '问题分类',
        'problem_responsible_person': '问题责任人',
        'current_node': '当前节点',
        'status': '状态',
        'pending_operator': '未操作者',
        'distribute_date': '分发日期',
        'archive_date': '归档日期',
        'problem_description': '问题描述',
        'immediate_action': '立即措施',
        'disposal_rework': '返工',
        'disposal_repair': '返修',
        'disposal_concession': '让步',
        'disposal_scrap': '报废',
        'disposal_reject': '拒收',
        'require_corrective_action': '要求制定纠正措施',
        'corrective_action': '纠正措施',
        'preventive_action': '预防措施',
        'deadline': '截止日期',
        'update_time': '更新时间'
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
        if (field === 'bhgpmc' || field === 'cpbhgztms' || field === 'bz' || 
            field === 'problem_description' || field === 'immediate_action' || 
            field === 'corrective_action' || field === 'preventive_action') {
          minWidth = 150;
          width = null;
        } else if (field === 'ch' || field === 'th' || field === 'xmh' || 
                   field === 'process_no' || field === 'project_no') {
          width = 150;
        } else if (field === 'sl' || field === 'wlbm' || field === 'quantity') {
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
      console.log('Row clicked:', row);
    };

    // 查看详情
    const viewDetail = (row) => {
      // 优先使用 process_no，如果没有则使用其他唯一标识字段
      const identifier = row.process_no || row.bhgpmc || row.id;
      if (!identifier) {
        ElMessage.warning('该记录没有可用的标识字段');
        return;
      }
      
      router.push({
        name: 'NcrItemDetail',
        params: { processNo: identifier }
      });
    };

    // 返回上一页
    const goBack = () => {
      // 使用 router.back() 返回浏览器历史记录的上一个页面
      router.back();
    };

    onMounted(() => {
      fetchData();
    });

    return {
      ncrList,
      totalCount,
      nodeStats,
      loading,
      currentPage,
      pageSize,
      tableColumns,
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
.ncr-current-node-detail-container {
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

.stats-section {
  margin-bottom: 20px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #303133;
}

.pagination-right {
  float: right;
}

.data-section {
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
