import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List  # 添加缺失的List导入
from datetime import datetime  # 添加datetime导入
import uvicorn

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
        # jgj-project数据库中没有project_members表，使用project_tasks中的project_manager字段
        load_sql = """
        SELECT project_manager, COUNT(task_id) as load_count
        FROM project_tasks
        WHERE project_manager IS NOT NULL
        GROUP BY project_manager
        """
        load_data = execute_query(load_sql, fetch_all=True) or []
        load_bar = [{"name": item["project_manager"], "value": item["load_count"]} for item in load_data if item and "project_manager" in item and "load_count" in item]
        
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

# 12. 获取任务负责人统计
@app.get(f"{API_PREFIX}/task-owner-stats", response_model=List[dict])
def get_task_owner_stats():
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
        required_columns = ['task_owner']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 查询任务负责人统计
        owner_stats_sql = """
        SELECT 
            task_owner,
            COUNT(*) as task_count
        FROM project_tasks
        WHERE task_owner IS NOT NULL 
          AND task_owner != ''
          AND task_owner != 'nan'
          AND task_owner != 'NaN'
          AND task_owner != 'null'
        GROUP BY task_owner
        ORDER BY task_count DESC
        """
        owner_stats_results = execute_query(owner_stats_sql, fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in owner_stats_results:
            if result is not None:
                owner_name = result.get('task_owner', '未知负责人')
                # 检查是否为异常数据
                if owner_name in ['nan', 'NaN', 'null', 'NULL', '<NULL>', 'None'] or str(owner_name).lower() == 'nan':
                    owner_name = '异常数据'
                
                formatted_results.append({
                    "owner_name": owner_name,
                    "task_count": result.get('task_count', 0)
                })
        
        return formatted_results
    except Exception as e:
        print(f"获取任务负责人统计出错: {e}")
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


# 16. 根据任务状态获取任务数据（用于扇形图点击跳转）
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


# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=8001,
        reload=True  # 开发模式自动重载
    )
