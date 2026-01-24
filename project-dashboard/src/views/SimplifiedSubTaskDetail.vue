<template>
  <TaskDetailTemplate
    :title="'子任务详情'"
    :subtitle="'查看子任务的详细信息'"
    :taskType="'subtask'"
    :showStatsCards="true"
    :showFilters="true"
    :showTaskType="false"
    :showPagination="true"
    :tableHeight="500"
    :totalTasksLabel="'子任务总数'"
    :completedTasksLabel="'已验收子任务'"
    :pendingTasksLabel="'待验收子任务'"
    :listTitle="'子任务列表'"
    :statusPlaceholder="'按状态筛选'"
    :searchPlaceholder="'搜索任务名称或负责人'"
    :statusOptions="[
      { label: '未开始', value: '未开始' },
      { label: '进行中', value: '进行中' },
      { label: '已完成', value: '已完成' },
      { label: '已验收', value: '已验收' }
    ]"
  />
</template>

<script setup>
import TaskDetailTemplate from './TaskDetailTemplate.vue'
</script>