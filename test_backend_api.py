#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试后端API接口，特别关注传递各种状态参数时的返回数据
"""

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

def test_database_connection():
    """测试数据库连接和表状态"""
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
                
                # 获取所有状态及其数量
                cursor.execute("SELECT task_status, COUNT(*) as count FROM project_tasks GROUP BY task_status ORDER BY count DESC")
                all_statuses = cursor.fetchall()
                print("  所有任务状态及数量:")
                for status in all_statuses:
                    print(f"    - '{status['task_status']}': {status['count']} 条")
                
                # 测试查询特定状态的数据
                print("\n测试查询特定状态的数据:")
                test_statuses = ['异常', '完成', '延期完成']
                for test_status in test_statuses:
                    cursor.execute("SELECT * FROM project_tasks WHERE task_status = %s LIMIT 3", (test_status,))
                    records = cursor.fetchall()
                    print(f"  状态为 '{test_status}' 的前3条记录:")
                    for i, record in enumerate(records):
                        print(f"    {i+1}. 任务名称: {record.get('task_name', 'N/A')}, 项目名称: {record.get('project_name', 'N/A')}, 负责人: {record.get('task_owner', 'N/A')}")
                    print(f"    总共有 {len(records)} 条记录符合状态 '{test_status}'")
            else:
                print("✗ project_tasks表不存在")
            
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

def test_api_with_different_params():
    """测试API使用不同参数时的行为"""
    print("\n" + "="*60)
    print("API测试 - 使用不同参数查询任务数据")
    print("="*60)
    
    # 导入FastAPI应用
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'project-backend'))
        # 使用exec执行文件来获取app对象
        with open('project-backend/main/main.py', 'r', encoding='utf-8') as f:
            code = f.read()
        local_vars = {}
        exec(code, {}, local_vars)
        app = local_vars.get('app')
        if app:
            print("成功导入FastAPI应用")
        else:
            print("未能获取到app对象")
    except Exception as e:
        print(f"导入FastAPI应用失败: {e}")
        print("将直接测试数据库查询逻辑")

def simulate_api_logic(status_param):
    """模拟API中处理状态参数的逻辑"""
    print(f"\n模拟API处理状态参数: '{status_param}'")
    
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # 首先检查数据库中存在的所有状态
        cursor.execute("SELECT DISTINCT task_status FROM project_tasks WHERE task_status IS NOT NULL")
        db_statuses = [row['task_status'] for row in cursor.fetchall()]
        print(f"数据库中所有任务状态: {db_statuses}")
        
        # 模拟API中的逻辑
        status_conditions = [status_param]
        
        # 如果传入的状态在数据库中存在，就单独查询
        if status_param in db_statuses:
            status_conditions = [status_param]
            print(f"状态 '{status_param}' 在数据库中存在，直接查询")
        else:
            # 否则尝试匹配常见变体
            print(f"状态 '{status_param}' 在数据库中不存在，尝试匹配常见变体...")
            if status_param in ['未开始', 'not_started']:
                variants = ['未开始', 'Not Started', 'not started', '未開始', 'Pending', '待开始']
            elif status_param in ['进行中', 'ongoing']:
                variants = ['进行中', 'Ongoing', 'in progress', '進行中', 'In Progress', '执行中', 'Running']
            elif status_param in ['已完成', 'completed']:
                variants = ['完成', 'Completed', 'completed', '已完成', 'Finished', 'Done']
            elif status_param in ['已验收', 'accepted']:
                variants = ['已验收', 'Accepted', 'accepted', '已驗收', '验收', '验收通过']
            else:
                variants = [status_param]  # 直接使用传入的状态
            
            # 找出在数据库中存在的变体
            found_variants = [v for v in variants if v in db_statuses]
            if found_variants:
                status_conditions = found_variants
                print(f"找到匹配的变体: {found_variants}")
            else:
                print(f"未找到匹配的变体，仍将尝试查询状态 '{status_param}'")
        
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
        LIMIT 10
        """
        
        cursor.execute(task_sql, tuple(status_conditions))
        tasks = cursor.fetchall()
        
        print(f"查询状态: {status_conditions}, 匹配到 {len(tasks)} 个任务")
        if tasks:
            print("前3个任务的详细信息:")
            for i, task in enumerate(tasks[:3]):
                print(f"  {i+1}. 任务名称: {task.get('task_name', 'N/A')}")
                print(f"      项目名称: {task.get('project_name', 'N/A')}")
                print(f"      任务负责人: {task.get('task_owner', 'N/A')}")
                print(f"      任务状态: {task.get('task_status', 'N/A')}")
                print(f"      计划开始时间: {task.get('planned_start_date', 'N/A')}")
                print(f"      计划结束时间: {task.get('planned_end_date', 'N/A')}")
                print(f"      进度: {task.get('progress', 'N/A')}")
                print()
        else:
            print("未找到匹配的任务数据")
        
        cursor.close()
        
    except Exception as e:
        print(f"查询过程中发生错误: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

def main():
    print("开始测试后端API与数据库交互...")
    
    # 首先测试数据库连接
    test_database_connection()
    
    # 测试不同状态参数的API逻辑
    test_params = ['异常', '完成', '延期完成', '未开始', '进行中', '已验收', 'nonexistent_status']
    for param in test_params:
        simulate_api_logic(param)

if __name__ == "__main__":
    main()