<template>
  <div class="ncr-item-detail-container">
    <div class="header-section">
      <el-page-header @back="goBack" content="NCR项目详情" />
      <h2>NCR项目详情</h2>
      <p>NCR编号: {{ ncrDetail.process_no }}</p>
    </div>

    <el-card class="detail-section" shadow="never">
      <div slot="header" class="card-header">
        <span>基本信息</span>
      </div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="NCR编号">{{ ncrDetail.process_no }}</el-descriptions-item>
        <el-descriptions-item label="项目编号">{{ ncrDetail.project_no || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ ncrDetail.defective_product_name }}</el-descriptions-item>
        <el-descriptions-item label="产品编号">{{ ncrDetail.product_no || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="发生部门">{{ ncrDetail.occurrence_department || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="责任部门">{{ ncrDetail.responsibility_department || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ ncrDetail.creator }}</el-descriptions-item>
        <el-descriptions-item label="创建日期">{{ ncrDetail.create_date || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="发生日期">{{ ncrDetail.occurrence_date || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="发生阶段">{{ ncrDetail.fsjd || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ ncrDetail.quantity || 0 }}</el-descriptions-item>
        <el-descriptions-item label="评审级别">{{ ncrDetail.review_level || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="问题分类">{{ ncrDetail.problem_category || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="问题责任人">{{ ncrDetail.problem_responsible_person || 'N/A' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="detail-section" shadow="never">
      <div slot="header" class="card-header">
        <span>状态信息</span>
      </div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="当前节点">{{ ncrDetail.current_node || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(ncrDetail.status)">
            {{ ncrDetail.status || 'N/A' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityTagType(ncrDetail.review_level)">
            {{ ncrDetail.review_level || 'N/A' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="未操作者">{{ ncrDetail.pending_operator || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="分发日期">{{ ncrDetail.distribute_date || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="归档日期">{{ ncrDetail.archive_date || 'N/A' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="detail-section" shadow="never">
      <div slot="header" class="card-header">
        <span>处置信息</span>
      </div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="问题描述">{{ ncrDetail.problem_description || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="立即措施">{{ ncrDetail.immediate_action || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="处置意见返工">
          <el-tag :type="ncrDetail.disposal_rework ? 'success' : 'info'">
            {{ ncrDetail.disposal_rework ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处置意见返修">
          <el-tag :type="ncrDetail.disposal_repair ? 'success' : 'info'">
            {{ ncrDetail.disposal_repair ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处置意见让步">
          <el-tag :type="ncrDetail.disposal_concession ? 'success' : 'info'">
            {{ ncrDetail.disposal_concession ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处置意见报废">
          <el-tag :type="ncrDetail.disposal_scrap ? 'success' : 'info'">
            {{ ncrDetail.disposal_scrap ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处置意见拒收">
          <el-tag :type="ncrDetail.disposal_reject ? 'success' : 'info'">
            {{ ncrDetail.disposal_reject ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="要求制定纠正措施">
          <el-tag :type="ncrDetail.require_corrective_action ? 'success' : 'info'">
            {{ ncrDetail.require_corrective_action ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="纠正措施">{{ ncrDetail.corrective_action || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="预防措施">{{ ncrDetail.preventive_action || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="截止日期">{{ ncrDetail.deadline || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ ncrDetail.update_time || 'N/A' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="detail-section" shadow="never">
      <div slot="header" class="card-header">
        <span>问题描述</span>
      </div>
      <div class="description-content">
        <p>{{ ncrDetail.problem_description || ncrDetail.defective_status_desc || '暂无描述' }}</p>
      </div>
    </el-card>

    <el-card class="detail-section" shadow="never">
      <div slot="header" class="card-header">
        <span>措施信息</span>
      </div>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="立即措施">
          <div class="measure-content">{{ ncrDetail.immediate_action || '暂无立即措施' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="纠正措施">
          <div class="measure-content">{{ ncrDetail.corrective_action || '暂无纠正措施' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="预防措施">
          <div class="measure-content">{{ ncrDetail.preventive_action || '暂无预防措施' }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="detail-section" shadow="never">
      <div slot="header" class="card-header">
        <span>备注信息</span>
      </div>
      <div class="remark-content">
        <p>{{ ncrDetail.remarks || '暂无备注' }}</p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { projectApi } from '../../api/index.js';
import { ElMessage } from 'element-plus';

export default {
  name: 'NcrItemDetail',
  setup() {
    const route = useRoute();
    const router = useRouter();
    
    const ncrDetail = ref({});
    const loading = ref(false);

    // 初始化数据
    const fetchData = async () => {
      loading.value = true;
      try {
        const processNo = route.params.processNo;
        if (!processNo) {
          ElMessage.error('缺少NCR编号参数');
          return;
        }
        
        // 获取NCR详情数据
        const response = await projectApi.getNcrDetail(processNo);
        if (response) {
          ncrDetail.value = response;
        } else {
          ElMessage.warning('未找到对应的NCR记录');
        }
      } catch (error) {
        console.error('获取NCR详情失败:', error);
        ElMessage.error('获取详情失败');
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

    // 返回上一页
    const goBack = () => {
      router.go(-1);
    };

    onMounted(() => {
      fetchData();
    });

    return {
      ncrDetail,
      loading,
      getStatusTagType,
      getPriorityTagType,
      goBack
    };
  }
};
</script>

<style scoped>
.ncr-item-detail-container {
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

.detail-section {
  margin-bottom: 20px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  font-weight: bold;
  color: #303133;
}

.description-content,
.remark-content {
  padding: 10px 0;
  line-height: 1.6;
  color: #606266;
}

.measure-content {
  padding: 10px 0;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>