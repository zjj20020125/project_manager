# 项目管理首页 API 接口文档

## 📋 概述

本文档描述了项目管理首页（HomePage.vue）中使用的所有后端 API 接口。

**基础信息：**
- Base URL: `/api` (通过 Vite 代理转发到后端服务)
- 实际后端地址：`http://172.16.33.192:8001`
- API 版本：`v1`
- 认证方式：Bearer Token (可选)
- 超时时间：30 秒

---

## 🔢 目录

1. [项目统计相关](#1-项目统计相关)
   - 1.1 获取项目统计数据
   - 1.2 获取项目分类统计
   - 1.3 获取项目详细数据
   - 1.4 获取项目列表

2. [任务统计相关](#2-任务统计相关)
   - 2.1 获取任务统计数据
   - 2.2 获取任务列表
   - 2.3 获取甘特图数据

3. [异常任务相关](#3-异常任务相关)
   - 3.1 获取异常节点负责人统计

4. [数据导入导出](#4-数据导入导出)
   - 4.1 导入项目数据
   - 4.2 导出项目数据

5. [项目操作](#5-项目操作)
   - 5.1 更新项目信息
   - 5.2 删除单个项目
   - 5.3 批量删除项目

---

## 1. 项目统计相关

### 1.1 获取项目统计数据

**功能描述**: 获取项目的总体统计数据（总数、未开始、进行中、已结项）

**接口信息**:
- **URL**: `/v1/project/stats`
- **方法**: `GET`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - fetchStats() 函数

**请求参数**: 无

**响应格式**:
```json
{
  "total_projects": 150,
  "unstarted_projects": 30,
  "ongoing_projects": 95,
  "completed_projects": 25
}
```

**字段说明**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| total_projects | Integer | 项目总数 |
| unstarted_projects | Integer | 未开始项目数 |
| ongoing_projects | Integer | 进行中项目数 |
| completed_projects | Integer | 已结项项目数 |

**前端调用示例**:
```javascript
const statsRes = await projectApi.getProjectStats();
projectStats.totalProjects = statsRes.total_projects || 0;
projectStats.notStartedProjects = statsRes.unstarted_projects || 0;
projectStats.runningProjects = statsRes.ongoing_projects || 0;
projectStats.completedProjects = statsRes.completed_projects || 0;
```

---

### 1.2 获取项目分类统计

**功能描述**: 获取按状态分类的项目统计数据（用于首页顶部卡片展示）

**接口信息**:
- **URL**: `/v1/projects/stats`
- **方法**: `GET`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - fetchProjectCategoryStats() 函数

**请求参数**: 无

**响应格式**:
```json
{
  "total_projects": 150,
  "not_started_projects": 30,
  "ongoing_projects": 95,
  "completed_projects": 25
}
```

**字段说明**:
| 字段名 | 类型 | 说明 | 业务逻辑 |
|--------|------|------|----------|
| total_projects | Integer | 项目总数 | COUNT(*) FROM projects |
| not_started_projects | Integer | 未开始项目数 | CURDATE() < planned_start_date |
| ongoing_projects | Integer | 进行中项目数 | 总数 - 未开始 - 已结项 |
| completed_projects | Integer | 已结项项目数 | actual_end_date IS NOT NULL AND actual_end_date < CURDATE() |

**前端调用示例**:
```javascript
const statsRes = await projectApi.getProjectCategoryStats();
if (statsRes) {
  projectCategoryStats.value = statsRes;
}
```

**UI 展示**:
- 项目总数卡片（紫色渐变）
- 未开始项目卡片（粉色渐变）
- 进行中项目卡片（蓝色渐变）
- 已结项项目卡片（青色渐变）

---

### 1.3 获取项目详细数据

**功能描述**: 获取所有项目的详细信息并自动分类

**接口信息**:
- **URL**: `/v1/projects/detail`
- **方法**: `GET`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - fetchProjectDetails() 函数

**请求参数**: 无

**响应格式**:
```json
[
  {
    "project_id": 1,
    "project_name": "DF4B-NG7583 型新能源机车 5#车高压柜",
    "project_manager": "景欢",
    "planned_start_date": "2026-01-31",
    "planned_end_date": "2026-03-10",
    "actual_start_date": "2026-01-31",
    "actual_end_date": null,
    "project_status": "进行中（延期）",
    "category": "进行中",
    "created_at": "2026-02-26 09:44:25",
    "updated_at": "2026-03-16 15:02:54"
  }
]
```

**字段说明**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| project_id | Integer | 项目ID（主键） |
| project_name | String | 项目名称 |
| project_manager | String | 项目负责人 |
| planned_start_date | Date/String | 计划开始日期 |
| planned_end_date | Date/String | 计划结束日期 |
| actual_start_date | Date/String | 实际开始日期 |
| actual_end_date | Date/String | 实际结束日期 |
| project_status | String | 项目状态 |
| category | String | 自动分类（未开始/进行中/已结项） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**分类逻辑**:
```python
if actual_end_date and actual_end_date < current_date:
    category = "已结项"
elif planned_start_date and planned_start_date > current_date:
    category = "未开始"
else:
    category = "进行中"
```

**前端调用示例**:
```javascript
projectDetailsLoading.value = true;
const detailRes = await projectApi.getProjectsDetail();
if (detailRes) {
  projectDetails.value = detailRes;
}
projectDetailsLoading.value = false;
```

---

### 1.4 获取项目列表

**功能描述**: 获取简化的项目列表（用于下拉选择）

**接口信息**:
- **URL**: `/v1/projects-list`
- **方法**: `GET`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - fetchProjectsList() 函数

**请求参数**: 无

**响应格式**:
```json
[
  {
    "project_id": 1,
    "project_name": "DF4B-NG7583 型新能源机车 5#车高压柜"
  },
  {
    "project_id": 2,
    "project_name": "川藏线蓄电池柜项目"
  }
]
```

**字段说明**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| project_id | Integer | 项目ID |
| project_name | String | 项目名称 |

**前端调用示例**:
```javascript
const response = await projectApi.getProjectsList();
if (response) {
  projectOptions.value = response;
  // 默认选中第一个项目
  if (response.length > 0) {
    selectedProjectId.value = response[0].project_id;
    selectedProjectName.value = `${response[0].project_name} - 任务甘特图`;
  }
}
```

---

## 2. 任务统计相关

### 2.1 获取任务统计数据

**功能描述**: 获取任务的总体统计数据

**接口信息**:
- **URL**: `/v1/task/stats`
- **方法**: `GET`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - fetchStats() 函数

**请求参数**: 无

**响应格式**:
```json
{
  "total_milestones": 50,
  "completed_milestones": 35,
  "total_subtasks": 200,
  "accepted_subtasks": 150,
  "completed_tasks": 180
}
```

**字段说明**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| total_milestones | Integer | 里程碑任务总数 |
| completed_milestones | Integer | 已完成里程碑数 |
| total_subtasks | Integer | 子任务总数 |
| accepted_subtasks | Integer | 已验收子任务数 |
| completed_tasks | Integer | 已完成任务总数 |

**前端调用示例**:
```javascript
const taskStatsRes = await projectApi.getTaskStats();
if (taskStatsRes) {
  taskStats.milestoneTasks = taskStatsRes.total_milestones || 0;
  taskStats.completedMilestones = taskStatsRes.completed_milestones || 0;
  taskStats.subTasks = taskStatsRes.total_subtasks || 0;
  taskStats.completedTasks = taskStatsRes.completed_tasks || 0;
}
```

---

### 2.2 获取任务列表

**功能描述**: 分页获取任务列表数据

**接口信息**:
- **URL**: `/v1/task/list`
- **方法**: `GET`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - fetchStats() 函数

**请求参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| limit | Integer | 否 | 20 | 每页数量 |
| offset | Integer | 否 | 0 | 偏移量 |

**请求示例**:
```
GET /v1/task/list?limit=10&offset=0
```

**响应格式**:
```json
{
  "data": [
    {
      "projectNo": "PRJ001",
      "projectName": "DF4B-NG7583 型新能源机车 5#车高压柜",
      "wbsNo": "1",
      "taskName": "设计评审",
      "owner": "张三",
      "taskType": "Milestone",
      "priority": "Important Not Urgent",
      "status": "进行中",
      "planStart": "2026-01-01",
      "planEnd": "2026-01-15",
      "progress": "80"
    }
  ]
}
```

**字段说明**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| projectNo | String | 项目编号 |
| projectName | String | 项目名称 |
| wbsNo | String | WBS 编码 |
| taskName | String | 任务名称 |
| owner | String | 负责人 |
| taskType | String | 任务类型（Milestone/Subtask） |
| priority | String | 优先级 |
| status | String | 任务状态 |
| planStart | String | 计划开始日期 |
| planEnd | String | 计划结束日期 |
| progress | String | 进度百分比 |

**前端调用示例**:
```javascript
const taskListRes = await projectApi.getTaskList({ page: 1, limit: 10 });
taskTableData.value = taskListRes?.data || [];
```

---

### 2.3 获取任务进度甘特图数据

**功能描述**: 获取甘特图展示所需的任务数据

**接口信息**:
- **URL**: `/v1/task-gantt-data`
- **方法**: `GET`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - initGantt() 函数

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| project_name | String | 否 | 项目名称（不传则返回所有项目） |

**请求示例**:
```
GET /v1/task-gantt-data?project_name=DF4B-NG7583 型新能源机车 5#车高压柜
```

**响应格式**:
```json
[
  {
    "task_id": 1,
    "task_name": "设计阶段",
    "wbs_code": "1",
    "planned_start_date": "2026-01-01",
    "planned_end_date": "2026-01-15",
    "actual_start_date": "2026-01-01",
    "actual_end_date": null,
    "progress": 80.0,
    "task_status": "进行中",
    "task_owner": "张三"
  }
]
```

**前端调用示例**:
```javascript
const getTaskGanttData = (projectName = null) => {
  const params = projectName ? `?project_name=${encodeURIComponent(projectName)}` : '';
  return apiClient.get(`/v1/task-gantt-data${params}`);
};
```

---

## 3. 异常任务相关

### 3.1 获取异常节点负责人统计

**功能描述**: 获取异常子任务负责人的统计数据（前 15 名）

**接口信息**:
- **URL**: `/v1/abnormal-task-owner-stats`
- **方法**: `GET`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - 异常子任务负责人统计表格

**请求参数**: 无

**响应格式**:
```json
[
  {
    "owner_name": "张三",
    "first_abnormal_count": 5,
    "delayed_progress_count": 3
  },
  {
    "owner_name": "李四",
    "first_abnormal_count": 3,
    "delayed_progress_count": 2
  }
]
```

**字段说明**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| owner_name | String | 负责人姓名 |
| first_abnormal_count | Integer | 首个异常节点数量 |
| delayed_progress_count | Integer | 进度推迟数量 |

**前端展示**:
```vue
<el-table :data="abnormalTaskOwnerStats">
  <el-table-column prop="owner_name" label="负责人姓名" />
  <el-table-column prop="first_abnormal_count" label="异常节点">
    <template #default="scope">
      <el-tag type="danger">{{ scope.row.first_abnormal_count || 0 }} 项</el-tag>
    </template>
  </el-table-column>
</el-table>
```

---

## 4. 数据导入导出

### 4.1 导入项目数据

**功能描述**: 通过 Excel 文件导入项目数据

**接口信息**:
- **URL**: `/v1/projects/import`
- **方法**: `POST`
- **权限**: 无需认证
- **Content-Type**: `multipart/form-data`
- **使用位置**: HomePage.vue - handleFileUpload() 函数

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | Excel 文件（.xlsx/.xls） |
| overwrite | Boolean | 否 | 是否覆盖已存在的数据 |

**请求示例**:
```javascript
const formData = new FormData();
formData.append('file', file.raw);

await projectApi.importProjects(formData, overwrite);
```

**响应格式**:
```json
{
  "message": "文件 项目数据.xlsx 导入成功",
  "existing_count": 0,
  "processed_count": 50,
  "details": {
    "success": true,
    "data_rows": 50
  }
}
```

**错误响应**:
```json
{
  "detail": "不支持的文件格式，请上传 Excel 或 CSV 文件"
}
```

---

### 4.2 导出项目数据

**功能描述**: 导出项目数据为 Excel 文件

**接口信息**:
- **URL**: `/v1/projects/export`
- **方法**: `POST`
- **权限**: 无需认证
- **Content-Type**: `application/json`
- **Response-Type**: `blob`
- **使用位置**: HomePage.vue - confirmExport() 函数

**请求参数**:
```json
{
  "project_ids": [1, 2, 3]  // 要导出的项目ID 列表，空数组表示导出所有
}
```

**响应格式**: Binary (Excel 文件流)

**Content-Disposition**:
```
attachment; filename*=UTF-8''项目数据_20260320_143025.xlsx
```

**前端调用示例**:
```javascript
const exportProjects = (projectIds) => {
  return apiClient.post('/v1/projects/export', 
    { project_ids: projectIds }, 
    { responseType: 'blob' }
  ).then(response => {
    if (response instanceof Blob) {
      // 创建下载链接
      const url = window.URL.createObjectURL(response);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `项目数据_${new Date().toISOString()}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    }
  });
};
```

---

## 5. 项目操作

### 5.1 更新项目信息

**功能描述**: 修改项目信息并记录修改日志

**接口信息**:
- **URL**: `/v1/projects/{project_id}`
- **方法**: `PUT`
- **权限**: 无需认证
- **Content-Type**: `application/json`
- **使用位置**: HomePage.vue - confirmModify() 函数

**路径参数**:
| 参数名 | 类型 | 说明 |
|--------|------|------|
| project_id | Integer | 项目ID |

**请求体**:
```json
{
  "project_name": "新项目名",
  "project_manager": "新负责人",
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "status": "进行中",
  "progress": 50.0,
  "budget": 1000000.00,
  "actual_cost": 500000.00,
  "remarks": "备注信息",
  "modifier_name": "修改人姓名",
  "remarks_for_modification": "修改原因"
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "项目修改成功"
}
```

**前端调用示例**:
```javascript
const response = await projectApi.updateProject(projectId, modifyData);
if (response.success) {
  ElMessage.success('项目修改成功');
  await fetchProjectDetails(); // 重新加载数据
}
```

---

### 5.2 删除单个项目

**功能描述**: 删除指定项目及其关联的任务数据

**接口信息**:
- **URL**: `/v1/projects/{project_id}`
- **方法**: `DELETE`
- **权限**: 无需认证
- **使用位置**: HomePage.vue - confirmDelete() 函数

**路径参数**:
| 参数名 | 类型 | 说明 |
|--------|------|------|
| project_id | Integer | 项目ID |

**响应格式**:
```json
{
  "success": true,
  "project_name": "项目名称",
  "deleted_tasks_count": 15
}
```

**前端调用示例**:
```javascript
const result = await projectApi.deleteProject(projectId);
ElMessage.success(`项目 '${result.project_name}' 删除成功，共删除 ${result.deleted_tasks_count} 条任务数据`);
```

---

### 5.3 批量删除项目

**功能描述**: 批量删除多个项目及其关联的任务数据

**接口信息**:
- **URL**: `/v1/projects/batch-delete`
- **方法**: `POST`
- **权限**: 无需认证
- **Content-Type**: `application/json`
- **使用位置**: HomePage.vue - confirmDelete() 函数

**请求体**:
```json
[1, 2, 3, 4, 5]  // 项目ID 数组
```

**响应格式**:
```json
{
  "success": true,
  "deleted_projects": 5,
  "deleted_tasks_total": 78
}
```

**前端调用示例**:
```javascript
const projectIds = multipleSelection.value.map(item => item.project_id);
const result = await projectApi.batchDeleteProjects(projectIds);
ElMessage.success(`成功删除 ${result.deleted_projects} 个项目，共删除 ${result.deleted_tasks_total} 条任务数据`);
```

---

## 📊 附录

### A. 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### B. 通用错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### C. 日期格式规范

- 日期格式：`YYYY-MM-DD` (例：`2026-03-20`)
- 日期时间格式：`YYYY-MM-DD HH:mm:ss` (例：`2026-03-20 14:30:25`)

### D. 状态枚举值

**项目状态**:
- `未开始`
- `进行中`
- `进行中（延期）`
- `已完成`
- `已完成（延期完成）`
- `已验收`
- `异常`

**任务状态**:
- `未开始`
- `进行中`
- `已完成`
- `已验收`
- `异常`
- `按时完成`
- `延期完成`
- `完成`

### E. 性能建议

1. **分页查询**: 对于列表数据，建议使用分页参数
2. **按需加载**: 甘特图等大数据量接口建议指定 project_name 参数
3. **缓存策略**: 统计数据可适当缓存，减少数据库查询

### F. 安全建议

1. **认证授权**: 生产环境建议添加 JWT 等认证机制
2. **输入验证**: 所有输入参数需进行合法性校验
3. **SQL 注入防护**: 使用参数化查询，避免 SQL 注入
4. **CORS 配置**: 正确配置跨域白名单

---

**文档版本**: v1.0  
**最后更新**: 2026-03-20  
**维护者**: 项目管理团队
