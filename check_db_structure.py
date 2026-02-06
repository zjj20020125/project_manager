import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'project-backend'))

from database.database import execute_query

print("=== 数据库表结构检查 ===")

# 显示所有表
tables = execute_query('SHOW TABLES', fetch_all=True)
print("\n数据库中的表:")
for table in tables:
    table_name = list(table.values())[0]
    print(f"  {table_name}")

# 检查每个表的结构
for table in tables:
    table_name = list(table.values())[0]
    print(f"\n--- {table_name} 表结构 ---")
    columns = execute_query(f'DESCRIBE {table_name}', fetch_all=True)
    if columns:
        for col in columns:
            print(f"  {col['Field']} {col['Type']} {col.get('Null', '')} {col.get('Key', '')}")

# 检查projects表的数据
print("\n=== Projects表数据样本 ===")
projects_sample = execute_query('SELECT * FROM projects LIMIT 3', fetch_all=True)
if projects_sample:
    for i, project in enumerate(projects_sample, 1):
        print(f"\n项目 {i}:")
        for key, value in project.items():
            print(f"  {key}: {value}")
else:
    print("没有找到项目数据")