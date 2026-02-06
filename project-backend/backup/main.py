import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List  # 添加缺失的List导入
from datetime import datetime  # 添加datetime导入
import uvicorn
import tempfile
import shutil

# 从config模块导入配置
import config.config
API_PREFIX = config.config.API_PREFIX
SERVER_HOST = config.config.SERVER_HOST
SERVER_PORT = config.config.SERVER_PORT

# 从database模块导入
import database.database
execute_query = database.database.execute_query

# 从models模块导入
import models.models
ProjectStats = models.models.ProjectStats
TaskStats = models.models.TaskStats
ChartData = models.models.ChartData
TaskItem = models.models.TaskItem

# 创建FastAPI应用
app = FastAPI(title="项目管理系统API", version="1.0")

# 配置跨域（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请指定具体前端域名（如http://localhost:5173）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# API接口定义
# --------------------------

# 1. 获取项目统计数据
@app.get(f"{API_PREFIX}/project/stats", response_model=ProjectStats)
def get_project_stats():
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return {
                "total_projects": 0,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        # 查询总项目数
        total_sql = "SELECT COUNT(*) as count FROM projects"
        total_result = execute_query(total_sql)
        if not total_result:
            print("警告: 无法获取项目总数")
            return {
                "total_projects": 0,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        total = total_result["count"] if total_result and "count" in total_result else 0
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return {
                "total_projects": total,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['planned_start_date', 'planned_end_date']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return {
                "total_projects": total,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        # 查询进行中项目数：当前日期在预计开始时间和预计结束时间之间
        ongoing_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE CURDATE() BETWEEN planned_start_date AND planned_end_date
        """
        ongoing_result = execute_query(ongoing_sql)
        ongoing = ongoing_result["count"] if ongoing_result and "count" in ongoing_result else 0
        
        # 查询未开始项目数：当前日期在预计开始时间之前
        unstarted_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE CURDATE() < planned_start_date
        """
        unstarted_result = execute_query(unstarted_sql)
        unstarted = unstarted_result["count"] if unstarted_result and "count" in unstarted_result else 0
        
        # 查询已结项项目数：当前日期在预计结束时间之后
        completed_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE CURDATE() > planned_end_date
        """
        completed_result = execute_query(completed_sql)
        completed = completed_result["count"] if completed_result and "count" in completed_result else 0
        
        return {
            "total_projects": total,  # 已立项项目数
            "unstarted_projects": unstarted,
            "ongoing_projects": ongoing,
            "completed_projects": completed
        }
    except Exception as e:
        print(f"获取项目统计数据出错: {e}")
        # 返回默认值
        return {
            "total_projects": 0,
            "unstarted_projects": 0,
            "ongoing_projects": 0,
            "completed_projects": 0
        }

# 2. 获取任务统计数据
@app.get(f"{API_PREFIX}/task/stats", response_model=TaskStats)
def get_task_stats():
    try:
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在")
            return {
                "total_milestones": 0,
                "completed_milestones": 0,
                "total_subtasks": 0,
                "accepted_subtasks": 0,
                "completed_tasks": 0
            }
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取project_tasks表结构")
            return {
                "total_milestones": 0,
                "completed_milestones": 0,
                "total_subtasks": 0,
                "accepted_subtasks": 0,
                "completed_tasks": 0
            }
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['wbs_code', 'task_status']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            # 尝试使用所有可用任务进行统计
            total_tasks_sql = "SELECT COUNT(*) as count FROM project_tasks"
            total_result = execute_query(total_tasks_sql)
            total_tasks = total_result["count"] if total_result and "count" in total_result else 0
            
            return {
                "total_milestones": 0,
                "completed_milestones": 0,
                "total_subtasks": total_tasks,
                "accepted_subtasks": 0,
                "completed_tasks": 0
            }
        
        # 由于jgj-project数据库使用project_tasks表结构，查询任务总数
        total_tasks_sql = "SELECT COUNT(*) as count FROM project_tasks"
        total_result = execute_query(total_tasks_sql)
        total_tasks = total_result["count"] if total_result and "count" in total_result else 0
        
        # 里程碑任务总数（根据wbs_code判断，纯数字如1,2,3为里程碑任务，而1.1,1.2等不是）
        milestone_sql = "SELECT COUNT(*) as count FROM project_tasks WHERE wbs_code REGEXP '^[0-9]+$'"
        milestone_result = execute_query(milestone_sql)
        total_milestones = milestone_result["count"] if milestone_result and "count" in milestone_result else 0
        
        # 已完成里程碑数（task_status为'完成'的里程碑任务）
        completed_milestone_sql = """
        SELECT COUNT(*) as count FROM project_tasks 
        WHERE wbs_code REGEXP '^[0-9]+$' AND task_status = '完成'
        """
        completed_result = execute_query(completed_milestone_sql)
        completed_milestones = completed_result["count"] if completed_result and "count" in completed_result else 0
        
        # 子任务总数（非里程碑任务）
        total_subtasks = total_tasks - total_milestones
        
        # 已验收子任务数（填写了实际开始时间和实际完成时间的非里程碑任务）
        accepted_subtask_sql = """
        SELECT COUNT(*) as count FROM project_tasks 
        WHERE wbs_code NOT REGEXP '^[0-9]+$' AND actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL
        """
        accepted_subtask_result = execute_query(accepted_subtask_sql)
        accepted_subtasks = accepted_subtask_result["count"] if accepted_subtask_result and "count" in accepted_subtask_result else 0
        
        # 已验收任务数（填写了实际开始时间和实际完成时间的任务，包括里程碑和子任务）
        completed_tasks_sql = """
        SELECT COUNT(*) as count FROM project_tasks 
        WHERE actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL
        """
        completed_tasks_result = execute_query(completed_tasks_sql)
        completed_tasks = completed_tasks_result["count"] if completed_tasks_result and "count" in completed_tasks_result else 0
        
        return {
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "total_subtasks": total_subtasks,
            "accepted_subtasks": accepted_subtasks,
            "completed_tasks": completed_tasks
        }
    except Exception as e:
        print(f"获取任务统计数据出错: {e}")
        # 返回默认值
        return {
            "total_milestones": 0,
            "completed_milestones": 0,
            "total_subtasks": 0,
            "accepted_subtasks": 0,
            "completed_tasks": 0
        }

# 3. 获取图表数据
@app.get(f"{API_PREFIX}/chart/data", response_model=ChartData)
def get_chart_data():
    try:
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在，返回模拟数据")
            # 1. 项目类型分布（模拟数据，可根据实际表结构调整）
            type_pie = [
                {"value": 7, "name": "产品设计"},
                {"value": 3, "name": "生产制造"},
                {"value": 2, "name": "工程项目"},
                {"value": 1, "name": "产品研发"},
                {"value": 1, "name": "软件交付"}
            ]
            
            # 2. 项目来源（模拟数据）
            source_bar = [
                {"name": "公开招标", "value": 1},
                {"name": "广告营销", "value": 1},
                {"name": "客户介绍", "value": 2},
                {"name": "朋友介绍", "value": 1},
                {"name": "销售自拓", "value": 9}
            ]
            
            # 3. 项目经理负载（空数组）
            load_bar = []
            
            # 4. 甘特图数据（空数组）
            gantt_data = []
            
            return {
                "type_pie": type_pie,
                "source_bar": source_bar,
                "load_bar": load_bar,
                "gantt_data": gantt_data
            }

        # 检查必要字段是否存在
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取project_tasks表结构，返回模拟数据")
            # 返回模拟数据
            type_pie = [
                {"value": 7, "name": "产品设计"},
                {"value": 3, "name": "生产制造"},
                {"value": 2, "name": "工程项目"},
                {"value": 1, "name": "产品研发"},
                {"value": 1, "name": "软件交付"}
            ]
            
            source_bar = [
                {"name": "公开招标", "value": 1},
                {"name": "广告营销", "value": 1},
                {"name": "客户介绍", "value": 2},
                {"name": "朋友介绍", "value": 1},
                {"name": "销售自拓", "value": 9}
            ]
            
            load_bar = []
            gantt_data = []
            
            return {
                "type_pie": type_pie,
                "source_bar": source_bar,
                "load_bar": load_bar,
                "gantt_data": gantt_data
            }
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_manager', 'wbs_code', 'project_name', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            # 返回模拟数据
            type_pie = [
                {"value": 7, "name": "产品设计"},
                {"value": 3, "name": "生产制造"},
                {"value": 2, "name": "工程项目"},
                {"value": 1, "name": "产品研发"},
                {"value": 1, "name": "软件交付"}
            ]
            
            source_bar = [
                {"name": "公开招标", "value": 1},
                {"name": "广告营销", "value": 1},
                {"name": "客户介绍", "value": 2},
                {"name": "朋友介绍", "value": 1},
                {"name": "销售自拓", "value": 9}
            ]
            
            load_bar = []
            gantt_data = []
            
            return {
                "type_pie": type_pie,
                "source_bar": source_bar,
                "load_bar": load_bar,
                "gantt_data": gantt_data
            }

        # 1. 项目类型分布（模拟数据，可根据实际表结构调整）
        type_pie = [
            {"value": 7, "name": "产品设计"},
            {"value": 3, "name": "生产制造"},
            {"value": 2, "name": "工程项目"},
            {"value": 1, "name": "产品研发"},
            {"value": 1, "name": "软件交付"}
        ]
        
        # 2. 项目来源（模拟数据）
        source_bar = [
            {"name": "公开招标", "value": 1},
            {"name": "广告营销", "value": 1},
            {"name": "客户介绍", "value": 2},
            {"name": "朋友介绍", "value": 1},
            {"name": "销售自拓", "value": 9}
        ]
        
        # 3. 项目经理负载（从数据库查询）
        # 统计每个项目经理负责的项目数量（去重）
        load_sql = """
        SELECT project_manager, COUNT(DISTINCT project_name) as project_count
        FROM project_tasks
        WHERE project_manager IS NOT NULL
        GROUP BY project_manager
        """
        load_data = execute_query(load_sql, fetch_all=True) or []
        load_bar = [{"name": item["project_manager"], "value": item["project_count"]} for item in load_data if item and "project_manager" in item and "project_count" in item]
        
        # 4. 甘特图数据（从任务表查询）
        gantt_sql = """
        SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
               task_name as taskName, task_owner as owner,
               CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN '里程碑' ELSE '子任务' END as taskType,
               '重要不紧急' as priority, task_status as status,
               planned_start_date as planStart, planned_end_date as planEnd,
               progress as progress
        FROM project_tasks
        LIMIT 10
        """
        raw_gantt_data = execute_query(gantt_sql, fetch_all=True) or []
        
        # 格式化甘特图数据以符合前端要求
        gantt_data = []
        for item in raw_gantt_data:
            if not item:
                continue
                
            progress_value = item.get("progress")
            if hasattr(progress_value, 'quantize'):  # 如果是Decimal类型
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"
            
            formatted_item = {
                "projectNo": item.get("projectNo", ""),
                "project_name": item.get("project_name", ""),  # 保持原字段名用于前端显示
                "wbsNo": item.get("wbsNo", ""),
                "taskName": item.get("taskName", ""),
                "owner": item.get("owner") or "",
                "taskType": item.get("taskType", ""),
                "priority": item.get("priority", ""),
                "status": item.get("status", ""),
                "planStart": str(item.get("planStart")) if item.get("planStart") else "",
                "planEnd": str(item.get("planEnd")) if item.get("planEnd") else "",
                "progress": progress_str.rstrip('0').rstrip('.') if '.' in progress_str else progress_str
            }
            gantt_data.append(formatted_item)
        
        return {
            "type_pie": type_pie,
            "source_bar": source_bar,
            "load_bar": load_bar,
            "gantt_data": gantt_data
        }
    except Exception as e:
        print(f"获取图表数据出错: {e}")
        # 返回默认模拟数据
        type_pie = [
            {"value": 7, "name": "产品设计"},
            {"value": 3, "name": "生产制造"},
            {"value": 2, "name": "工程项目"},
            {"value": 1, "name": "产品研发"},
            {"value": 1, "name": "软件交付"}
        ]
        
        source_bar = [
            {"name": "公开招标", "value": 1},
            {"name": "广告营销", "value": 1},
            {"name": "客户介绍", "value": 2},
            {"name": "朋友介绍", "value": 1},
            {"name": "销售自拓", "value": 9}
        ]
        
        load_bar = []
        gantt_data = []
        
        return {
            "type_pie": type_pie,
            "source_bar": source_bar,
            "load_bar": load_bar,
            "gantt_data": gantt_data
        }

# 5. 获取项目详细数据并分类
@app.get(f"{API_PREFIX}/projects/detail", response_model=List[dict])
def get_projects_detail():
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return []
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'planned_start_date', 'actual_end_date']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return []
        
        # 查询所有项目数据
        projects_sql = """
        SELECT project_id, project_name, project_manager, planned_start_date, planned_end_date, 
               actual_start_date, actual_end_date, project_status, created_at
        FROM projects
        ORDER BY created_at DESC
        """
        all_projects = execute_query(projects_sql, fetch_all=True) or []
        
        # 获取当前日期进行分类
        current_date = datetime.now().date()
        
        categorized_projects = []
        for project in all_projects:
            if project is None:
                continue
                
            proj_dict = dict(project)
            
            # 根据日期对项目进行分类
            planned_start = proj_dict.get('planned_start_date')
            actual_end = proj_dict.get('actual_end_date')
            
            # 确保日期值是date类型
            if isinstance(planned_start, datetime):
                planned_start = planned_start.date()
            if isinstance(actual_end, datetime):
                actual_end = actual_end.date()
            
            if actual_end and actual_end < current_date:
                category = "已结项"
            elif planned_start and planned_start > current_date:
                category = "未开始"
            else:
                category = "进行中"
            
            proj_dict['category'] = category
            categorized_projects.append(proj_dict)
        
        return categorized_projects
    except Exception as e:
        print(f"获取项目详细数据出错: {e}")
        return []

# 6. 获取项目分类统计
@app.get(f"{API_PREFIX}/projects/stats", response_model=dict)
def get_project_category_stats():
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return {
                "total_projects": 0,
                "not_started_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return {
                "total_projects": 0,
                "not_started_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['planned_start_date', 'actual_end_date']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return {
                "total_projects": 0,
                "not_started_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        # 查询项目总数
        total_sql = "SELECT COUNT(*) as count FROM projects"
        total_result = execute_query(total_sql)
        total_projects = total_result["count"] if total_result and "count" in total_result else 0
        
        # 查询未开始项目数：当前时间早于planned_start_date
        not_started_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE CURDATE() < planned_start_date
        """
        not_started_result = execute_query(not_started_sql)
        not_started_projects = not_started_result["count"] if not_started_result and "count" in not_started_result else 0
        
        # 查询已结项项目数：actual_end_date早于当前时间
        completed_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE actual_end_date IS NOT NULL AND actual_end_date < CURDATE()
        """
        completed_result = execute_query(completed_sql)
        completed_projects = completed_result["count"] if completed_result and "count" in completed_result else 0
        
        # 进行中项目数 = 总数 - 未开始 - 已结项
        ongoing_projects = total_projects - not_started_projects - completed_projects
        
        return {
            "total_projects": total_projects,
            "not_started_projects": not_started_projects,
            "ongoing_projects": ongoing_projects,
            "completed_projects": completed_projects
        }
    except Exception as e:
        print(f"获取项目分类统计出错: {e}")
        return {
            "total_projects": 0,
            "not_started_projects": 0,
            "ongoing_projects": 0,
            "completed_projects": 0
        }

# 7. 根据项目状态获取项目列表
@app.get(f"{API_PREFIX}/projects/status/{{status}}", response_model=List[dict])
def get_projects_by_status(status: str, limit: int = 10, offset: int = 0):
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return []
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'planned_start_date', 'actual_end_date']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return []
        
        # 根据状态查询项目
        current_date = datetime.now().date()
        
        if status == "total":
            # 所有项目
            sql = """
            SELECT project_id, project_name, project_manager, planned_start_date, planned_end_date, 
                   actual_start_date, actual_end_date, project_status, created_at
            FROM projects
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            projects = execute_query(sql, (limit, offset), fetch_all=True) or []
            
        elif status == "not_started":
            # 未开始项目：当前时间早于planned_start_date
            sql = f"""
            SELECT project_id, project_name, project_manager, planned_start_date, planned_end_date, 
                   actual_start_date, actual_end_date, project_status, created_at
            FROM projects 
            WHERE CURDATE() < planned_start_date
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            projects = execute_query(sql, (limit, offset), fetch_all=True) or []
            
        elif status == "ongoing":
            # 进行中项目：当前时间在planned_start_date和planned_end_date之间，或actual_end_date为空
            sql = f"""
            SELECT p.project_id, p.project_name, p.project_manager, p.planned_start_date, p.planned_end_date, 
                   p.actual_start_date, p.actual_end_date, p.project_status, p.created_at
            FROM projects p
            WHERE CURDATE() >= p.planned_start_date AND (p.planned_end_date IS NULL OR CURDATE() <= p.planned_end_date) 
              AND (p.actual_end_date IS NULL OR p.actual_end_date >= CURDATE())
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
            """
            projects = execute_query(sql, (limit, offset), fetch_all=True) or []
            
        elif status == "completed":
            # 已结项项目：actual_end_date早于当前时间
            sql = f"""
            SELECT project_id, project_name, project_manager, planned_start_date, planned_end_date, 
                   actual_start_date, actual_end_date, project_status, created_at
            FROM projects 
            WHERE actual_end_date IS NOT NULL AND actual_end_date < CURDATE()
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            projects = execute_query(sql, (limit, offset), fetch_all=True) or []
        else:
            return []
        
        # 转换项目数据并添加分类信息
        result = []
        for project in projects:
            if project is None:
                continue
            proj_dict = dict(project)
            
            # 添加分类信息
            planned_start = proj_dict.get('planned_start_date')
            actual_end = proj_dict.get('actual_end_date')
            
            # 确保日期值是date类型
            if isinstance(planned_start, datetime):
                planned_start = planned_start.date()
            if isinstance(actual_end, datetime):
                actual_end = actual_end.date()
            
            if actual_end and actual_end < current_date:
                category = "已结项"
            elif planned_start and planned_start > current_date:
                category = "未开始"
            else:
                category = "进行中"
            
            proj_dict['category'] = category
            result.append(proj_dict)
        
        return result
    except Exception as e:
        print(f"获取项目分类列表出错: {e}")
        return []

# 4. 获取任务列表
@app.get(f"{API_PREFIX}/task/list", response_model=List[TaskItem])
def get_task_list(limit: int = 20, offset: int = 0):
    try:
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
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []

        task_sql = """
        SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
               task_name as taskName, task_owner as owner,
               CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN '里程碑' ELSE '子任务' END as taskType,
               '重要不紧急' as priority, task_status as status,
               planned_start_date as planStart, planned_end_date as planEnd,
               progress as progress
        FROM project_tasks
        LIMIT %s OFFSET %s
        """
        tasks = execute_query(task_sql, (limit, offset), fetch_all=True) or []
        
        # 格式化数据以符合Pydantic模型要求
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue
                
            # 处理Decimal类型转换为字符串
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):  # 如果是Decimal类型
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"
            
            # 格式化日期字段
            plan_start = task.get("planStart")
            plan_end = task.get("planEnd")
            
            formatted_task = {
                "projectNo": task.get("projectNo", ""),
                "projectName": task.get("project_name", ""),  # 映射到正确的字段名
                "wbsNo": task.get("wbsNo", ""),
                "taskName": task.get("taskName", ""),
                "owner": task.get("owner") or "",
                "taskType": task.get("taskType", ""),
                "priority": task.get("priority", ""),
                "status": task.get("status", ""),
                "planStart": str(plan_start) if plan_start else "",
                "planEnd": str(plan_end) if plan_end else "",
                "progress": progress_str.rstrip('0').rstrip('.') if '.' in progress_str else progress_str  # 清理多余的0
            }
            formatted_tasks.append(formatted_task)
        
        return formatted_tasks
    except Exception as e:
        print(f"获取任务列表出错: {e}")
        return []

# 8. 根据任务类型获取任务列表
@app.get(f"{API_PREFIX}/tasks/type/{{type}}", response_model=List[dict])
def get_tasks_by_type(type: str, limit: int = 10, offset: int = 0):
    try:
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
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 根据任务类型查询任务
        if type == "milestone":
            # 里程碑任务：wbs_code为纯数字
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   '里程碑' as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code REGEXP '^[0-9]+$'
            LIMIT %s OFFSET %s
            """
        elif type == "completed_milestone":
            # 已验收里程碑任务：wbs_code为纯数字且task_status为'完成'或'已验收'
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   '里程碑' as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code REGEXP '^[0-9]+$' AND (task_status = '完成' OR task_status = '已验收')
            LIMIT %s OFFSET %s
            """
        elif type == "subtask":
            # 子任务：wbs_code包含小数点
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   '子任务' as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code NOT REGEXP '^[0-9]+$'
            LIMIT %s OFFSET %s
            """
        elif type == "completed_task":
            # 已验收任务：填写了实际开始和结束时间的任务
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN '里程碑' ELSE '子任务' END as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL
            LIMIT %s OFFSET %s
            """
        else:
            # 默认返回所有任务
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN '里程碑' ELSE '子任务' END as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            LIMIT %s OFFSET %s
            """
        
        tasks = execute_query(task_sql, (limit, offset), fetch_all=True) or []
        
        # 格式化数据以符合前端要求
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue
                
            # 处理Decimal类型转换为字符串
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):  # 如果是Decimal类型
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"
            
            # 格式化日期字段
            plan_start = task.get("planStart")
            plan_end = task.get("planEnd")
            
            formatted_task = {
                "projectNo": task.get("projectNo", ""),
                "projectName": task.get("project_name", ""),
                "wbsNo": task.get("wbsNo", ""),
                "taskName": task.get("taskName", ""),
                "owner": task.get("owner") or "",
                "taskType": task.get("taskType", ""),
                "priority": task.get("priority", ""),
                "status": task.get("status", ""),
                "planStart": str(plan_start) if plan_start else "",
                "planEnd": str(plan_end) if plan_end else "",
                "progress": progress_str.rstrip('0').rstrip('.') if '.' in progress_str else progress_str  # 清理多余的0
            }
            formatted_tasks.append(formatted_task)
        
        return formatted_tasks
    except Exception as e:
        print(f"获取任务分类列表出错: {e}")
        return []


# 9. 获取指定类型任务的总数
@app.get(f"{API_PREFIX}/tasks/type/{{type}}/count", response_model=int)
def get_tasks_by_type_count(type: str):
    try:
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在")
            return 0
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取project_tasks表结构")
            return 0
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return 0
        
        # 根据任务类型查询任务总数
        if type == "milestone":
            # 里程碑任务：wbs_code为纯数字
            count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE wbs_code REGEXP '^[0-9]+$'"
        elif type == "completed_milestone":
            # 已验收里程碑任务：wbs_code为纯数字且task_status为'完成'或'已验收'
            count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE wbs_code REGEXP '^[0-9]+$' AND (task_status = '完成' OR task_status = '已验收')"
        elif type == "subtask":
            # 子任务：wbs_code包含小数点
            count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE wbs_code NOT REGEXP '^[0-9]+$'"
        elif type == "completed_task":
            # 已验收任务：填写了实际开始和结束时间的任务
            count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL"
        else:
            # 默认返回所有任务总数
            count_sql = "SELECT COUNT(*) as total FROM project_tasks"
        
        count_result = execute_query(count_sql)
        total_count = count_result["total"] if count_result and "total" in count_result else 0
        
        return total_count
    except Exception as e:
        print(f"获取任务总数出错: {e}")
        return 0


# 10. 获取项目状态分布数据
@app.get(f"{API_PREFIX}/project-status-stats", response_model=List[dict])
def get_project_status_stats():
    try:
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
        required_columns = ['task_status']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 查询项目状态分布
        status_sql = """
        SELECT 
            task_status as status,
            COUNT(*) as count
        FROM project_tasks
        GROUP BY task_status
        ORDER BY count DESC
        """
        
        status_results = execute_query(status_sql, fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in status_results:
            if result is not None:
                formatted_results.append({
                    "name": result.get('status', '未知状态'),
                    "value": result.get('count', 0)
                })
        
        # 如果没有数据，返回默认状态分布
        if not formatted_results:
            formatted_results = [
                {"name": "未开始", "value": 0},
                {"name": "进行中", "value": 0},
                {"name": "已完成", "value": 0},
                {"name": "已验收", "value": 0}
            ]
        
        return formatted_results
    except Exception as e:
        print(f"获取项目状态分布数据出错: {e}")
        return []

# 10. 获取项目列表
@app.get(f"{API_PREFIX}/projects-list", response_model=List[dict])
def get_projects_list():
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return []
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return []
        
        # 查询项目列表
        projects_sql = """
        SELECT DISTINCT project_id, project_name
        FROM projects
        ORDER BY project_name
        """
        
        projects_results = execute_query(projects_sql, fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in projects_results:
            if result is not None:
                formatted_results.append({
                    "project_id": result.get('project_id'),
                    "project_name": result.get('project_name', '')
                })
        
        return formatted_results
    except Exception as e:
        print(f"获取项目列表数据出错: {e}")
        return []


# 11. 获取任务进度甘特图数据
@app.get(f"{API_PREFIX}/task-gantt-data")
def get_task_gantt_data(project_name: str = None):
    try:
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
        required_columns = ['project_name', 'task_name', 'task_owner', 'planned_start_date', 'planned_end_date']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 根据项目名称查询任务进度甘特图数据
        if project_name:
            gantt_sql = """
            SELECT 
                project_name,
                task_name,
                task_owner,
                planned_start_date,
                planned_end_date
            FROM project_tasks
            WHERE project_name = %s
            ORDER BY planned_start_date
            LIMIT 50
            """
            gantt_results = execute_query(gantt_sql, (project_name,), fetch_all=True) or []
        else:
            # 查询所有任务数据，不强制要求日期有效（仅要求至少有一个日期字段不为空）
            gantt_sql = """
            SELECT 
                project_name,
                task_name,
                task_owner,
                planned_start_date,
                planned_end_date
            FROM project_tasks
            WHERE (planned_start_date IS NOT NULL OR planned_end_date IS NOT NULL)
            ORDER BY project_name, planned_start_date
            LIMIT 100  -- 增加限制数量，以便能看到更多数据
            """
            gantt_results = execute_query(gantt_sql, fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in gantt_results:
            if result is not None:
                # 不强制要求开始日期小于等于结束日期，只要日期存在就返回
                start_date = result.get('planned_start_date')
                end_date = result.get('planned_end_date')
                
                # 如果其中一个日期为空，则用另一个日期代替，或使用默认日期
                if start_date is None and end_date is None:
                    continue  # 跳过两个日期都为空的记录
                
                if start_date is None:
                    start_date = end_date
                if end_date is None:
                    end_date = start_date
                
                formatted_results.append({
                    "project_name": result.get('project_name', ''),
                    "task_name": result.get('task_name', ''),
                    "task_owner": result.get('task_owner', ''),
                    "planned_start_date": str(start_date) if start_date else '',
                    "planned_end_date": str(end_date) if end_date else ''
                })
        
        print(f"返回甘特图数据: {len(formatted_results)} 条")
        return formatted_results
    except Exception as e:
        print(f"获取任务进度甘特图数据出错: {e}")
        import traceback
        traceback.print_exc()
        return []

# 12. 获取异常节点负责人统计
@app.get(f"{API_PREFIX}/abnormal-task-owner-stats", response_model=List[dict])
def get_abnormal_task_owner_stats():
    try:
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
        required_columns = ['task_owner', 'task_status', 'wbs_code']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 查询异常状态的任务（状态为'异常'的任务）
        abnormal_tasks_sql = """
        SELECT 
            task_owner,
            task_name
        FROM project_tasks
        WHERE task_status = '异常'
          AND task_owner IS NOT NULL 
          AND task_owner != ''
          AND task_owner != 'nan'
          AND task_owner != 'NaN'
          AND task_owner != 'null'
        """
        abnormal_tasks_results = execute_query(abnormal_tasks_sql, fetch_all=True) or []
        
        # 统计负责人数量，处理多人负责的情况
        owner_count = {}
        
        for task in abnormal_tasks_results:
            if task is not None:
                task_owner = task.get('task_owner', '')
                if task_owner and task_owner.strip():
                    # 处理多个负责人的情况（逗号、分号、顿号分隔）
                    separators = [',', '，', ';', '；', '/', '、']
                    names = [task_owner]
                    
                    # 尝试分割多个负责人
                    for sep in separators:
                        if sep in task_owner:
                            names = task_owner.split(sep)
                            break
                    
                    # 清理并统计每个负责人
                    for name in names:
                        clean_name = name.strip()
                        if clean_name and clean_name not in ['nan', 'NaN', 'null', 'NULL', '<NULL>', 'None']:
                            owner_count[clean_name] = owner_count.get(clean_name, 0) + 1
        
        # 转换为所需格式并排序
        formatted_results = []
        for owner_name, count in owner_count.items():
            formatted_results.append({
                "owner_name": owner_name,
                "task_count": count
            })
        
        # 按任务数量降序排列，只返回前10名
        formatted_results.sort(key=lambda x: x['task_count'], reverse=True)
        return formatted_results[:10]
        
    except Exception as e:
        print(f"获取异常节点负责人统计出错: {e}")
        return []

# 13. 获取指定负责人负责的任务详情
@app.get(f"{API_PREFIX}/owner-tasks/{{owner}}", response_model=List[dict])
def get_owner_tasks(owner: str):
    try:
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
        required_columns = ['task_owner', 'task_name', 'project_name', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'task_status', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 查询指定负责人负责的任务详情
        owner_tasks_sql = """
        SELECT 
            task_id,
            task_name,
            project_name,
            task_owner,
            planned_start_date,
            planned_end_date,
            actual_start_date,
            actual_end_date,
            task_status,
            created_at
        FROM project_tasks
        WHERE task_owner = %s
        ORDER BY created_at DESC
        """
        owner_tasks_results = execute_query(owner_tasks_sql, (owner,), fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in owner_tasks_results:
            if result is not None:
                formatted_results.append({
                    "task_id": result.get('task_id'),
                    "task_name": result.get('task_name', ''),
                    "project_name": result.get('project_name', ''),
                    "task_owner": result.get('task_owner', ''),
                    "planned_start_date": str(result.get('planned_start_date')) if result.get('planned_start_date') else None,
                    "planned_end_date": str(result.get('planned_end_date')) if result.get('planned_end_date') else None,
                    "actual_start_date": str(result.get('actual_start_date')) if result.get('actual_start_date') else None,
                    "actual_end_date": str(result.get('actual_end_date')) if result.get('actual_end_date') else None,
                    "task_status": result.get('task_status', ''),
                    "created_at": str(result.get('created_at')) if result.get('created_at') else None
                })
        
        return formatted_results
    except Exception as e:
        print(f"获取负责人任务详情出错: {e}")
        return []

# 13.1 获取指定负责人负责的异常任务详情
@app.get(f"{API_PREFIX}/owner-abnormal-tasks/{{owner}}", response_model=List[dict])
def get_owner_abnormal_tasks(owner: str):
    try:
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
        required_columns = ['task_owner', 'task_name', 'project_name', 'wbs_code', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'task_status', 'progress', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 查询指定负责人负责的异常任务详情
        # 处理多个负责人的情况
        owner_abnormal_tasks_sql = """
        SELECT 
            task_id,
            task_name,
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
        WHERE task_status = '异常'
          AND (
            task_owner = %s OR
            task_owner LIKE CONCAT('%%', %s, ',%%') OR
            task_owner LIKE CONCAT('%%', %s, '，%%') OR
            task_owner LIKE CONCAT('%%', %s, ';%%') OR
            task_owner LIKE CONCAT('%%', %s, '；%%') OR
            task_owner LIKE CONCAT('%%', %s, '/%%') OR
            task_owner LIKE CONCAT('%%', %s, '、%%') OR
            task_owner LIKE CONCAT(%s, ',%%') OR
            task_owner LIKE CONCAT(%s, '，%%') OR
            task_owner LIKE CONCAT(%s, ';%%') OR
            task_owner LIKE CONCAT(%s, '；%%') OR
            task_owner LIKE CONCAT(%s, '/%%') OR
            task_owner LIKE CONCAT(%s, '、%%')
          )
        ORDER BY created_at DESC
        """
        
        owner_abnormal_tasks_results = execute_query(owner_abnormal_tasks_sql, 
            (owner, owner, owner, owner, owner, owner, owner, 
             owner, owner, owner, owner, owner, owner), fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in owner_abnormal_tasks_results:
            if result is not None:
                formatted_results.append({
                    "task_id": result.get('task_id'),
                    "taskName": result.get('task_name', ''),
                    "projectName": result.get('project_name', ''),
                    "task_owner": result.get('task_owner', ''),
                    "wbsNo": result.get('wbs_code', ''),
                    "planStart": str(result.get('planned_start_date')) if result.get('planned_start_date') else None,
                    "planEnd": str(result.get('planned_end_date')) if result.get('planned_end_date') else None,
                    "actual_start_date": str(result.get('actual_start_date')) if result.get('actual_start_date') else None,
                    "actual_end_date": str(result.get('actual_end_date')) if result.get('actual_end_date') else None,
                    "status": result.get('task_status', ''),
                    "progress": float(result.get('progress')) if result.get('progress') is not None else 0.0,
                    "created_at": str(result.get('created_at')) if result.get('created_at') else None
                })
        
        return formatted_results
    except Exception as e:
        print(f"获取负责人异常任务详情出错: {e}")
        return []

# 21. 获取NCR类型分布统计（用于饼图）
@app.get(f"{API_PREFIX}/ncr/type-distribution", response_model=List[dict])
def get_ncr_type_distribution():
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
            # 检查jgjncr表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr表也不存在")
                return []
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 检查fsjd字段是否存在
        if 'fsjd' in column_names:
            # 根据fsjd字段统计分布
            type_sql = f"""
            SELECT 
                COALESCE(fsjd, '未知类型') as type,
                COUNT(*) as count
            FROM {table_name}
            GROUP BY fsjd
            ORDER BY count DESC
            LIMIT 10  -- 限制最多返回10种类型
            """
        elif 'problem_category' in column_names:
            # 如果没有fsjd字段，使用problem_category作为备选
            type_sql = f"""
            SELECT 
                COALESCE(problem_category, '未知类型') as type,
                COUNT(*) as count
            FROM {table_name}
            GROUP BY problem_category
            ORDER BY count DESC
            LIMIT 10
            """
        elif 'defective_product_name' in column_names:
            # 如果没有problem_category，可以根据defective_product_name的首字母或其他方式进行分类
            type_sql = f"""
            SELECT 
                CASE 
                    WHEN defective_product_name LIKE '%产品%' THEN '产品质量'
                    WHEN defective_product_name LIKE '%工艺%' THEN '工艺问题'
                    WHEN defective_product_name LIKE '%材料%' THEN '材料问题'
                    WHEN defective_product_name LIKE '%设备%' THEN '设备问题'
                    WHEN defective_product_name LIKE '%人员%' THEN '人员问题'
                    ELSE '其他类型'
                END as type,
                COUNT(*) as count
            FROM {table_name}
            GROUP BY 
                CASE 
                    WHEN defective_product_name LIKE '%产品%' THEN '产品质量'
                    WHEN defective_product_name LIKE '%工艺%' THEN '工艺问题'
                    WHEN defective_product_name LIKE '%材料%' THEN '材料问题'
                    WHEN defective_product_name LIKE '%设备%' THEN '设备问题'
                    WHEN defective_product_name LIKE '%人员%' THEN '人员问题'
                    ELSE '其他类型'
                END
            ORDER BY count DESC
            """
        else:
            # 如果没有合适的分类字段，返回总计数
            total_sql = f"SELECT '总计' as type, COUNT(*) as count FROM {table_name}"
            type_results = execute_query(total_sql, fetch_all=True) or []
            
            formatted_results = []
            for result in type_results:
                if result is not None and 'type' in result and 'count' in result:
                    formatted_results.append({
                        "name": result['type'],
                        "value": result['count']
                    })
            return formatted_results
        
        type_results = execute_query(type_sql, fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in type_results:
            if result is not None and 'type' in result and 'count' in result:
                formatted_results.append({
                    "name": result['type'],
                    "value": result['count']
                })
        
        # 如果没有数据，返回默认类型分布
        if not formatted_results:
            formatted_results = [
                {"name": "产品质量", "value": 0},
                {"name": "工艺问题", "value": 0},
                {"name": "材料问题", "value": 0},
                {"name": "设备问题", "value": 0},
                {"name": "人员问题", "value": 0}
            ]
        
        return formatted_results
    except Exception as e:
        print(f"获取NCR类型分布统计出错: {e}")
        return []


# 22. 获取NCR发生阶段分布统计（用于第一个饼图，基于fsjd字段）
@app.get(f"{API_PREFIX}/ncr/stage-distribution", response_model=List[dict])
def get_ncr_stage_distribution():
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
            # 检查jgjncr表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr表也不存在")
                return []
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 检查fsjd字段是否存在
        if 'fsjd' in column_names:
            # 根据fsjd字段统计分布
            stage_sql = f"""
            SELECT 
                COALESCE(fsjd, '未知阶段') as stage,
                COUNT(*) as count
            FROM {table_name}
            GROUP BY fsjd
            ORDER BY count DESC
            LIMIT 10  -- 限制最多返回10种阶段
            """
        elif 'occurrence_stage' in column_names:
            # 如果没有fsjd字段，使用occurrence_stage作为备选
            stage_sql = f"""
            SELECT 
                COALESCE(occurrence_stage, '未知阶段') as stage,
                COUNT(*) as count
            FROM {table_name}
            GROUP BY occurrence_stage
            ORDER BY count DESC
            LIMIT 10
            """
        else:
            # 如果没有合适的阶段字段，返回总计数
            total_sql = f"SELECT '总计' as stage, COUNT(*) as count FROM {table_name}"
            stage_results = execute_query(total_sql, fetch_all=True) or []
            
            formatted_results = []
            for result in stage_results:
                if result is not None and 'stage' in result and 'count' in result:
                    formatted_results.append({
                        "name": result['stage'],
                        "value": result['count']
                    })
            return formatted_results
        
        stage_results = execute_query(stage_sql, fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in stage_results:
            if result is not None and 'stage' in result and 'count' in result:
                formatted_results.append({
                    "name": result['stage'],
                    "value": result['count']
                })
        
        # 如果没有数据，返回默认阶段分布
        if not formatted_results:
            formatted_results = [
                {"name": "生产中", "value": 0},
                {"name": "安装后", "value": 0},
                {"name": "检验时", "value": 0},
                {"name": "使用中", "value": 0},
                {"name": "运输中", "value": 0}
            ]
        
        return formatted_results
    except Exception as e:
        print(f"获取NCR发生阶段分布统计出错: {e}")
        return []


# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=8001,
        reload=True  # 开发模式自动重载
    )

# 23. 获取评审阶段责任人员分布统计（用于展示dqjd为'3-评审'的记录中wczz字段的人员统计）
@app.get(f"{API_PREFIX}/ncr/responsibility-analysis", response_model=List[dict])
def get_responsibility_analysis():
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在")
            return []
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE jgjncr_copy"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取jgjncr_copy表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 检查dqjd和wczz字段是否存在
        if 'dqjd' not in column_names or 'wczz' not in column_names:
            print("警告: jgjncr_copy表缺少dqjd或wczz字段")
            return []
        
        # 查询dqjd为'3-评审'的记录中wczz字段的统计
        responsibility_sql = """
        SELECT wczz
        FROM jgjncr_copy
        WHERE dqjd = '3-评审' AND wczz IS NOT NULL AND TRIM(wczz) != ''
        """
        
        wczz_results = execute_query(responsibility_sql, fetch_all=True) or []
        
        # 统计每个人员姓名出现的次数（先拆分wczz字段中的姓名）
        name_count = {}
        for row in wczz_results:
            if row and 'wczz' in row:
                wczz_value = row['wczz']
                if wczz_value:
                    # 按逗号或分号拆分姓名
                    names = []
                    # 尝试多种可能的分隔符
                    if ',' in wczz_value:
                        names = wczz_value.split(',')
                    elif '，' in wczz_value:
                        names = wczz_value.split('，')
                    elif ';' in wczz_value:
                        names = wczz_value.split(';')
                    elif '；' in wczz_value:
                        names = wczz_value.split('；')
                    else:
                        names = [wczz_value]
                    
                    # 清理姓名并统计
                    for name in names:
                        clean_name = name.strip()
                        if clean_name and clean_name != 'nan' and clean_name != 'NULL':
                            name_count[clean_name] = name_count.get(clean_name, 0) + 1
        
        # 格式化返回数据
        formatted_results = []
        for name, count in name_count.items():
            formatted_results.append({
                "name": name,
                "value": count
            })
        
        # 按数量降序排列
        formatted_results.sort(key=lambda x: x['value'], reverse=True)
        
        # 只返回前五名
        return formatted_results[:5]
    except Exception as e:
        print(f"获取责任人员分析统计出错: {e}")
        return []


# 13.1 获取指定负责人负责的任务总数
@app.get(f"{API_PREFIX}/owner-tasks-count/{{owner}}", response_model=int)
def get_owner_tasks_count(owner: str):
    try:
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在")
            return 0
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取project_tasks表结构")
            return 0
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['task_owner']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return 0
        
        # 查询指定负责人负责的任务总数
        count_sql = """
        SELECT COUNT(*) as total
        FROM project_tasks
        WHERE task_owner = %s
        """
        count_result = execute_query(count_sql, (owner,), fetch_one=True)
        total_count = count_result.get('total', 0) if count_result else 0
        
        return total_count
    except Exception as e:
        print(f"获取负责人任务总数出错: {e}")
        return 0


# 14. 根据任务状态获取任务列表
@app.get(f"{API_PREFIX}/tasks/status/{{status}}", response_model=List[dict])
def get_tasks_by_status(status: str, limit: int = 100, offset: int = 0):
    try:
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
        required_columns = ['task_status', 'task_name', 'project_name', 'task_owner', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 首先获取所有任务状态的计数以调试
        all_status_sql = "SELECT DISTINCT task_status, COUNT(*) as count FROM project_tasks GROUP BY task_status"
        all_status_results = execute_query(all_status_sql, fetch_all=True)
        print(f"数据库中所有任务状态: {all_status_results}")
        
        # 根据任务状态查询任务
        status_map = {
            "not_started": "未开始",
            "ongoing": "进行中",
            "completed": "已完成",
            "accepted": "已验收"
        }
        
        db_status = status_map.get(status, status)  # 如果不在映射中则直接使用传入的状态
        print(f"查询的任务状态: {status}, 映射到数据库值: {db_status}")
        
        # 检查数据库中是否存在该状态的任务
        count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE task_status = %s"
        count_result = execute_query(count_sql, (db_status,))
        total_count = count_result.get('total', 0) if count_result else 0
        print(f"状态为 '{db_status}' 的任务总数: {total_count}")
        
        task_sql = """
        SELECT 
            task_id,
            task_name,
            project_name,
            task_owner,
            planned_start_date,
            planned_end_date,
            actual_start_date,
            actual_end_date,
            task_status,
            created_at
        FROM project_tasks
        WHERE task_status = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        tasks = execute_query(task_sql, (db_status, limit, offset), fetch_all=True) or []
        print(f"获取到的任务数量: {len(tasks)}")
        
        # 格式化数据
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue
                
            formatted_task = {
                "task_id": task.get("task_id"),
                "task_name": task.get("task_name", ""),
                "project_name": task.get("project_name", ""),
                "task_owner": task.get("task_owner", ""),
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else None,
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else None,
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else None,
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else None,
                "task_status": task.get("task_status", ""),
                "created_at": str(task.get("created_at")) if task.get("created_at") else None
            }
            formatted_tasks.append(formatted_task)
        
        print(f"格式化后的任务数量: {len(formatted_tasks)}")
        return formatted_tasks
    except Exception as e:
        print(f"获取任务状态列表出错: {e}")
        return []


# 15. 根据项目状态获取对应的任务数据
@app.get(f"{API_PREFIX}/tasks-by-status/{{status}}", response_model=List[dict])
def get_tasks_by_status_api(status: str):
    try:
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
        required_columns = ['task_status', 'task_name', 'project_name', 'task_owner', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'created_at', 'wbs_code', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 根据状态查询任务数据
        # 首先检查数据库中存在的所有状态
        all_status_sql = "SELECT DISTINCT task_status FROM project_tasks WHERE task_status IS NOT NULL"
        all_status_results = execute_query(all_status_sql, fetch_all=True)
        db_statuses = [row['task_status'] for row in all_status_results if row]
        print(f"数据库中所有任务状态: {db_statuses}")
        
        # 简化逻辑：直接使用传入的状态值，如果是数据库中存在的就查询
        # 从测试结果我们知道数据库中的真实状态是 '完成', '异常', '延期完成'
        status_conditions = [status]
        
        # 如果传入的状态在数据库中存在，就单独查询
        if status in db_statuses:
            status_conditions = [status]
        # 否则，为了兼容性，也可以尝试一些常见的变体
        else:
            # 如果传入的状态不在数据库中，仍使用原逻辑尝试匹配
            if status in ['未开始', 'not_started']:
                status_conditions = ['未开始', 'Not Started', 'not started', '未開始', 'Pending', '待开始']
            elif status in ['进行中', 'ongoing']:
                status_conditions = ['进行中', 'Ongoing', 'in progress', '進行中', 'In Progress', '执行中', 'Running']
            elif status in ['已完成', 'completed']:
                # 特别添加数据库中存在的真实状态
                status_conditions = ['完成', 'Completed', 'completed', '已完成', 'Finished', 'Done']
            elif status in ['已验收', 'accepted']:
                status_conditions = ['已验收', 'Accepted', 'accepted', '已驗收', '验收', '验收通过']
            else:
                # 如果都不是常见状态，直接使用传入的状态
                status_conditions = [status]
        
        # 构造查询条件
        placeholders = ','.join(['%s'] * len(status_conditions))
        task_sql = f"""
        SELECT 
            task_id,
            task_name,
            project_name,
            task_owner,
            wbs_code,
            task_type,
            planned_start_date,
            planned_end_date,
            actual_start_date,
            actual_end_date,
            task_status,
            progress,
            created_at
        FROM project_tasks
        WHERE task_status IN ({placeholders})
        ORDER BY created_at DESC
        """
        
        tasks = execute_query(task_sql, tuple(status_conditions), fetch_all=True) or []
        print(f"查询状态: {status_conditions}, 匹配到任务数量: {len(tasks)}")
        
        # 格式化数据
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue
                
            formatted_task = {
                "task_id": task.get("task_id"),
                "task_name": task.get("task_name", ""),
                "project_name": task.get("project_name", ""),
                "task_owner": task.get("task_owner", ""),
                "wbs_code": task.get("wbs_code", ""),
                "task_type": "",  # 数据库中没有task_type字段，设为空字符串
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else "",
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else "",
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else "",
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else "",
                "task_status": task.get("task_status", ""),
                "progress": float(task.get("progress")) if task.get("progress") is not None else 0.0,
                "created_at": str(task.get("created_at")) if task.get("created_at") else ""
            }
            formatted_tasks.append(formatted_task)
        
        print(f"最终返回任务数量: {len(formatted_tasks)}")
        return formatted_tasks
    except Exception as e:
        print(f"获取项目状态对应的任务数据出错: {e}")
        import traceback
        traceback.print_exc()
        return []


# 16. 根据项目ID或项目名称获取子任务数据（用于项目详情页显示子任务）
@app.get(f"{API_PREFIX}/project-subtasks/{{project_identifier}}", response_model=List[dict])
def get_project_subtasks(project_identifier: str):
    try:
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


# 17. 根据任务状态获取任务数据（用于扇形图点击跳转）
@app.get(f"{API_PREFIX}/tasks-by-project-status/{{status}}", response_model=List[dict])
def get_tasks_by_project_status(status: str):
    try:
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
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 由于扇形图显示的是任务状态分布，所以直接根据任务状态查询任务
        # 首先检查数据库中存在的所有任务状态
        all_status_sql = "SELECT DISTINCT task_status FROM project_tasks WHERE task_status IS NOT NULL"
        all_status_results = execute_query(all_status_sql, fetch_all=True)
        db_statuses = [row['task_status'] for row in all_status_results if row]
        print(f"数据库中所有任务状态: {db_statuses}")
        print(f"收到的查询状态: {status}")
        
        # 如果传入的状态存在于数据库中，则直接查询
        if status in db_statuses:
            status_conditions = [status]
        else:
            # 尝试使用状态映射来匹配常见的状态
            status_map = {
                "未开始": ["未开始"],
                "进行中": ["进行中"],
                "已完成": ["完成", "已完成"],
                "已验收": ["已验收"],
                # 对于其他特殊状态，直接使用原状态值
            }
            # 检查是否在映射中
            mapped_statuses = []
            for db_status in db_statuses:
                if status in db_status or db_status in status:  # 模糊匹配
                    mapped_statuses.append(db_status)
            
            if mapped_statuses:
                status_conditions = mapped_statuses
            else:
                # 如果没有找到匹配项，使用原状态值尝试查询
                status_conditions = [status]
        
        # 构造查询条件
        placeholders = ','.join(['%s'] * len(status_conditions))
        task_sql = f"""
        SELECT 
            task_id,
            task_name,
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
        WHERE task_status IN ({placeholders})
        ORDER BY created_at DESC
        """
        
        tasks = execute_query(task_sql, tuple(status_conditions), fetch_all=True) or []
        
        # 格式化数据
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue
                
            formatted_task = {
                "task_id": task.get("task_id"),
                "task_name": task.get("task_name", ""),
                "project_name": task.get("project_name", ""),
                "task_owner": task.get("task_owner", ""),
                "wbs_code": task.get("wbs_code", ""),
                "task_type": "",  # 数据库中没有task_type字段，设为空字符串
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else "",
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else "",
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else "",
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else "",
                "task_status": task.get("task_status", ""),
                "progress": float(task.get("progress")) if task.get("progress") is not None else 0.0,
                "created_at": str(task.get("created_at")) if task.get("created_at") else ""
            }
            formatted_tasks.append(formatted_task)
        
        print(f"根据任务状态'{status}'查询到 {len(formatted_tasks)} 个任务")
        return formatted_tasks
    except Exception as e:
        print(f"获取任务状态对应的任务数据出错: {e}")
        import traceback
        traceback.print_exc()
        return []


# 23. 根据阶段获取NCR数据（用于NCR阶段详情页面）
@app.get(f"{API_PREFIX}/ncr/by-stage")
async def get_ncr_by_stage(stage: str = None, status: str = None, priority: str = None, page: int = 1, limit: int = 20):
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
            # 检查jgjncr表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr表也不存在")
                return {"data": [], "total": 0}
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            return {"data": [], "total": 0}
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 构建查询条件
        conditions = []
        params = []
        
        if stage:
            if 'fsjd' in column_names:
                conditions.append("fsjd = %s")
                params.append(stage)
            elif 'occurrence_stage' in column_names:
                conditions.append("occurrence_stage = %s")
                params.append(stage)
            else:
                print("警告: 表中没有fsjd或occurrence_stage字段")
                return {"data": [], "total": 0}
        
        if status:
            if 'status' in column_names:
                conditions.append("status = %s")
                params.append(status)
            else:
                print("警告: 表中没有status字段")
        
        if priority:
            if 'review_level' in column_names:
                conditions.append("review_level = %s")
                params.append(priority)
            else:
                print("警告: 表中没有review_level字段")
        
        # 构建WHERE子句
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询数据总数
        count_sql = f"SELECT COUNT(*) as total FROM {table_name} WHERE {where_clause}"
        count_result = execute_query(count_sql, tuple(params))
        total_count = count_result.get('total', 0) if count_result else 0
        
        # 查询数据
        query_sql = f"""
        SELECT * FROM {table_name} 
        WHERE {where_clause}
        ORDER BY create_date DESC, process_no DESC
        LIMIT %s OFFSET %s
        """
        
        # 添加LIMIT和OFFSET参数
        params.extend([limit, offset])
        
        ncr_data = execute_query(query_sql, tuple(params), fetch_all=True) or []
        
        # 格式化数据
        formatted_data = []
        for record in ncr_data:
            if record is not None:
                formatted_record = {}
                for key, value in record.items():
                    # 处理日期字段
                    if isinstance(value, datetime):
                        formatted_record[key] = str(value)
                    # 处理数字字段
                    elif hasattr(value, 'quantize'):  # Decimal类型
                        formatted_record[key] = float(value)
                    else:
                        formatted_record[key] = value
                formatted_data.append(formatted_record)
        
        return {
            "data": formatted_data,
            "total": total_count
        }
    except Exception as e:
        print(f"根据阶段获取NCR数据出错: {e}")
        return {"data": [], "total": 0}


# 24. 获取NCR详情（用于NCR项目详情页面）
@app.get(f"{API_PREFIX}/ncr/detail/{{process_no}}")
async def get_ncr_detail(process_no: str):
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
            # 检查jgjncr表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr表也不存在")
                raise HTTPException(status_code=404, detail="NCR表不存在")
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            raise HTTPException(status_code=404, detail="无法获取表结构")
        
        # 查询特定NCR记录
        query_sql = f"SELECT * FROM {table_name} WHERE process_no = %s"
        ncr_record = execute_query(query_sql, (process_no,), fetch_one=True)
        
        if not ncr_record:
            raise HTTPException(status_code=404, detail=f"未找到NCR编号为 {process_no} 的记录")
        
        # 格式化数据
        formatted_record = {}
        for key, value in ncr_record.items():
            # 处理日期字段
            if isinstance(value, datetime):
                formatted_record[key] = str(value)
            # 处理数字字段
            elif hasattr(value, 'quantize'):  # Decimal类型
                formatted_record[key] = float(value)
            else:
                formatted_record[key] = value
        
        return formatted_record
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取NCR详情出错: {e}")
        raise HTTPException(status_code=500, detail="获取NCR详情失败")


# 25. 获取NCR列表（用于NCR概览页面）
@app.get(f"{API_PREFIX}/ncr/list")
async def get_ncr_list(page: int = 1, limit: int = 20):
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
            # 检查jgjncr表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr表也不存在")
                return []
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 查询NCR数据
        query_sql = f"""
        SELECT * FROM {table_name}
        ORDER BY create_date DESC, process_no DESC
        LIMIT %s OFFSET %s
        """
        
        ncr_data = execute_query(query_sql, (limit, offset), fetch_all=True) or []
        
        # 格式化数据
        formatted_data = []
        for record in ncr_data:
            if record is not None:
                formatted_record = {}
                for key, value in record.items():
                    # 处理日期字段
                    if isinstance(value, datetime):
                        formatted_record[key] = str(value)
                    # 处理数字字段
                    elif hasattr(value, 'quantize'):  # Decimal类型
                        formatted_record[key] = float(value)
                    else:
                        formatted_record[key] = value
                formatted_data.append(formatted_record)
        
        return formatted_data
    except Exception as e:
        print(f"获取NCR列表出错: {e}")
        return []


# 26. 获取DQJD和WCZZ数据统计（用于展示未完成项目的阶段分布和完成单位统计）
@app.get(f"{API_PREFIX}/dqjd-wczz-data")
async def get_dqjd_wczz_data():
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
            # 检查jgjncr表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr表也不存在")
                return {"dqjdStats": [], "wczzStats": [], "tableData": []}
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            return {"dqjdStats": [], "wczzStats": [], "tableData": []}
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 检查所需字段是否存在
        if 'dqjd' not in column_names:
            print(f"警告: {table_name}表中没有dqjd字段")
            return {"dqjdStats": [], "wczzStats": [], "tableData": []}
        
        if 'wczz' not in column_names:
            print(f"警告: {table_name}表中没有wczz字段")
            return {"dqjdStats": [], "wczzStats": [], "tableData": []}
        
        # 构建查询条件 - 只查询DQJD不等于'9-完成'的记录
        where_clause = "WHERE dqjd != %s OR dqjd IS NULL"
        exclude_value = '9-完成'
        
        # 查询DQJD统计
        dqjd_sql = f"SELECT dqjd, COUNT(*) as count FROM {table_name} {where_clause} GROUP BY dqjd ORDER BY count DESC"
        dqjd_data = execute_query(dqjd_sql, (exclude_value,), fetch_all=True) or []
        
        # 格式化DQJD统计数据
        dqjd_stats = []
        for record in dqjd_data:
            if record and record.get('dqjd') is not None:
                dqjd_stats.append({
                    'name': record['dqjd'],
                    'value': record['count']
                })
        
        # 查询WCZZ原始数据（不进行GROUP BY，以便拆分多个姓名）
        wczz_sql = f"SELECT wczz FROM {table_name} {where_clause}"
        wczz_raw_data = execute_query(wczz_sql, (exclude_value,), fetch_all=True) or []
        
        # 格式化WCZZ统计数据 - 拆分多个姓名并累加计数
        wczz_stats_dict = {}
        for record in wczz_raw_data:
            if record and record.get('wczz') is not None:
                wczz_value = record['wczz']
                # 按多种分隔符分割姓名：逗号、中文逗号、分号、中文分号、顿号
                import re
                names = re.split(r'[,,，,;,；,、,+]', str(wczz_value))
                for name in names:
                    name = name.strip()  # 去除空白字符
                    if name:  # 确保姓名不为空
                        if name in wczz_stats_dict:
                            wczz_stats_dict[name] += 1
                        else:
                            wczz_stats_dict[name] = 1
        
        # 转换为数组格式
        wczz_stats = []
        for name, count in wczz_stats_dict.items():
            wczz_stats.append({
                'name': name,
                'value': count
            })
        
        # 查询详细表格数据
        table_sql = f"SELECT * FROM {table_name} {where_clause} ORDER BY create_date DESC LIMIT 100"
        table_data = execute_query(table_sql, (exclude_value,), fetch_all=True) or []
        
        # 格式化表格数据
        formatted_table_data = []
        for record in table_data:
            if record is not None:
                formatted_record = {}
                for key, value in record.items():
                    # 处理日期字段
                    if isinstance(value, datetime):
                        formatted_record[key] = str(value)
                    # 处理数字字段
                    elif hasattr(value, 'quantize'):  # Decimal类型
                        formatted_record[key] = float(value)
                    else:
                        formatted_record[key] = value
                formatted_table_data.append(formatted_record)
        
        return {
            "dqjdStats": dqjd_stats,
            "wczzStats": wczz_stats,
            "tableData": formatted_table_data
        }
    except Exception as e:
        print(f"获取DQJD/WCZZ数据出错: {e}")
        import traceback
        traceback.print_exc()
        return {"dqjdStats": [], "wczzStats": [], "tableData": []}


# 28. 获取未评审状态下的负责人统计（用于展示dqjd为'3-未评审'的记录中wczz字段的人员统计，显示前15名）
@app.get(f"{API_PREFIX}/ncr/unreviewed-responsibility", response_model=List[dict])
def get_unreviewed_responsibility_stats():
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在")
            return []
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE jgjncr_copy"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取jgjncr_copy表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 检查dqjd和wczz字段是否存在
        if 'dqjd' not in column_names or 'wczz' not in column_names:
            print("警告: jgjncr_copy表缺少dqjd或wczz字段")
            return []
        
        # 查询dqjd为'3-未评审'的记录中wczz字段的统计
        unreviewed_sql = """
        SELECT wczz
        FROM jgjncr_copy
        WHERE dqjd = '3-未评审' AND wczz IS NOT NULL AND TRIM(wczz) != ''
        """
        
        wczz_results = execute_query(unreviewed_sql, fetch_all=True) or []
        
        # 统计每个人员姓名出现的次数（先拆分wczz字段中的姓名）
        name_count = {}
        for record in wczz_results:
            if record and record.get('wczz'):
                wczz_value = record['wczz']
                # 按多种分隔符分割姓名：逗号、中文逗号、分号、中文分号、顿号、加号
                import re
                names = re.split(r'[,,，,;,；,、,+]', str(wczz_value))
                for name in names:
                    name = name.strip()  # 去除空白字符
                    if name:  # 确保姓名不为空
                        if name in name_count:
                            name_count[name] += 1
                        else:
                            name_count[name] = 1
        
        # 转换为数组格式
        formatted_results = []
        for name, count in name_count.items():
            formatted_results.append({
                "name": name,
                "value": count
            })
        
        # 按数量降序排列
        formatted_results.sort(key=lambda x: x['value'], reverse=True)
        
        # 只返回前15名
        return formatted_results[:15]
    except Exception as e:
        print(f"获取未评审责任人统计出错: {e}")
        import traceback
        traceback.print_exc()
        return []


# 27. 导入项目数据
@app.post(f"{API_PREFIX}/projects/import")
async def import_projects(file: UploadFile = File(...)):
    try:
        import pandas as pd
        import io
        from datetime import datetime
        import re
        
        # 检查文件类型
        if not file.filename.lower().endswith((".xlsx", ".xls", ".csv")):
            raise HTTPException(status_code=400, detail="不支持的文件格式，请上传Excel或CSV文件")
        
        # 读取文件内容
        contents = await file.read()
        
        # 根据文件类型处理数据
        if file.filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        else:  # CSV
            df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
        
        # 数据验证 - 检查文件是否为空
        if df.empty:
            raise HTTPException(status_code=400, detail="文件中没有数据")
        
        # 数据验证 - 检查必要的列是否存在
        required_columns = ['任务名称', 'task_name', 'task', '工作内容', '任务描述', 'task_description', '任务', 'name']
        available_columns = [col.strip().replace('\u3000', '').replace(' ', '').lower() for col in df.columns]
        
        has_required_col = any(any(req_col.replace('\u3000', '').replace(' ', '').lower() in avail_col 
                                   for req_col in ['任务名称', 'task_name', 'task', '工作内容', '任务描述', 'task_description', '任务', 'name']) 
                                   for avail_col in available_columns)
        
        if not has_required_col:
            # 如果没有找到必要的列，发出警告但仍继续处理
            print("警告: 未找到标准的任务名称列，仍将尝试导入数据")
        
        # 从文件名解析项目名和项目经理
        filename = file.filename
        name_without_ext = os.path.splitext(filename)[0]
        
        # 尝试匹配 "xxx(项目名)-项目经理姓名" 格式
        match = re.match(r'.*\((.+)\)-(.+)', name_without_ext)
        
        if match:
            project_name = match.group(1).strip()
            manager_name = match.group(2).strip()
        else:
            # 如果不符合上述格式，尝试匹配 "项目名-项目经理姓名" 格式
            last_dash_index = name_without_ext.rfind('-')
            if last_dash_index != -1:
                project_name = name_without_ext[:last_dash_index].strip()
                manager_name = name_without_ext[last_dash_index+1:].strip()
            else:
                # 如果都不符合，返回整个名字作为项目名，项目经理为未知
                project_name = name_without_ext
                manager_name = "未知"
        
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            raise HTTPException(status_code=400, detail="数据库中不存在projects表")
        
        # 检查project_tasks表是否存在
        check_tasks_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        tasks_table_exists = execute_query(check_tasks_table_sql)
        if not tasks_table_exists:
            raise HTTPException(status_code=400, detail="数据库中不存在project_tasks表")
        
        # 检查项目是否已存在
        check_project_sql = "SELECT project_id FROM projects WHERE project_name = %s"
        check_result = execute_query(check_project_sql, (project_name,))
        
        if check_result:
            # 项目已存在，获取现有项目ID
            project_id = check_result['project_id']
            print(f"项目 '{project_name}' 已存在，使用现有ID: {project_id}")
        else:
            # 分析Excel数据以提取关键信息
            planned_start_cols = ['计划开始时间', '计划开始日期', 'planned_start', 'planned_start_date', 'start_date_plan', '计划开始', '计划开工']
            planned_end_cols = ['计划结束时间', '计划结束日期', 'planned_end', 'planned_end_date', 'end_date_plan', '计划结束', '计划完工']
            actual_start_cols = ['实际开始时间', '实际开始日期', 'actual_start', 'actual_start_date', 'start_date_actual', '实际开始', '实际开工']
            actual_end_cols = ['实际结束时间', '实际结束日期', 'actual_end', 'actual_end_date', 'end_date_actual', '实际结束', '实际完工']

            # 收集所有日期值
            planned_starts = []
            planned_ends = []
            actual_starts = []
            actual_ends = []

            for col_name in df.columns:
                col_name_clean = col_name.strip().replace('\u3000', '').replace(' ', '')  # 去除全角空格和普通空格
                col_name_lower = col_name_clean.lower()

                # 检查列名是否匹配计划开始日期
                if any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_start_cols]):
                    for val in df[col_name]:
                        if pd.notna(val):
                            try:
                                date_val = pd.to_datetime(val).date()
                                planned_starts.append(date_val)
                            except:
                                continue

                # 检查列名是否匹配计划结束日期
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_end_cols]):
                    for val in df[col_name]:
                        if pd.notna(val):
                            try:
                                date_val = pd.to_datetime(val).date()
                                planned_ends.append(date_val)
                            except:
                                continue

                # 检查列名是否匹配实际开始日期
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_start_cols]):
                    for val in df[col_name]:
                        if pd.notna(val):
                            try:
                                date_val = pd.to_datetime(val).date()
                                actual_starts.append(date_val)
                            except:
                                continue

                # 检查列名是否匹配实际结束日期
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_end_cols]):
                    for val in df[col_name]:
                        if pd.notna(val):
                            try:
                                date_val = pd.to_datetime(val).date()
                                actual_ends.append(date_val)
                            except:
                                continue

            # 计算最早的计划开始时间和最晚的计划结束时间
            earliest_planned_start = min(planned_starts) if planned_starts else None
            latest_planned_end = max(planned_ends) if planned_ends else None
            earliest_actual_start = min(actual_starts) if actual_starts else None
            latest_actual_end = max(actual_ends) if actual_ends else None

            # 根据数据确定项目状态
            if latest_actual_end and latest_actual_end < datetime.now().date():
                status = "已完成"
            elif earliest_actual_start:
                status = "进行中"
            elif earliest_planned_start and earliest_planned_start > datetime.now().date():
                status = "未开始"
            else:
                status = "已计划"

            # 插入项目数据
            insert_project_sql = """
            INSERT INTO projects (project_name, project_manager, planned_start_date, planned_end_date, 
                                 actual_start_date, actual_end_date, project_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(insert_project_sql, (
                project_name, manager_name, 
                earliest_planned_start, latest_planned_end,
                earliest_actual_start, latest_actual_end, 
                status
            ), fetch_one=False)
            
            # 获取新插入的项目ID
            project_id = execute_query("SELECT LAST_INSERT_ID()")
            print(f"成功创建项目 '{project_name}'，ID: {project_id}")

        # 识别可能的列名 - 与simple_datadeal.py保持一致
        task_name_cols = ['任务名称', 'task_name', 'task', '工作内容', '任务描述', 'task_description', '任务', 'name']
        wbs_code_cols = ['WBS编码', 'wbs_code', 'wbs', 'WBS', '工作分解结构', 'work_breakdown_structure']
        task_owner_cols = ['负责人', 'task_owner', 'owner', '责任人', 'task_responsible', 'person_in_charge']
        planned_start_cols = ['计划开始时间', '计划开始日期', 'planned_start', 'planned_start_date', 'start_date_plan', '计划开始', '计划开工']
        planned_end_cols = ['计划结束时间', '计划结束日期', 'planned_end', 'planned_end_date', 'end_date_plan', '计划结束', '计划完工']
        actual_start_cols = ['实际开始时间', '实际开始日期', 'actual_start', 'actual_start_date', 'start_date_actual', '实际开始', '实际开工']
        actual_end_cols = ['实际结束时间', '实际结束日期', 'actual_end', 'actual_end_date', 'end_date_actual', '实际结束', '实际完工']
        progress_cols = ['进度', 'progress', '完成度', 'completion_rate', 'percentage']
        lag_days_cols = ['滞后度(天)', 'lag_days', 'delay_days', 'delay']
        task_status_cols = ['状态', 'task_status', 'status', '任务状态', '工作状态']

        # 检查该项目是否已经有任务数据
        check_tasks_sql = "SELECT COUNT(*) as count FROM project_tasks WHERE project_name = %s AND project_id = %s"
        check_tasks_result = execute_query(check_tasks_sql, (project_name, project_id))
        count = check_tasks_result['count'] if check_tasks_result and 'count' in check_tasks_result else 0
        
        if count > 0:
            print(f"项目 '{project_name}' (ID: {project_id}) 已有 {count} 条任务数据")
            # 询问用户是否覆盖现有数据
            overwrite = request_data.get('overwrite', False) if request_data else False
            if not overwrite:
                return {"message": f"项目已存在 {count} 条任务数据，如需覆盖请使用overwrite=true参数", "existing_count": count}
            else:
                # 删除现有任务数据
                delete_tasks_sql = "DELETE FROM project_tasks WHERE project_name = %s AND project_id = %s"
                execute_query(delete_tasks_sql, (project_name, project_id), fetch_one=False)
                print(f"已删除项目 '{project_name}' (ID: {project_id}) 的 {count} 条旧任务数据")

        print(f"开始处理项目 '{project_name}' 的 {len(df)} 行数据")
        
        inserted_count = 0
        
        # 遍历数据行，插入任务数据
        for i, row in df.iterrows():
            task_name = None
            wbs_code = None
            task_owner = None
            planned_start = None
            planned_end = None
            actual_start = None
            actual_end = None
            progress = None
            lag_days = None
            task_status = None

            # 遍历行中的每一列，查找匹配的字段
            for col_name, col_value in row.items():
                col_name_clean = col_name.strip().replace('\u3000', '').replace(' ', '')  # 去除全角空格和普通空格
                col_name_lower = col_name_clean.lower()

                if any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_name_cols]) and not task_name:
                    task_name = str(col_value) if pd.notna(col_value) else None
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in wbs_code_cols]) and not wbs_code:
                    wbs_code = str(col_value) if pd.notna(col_value) else None
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_owner_cols]) and not task_owner:
                    task_owner = str(col_value) if pd.notna(col_value) else None
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_start_cols]) and not planned_start:
                    if pd.notna(col_value):
                        try:
                            planned_start = pd.to_datetime(col_value).date()
                        except:
                            pass
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_end_cols]) and not planned_end:
                    if pd.notna(col_value):
                        try:
                            planned_end = pd.to_datetime(col_value).date()
                        except:
                            pass
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_start_cols]) and not actual_start:
                    if pd.notna(col_value):
                        try:
                            actual_start = pd.to_datetime(col_value).date()
                        except:
                            pass
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_end_cols]) and not actual_end:
                    if pd.notna(col_value):
                        try:
                            actual_end = pd.to_datetime(col_value).date()
                        except:
                            pass
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in progress_cols]) and not progress:
                    if pd.notna(col_value):
                        try:
                            # 处理百分比格式
                            val_str = str(col_value).replace('%', '')
                            if val_str.replace('.', '').replace('-', '').isdigit():
                                progress = float(val_str)
                            else:
                                progress = None
                        except:
                            progress = None
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in lag_days_cols]) and not lag_days:
                    if pd.notna(col_value):
                        try:
                            lag_days = float(str(col_value)) if str(col_value).replace('-', '').replace('.', '').isdigit() else None
                        except:
                            lag_days = None
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_status_cols]):
                    task_status = str(col_value) if pd.notna(col_value) else None

            # 只有当至少有任务名称时才插入记录
            if task_name and task_name.strip() != '':
                # 如果task_status未明确指定或为空值，则根据条件计算
                if not task_status or task_status == 'None' or task_status == '' or task_status.lower() == 'none':
                    task_status = determine_task_status_import(planned_start, planned_end, actual_start, actual_end, lag_days)
                else:
                    # 标准化状态值
                    if task_status in ['完成', '已完成', 'Finish', 'Finished']:
                        task_status = '完成'
                    elif task_status in ['进行中', '执行中', 'In Progress', 'Ongoing']:
                        task_status = '进行中'
                    elif task_status in ['未开始', 'Pending', 'Not Started']:
                        task_status = '未开始'
                    elif task_status in ['延期完成', 'Delayed Finish']:
                        task_status = '延期完成'
                    elif task_status in ['异常', 'Exception', 'Abnormal']:
                        task_status = '异常'
                    else:
                        # 再次使用函数判断状态
                        task_status = determine_task_status_import(planned_start, planned_end, actual_start, actual_end, lag_days)

                # 根据实际的数据库结构插入任务数据，包括project_id
                insert_task_sql = """
                INSERT INTO project_tasks (
                    project_id, project_name, project_manager, task_name, wbs_code, 
                    planned_start_date, planned_end_date, actual_start_date, actual_end_date,
                    progress, task_owner, task_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                try:
                    result = execute_query(insert_task_sql, (
                        project_id, project_name, manager_name, task_name, wbs_code,
                        planned_start, planned_end, actual_start, actual_end,
                        progress, task_owner, task_status
                    ), fetch_one=False)
                    if result is not None:  # 检查插入是否成功
                        inserted_count += 1
                except Exception as e:
                    print(f"    插入任务 '{task_name}' 时出错: {e}")

        if inserted_count > 0:
            print(f"成功插入 {inserted_count} 个任务到项目 '{project_name}' (ID: {project_id})")
        else:
            print(f"项目 '{project_name}' 没有找到有效的任务数据或插入失败")
        
        return {"message": f"成功导入 {inserted_count} 条任务数据到项目 '{project_name}'"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"导入项目数据出错: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


def determine_task_status_import(planned_start, planned_end, actual_start, actual_end, lag_days):
    """
    根据条件确定任务状态 - 与simple_datadeal.py保持一致
    完成：滞后度一列中为0的，或者说实际开始时间，实际完成时间早于或者等于预计开始时间，预计完成时间
    延期完成：实际开始时间，实际完成时间晚于预计开始时间，预计完成时间
    异常：实际开始时间，实际完成时间为空
    进行中：根据实时的日期，处于预计完成时间跟预计开始时间中间，只填写了实际开始时间
    """
    from datetime import datetime
    current_date = datetime.now().date()
    
    # 检查异常情况：实际开始时间或实际完成时间为空
    if actual_start is None or actual_end is None:
        if actual_start is None and actual_end is None:
            return "异常"
        elif actual_start is not None and actual_end is None:
            # 如果仅有实际开始时间，检查是否在计划范围内
            if planned_start and planned_end and planned_start <= current_date <= planned_end:
                return "进行中"
            else:
                return "异常"
        elif actual_start is None and actual_end is not None:
            return "异常"
    
    # 如果实际开始和完成时间都存在
    if actual_start and actual_end:
        # 检查是否为延期完成：实际开始时间或实际完成时间晚于预计开始时间或预计完成时间
        if ((planned_start and actual_start > planned_start) or 
            (planned_end and actual_end > planned_end)):
            return "延期完成"
        # 检查是否为完成：实际开始时间完成时间早于或等于预计开始时间和完成时间
        elif ((planned_start and actual_start <= planned_start) and 
              (planned_end and actual_end <= planned_end)):
            return "完成"
        # 如果在计划时间范围内完成
        elif ((planned_start and planned_end) and 
              (planned_start <= actual_start <= planned_end) and 
              (planned_end and actual_end <= planned_end)):
            return "完成"
        else:
            return "延期完成"
    
    # 检查进行中：当前日期在计划开始和结束之间，且只有实际开始时间
    if (planned_start and planned_end and 
        planned_start <= current_date <= planned_end and 
        actual_start is not None and actual_end is None):
        return "进行中"
    
    # 默认为异常
    return "异常"


# 28. 导出项目数据
@app.post(f"{API_PREFIX}/projects/export")
async def export_projects(request_data: dict):
    try:
        import pandas as pd
        from fastapi.responses import StreamingResponse
        import io
        
        # 获取要导出的项目ID列表
        project_ids = request_data.get('project_ids', [])
        
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            raise HTTPException(status_code=400, detail="数据库中不存在projects表")
        
        # 查询项目数据
        if project_ids:  # 如果指定了项目ID，则导出选中的项目
            placeholders = ','.join(['%s'] * len(project_ids))
            select_sql = f"SELECT * FROM projects WHERE project_id IN ({placeholders}) ORDER BY created_at DESC"
            projects = execute_query(select_sql, tuple(project_ids), fetch_all=True) or []
        else:  # 否则导出所有项目
            select_sql = "SELECT * FROM projects ORDER BY created_at DESC"
            projects = execute_query(select_sql, fetch_all=True) or []
        
        if not projects:
            raise HTTPException(status_code=404, detail="没有找到要导出的项目数据")
        
        # 将数据转换为DataFrame，并确保数据类型正确
        # 遍历数据，处理可能存在的不可序列化对象
        processed_projects = []
        for project in projects:
            processed_project = {}
            for key, value in project.items():
                # 处理日期和时间类型
                if isinstance(value, (datetime, type(pd.Timestamp))):
                    processed_project[key] = str(value)
                # 处理十进制类型
                elif hasattr(value, 'quantize'):  # 检查是否为Decimal类型
                    processed_project[key] = float(value)
                # 其他类型直接使用
                else:
                    processed_project[key] = value
            processed_projects.append(processed_project)
        
        df = pd.DataFrame(processed_projects)
        
        # 创建内存中的字节流
        output = io.BytesIO()
        
        # 将DataFrame写入Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='项目数据')
        
        # 获取字节流内容
        output.seek(0)
        
        # 创建StreamingResponse返回Excel文件
        def iterfile():
            yield output.getvalue()

        from datetime import datetime
        return StreamingResponse(
            iterfile(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=\"项目数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx\""}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"导出项目数据出错: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=8001,
        reload=True  # 开发模式自动重载
    )
