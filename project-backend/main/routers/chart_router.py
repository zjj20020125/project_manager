"""
图表统计路由模块
包含图表相关的API接口
"""

from fastapi import APIRouter
from typing import List
from datetime import datetime

# 从database模块导入
from database.database import execute_query

# 从models模块导入
from models.models import ChartData

# 创建路由器实例
router = APIRouter(prefix="/v1", tags=["图表统计"])

# 3. 获取图表数据
@router.get("/chart/data", response_model=ChartData)
async def get_chart_data():
    """获取图表数据"""
    try:
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在，返回模拟数据")
            # 1. 项目类型分布（模拟数据）
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

        # 1. 项目类型分布（模拟数据）
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
        
        # 格式化甘特图数据
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
                "project_name": item.get("project_name", ""),
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

# 10. 获取项目状态分布数据
@router.get("/project-status-stats")
async def get_project_status_stats():
    """获取项目状态分布数据"""
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

# 11. 获取任务进度甘特图数据
@router.get("/task-gantt-data")
async def get_task_gantt_data(project_name: str = None):
    """获取任务进度甘特图数据"""
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
            # 查询所有任务数据
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
            LIMIT 100
            """
            gantt_results = execute_query(gantt_sql, fetch_all=True) or []

        # 格式化返回数据
        formatted_results = []
        for result in gantt_results:
            if result is not None:
                start_date = result.get('planned_start_date')
                end_date = result.get('planned_end_date')

                # 如果其中一个日期为空，则用另一个日期代替
                if start_date is None and end_date is None:
                    continue

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

# 12. 根据状态获取project_tasks表中的完整数据
@router.get("/chart/project-tasks/status/{status}")
async def get_project_tasks_by_status(status: str):
    """根据状态获取project_tasks表中的完整数据"""
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

        # 根据状态查询project_tasks表中的完整数据
        tasks_sql = """
        SELECT *
        FROM project_tasks
        WHERE task_status = %s
        ORDER BY planned_start_date ASC
        """
        
        tasks_results = execute_query(tasks_sql, (status,), fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in tasks_results:
            if result is not None:
                # 处理日期字段
                planned_start_date = result.get('planned_start_date')
                planned_end_date = result.get('planned_end_date')
                actual_start_date = result.get('actual_start_date')
                actual_end_date = result.get('actual_end_date')
                created_at = result.get('created_at')
                updated_at = result.get('updated_at')
                
                # 处理进度字段
                progress = result.get('progress')
                if hasattr(progress, 'quantize'):  # 如果是Decimal类型
                    progress_value = float(progress)
                else:
                    progress_value = float(progress) if progress is not None else 0.0
                
                formatted_item = {
                    "task_id": result.get('task_id'),
                    "project_id": result.get('project_id'),
                    "project_name": result.get('project_name', ''),
                    "project_manager": result.get('project_manager', ''),
                    "wbs_code": result.get('wbs_code', ''),
                    "task_name": result.get('task_name', ''),
                    "task_owner": result.get('task_owner', ''),
                    "task_status": result.get('task_status', ''),
                    "planned_start_date": str(planned_start_date) if planned_start_date else '',
                    "planned_end_date": str(planned_end_date) if planned_end_date else '',
                    "actual_start_date": str(actual_start_date) if actual_start_date else '',
                    "actual_end_date": str(actual_end_date) if actual_end_date else '',
                    "progress": progress_value,
                    "created_at": str(created_at) if created_at else '',
                    "updated_at": str(updated_at) if updated_at else ''
                }
                formatted_results.append(formatted_item)

        print(f"根据状态'{status}'返回project_tasks数据: {len(formatted_results)} 条")
        return formatted_results
        
    except Exception as e:
        print(f"根据状态获取project_tasks数据出错: {e}")
        import traceback
        traceback.print_exc()
        return []