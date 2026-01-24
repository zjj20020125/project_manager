from fastapi import FastAPI
from typing import List
import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# 从database模块导入
import database.database
execute_query = database.database.execute_query

# 定义甘特图数据模型
class GanttData:
    def __init__(self):
        self.project_name = ""
        self.task_name = ""
        self.task_owner = ""
        self.planned_start_date = ""
        self.planned_end_date = ""

# 甘特图相关API
def register_gantt_routes(app):
    @app.get("/api/v1/task-gantt-data")
    async def get_task_gantt_data():
        """
        获取任务进度甘特图数据
        """
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

            # 查询任务进度甘特图数据
            gantt_sql = """
            SELECT 
                project_name,
                task_name,
                task_owner,
                planned_start_date,
                planned_end_date
            FROM project_tasks
            WHERE planned_start_date IS NOT NULL 
              AND planned_end_date IS NOT NULL
              AND planned_start_date <= planned_end_date
            ORDER BY project_name, planned_start_date
            LIMIT 50
            """
            gantt_results = execute_query(gantt_sql, fetch_all=True) or []

            # 格式化返回数据
            formatted_results = []
            for result in gantt_results:
                if result is not None:
                    formatted_results.append({
                        "project_name": result.get('project_name', ''),
                        "task_name": result.get('task_name', ''),
                        "task_owner": result.get('task_owner', ''),
                        "planned_start_date": str(result.get('planned_start_date', '')) if result.get('planned_start_date') else '',
                        "planned_end_date": str(result.get('planned_end_date', '')) if result.get('planned_end_date') else ''
                    })

            return formatted_results
        except Exception as e:
            print(f"获取任务进度甘特图数据出错: {e}")
            return []