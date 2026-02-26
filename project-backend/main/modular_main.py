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
app.include_router(gantt_router)
app.include_router(task_router)
app.include_router(project_detail_router)
app.include_router(data_router)
# 注意：chart_router和ncr_router放在最后，避免路由冲突
app.include_router(chart_router)
app.include_router(ncr_router)

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

# 添加缺失的project-subtasks路由
@app.get("/v1/project-subtasks/{project_identifier}")
async def get_project_subtasks(project_identifier: str):
    """根据项目ID或项目名称获取子任务数据"""
    try:
        # 从database模块导入
        from database.database import execute_query
        
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在")
            return []
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取project_tasks表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'project_id', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 尝试按项目ID查询（如果project_identifier是数字）
        task_sql = """
        SELECT 
            task_id,
            task_name,
            project_id,
            project_name,
            task_owner,
            wbs_code,
            planned_start_date,
            planned_end_date,
            actual_start_date,
            actual_end_date,
            task_status,
            progress,
            created_at
        FROM project_tasks
        WHERE 
        """
        
        # 首先尝试将project_identifier作为项目ID（数字）查询
        try:
            project_id_int = int(project_identifier)
            task_sql += "project_id = %s OR project_name = %s"
            tasks = execute_query(task_sql, (project_id_int, project_identifier), fetch_all=True) or []
        except ValueError:
            # 如果project_identifier不是数字，则只按项目名称查询
            task_sql += "project_name = %s"
            tasks = execute_query(task_sql, (project_identifier,), fetch_all=True) or []
        
        # 格式化数据
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue
                
            formatted_task = {
                "task_id": task.get("task_id"),
                "task_name": task.get("task_name", ""),
                "project_id": task.get("project_id"),
                "project_name": task.get("project_name", ""),
                "task_owner": task.get("task_owner", ""),
                "wbs_code": task.get("wbs_code", ""),
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else "",
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else "",
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else "",
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else "",
                "task_status": task.get("task_status", ""),
                "progress": float(task.get("progress")) if task.get("progress") is not None else 0.0,
                "created_at": str(task.get("created_at")) if task.get("created_at") else ""
            }
            formatted_tasks.append(formatted_task)
        
        print(f"根据项目标识符'{project_identifier}'查询到 {len(formatted_tasks)} 个子任务")
        return formatted_tasks
    except Exception as e:
        print(f"获取项目子任务数据出错: {e}")
        import traceback
        traceback.print_exc()
        return []

# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        "modular_main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True  # 开发模式自动重载
    )