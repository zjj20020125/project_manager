# -*- coding: utf-8 -*-
import mysql.connector

def clear_tasks_table():
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
        print(f'成功删除 {cursor.rowcount} 条任务记录')
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f'清空任务表时出错: {e}')
        return False

def main():
    print("开始清空project_tasks表...")
    if clear_tasks_table():
        print("表已清空，现在开始重新运行数据导入...")
        
        # 导入并运行数据导入功能
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from simple_datadeal import main as import_main
        import_main()
        
        print("\n数据导入完成，正在检查状态数据...")
        
        # 检查导入的数据状态
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
            cursor.execute('SELECT task_name, task_status FROM project_tasks LIMIT 5;')
            sample_data = cursor.fetchall()
            print(f'\n示例数据 (前5条):')
            for task_name, status in sample_data:
                print(f'  任务名: {task_name}, 状态: {status}')
            
            cursor.close()
            connection.close()
        except Exception as e:
            print(f'检查数据时出错: {e}')
    else:
        print("清空表失败，停止执行")

if __name__ == "__main__":
    main()