# -*- coding: utf-8 -*-
import mysql.connector
import sys
sys.path.append('..')

try:
    import config.config
    DB_CONFIG = config.config.DATABASE_CONFIG
except ImportError:
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "zjj520111314",
        "database": "jgj-project",
        "charset": "utf8mb4"
    }

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # 检查project_tasks表结构
    cursor.execute('DESCRIBE project_tasks;')
    columns = cursor.fetchall()
    print('project_tasks表结构:')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')

    # 检查是否有task_status列
    has_task_status = any(col[0] == 'task_status' for col in columns)
    print(f'\ntask_status列存在: {has_task_status}')

    # 检查一些示例数据
    cursor.execute('SELECT task_name, task_status FROM project_tasks LIMIT 10;')
    sample_data = cursor.fetchall()
    print(f'\n示例数据 (共{len(sample_data)}条):')
    for row in sample_data:
        print(f'  任务名: {row[0]}, 状态: {row[1]}')

    # 统计各种状态的数量
    cursor.execute('SELECT task_status, COUNT(*) FROM project_tasks GROUP BY task_status;')
    status_counts = cursor.fetchall()
    print(f'\n状态统计:')
    for status, count in status_counts:
        print(f'  {status}: {count}个')

    cursor.close()
    connection.close()
except Exception as e:
    print(f"数据库查询出错: {e}")