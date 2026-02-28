<template>
  <TaskDetailTemplate
    :title="'里程碑任务详情'"
    :subtitle="'查看里程碑任务的详细信息'"
    :taskType="'milestone'"
    :showStatsCards="true"
    :showFilters="true"
    :showTaskType="false"
    :showPagination="true"
    :tableHeight="500"
    :totalTasksLabel="'总里程碑任务数'"
    :completedTasksLabel="'已完成里程碑任务'"
    :pendingTasksLabel="'未完成里程碑任务'"
    :listTitle="'里程碑任务列表'"
    :statusPlaceholder="'按状态筛选'"
    :searchPlaceholder="'搜索任务名称或负责人'"
    :statusOptions="[
      { label: '未开始', value: '未开始' },
      { label: '进行中', value: '进行中' },
      { label: '完成', value: '完成' },
      { label: '延期完成', value: '延期完成' },
      { label: '异常', value: '异常' }
    ]"
  />
</template>

<script setup>
import TaskDetailTemplate from './project/TaskDetailTemplate.vue'
</script>