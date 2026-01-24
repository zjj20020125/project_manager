import sys
import os

# 添加项目路径到Python模块搜索路径
project_backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project-backend')
sys.path.append(project_backend_path)

# 添加main模块路径
main_path = os.path.join(project_backend_path, 'main')
sys.path.append(main_path)

# 现在可以导入模块了
from database import database
execute_query = database.execute_query

print('检查project_tasks表中的日期字段数据...')
try:
    # 检查project_tasks表中的日期字段
    result = execute_query('SELECT task_name, planned_start_date, planned_end_date FROM project_tasks LIMIT 10')
    print('Sample data:', result)
    
    # 检查有多少条记录具有有效的日期
    valid_dates_query = "SELECT COUNT(*) as count FROM project_tasks WHERE planned_start_date IS NOT NULL AND planned_end_date IS NOT NULL"
    valid_dates_result = execute_query(valid_dates_query)
    print('具有有效日期的记录数:', valid_dates_result)
    
    # 检查日期范围
    date_range_query = "SELECT MIN(planned_start_date), MAX(planned_start_date), MIN(planned_end_date), MAX(planned_end_date) FROM project_tasks WHERE planned_start_date IS NOT NULL AND planned_end_date IS NOT NULL"
    date_range_result = execute_query(date_range_query)
    print('日期范围:', date_range_result)
    
    # 检查是否有任意日期数据
    any_dates_query = "SELECT COUNT(*) as count FROM project_tasks WHERE planned_start_date IS NOT NULL OR planned_end_date IS NOT NULL"
    any_dates_result = execute_query(any_dates_query)
    print('具有任意日期的记录数:', any_dates_result)
    
except Exception as e:
    print(f"查询出错: {e}")
    import traceback
    traceback.print_exc()