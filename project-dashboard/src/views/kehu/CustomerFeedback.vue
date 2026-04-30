<template>
  <el-container style="min-height: 100vh; padding-top: 100px;">
    <!-- 标题栏 -->
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <el-button 
            type="primary" 
            @click="goToHome" 
            class="back-button"
            icon="ArrowLeft"
          >
            <span class="button-text">返回首页</span>
          </el-button>
        </div>
        
        <div style="text-align: center; flex: 1;">
          <h1 style="margin: 0; font-size: 28px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">
            客户反馈信息管理
          </h1>
          <p style="margin-top: 8px; color: rgba(255, 255, 255, 0.9); font-size: 14px;">结构件事业部</p>
        </div>
        
        <div style="color: white; font-size: 16px; min-width: 120px; text-align: right;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <el-main style="padding: 20px 0; display: flex; justify-content: center;">
      <div style="max-width: 1400px; width: 100%; padding: 0 20px;">
        
        <!-- 筛选条件区 -->
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <template #header>
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 16px; font-weight: bold;">筛选条件</span>
              <div style="display: flex; gap: 10px;">
                <el-button 
                  type="primary" 
                  @click="showAddDialog" 
                  icon="Plus"
                  size="default"
                >
                  新增质量问题
                </el-button>
                <el-button 
                  type="success" 
                  @click="showImportDialog" 
                  icon="Upload"
                  size="default"
                >
                  导入质量问题数据
                </el-button>
              </div>
            </div>
          </template>
          
          <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: flex-end; padding: 10px 0;">
            <!-- 第一行 -->
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">问题定性</div>
              <el-select 
                v-model="filterForm.problem_type" 
                placeholder="全部问题定性" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="nature in filterOptions.problem_natures" 
                  :key="nature" 
                  :label="nature" 
                  :value="nature" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">新责任班组</div>
              <el-select 
                v-model="filterForm.department" 
                placeholder="全部新责任班组" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="dept in filterOptions.new_responsible_teams" 
                  :key="dept" 
                  :label="dept" 
                  :value="dept" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">市场分类</div>
              <el-select 
                v-model="filterForm.market_category" 
                placeholder="全部市场分类" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="item in filterOptions.market_categories" 
                  :key="item" 
                  :label="item" 
                  :value="item" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">发生单位</div>
              <el-select 
                v-model="filterForm.occurrence_unit" 
                placeholder="全部发生单位" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="item in filterOptions.occurrence_units" 
                  :key="item" 
                  :label="item" 
                  :value="item" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">车型</div>
              <el-select 
                v-model="filterForm.vehicle_model" 
                placeholder="全部车型" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="item in filterOptions.vehicle_models" 
                  :key="item" 
                  :label="item" 
                  :value="item" />
              </el-select>
            </div>
            
            <!-- 第二行 -->
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">产品类型</div>
              <el-select 
                v-model="filterForm.product_type" 
                placeholder="全部产品类型" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="type in filterOptions.product_types" 
                  :key="type" 
                  :label="type" 
                  :value="type" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">发生月份</div>
              <el-select 
                v-model="filterForm.month" 
                placeholder="全部月份" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="month in filterOptions.months" 
                  :key="month" 
                  :label="month" 
                  :value="month" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">发生周数</div>
              <el-select 
                v-model="filterForm.week" 
                placeholder="全部周数" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="week in filterOptions.weeks" 
                  :key="week" 
                  :label="week" 
                  :value="week" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">新造/检修</div>
              <el-select 
                v-model="filterForm.repair_type" 
                placeholder="全部类型" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="item in filterOptions.repair_types" 
                  :key="item" 
                  :label="item" 
                  :value="item" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">问题分类</div>
              <el-select 
                v-model="filterForm.problem_category" 
                placeholder="全部问题分类" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="item in filterOptions.problem_categories" 
                  :key="item" 
                  :label="item" 
                  :value="item" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">问题分类1</div>
              <el-select 
                v-model="filterForm.problem_category_1" 
                placeholder="全部分类1" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="item in filterOptions.problem_category_1_list" 
                  :key="item" 
                  :label="item" 
                  :value="item" />
              </el-select>
            </div>
            
            <div style="width: 160px;">
              <div style="font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500;">补充分类2</div>
              <el-select 
                v-model="filterForm.supplement_category_2" 
                placeholder="全部分类2" 
                clearable 
                multiple
                collapse-tags
                collapse-tags-tooltip
                @change="handleFilterChange" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="item in filterOptions.supplement_category_2_list" 
                  :key="item" 
                  :label="item" 
                  :value="item" />
              </el-select>
            </div>
            
            <div style="margin-left: auto;">
              <el-button type="primary" @click="resetFilters" icon="Refresh" size="default">重置</el-button>
            </div>
          </div>
        </el-card>

        <!-- 数据统计区 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="8">
            <el-card shadow="hover" class="stats-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <div class="card-title" style="color: white; font-size: 16px; margin-bottom: 10px;">问题总数</div>
              <div class="card-value" style="color: white; font-size: 32px; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                {{ problemStats.total || 0 }}
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" class="stats-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <div class="card-title" style="color: white; font-size: 16px; margin-bottom: 10px;">平均考核金额</div>
              <div class="card-value" style="color: white; font-size: 32px; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                ¥{{ problemStats.average_amount || 0 }}
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" class="stats-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
              <div class="card-title" style="color: white; font-size: 16px; margin-bottom: 10px;">已关闭问题数</div>
              <div class="card-value" style="color: white; font-size: 32px; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                {{ kpiMetrics.closed_count || 0 }}
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 关键指标卡片区 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="12">
            <el-card shadow="hover" class="kpi-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
              <div class="card-title" style="color: #333; font-size: 16px; margin-bottom: 10px;">累计考核金额</div>
              <div class="card-value" style="color: #f56c6c; font-size: 32px; font-weight: bold;">
                ¥{{ kpiMetrics.total_amount || 0 }}
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover" class="kpi-card" style="background: linear-gradient(135deg, #fccb90 0%, #d57eeb 100%);">
              <div class="card-title" style="color: #333; font-size: 16px; margin-bottom: 10px;">问题关闭率</div>
              <div class="card-value" style="color: #67c23a; font-size: 32px; font-weight: bold;">
                {{ problemStats.total > 0 ? ((kpiMetrics.closed_count / problemStats.total) * 100).toFixed(1) : 0 }}%
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 数据可视化区 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span style="font-size: 16px; font-weight: bold;">问题定性统计</span>
                </div>
              </template>
              <div ref="typePieRef" style="height: 350px;" v-loading="chartLoading"></div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span style="font-size: 16px; font-weight: bold;">责任主体统计</span>
                </div>
              </template>
              <div ref="responsibleBarRef" style="height: 350px;" v-loading="chartLoading"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span style="font-size: 16px; font-weight: bold;">产品类型统计</span>
                </div>
              </template>
              <div ref="productPieRef" style="height: 350px;" v-loading="chartLoading"></div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span style="font-size: 16px; font-weight: bold;">问题分类统计</span>
                </div>
              </template>
              <div ref="issueBarRef" style="height: 350px;" v-loading="chartLoading"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 新增：问题分类 1 和补充分类 2 图表 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span style="font-size: 16px; font-weight: bold;">📊 问题分类 1 统计</span>
                </div>
              </template>
              <div ref="category1PieRef" style="height: 350px;" v-loading="chartLoading"></div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span style="font-size: 16px; font-weight: bold;">📊 补充分类 2 统计</span>
                </div>
              </template>
              <div ref="supplement2BarRef" style="height: 350px;" v-loading="chartLoading"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 详细表格区 -->
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <template #header>
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 16px; font-weight: bold;">质量问题明细</span>
              <div style="display: flex; gap: 10px; align-items: center;">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索产品名称、问题描述、责任班组..."
                  clearable
                  @change="handleSearch"
                  @clear="handleSearch"
                  prefix-icon="Search"
                  style="width: 300px;"
                />
                <el-button 
                  type="danger" 
                  @click="handleBatchDelete" 
                  icon="Delete" 
                  size="default"
                  :disabled="selectedRows.length === 0"
                >
                  批量删除 ({{ selectedRows.length }})
                </el-button>
              </div>
            </div>
          </template>


          <el-table
            :data="problemList"
            border
            style="width: 100%"
            v-loading="tableLoading"
            header-align="center"
            :default-sort="{ prop: 'occur_date', order: 'descending' }"
            empty-text="暂无数据"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column type="index" label="序号" width="60" align="center" />
            
            <el-table-column prop="occur_date" label="发生日期" width="120" sortable />
            
            <el-table-column prop="product_name" label="产品名称" width="180" show-overflow-tooltip />
            
            <!-- 新增的12个筛选条件字段 -->
            <el-table-column prop="market_category" label="市场分类" width="100" />
            
            <el-table-column prop="occurrence_unit" label="发生单位" width="150" show-overflow-tooltip />
            
            <el-table-column prop="vehicle_model" label="车型" width="120" show-overflow-tooltip />
            
            <el-table-column prop="production_repair_type" label="新造/检修" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.production_repair_type === '新造' ? 'success' : 'warning'" size="small">
                  {{ scope.row.production_repair_type || '-' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="problem_category" label="问题分类" width="120" show-overflow-tooltip />
            
            <el-table-column prop="problem_category_1" label="问题分类1" width="120" show-overflow-tooltip />
            
            <el-table-column prop="supplement_category_2" label="补充分类2" width="120" show-overflow-tooltip />
            
            <el-table-column prop="problem_type" label="问题定性" width="120">
              <template #default="scope">
                <el-tag :type="getProblemTypeTag(scope.row.problem_type)" size="small">
                  {{ scope.row.problem_type }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="department" label="新责任班组" width="120" />
            
            <el-table-column prop="product_type" label="产品类型" width="120" />
            
            <el-table-column prop="month" label="月份" width="100" />
            
            <el-table-column prop="week" label="周数" width="80" />
            <!-- 原有字段 -->
            <el-table-column prop="problem_desc" label="问题描述" min-width="200" show-overflow-tooltip />
            
            <el-table-column prop="assessment_amount" label="考核金额" width="100" align="right">
              <template #default="scope">
                <span style="color: #f56c6c; font-weight: bold;">¥{{ scope.row.assessment_amount }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTag(scope.row.status)" size="small">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleViewDetail(scope.row)"
                  icon="View"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.limit"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="pagination.total"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </el-card>
      </div>
    </el-main>

    <!-- 问题详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="质量问题详情"
      width="800px"
    >
      <el-descriptions :column="2" border v-loading="detailLoading">
        <el-descriptions-item label="问题 ID">{{ currentFeedback.problem_id }}</el-descriptions-item>
        <el-descriptions-item label="发生日期">{{ formatDate(currentFeedback.occur_date) }}</el-descriptions-item>
        <el-descriptions-item label="客户姓名">{{ currentFeedback.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ currentFeedback.product_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="问题定性">
          <el-tag :type="getProblemTypeTag(currentFeedback.problem_type)">
            {{ currentFeedback.problem_type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="新责任班组">{{ currentFeedback.department || '-' }}</el-descriptions-item>
        <el-descriptions-item label="严重程度">{{ currentFeedback.severity || '-' }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityTag(currentFeedback.priority)">
            {{ currentFeedback.priority }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(currentFeedback.status)">
            {{ currentFeedback.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="考核金额">
          <span style="color: #f56c6c; font-weight: bold;">¥{{ currentFeedback.assessment_amount || 0 }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="问题描述" :span="2">
          {{ currentFeedback.problem_desc }}
        </el-descriptions-item>
        <el-descriptions-item label="处理人">{{ currentFeedback.handler || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(currentFeedback.update_time) }}</el-descriptions-item>
        <el-descriptions-item label="解决方案" :span="2">
          {{ currentFeedback.solution || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新增质量问题对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="新增质量问题"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="addFormRef"
        :model="addForm"
        :rules="addFormRules"
        label-width="120px"
        style="max-height: 600px; overflow-y: auto; padding-right: 10px;"
      >
        <!-- 第一部分：基本信息（按模型顺序）-->
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="序号" prop="serial_number">
              <el-input-number v-model="addForm.serial_number" :min="0" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="月份" prop="month">
              <el-input v-model="addForm.month" placeholder="如：2026-01" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="市场分类" prop="market_category">
              <el-select v-model="addForm.market_category" placeholder="请选择" style="width: 100%;">
                <el-option label="国内" value="国内" />
                <el-option label="海外" value="海外" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="发生日期" prop="occurrence_date">
              <el-date-picker
                v-model="addForm.occurrence_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="发生单位" prop="occurrence_unit">
              <el-input v-model="addForm.occurrence_unit" placeholder="客户/部门名称" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="新造/检修类型">
              <el-select v-model="addForm.production_repair_type" placeholder="请选择" style="width: 100%;">
                <el-option label="新造" value="新造" />
                <el-option label="检修" value="检修" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="OA 编号">
              <el-input v-model="addForm.oa_number" placeholder="OA 系统编号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="车型">
              <el-input v-model="addForm.vehicle_model" placeholder="车型" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="车号">
              <el-input v-model="addForm.vehicle_number" placeholder="车号" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第二部分：问题信息 -->
        <el-divider content-position="left">问题信息</el-divider>

        <el-form-item label="问题描述">
          <el-input
            v-model="addForm.problem_description"
            type="textarea"
            :rows="3"
            placeholder="请详细描述问题"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="问题分类 1">
              <el-input v-model="addForm.problem_category_1" placeholder="如：设计问题/工艺问题" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="补充分类 2">
              <el-input v-model="addForm.supplement_category_2" placeholder="如：原材料/外协加工" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="问题分类">
              <el-input v-model="addForm.problem_category" placeholder="如：外观问题/尺寸超差" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="问题定性" prop="problem_nature">
              <el-select v-model="addForm.problem_nature" placeholder="请选择问题定性" style="width: 100%;">
                <el-option label="设计问题" value="设计问题" />
                <el-option label="工艺问题" value="工艺问题" />
                <el-option label="材料问题" value="材料问题" />
                <el-option label="操作问题" value="操作问题" />
                <el-option label="设备问题" value="设备问题" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否关闭" prop="is_closed">
              <el-select v-model="addForm.is_closed" placeholder="请选择" style="width: 100%;">
                <el-option label="是" value="是" />
                <el-option label="否" value="否" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第三部分：分析与措施 -->
        <el-divider content-position="left">分析与措施</el-divider>

        <el-form-item label="原因分析">
          <el-input
            v-model="addForm.cause_analysis"
            type="textarea"
            :rows="2"
            placeholder="逐条分析原因"
          />
        </el-form-item>

        <el-form-item label="纠正措施">
          <el-input
            v-model="addForm.corrective_measures"
            type="textarea"
            :rows="2"
            placeholder="纠正措施"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="措施执行情况">
              <el-select v-model="addForm.measure_implementation" placeholder="请选择" style="width: 100%;">
                <el-option label="已完成" value="已完成" />
                <el-option label="进行中" value="进行中" />
                <el-option label="未开始" value="未开始" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="考核单">
              <el-input v-model="addForm.assessment_form" placeholder="考核单编号" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第四部分：责任与人员 -->
        <el-divider content-position="left">责任与人员</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="考核金额">
              <el-input-number
                v-model="addForm.assessment_amount"
                :min="0"
                :max="10000"
                :precision="2"
                controls-position="right"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="所属车间">
              <el-input v-model="addForm.workshop" placeholder="车间名称" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="质量工程师">
              <el-input v-model="addForm.quality_engineer" placeholder="姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="检验员">
              <el-input v-model="addForm.inspector" placeholder="姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="责任班组">
              <el-select v-model="addForm.responsible_team" placeholder="请选择" style="width: 100%;">
                <el-option v-for="dept in filterOptions.new_responsible_teams" :key="dept" :label="dept" :value="dept" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="供应商">
              <el-input v-model="addForm.supplier" placeholder="供应商名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="责任人">
              <el-input v-model="addForm.responsible_person" placeholder="责任人姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="二维码导入状态">
              <el-select v-model="addForm.qrcode_import_status" placeholder="请选择" style="width: 100%;">
                <el-option label="已导入" value="已导入" />
                <el-option label="未导入" value="未导入" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第五部分：关闭信息 -->
        <el-divider content-position="left">关闭信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关闭日期">
              <el-date-picker
                v-model="addForm.closing_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注">
              <el-input
                v-model="addForm.remark"
                type="textarea"
                :rows="2"
                placeholder="备注信息"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 预留字段 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预留字段 1">
              <el-input v-model="addForm.other1" placeholder="预留字段 1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预留字段 2">
              <el-input v-model="addForm.other2" placeholder="预留字段 2" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleAddProblem"
          :loading="addLoading"
          icon="Check"
        >
          {{ addLoading ? '提交中...' : '确认提交' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 质量问题数据导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入质量问题数据"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <p style="margin: 0; line-height: 1.8;">
          1. 仅支持 Excel 文件格式（.xls 或 .xlsx）<br>
          2. 文件应包含质量问题台账数据<br>
          3. 导入的数据将用于更新筛选条件和统计信息<br>
          4. 导入过程会调用 data.py 脚本的处理逻辑
        </p>
      </el-alert>

      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :on-change="handleImportFileChange"
        :limit="1"
        accept=".xls,.xlsx"
        style="width: 100%;"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xls/xlsx 格式的文件
          </div>
        </template>
      </el-upload>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleImport"
          :loading="importLoading"
          icon="Upload"
        >
          {{ importLoading ? '导入中...' : '确认导入' }}
        </el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, View, ArrowLeft } from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import { feedbackApi } from '@/api';

const router = useRouter();

// 当前时间
const currentTime = ref('');
const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 统计数据
const problemStats = ref({
  total: 0,
  average_amount: 0,
  closed: 0
});

// KPI 指标
const kpiMetrics = ref({
  closed_count: 0,
  total_amount: 0
});

// 图表引用
const typePieRef = ref(null);
const responsibleBarRef = ref(null);
const productPieRef = ref(null);
const issueBarRef = ref(null);
const category1PieRef = ref(null); // 问题分类 1 饼图
const supplement2BarRef = ref(null); // 补充分类 2 柱状图

// 表格数据
const problemList = ref([]);
const tableLoading = ref(false);
const chartLoading = ref(false);

// 分页
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
});

// 筛选条件(支持多选)
const filterForm = reactive({
  problem_type: [],  // 问题定性
  department: [],    // 新责任班组
  product_type: [],  // 产品类型
  month: [],         // 月份
  week: [],          // 周数
  market_category: [],  // 市场分类
  occurrence_unit: [],  // 发生单位
  vehicle_model: [],  // 车型
  repair_type: [],  // 新造/检修类型
  problem_category: [],  // 问题分类
  problem_category_1: [],  // 问题分类1
  supplement_category_2: []  // 补充分类2
});

// 搜索关键词
const searchKeyword = ref('');

// 筛选条件选项（从数据库动态加载）
const filterOptions = ref({
  months: [],
  weeks: [],  // 周数列表
  new_responsible_teams: [],  // 新责任班组
  product_types: [],
  problem_natures: [],  // 问题定性
  market_categories: [],  // 市场分类
  occurrence_units: [],  // 发生单位
  vehicle_models: [],  // 车型
  repair_types: [],  // 新造/检修类型
  problem_categories: [],  // 问题分类
  problem_category_1_list: [],  // 问题分类1
  supplement_category_2_list: []  // 补充分类2
});

// 对话框
const detailDialogVisible = ref(false);
const detailLoading = ref(false);
const currentFeedback = ref({});

// 导入对话框相关
const importDialogVisible = ref(false);
const importLoading = ref(false);
const importFile = ref(null);

// 新增问题对话框相关
const addDialogVisible = ref(false);
const addLoading = ref(false);
const addFormRef = ref(null);
const addForm = reactive({
  // 必填字段
  serial_number: 0,
  month: '',
  market_category: '国内',
  occurrence_date: '',
  occurrence_unit: '',
  product_name: '',
  problem_nature: '',
  is_closed: '否',
  
  // 可选字段
  oa_number: '',
  vehicle_model: '',
  vehicle_number: '',
  drawing_number: '',
  product_quantity: 0,
  product_category: '',
  production_repair_type: '',  // 新造/检修类型
  problem_description: '',
  problem_category_1: '',
  supplement_category_2: '',
  problem_category: '',
  cause_analysis: '',
  corrective_measures: '',
  measure_implementation: '',
  assessment_form: '',
  assessment_amount: 0,
  workshop: '',
  quality_engineer: '',
  inspector: '',
  responsible_team: '',
  supplier: '',
  responsible_person: '',
  qrcode_import_status: '',
  closing_date: '',
  remark: '',
  other1: '',
  other2: ''
});

// 表单验证规则
const addFormRules = {
  month: [{ required: true, message: '请输入月份', trigger: 'blur' }],
  occurrence_date: [{ required: true, message: '请选择发生日期', trigger: 'change' }],
  occurrence_unit: [{ required: true, message: '请输入发生单位', trigger: 'blur' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  problem_nature: [{ required: true, message: '请选择问题定性', trigger: 'change' }]
};

// 批量选择相关
const selectedRows = ref([]);

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true;
  importFile.value = null;
};

// 显示新增对话框
const showAddDialog = () => {
  addDialogVisible.value = true;
  // 重置表单
  if (addFormRef.value) {
    addFormRef.value.resetFields();
  }
  Object.assign(addForm, {
    occur_date: '',
    customer_name: '',
    product_name: '',
    problem_type: '',
    department: '',
    product_type: '',
    severity: '',
    priority: '',
    assessment_amount: 0,
    status: '待处理',
    handler: '',
    problem_desc: '',
    solution: '',
    remarks: '',
    problem_category_1: '',
    supplement_category_2: '',
    month: '',
    production_repair_type: ''  // 重置新造/检修类型
  });
};

// 处理文件选择
const handleImportFileChange = (file) => {
  importFile.value = file;
  ElMessage.success(`已选择文件：${file.name}`);
};

// 处理表格选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection;
};

// 批量删除
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的记录');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条记录吗？此操作不可恢复！`,
      '批量删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
  } catch {
    // 用户取消删除
    return;
  }

  tableLoading.value = true;
  
  try {
    // 获取所有选中行的 ID
    const idsToDelete = selectedRows.value.map(row => row.problem_id);
    
    console.log('批量删除 IDs:', idsToDelete);
    
    // 调用后端批量删除 API
    const response = await fetch('/api/v1/feedback/problem/batch-delete', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ids: idsToDelete })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '删除失败');
    }

    const result = await response.json();
    
    if (result.success) {
      ElMessage.success(`成功删除 ${result.deleted_count || idsToDelete.length} 条记录`);
      // 清空选择
      selectedRows.value = [];
      // 刷新数据
      await Promise.all([
        fetchFilterOptions(),
        fetchStats(),
        fetchProblemList()
      ]);
    } else {
      throw new Error(result.message || '删除失败');
    }
  } catch (error) {
    console.error('批量删除失败:', error);
    if (error.message !== '删除失败') {
      ElMessage.error(`删除失败：${error.message}`);
    }
  } finally {
    tableLoading.value = false;
  }
};

// 执行导入操作
const handleImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的 Excel 文件');
    return;
  }

  // 检查文件类型
  const fileName = importFile.value.name;
  if (!fileName.endsWith('.xls') && !fileName.endsWith('.xlsx')) {
    ElMessage.error('仅支持 Excel 文件格式(.xls 或 .xlsx)');
    return;
  }

  importLoading.value = true;

  try {
    const formData = new FormData();
    // 使用 raw File 对象而不是 UploadFile 组件的 file
    const rawFile = importFile.value.raw || importFile.value;
    formData.append('file', rawFile);
    formData.append('overwrite', 'false');

    console.log('开始上传文件:', fileName, '大小:', rawFile.size);

    // 调用后端导入 API(通过 Vite 代理)
    const response = await fetch('/api/v1/feedback/import-quality', {
      method: 'POST',
      body: formData
    });

    console.log('响应状态码:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('响应错误:', errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    console.log('导入结果:', result);

    if (result.success) {
      ElMessage.success(`导入成功!共导入 ${result.imported_count || 0} 条数据`);
      importDialogVisible.value = false;
      // 刷新所有数据
      Promise.all([
        fetchFilterOptions(),
        fetchStats(),
        fetchProblemList()
      ]);
    } else {
      ElMessage.error(`导入失败:${result.message || '未知错误'}`);
    }
  } catch (error) {
    console.error('导入过程中发生错误:', error);
    ElMessage.error(`导入失败:${error.message || '请检查文件格式或联系管理员'}`);
  } finally {
    importLoading.value = false;
  }
};

// 提交新增问题
const handleAddProblem = async () => {
  if (!addFormRef.value) return;
  
  await addFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请填写必填项');
      return;
    }

    addLoading.value = true;
    try {
      // 准备提交数据
      const submitData = {
        ...addForm,
        assessment_amount: Number(addForm.assessment_amount) || 0
      };

      console.log('提交数据:', submitData);

      const response = await feedbackApi.createProblem(submitData);

      if (response && response.success) {
        ElMessage.success('质量问题创建成功!');
        addDialogVisible.value = false;
        // 刷新所有数据
        await Promise.all([
          fetchFilterOptions(),
          fetchStats(),
          fetchProblemList()
        ]);
      } else {
        throw new Error(response?.message || '创建失败');
      }
    } catch (error) {
      console.error('创建质量问题失败:', error);
      ElMessage.error(`创建失败:${error.message || '请稍后重试'}`);
    } finally {
      addLoading.value = false;
    }
  });
};

// 获取筛选条件选项
const fetchFilterOptions = async () => {
  try {
    const res = await feedbackApi.getProblemFilters();
    if (res && res.data) {
      const data = res.data;
      filterOptions.value = {
        months: data.months || [],
        weeks: data.weeks || [],
        new_responsible_teams: data.new_responsible_teams || [],
        product_types: data.product_types || [],
        problem_natures: data.problem_natures || [],
        market_categories: data.market_categories || [],
        occurrence_units: data.occurrence_units || [],
        vehicle_models: data.vehicle_models || [],
        repair_types: data.repair_types || [],
        problem_categories: data.problem_categories || [],
        problem_category_1_list: data.problem_category_1_list || [],
        supplement_category_2_list: data.supplement_category_2_list || []
      };
    }
  } catch (error) {
    console.error('获取筛选条件选项失败:', error);
    // 使用默认选项作为降级方案
    filterOptions.value = {
      months: [],
      weeks: [],
      new_responsible_teams: ['技术部', '生产部', '质量部', '采购部', '销售部'],
      product_types: ['蓄电池柜', '制动柜', '风源柜', '网侧柜', '动力电池柜', '其他'],
      problem_natures: ['设计问题', '工艺问题', '材料问题', '操作问题', '设备问题', '其他'],
      market_categories: ['国内', '海外'],
      occurrence_units: [],
      vehicle_models: [],
      repair_types: ['新造', '检修'],
      problem_categories: [],
      problem_category_1_list: [],
      supplement_category_2_list: []
    };
  }
};

// 获取统计数据
const fetchStats = async () => {
  try {
    const params = { ...filterForm };
    // 处理多选的筛选项：将数组转为逗号分隔的字符串
    const arrayFields = [
      'problem_type', 'department', 'product_type', 'month', 'week',
      'market_category', 'occurrence_unit', 'vehicle_model', 'repair_type',
      'problem_category', 'problem_category_1', 'supplement_category_2'
    ];
    
    arrayFields.forEach(field => {
      if (Array.isArray(params[field]) && params[field].length > 0) {
        params[field] = params[field].join(',');
      }
    });
    
    // 移除空值和空数组
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === '' || (Array.isArray(params[key]) && params[key].length === 0)) {
        delete params[key];
      }
    });
    
    const res = await feedbackApi.getProblemStats(params);
    if (res && res.data) {
      const data = res.data;
      problemStats.value = {
        total: data.total || 0,
        average_amount: data.average_amount || 0,
        closed: data.closed || 0
      };
      
      // 更新 KPI 指标
      kpiMetrics.value = {
        closed_count: data.kpi_metrics?.closed_count || 0,
        total_amount: data.kpi_metrics?.total_amount || 0
      };
      
      // 渲染图表
      renderTypePieChart(data.type_distribution || {});
      renderResponsibleBarChart(data.responsible_subject_distribution || {});
      renderProductPieChart(data.product_category_distribution || {});
      renderIssueBarChart(data.issue_category_distribution || {});
      renderCategory1PieChart(data.category_1_distribution || {});
      renderSupplement2BarChart(data.supplement_category_2_distribution || {});
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

// 获取问题列表
const fetchProblemList = async () => {
  tableLoading.value = true;
  try {
    const params = {
      page: pagination.page,
      limit: pagination.limit,
      ...filterForm
    };
    // 处理多选的筛选项：将数组转为逗号分隔的字符串
    const arrayFields = [
      'problem_type', 'department', 'product_type', 'month', 'week',
      'market_category', 'occurrence_unit', 'vehicle_model', 'repair_type',
      'problem_category', 'problem_category_1', 'supplement_category_2'
    ];
    
    arrayFields.forEach(field => {
      if (Array.isArray(params[field]) && params[field].length > 0) {
        params[field] = params[field].join(',');
      }
    });
    
    // 添加搜索关键词
    if (searchKeyword.value && searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim();
    }
    // 移除空值和空数组
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === '' || (Array.isArray(params[key]) && params[key].length === 0)) {
        delete params[key];
      }
    });
    
    const res = await feedbackApi.getProblemList(params);
    if (res) {
      problemList.value = res.list || [];
      pagination.total = res.total || 0;
    }
  } catch (error) {
    console.error('获取问题列表失败:', error);
    ElMessage.error('获取问题列表失败');
  } finally {
    tableLoading.value = false;
  }
};

// 渲染类型饼图（问题定性统计）
const renderTypePieChart = (typeData) => {
  if (!typePieRef.value) return;
  
  const chart = echarts.init(typePieRef.value);
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '问题定性',
        type: 'pie',
        radius: '60%',
        data: Object.keys(typeData).map(key => ({
          name: key,
          value: typeData[key]
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };
  chart.setOption(option);
};

// 渲染责任主体柱状图
const renderResponsibleBarChart = (subjectData) => {
  if (!responsibleBarRef.value) return;
  
  chartLoading.value = true;
  setTimeout(() => {
    const chart = echarts.init(responsibleBarRef.value);
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: Object.keys(subjectData),
        axisLabel: {
          interval: 0,
          rotate: 30
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '问题数',
          type: 'bar',
          data: Object.keys(subjectData).map(key => subjectData[key]),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }
      ]
    };
    chart.setOption(option);
    chartLoading.value = false;
  }, 100);
};

// 渲染产品类型饼图
const renderProductPieChart = (productData) => {
  if (!productPieRef.value) return;
  
  const chart = echarts.init(productPieRef.value);
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '产品类型',
        type: 'pie',
        radius: '60%',
        data: Object.keys(productData).map(key => ({
          name: key,
          value: productData[key]
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };
  chart.setOption(option);
};

// 渲染问题分类柱状图
const renderIssueBarChart = (issueData) => {
  if (!issueBarRef.value) return;
  
  chartLoading.value = true;
  setTimeout(() => {
    const chart = echarts.init(issueBarRef.value);
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: Object.keys(issueData),
        axisLabel: {
          interval: 0,
          rotate: 30
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '问题数',
          type: 'bar',
          data: Object.keys(issueData).map(key => issueData[key]),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#f093fb' },
              { offset: 0.5, color: '#f5576c' },
              { offset: 1, color: '#f5576c' }
            ])
          }
        }
      ]
    };
    chart.setOption(option);
    chartLoading.value = false;
  }, 100);
};

