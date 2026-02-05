"""
公共工具函数模块
包含项目中通用的辅助函数和工具方法
"""

from datetime import datetime
import re

def determine_task_status_import(planned_start, planned_end, actual_start, actual_end, lag_days):
    """
    根据条件确定任务状态 - 与simple_datadeal.py保持一致
    完成：滞后度一列中为0的，或者说实际开始时间，实际完成时间早于或者等于预计开始时间，预计完成时间
    延期完成：实际开始时间，实际完成时间晚于预计开始时间，预计完成时间
    异常：实际开始时间，实际完成时间为空
    进行中：根据实时的日期，处于预计完成时间跟预计开始时间中间，只填写了实际开始时间
    """
    current_date = datetime.now().date()
    
    # 检查异常情况：实际开始时间或实际完成时间为空
    if actual_start is None or actual_end is None:
        if actual_start is None and actual_end is None:
            return "异常"
        elif actual_start is not None and actual_end is None:
            # 如果仅有实际开始时间，检查是否在计划范围内
            if planned_start and planned_end and planned_start <= current_date <= planned_end:
                return "进行中"
            else:
                return "异常"
        elif actual_start is None and actual_end is not None:
            return "异常"
    
    # 如果实际开始和完成时间都存在
    if actual_start and actual_end:
        # 检查是否为延期完成：实际开始时间或实际完成时间晚于预计开始时间或预计完成时间
        if ((planned_start and actual_start > planned_start) or 
            (planned_end and actual_end > planned_end)):
            return "延期完成"
        # 检查是否为完成：实际开始时间完成时间早于或等于预计开始时间和完成时间
        elif ((planned_start and actual_start <= planned_start) and 
              (planned_end and actual_end <= planned_end)):
            return "完成"
        # 如果在计划时间范围内完成
        elif ((planned_start and planned_end) and 
              (planned_start <= actual_start <= planned_end) and 
              (planned_end and actual_end <= planned_end)):
            return "完成"
        else:
            return "延期完成"
    
    # 检查进行中：当前日期在计划开始和结束之间，且只有实际开始时间
    if (planned_start and planned_end and 
        planned_start <= current_date