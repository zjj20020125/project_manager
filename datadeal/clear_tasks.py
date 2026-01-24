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

    # 清空project_tasks表中的数据
    cursor.execute('DELETE FROM project_tasks;')
    connection.commit()
    print(f'已清空project_tasks表，影响了 {cursor.rowcount} 行')

    cursor.close()
    connection.close()
    print('数据库连接已关闭')
except Exception as e:
    print(f"数据库操作出错: {e}")