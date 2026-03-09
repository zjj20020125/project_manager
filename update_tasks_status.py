# -*- coding: utf-8 -*-
"""
批量更新子任务状态脚本
根据新的状态判断逻辑，更新数据库中所有子任务的任务状态
"""

import mysql.connector
from datetime import datetime, date

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "zjj520111314",
    "database": "jgj-project",
    "charset": "utf8mb4"
}

def connect_to_database():
    """连接到数据库"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"数据库连接失败：{e}")
        return None

def determine_task_status(planned_start, planned_end, actual_start, actual_end, lag_days):
    """
    根据新标准判定子任务状态 - 细化状态分类
    
    状态判断的核心逻辑：
    1. 已完成的任务：实际开始和结束时间都有数据
       - 按时完成：实际时间完全在计划时间范围内
       - 延期完成：实际结束时间超过计划结束时间
       - 延期完成：实际开始时间和实际完成时间都晚于计划时间
       - 完成：特殊情况（其他完成情况）
    
    2. 进行中的任务：只有实际开始时间，没有实际结束时间
       - 进行中：当前日期在计划时间范围内
       - 异常：当前日期超过计划结束时间
    
    3. 未启动的任务：实际开始和结束时间都没有数据
       - 未开始：当前日期在计划开始时间之前
       - 异常：当前日期在计划时间范围内或之后
    """
    current_date = datetime.now().date()
    
    # 情况 1：已完成的任务（实际开始和结束时间都有数据）
    if actual_start is not None and actual_end is not None:
        # 按时完成：实际时间完全在计划时间范围内
        if (planned_start and planned_end and 
            planned_start <= actual_start <= planned_end and 
            planned_start <= actual_end <= planned_end):
            return "按时完成"
            
        # 延期完成：实际结束时间超过计划结束时间
        elif planned_end and actual_end > planned_end:
            return "延期完成"
            
        # 延期完成：实际开始时间和实际完成时间都晚于计划时间
        elif (planned_start and planned_end and 
              actual_start > planned_start and actual_end > planned_end):
            return "延期完成"
            
        # 完成：其他特殊情况
        else:
            return "完成"
    
    # 情况 2：进行中的任务（只有实际开始时间，没有实际结束时间）
    elif actual_start is not None and actual_end is None:
        # 如果既有实际开始时间又有计划时间
        if planned_start and planned_end:
            # 如果实际开始时间在计划时间范围内
            if planned_start <= actual_start <= planned_end:
                # 再检查当前日期是否已经超过计划结束时间
                if current_date > planned_end:
                    return "异常"  # 超期进行中，标记为异常
                else:
                    return "进行中"
            
            # 如果实际开始时间早于计划开始时间
            elif actual_start < planned_start:
                # 检查当前日期是否已经超过计划结束时间
                if current_date > planned_end:
                    return "异常"
                else:
                    return "进行中"
            
            # 如果实际开始时间晚于计划结束时间
            elif actual_start > planned_end:
                return "异常"
        
        # 如果没有计划时间，但有实际开始时间，则认为是进行中
        elif actual_start:
            return "进行中"
        
        # 默认情况
        else:
            return "进行中"
    
    # 情况 3：未启动的任务（实际开始和结束时间都没有数据）
    elif actual_start is None and actual_end is None:
        # 未开始：当前日期在计划开始时间之前
        if planned_start and current_date < planned_start:
            return "未开始"
        
        # 异常：当前日期在计划时间范围内（应该已开始但没开始）
        # 或当前日期超过计划结束时间（严重滞后）
        elif planned_start and planned_end:
            if planned_start <= current_date <= planned_end or current_date > planned_end:
                return "异常"
        
        # 默认情况
        else:
            return "未开始"
    
    # 其他异常情况
    else:
        return "异常"

def update_all_tasks_status():
    """批量更新所有子任务的状态"""
    connection = connect_to_database()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # 查询所有子任务
        select_sql = """
        SELECT 
            task_id, project_name, task_name, wbs_code,
            planned_start_date, planned_end_date, 
            actual_start_date, actual_end_date,
            progress, task_owner, task_status
        FROM project_tasks
        ORDER BY project_name, wbs_code
        """
        
        cursor.execute(select_sql)
        tasks = cursor.fetchall()
        
        print(f"共找到 {len(tasks)} 条子任务")
        print("=" * 80)
        
        updated_count = 0
        unchanged_count = 0
        
        for task in tasks:
            task_id = task[0]
            project_name = task[1]
            task_name = task[2]
            wbs_code = task[3]
            planned_start = task[4]
            planned_end = task[5]
            actual_start = task[6]
            actual_end = task[7]
            progress = task[8]
            task_owner = task[9]
            old_status = task[10]
            
            # 根据新的逻辑计算状态
            new_status = determine_task_status(
                planned_start, planned_end, 
                actual_start, actual_end, 
                None  # lag_days 设为 None
            )
            
            # 如果状态发生变化，则更新
            if old_status != new_status:
                update_sql = """
                UPDATE project_tasks 
                SET task_status = %s
                WHERE task_id = %s
                """
                cursor.execute(update_sql, (new_status, task_id))
                
                print(f"✓ 更新：{project_name} - {task_name}")
                print(f"  WBS: {wbs_code}")
                print(f"  状态：{old_status} → {new_status}")
                print(f"  计划：{planned_start} ~ {planned_end}")
                print(f"  实际：{actual_start} ~ {actual_end}")
                print()
                
                updated_count += 1
            else:
                unchanged_count += 1
        
        connection.commit()
        
        print("=" * 80)
        print(f"更新完成！")
        print(f"  总任务数：{len(tasks)}")
        print(f"  更新数量：{updated_count}")
        print(f"  未变数量：{unchanged_count}")
        print()
        
        # 统计各状态的数量
        status_sql = """
        SELECT 
            task_status,
            COUNT(*) as count
        FROM project_tasks
        GROUP BY task_status
        ORDER BY count DESC
        """
        cursor.execute(status_sql)
        status_stats = cursor.fetchall()
        
        print("状态分布统计：")
        for status_row in status_stats:
            print(f"  {status_row[0]}: {status_row[1]} 条")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"更新任务状态时出错：{e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("=" * 80)
    print("开始批量更新子任务状态...")
    print(f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    success = update_all_tasks_status()
    
    if success:
        print("\n✓ 所有子任务状态更新完成！")
    else:
        print("\n✗ 更新过程中出现错误")
