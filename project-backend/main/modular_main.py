"""
模块化项目管理系统主入口文件
将项目管理和NCR管理功能分离到不同模块中
保持原有功能完整性和向后兼容性
"""

import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 从config模块导入配置
import config.config
API_PREFIX = config.config.API_PREFIX
SERVER_HOST = config.config.SERVER_HOST
SERVER_PORT = config.config.SERVER_PORT

# 导入各个功能模块
from main.project_apis import router as project_router
from main.ncr_apis import router as ncr_router
from main.gantt_api import router as gantt_router
from main.routers.task_router import router as task_router
from main.routers.chart_router import router as chart_router
from main.routers.project_router import router as project_detail_router
from main.routers.data_router import router as data_router

# 导入服务层（用于未来扩展）
from services.project_service import ProjectService
from services.ncr_service import NcrService
from services.task_service import TaskService

# 导入工具模块
from utils.helpers import *
from utils.validators import *

# 创建FastAPI应用
app = FastAPI(
    title="模块化项目管理系统API", 
    version="2.0",
    description="将项目管理和NCR管理功能分离的模块化版本"
)

# 配置跨域（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请指定具体前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册各个功能模块的路由
app.include_router(project_router)
app.include_router(ncr_router)
app.include_router(gantt_router)
app.include_router(task_router)
app.include_router(project_detail_router)
app.include_router(data_router)
# 注意：chart_router放在最后，避免路由冲突
app.include_router(chart_router)

# 健康检查端点
@app.get("/")
async def root():
    return {
        "message": "模块化项目管理系统API服务正在运行",
        "version": "2.0",
        "modules": {
            "project_management": "/v1/project/stats",
            "ncr_management": "/v1/ncr/type-distribution",
            "gantt_chart": "/v1/gantt/tasks",
            "task_management": "/v1/task/list",
            "chart_statistics": "/v1/chart/data",
            "project_details": "/v1/projects/detail",
            "data_management": "/v1/projects/import"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "project-management-api"}

# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        "modular_main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True  # 开发模式自动重载
    )