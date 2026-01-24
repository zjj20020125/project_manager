# 前后端连接问题修复总结

## 问题描述
前后端连接出现问题，前端无法正常访问后端API。

## 问题原因
1. 后端服务端口配置冲突：后端服务原本配置为8001端口，但该端口已被占用
2. 前端代理配置错误：前端Vite配置中代理指向了错误的后端端口

## 修复步骤
1. 启动后端服务在8000端口（因为8001端口已被占用）
2. 修改前端Vite配置文件，将代理目标从 `http://localhost:8001` 更改为 `http://localhost:8000`

## 修改文件
- `project-dashboard/vite.config.js`: 更新了代理目标端口

## 验证结果
- 所有API端点均正常工作
- 前端代理配置正常工作
- 前后端数据交互正常

## 技术细节
- 后端服务运行在 `http://localhost:8000`
- 前端服务运行在 `http://localhost:3024`（自动选择可用端口）
- 前端通过代理 `/api` 路径访问后端API
- API路径映射：前端请求 `/api/v1/project/stats` → 代理到后端 `/v1/project/stats`

## 测试过的API端点
- `/v1/project/stats` - 项目统计数据
- `/v1/task/stats` - 任务统计数据
- `/v1/chart/data` - 图表数据
- `/v1/projects/detail` - 项目详细数据
- `/v1/projects/stats` - 项目分类统计
- `/v1/task/list` - 任务列表
- `/v1/project-status-stats` - 项目状态分布
- `/v1/task-owner-stats` - 任务负责人统计
- `/v1/projects-list` - 项目列表