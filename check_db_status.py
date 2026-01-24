#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到模块搜索路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project-backend'))

try:
    import config.config
    DB_CONFIG = config.config.DATABASE_CONFIG
    print("成功导入数据库配置")
    print(f"数据库配置: {DB_CONFIG}")
except ImportError as e:
    print(f"导入数据库配置失败: {e}")
    # 使用默认配置
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "zjj520111314",
        "database": "jgj-project",
        "charset": "utf8mb4"
    }

try:
    import mysql.connector
    print("成功导入mysql.connector")
except ImportError as e:
    print(f"导入mysql.connector失败: {e}")
    exit(1)

def check_database():
    """检查数据库连接和表状态"""
    connection = None
    try:
        print("\n尝试连接数据库...")
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✓ 数据库连接成功!")
            cursor = connection.cursor(dictionary=True)
            
            # 检查project_tasks表是否存在及是否有数据
            print("\n检查project_tasks表...")
            cursor.execute("SHOW TABLES LIKE 'project_tasks'")
            result = cursor.fetchone()
            if result:
                print("✓ project_tasks表存在")
                cursor.execute("SELECT COUNT(*) as count FROM project_tasks")
                count_result = cursor.fetchone()
                print(f"  project_tasks表中有 {count_result['count']} 条记录")
                
                if count_result['count'] > 0:
                    # 获取一些示例数据查看状态值
                    cursor.execute("SELECT DISTINCT task_status FROM project_tasks LIMIT 10")
                    statuses = cursor.fetchall()
                    print("  数据库中的任务状态:")
                    for status in statuses:
                        print(f"    - '{status['task_status']}'")
                    
                    # 获取所有状态及其数量
                    cursor.execute("SELECT task_status, COUNT(*) as count FROM project_tasks GROUP BY task_status ORDER BY count DESC")
                    all_statuses = cursor.fetchall()
                    print("  所有任务状态及数量:")
                    for status in all_statuses:
                        print(f"    - '{status['task_status']}': {status['count']} 条")
            else:
                print("✗ project_tasks表不存在")
            
            # 检查projects表
            print("\n检查projects表...")
            cursor.execute("SHOW TABLES LIKE 'projects'")
            result = cursor.fetchone()
            if result:
                print("✓ projects表存在")
                cursor.execute("SELECT COUNT(*) as count FROM projects")
                count_result = cursor.fetchone()
                print(f"  projects表中有 {count_result['count']} 条记录")
            else:
                print("✗ projects表不存在")
            
            cursor.close()
        else:
            print("✗ 数据库连接失败")
            
    except mysql.connector.Error as e:
        print(f"✗ 数据库操作错误: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    check_database()