// 渲染问题分类 1 饼图（新增）
const renderCategory1PieChart = (category1Data) => {
  if (!category1PieRef.value) return;
  
  chartLoading.value = true;
  setTimeout(() => {
    const chart = echarts.init(category1PieRef.value);
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center'
      },
      series: [
        {
          name: '问题分类 1',
          type: 'pie',
          radius: '60%',
          data: Object.keys(category1Data).map(key => ({
            name: key,
            value: category1Data[key]
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
    chart.setOption(option);
    chartLoading.value = false;
  }, 100);
};

// 渲染补充分类 2 柱状图（新增）
const renderSupplement2BarChart = (supplement2Data) => {
  if (!supplement2BarRef.value) return;
  
  chartLoading.value = true;
  setTimeout(() => {
    const chart = echarts.init(supplement2BarRef.value);
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: Object.keys(supplement2Data),
        axisLabel: {
          interval: 0,
          rotate: 30
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '问题数',
          type: 'bar',
          data: Object.keys(supplement2Data).map(key => supplement2Data[key]),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#84fab0' },
              { offset: 0.5, color: '#8fd3f4' },
              { offset: 1, color: '#8fd3f4' }
            ])
          }
        }
      ]
    };
    chart.setOption(option);
    chartLoading.value = false;
  }, 100);
};

