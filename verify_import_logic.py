#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证导入处理逻辑是否使用了新的状态判断
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'datadeal'))

# 模拟导入处理流程
def simulate_import_process():
    """模拟导入处理流程"""
    print("=== 模拟导入处理流程 ===")
    
    # 模拟从Excel读取的数据
    mock_excel_data = [
        {
            '任务名称': '设计阶段',
            '计划开始时间': '2024-01-01',
            '计划结束时间': '2024-03-31',
            '实际开始时间': '2024-01-15',
            '实际结束时间': '2024-03-20',  # 按期完成
            '状态': ''  # 空状态，需要计算
        },
        {
            '任务名称': '开发阶段',
            '计划开始时间': '2024-04-01',
            '计划结束时间': '2024-08-31',
            '实际开始时间': '2024-04-15',
            '实际结束时间': '2024-09-15',  # 延期完成
            '状态': ''  # 空状态，需要计算
        },
        {
            '任务名称': '测试阶段',
            '计划开始时间': '2024-09-01',
            '计划结束时间': '2024-10-31',
            '实际开始时间': '2024-09-10',
            '实际结束时间': '',  # 进行中
            '状态': ''  # 空状态，需要计算
        },
        {
            '任务名称': '部署阶段',
            '计划开始时间': '2024-11-01',
            '计划结束时间': '2024-11-30',
            '实际开始时间': '',
            '实际结束时间': '',
            '状态': ''  # 空状态，需要计算
        }
    ]
    
    # 导入必要的函数
    from simple_datadeal import determine_task_status, extract_date_from_cell
    
    print("处理每个任务的状态判断：")
    print("-" * 50)
    
    for i, task in enumerate(mock_excel_data, 1):
        print(f"任务 {i}: {task['任务名称']}")
        print(f"  计划时间: {task['计划开始时间']} ~ {task['计划结束时间']}")
        print(f"  实际时间: {task['实际开始时间']} ~ {task['实际结束时间']}")
        print(f"  Excel状态: '{task['状态']}'")
        
        # 提取日期
        planned_start = extract_date_from_cell(task['计划开始时间'])
        planned_end = extract_date_from_cell(task['计划结束时间'])
        actual_start = extract_date_from_cell(task['实际开始时间']) if task['实际开始时间'] else None
        actual_end = extract_date_from_cell(task['实际结束时间']) if task['实际结束时间'] else None
        
        print(f"  解析后 - 计划开始: {planned_start}, 计划结束: {planned_end}")
        print(f"  解析后 - 实际开始: {actual_start}, 实际结束: {actual_end}")
        
        # 判断状态
        if not task['状态'] or task['状态'].strip() == '':
            calculated_status = determine_task_status(
                planned_start, planned_end, actual_start, actual_end, None
            )
            print(f"  ✓ 使用新逻辑计算状态: {calculated_status}")
        else:
            calculated_status = task['状态']
            print(f"  ○ 使用Excel中的状态: {calculated_status}")
        
        print()
    
    print("=== 导入处理验证完成 ===")

if __name__ == "__main__":
    simulate_import_process()