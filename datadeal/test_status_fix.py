# -*- coding: utf-8 -*-
import mysql.connector
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clear_project_tasks():
    """清空project_tasks表"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='zjj520111314',
            database='jgj-project',
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # 清空project_tasks表
        cursor.execute('DELETE FROM project_tasks;')
        connection.commit()
        rows_deleted = cursor.rowcount
        print(f'成功删除 {rows_deleted} 条任务记录')
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f'清空任务表时出错: {e}')
        return False

def test_determine_task_status():
    """测试状态判断函数"""
    from simple_datadeal import determine_task_status
    from datetime import datetime, date
    
    # 测试不同情况
    print("测试状态判断函数:")
    
    # 测试完成状态
    status1 = determine_task_status(
        date(2025, 12, 1),  # planned_start
        date(2025, 12, 10), # planned_end
        date(2025, 11, 28), # actual_start
        date(2025, 12, 8),  # actual_end
        None
    )
    print(f"  提前完成: {status1}")
    
    # 测试延期完成
    status2 = determine_task_status(
        date(2025, 12, 1),  # planned_start
        date(2025, 12, 10), # planned_end
        date(2025, 12, 2),  # actual_start
        date(2025, 12, 15), # actual_end
        None
    )
    print(f"  延期完成: {status2}")
    
    # 测试进行中
    status3 = determine_task_status(
        date(2025, 12, 1),  # planned_start
        date(2025, 12, 10), # planned_end
        date(2025, 12, 2),  # actual_start
        None,                # actual_end
        None
    )
    print(f"  进行中: {status3}")
    
    # 测试异常
    status4 = determine_task_status(
        date(2025, 12, 1),  # planned_start
        date(2025, 12, 10), # planned_end
        None,                # actual_start
        None,                # actual_end
        None
    )
    print(f"  异常: {status4}")

def run_data_import():
    """运行数据导入"""
    print("\n开始运行数据导入...")
    try:
        from simple_datadeal import main
        main()
        print("数据导入完成")
    except Exception as e:
        print(f"数据导入出错: {e}")

def check_status_data():
    """检查状态数据"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='zjj520111314',
            database='jgj-project',
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # 统计各种状态的数量
        cursor.execute('SELECT task_status, COUNT(*) FROM project_tasks GROUP BY task_status;')
        status_counts = cursor.fetchall()
        print(f'\n状态统计:')
        for status, count in status_counts:
            print(f'  {status}: {count}个')
        
        # 显示一些示例数据
        cursor.execute('SELECT task_name, task_status FROM project_tasks LIMIT 10;')
        sample_data = cursor.fetchall()
        print(f'\n示例数据 (前10条):')
        for task_name, status in sample_data:
            print(f'  任务名: {task_name}, 状态: {status}')
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f'检查数据时出错: {e}')

def main():
    print("开始测试状态判断修复...")
    
    # 测试状态判断函数
    test_determine_task_status()
    
    # 清空现有数据
    print("\n正在清空现有任务数据...")
    if not clear_project_tasks():
        print("清空数据失败，停止测试")
        return
    
    # 运行数据导入
    run_data_import()
    
    # 检查导入的数据状态
    print("\n正在检查导入的状态数据...")
    check_status_data()

if __name__ == "__main__":
    main()