// 筛选条件变化处理 - 同时更新所有模块
const handleFilterChange = () => {
  pagination.page = 1;
  // 并行执行所有更新，无先后顺序
  Promise.all([
    fetchStats(),
    fetchProblemList()
  ]);
};

// 搜索处理
const handleSearch = () => {
  pagination.page = 1;
  fetchProblemList();
};

// 重置筛选条件
const resetFilters = () => {
  filterForm.problem_type = [];
  filterForm.department = [];
  filterForm.product_type = [];
  filterForm.month = [];
  filterForm.week = [];
  filterForm.market_category = [];
  filterForm.occurrence_unit = [];
  filterForm.vehicle_model = [];
  filterForm.repair_type = [];
  filterForm.problem_category = [];
  filterForm.problem_category_1 = [];
  filterForm.supplement_category_2 = [];
  handleFilterChange();
};

// 分页处理
const handleSizeChange = (size) => {
  pagination.limit = size;
  fetchProblemList();
};

const handlePageChange = (page) => {
  pagination.page = page;
  fetchProblemList();
};

// 查看详情
const handleViewDetail = async (row) => {
  detailLoading.value = true;
  detailDialogVisible.value = true;
  try {
    const res = await feedbackApi.getProblemDetail(row.problem_id);
    if (res) {
      currentFeedback.value = res;
    }
  } catch (error) {
    console.error('获取问题详情失败:', error);
    ElMessage.error('获取问题详情失败');
  } finally {
    detailLoading.value = false;
  }
};

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN');
};

// 获取标签类型
const getProblemTypeTag = (type) => {
  const typeMap = {
    '设计问题': 'danger',
    '工艺问题': 'warning',
    '材料问题': 'info',
    '操作问题': 'success',
    '设备问题': '',
    '其他': ''
  };
  return typeMap[type] || '';
};

const getPriorityTag = (priority) => {
  const priorityMap = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  };
  return priorityMap[priority] || '';
};

const getStatusTag = (status) => {
  const statusMap = {
    '待处理': 'warning',
    '处理中': 'info',
    '已解决': 'success',
    '已关闭': ''
  };
  return statusMap[status] || '';
};

// 返回首页
const goToHome = () => {
  router.push('/')
};

// 生命周期
onMounted(() => {
  updateTime();
  setInterval(updateTime, 1000);
  // 并行加载所有数据
  Promise.all([
    fetchFilterOptions(),  // 加载筛选条件选项
    fetchStats(),
    fetchProblemList()
  ]);
});
</script>

<style scoped>
.stats-card {
  transition: transform 0.3s;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.card-title {
  font-size: 14px;
  opacity: 0.9;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
}
</style>
