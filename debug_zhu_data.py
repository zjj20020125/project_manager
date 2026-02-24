import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'project-backend'))

# 动态导入数据库模块
import importlib.util
spec = importlib.util.spec_from_file_location("database", "project-backend/database/database.py")
database_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database_module)
execute_query = database_module.execute_query

# 查询朱剑文的所有异常任务
sql = """
SELECT 
    project_name,
    task_owner,
    task_name,
    created_at,
    task_status
FROM project_tasks 
WHERE task_status = '异常' 
  AND (
    task_owner = '朱剑文' OR
    task_owner LIKE '%朱剑文,%' OR
    task_owner LIKE '%朱剑文，%' OR
    task_owner LIKE '%,朱剑文%' OR
    task_owner LIKE '%，朱剑文%'
  )
ORDER BY project_name, created_at ASC
"""

results = execute_query(sql, fetch_all=True)
print(f"朱剑文的异常任务总数: {len(results)}")
print("\n详细数据:")
for i, task in enumerate(results, 1):
    print(f"{i}. 项目: {task['project_name']}")
    print(f"   任务: {task['task_name']}")
    print(f"   负责人: {task['task_owner']}")
    print(f"   创建时间: {task['created_at']}")
    print("---")

# 按项目分组统计
from collections import defaultdict
project_tasks = defaultdict(list)
for task in results:
    project_tasks[task['project_name']].append(task)

print(f"\n按项目分组:")
for project, tasks in project_tasks.items():
    print(f"\n项目: {project}")
    tasks_sorted = sorted(tasks, key=lambda x: x['created_at'])
    for i, task in enumerate(tasks_sorted):
        abnormal_type = "首个异常节点" if i == 0 else "进度推迟"
        print(f"  {i+1}. {task['task_name']} - {abnormal_type} ({task['created_at']})")