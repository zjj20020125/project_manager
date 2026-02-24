#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试导入逻辑的状态判断功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'datadeal'))

from simple_datadeal import determine_task_status, analyze_excel_data
from datetime import datetime, date

def test_status_determination():
    """测试状态判断逻辑"""
    print("=== 测试状态判断逻辑 ===")
    
    current_date = datetime.now().date()
    print(f"当前日期: {current_date}")
    
    # 测试用例1: 按期完成的任务
    status1 = determine_task_status(
        planned_start=date(2024, 1, 1),
        planned_end=date(2024, 12, 31),
        actual_start=date(2024, 2, 1),
        actual_end=date(2024, 11, 30),
        lag_days=0
    )
    print(f"测试1 - 按期完成: {status1}")
    
    # 测试用例2: 延期完成的任务
    status2 = determine_task_status(
        planned_start=date(2024, 1, 1),
        planned_end=date(2024, 12, 31),
        actual_start=date(2024, 2, 1),
        actual_end=date(2025, 1, 15),  # 超过计划结束时间
        lag_days=15
    )
    print(f"测试2 - 延期完成: {status2}")
    
    # 测试用例3: 进行中的任务
    status3 = determine_task_status(
        planned_start=date(2024, 1, 1),
        planned_end=date(2024, 12, 31),
        actual_start=date(2024, 6, 1),
        actual_end=None,  # 没有实际结束时间
        lag_days=None
    )
    print(f"测试3 - 进行中: {status3}")
    
    # 测试用例4: 未开始的任务
    status4 = determine_task_status(
        planned_start=date(2025, 1, 1),  # 计划开始时间在未来
        planned_end=date(2025, 12, 31),
        actual_start=None,
        actual_end=None,
        lag_days=None
    )
    print(f"测试4 - 未开始: {status4}")
    
    # 测试用例5: 异常任务（应该开始但没开始）
    status5 = determine_task_status(
        planned_start=date(2024, 1, 1),  # 计划开始时间在过去
        planned_end=date(2024, 12, 31),
        actual_start=None,  # 没有实际开始时间
        actual_end=None,
        lag_days=None
    )
    print(f"测试5 - 异常: {status5}")
    
    print("=== 状态判断测试完成 ===\n")

def test_project_level_status():
    """测试项目级别状态判断"""
    print("=== 测试项目级别状态判断 ===")
    
    # 模拟一些任务数据的时间范围
    test_cases = [
        {
            "name": "已完成项目",
            "planned_starts": [date(2024, 1, 1), date(2024, 2, 1)],
            "planned_ends": [date(2024, 10, 31), date(2024, 11, 30)],
            "actual_starts": [date(2024, 1, 15), date(2024, 2, 15)],
            "actual_ends": [date(2024, 9, 30), date(2024, 10, 31)],  # 都已完成
            "expected": "完成"
        },
        {
            "name": "进行中项目",
            "planned_starts": [date(2024, 1, 1), date(2024, 2, 1)],
            "planned_ends": [date(2026, 12, 31), date(2027, 1, 31)],
            "actual_starts": [date(2024, 1, 15), date(2024, 2, 15)],
            "actual_ends": [None, None],  # 部分任务未完成
            "expected": "进行中"
        },
        {
            "name": "未开始项目",
            "planned_starts": [date(2026, 6, 1), date(2026, 7, 1)],  # 修改为未来时间
            "planned_ends": [date(2027, 6, 1), date(2027, 7, 1)],
            "actual_starts": [None, None],
            "actual_ends": [None, None],
            "expected": "未开始"
        }
    ]
    
    for case in test_cases:
        print(f"测试项目: {case['name']}")
        
        # 过滤掉NaT值
        filtered_planned_starts = [d for d in case['planned_starts'] if d is not None]
        filtered_planned_ends = [d for d in case['planned_ends'] if d is not None]
        filtered_actual_starts = [d for d in case['actual_starts'] if d is not None]
        filtered_actual_ends = [d for d in case['actual_ends'] if d is not None]
        
        # 计算极值
        earliest_planned_start = min(filtered_planned_starts) if filtered_planned_starts else None
        latest_planned_end = max(filtered_planned_ends) if filtered_planned_ends else None
        earliest_actual_start = min(filtered_actual_starts) if filtered_actual_starts else None
        latest_actual_end = max(filtered_actual_ends) if filtered_actual_ends else None
        
        print(f"  计划开始: {earliest_planned_start}")
        print(f"  计划结束: {latest_planned_end}")
        print(f"  实际开始: {earliest_actual_start}")
        print(f"  实际结束: {latest_actual_end}")
        
        # 使用新的状态判断逻辑
        current_date = datetime.now().date()
        print(f"  当前日期: {current_date}")
        
        if latest_actual_end and latest_actual_end < current_date:
            print("  情况1：已完成的任务")
            if latest_planned_end and latest_actual_end > latest_planned_end:
                status = "延期完成"
            else:
                status = "完成"
        elif earliest_actual_start and not latest_actual_end:
            print("  情况2：进行中的任务")
            print(f"    计划开始: {earliest_planned_start}")
            print(f"    计划结束: {latest_planned_end}")
            print(f"    当前日期: {current_date}")
            # 进行中：当前日期在计划时间范围内
            if (earliest_planned_start and latest_planned_end and 
                earliest_planned_start <= current_date <= latest_planned_end):
                status = "进行中"
            # 未开始：当前日期在计划开始时间之前
            elif earliest_planned_start and current_date < earliest_planned_start:
                status = "未开始"
            # 异常：当前日期超过计划结束时间
            elif latest_planned_end and current_date > latest_planned_end:
                status = "异常"
            else:
                status = "进行中"
        elif not earliest_actual_start and not latest_actual_end:
            print("  情况3：未启动的任务")
            print(f"    计划开始: {earliest_planned_start}")
            print(f"    计划结束: {latest_planned_end}")
            print(f"    当前日期: {current_date}")
            # 未开始：当前日期在计划开始时间之前
            if earliest_planned_start and current_date < earliest_planned_start:
                status = "未开始"
            # 异常：当前日期在计划时间范围内（应该已开始但没开始）
            elif (earliest_planned_start and latest_planned_end and 
                  earliest_planned_start <= current_date <= latest_planned_end):
                status = "异常"
            # 严重异常：当前日期超过计划结束时间（严重滞后）
            elif latest_planned_end and current_date > latest_planned_end:
                status = "异常"
            else:
                status = "未开始"
        else:
            status = "异常"
        
        print(f"  最终判定: {status}")
        
        print(f"  判定状态: {status}")
        print(f"  期望状态: {case['expected']}")
        print(f"  结果: {'✓' if status == case['expected'] else '✗'}")
        print()

if __name__ == "__main__":
    test_status_determination()
    test_project_level_status()
    print("所有测试完成！")