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
      <el-table 
        :data="ncrList" 
        v-loading="loading"
        style="width: 100%"
        border
        @row-click="handleRowClick"
        highlight-current-row>
        <el-table-column prop="process_no" label="NCR编号" width="120" align="center" />
        <el-table-column prop="defective_product_name" label="缺陷产品名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="product_no" label="产品编号" width="120" align="center" />
        <el-table-column prop="creator" label="创建人" width="100" align="center" />
        <el-table-column prop="create_date" label="创建日期" width="120" align="center" />
        <el-table-column prop="occurrence_date" label="发生日期" width="120" align="center" />
        <el-table-column prop="fsjd" label="发生阶段" width="120" align="center" />
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column prop="review_level" label="评审级别" width="100" align="center" />
        <el-table-column prop="problem_category" label="问题分类" width="120" align="center" />
        <el-table-column prop="problem_description" label="问题描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="problem_responsible_person" label="问题责任人" width="120" align="center" />
        <el-table-column prop="occurrence_department" label="发生部门" width="120" align="center" />
        <el-table-column prop="responsibility_department" label="责任部门" width="120" align="center" />
        <el-table-column prop="immediate_action" label="立即措施" min-width="150" show-overflow-tooltip />
        <el-table-column prop="corrective_action" label="纠正措施" min-width="150" show-overflow-tooltip />
        <el-table-column prop="preventive_action" label="预防措施" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="update_time" label="更新时间" width="150" align="center" />
        <el-table-column prop="deadline" label="截止日期" width="120" align="center" />
        <el-table-column label="操作" width="150" align="center">
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
        
        // 获取NCR数据
        const params = {
          stage: stageName.value,
          status: filterForm.status,
          priority: filterForm.priority,
          page: currentPage.value,
          limit: pageSize.value
        };
        
        // 使用NCR API获取数据
        const response = await projectApi.getNcrByStage(params);
        if (response) {
          ncrList.value = response.data || [];
          totalCount.value = response.total || 0;
        }
      } catch (error) {
        console.error('获取NCR数据失败:', error);
        ElMessage.error('获取数据失败');
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
      router.push({ name: 'NcrFlowChart' });
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
      filterForm,
      getStatusTagType,
      getPriorityTagType,
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