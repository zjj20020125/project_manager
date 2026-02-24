"""
公共工具函数模块
包含项目中通用的辅助函数和工具方法
"""

from datetime import datetime
import re

def determine_task_status_import(planned_start, planned_end, actual_start, actual_end, lag_days):
    """
    根据新标准判定子任务状态 - 与simple_datadeal.py保持一致
    
    状态判断的核心逻辑：
    1. 已完成的任务：实际开始和结束时间都有数据
       - 按期完成：实际时间在计划时间内
       - 延期完成：实际结束时间超过计划结束时间
       - 其他完成：其他情况统一标记为"完成"
    
    2. 进行中的任务：只有实际开始时间，没有实际结束时间
       - 进行中：当前日期在计划时间范围内
       - 未开始：当前日期在计划开始时间之前
       - 异常：当前日期超过计划结束时间
    
    3. 未启动的任务：实际开始和结束时间都没有数据
       - 未开始：当前日期在计划开始时间之前
       - 异常：当前日期在计划时间范围内（应该已开始但没开始）
       - 严重异常：当前日期超过计划结束时间（严重滞后）
    """
    current_date = datetime.now().date()
    
    # 情况1：已完成的任务（实际开始和结束时间都有数据）
    if actual_start is not None and actual_end is not None:
        # 检查是否按期完成
        if (planned_start and planned_end and 
            planned_start <= actual_start <= planned_end and 
            planned_start <= actual_end <= planned_end):
            return "完成"  # 按期完成
        
        # 检查是否延期完成
        elif planned_end and actual_end > planned_end:
            return "延期完成"
        
        # 其他完成情况
        else:
            return "完成"
    
    # 情况2：进行中的任务（只有实际开始时间，没有实际结束时间）
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
    
    # 情况3：未启动的任务（实际开始和结束时间都没有数据）
    elif actual_start is None and actual_end is None:
        # 未开始：当前日期在计划开始时间之前
        if planned_start and current_date < planned_start:
            return "未开始"
        
        # 异常：当前日期在计划时间范围内（应该已开始但没开始）
        elif (planned_start and planned_end and 
              planned_start <= current_date <= planned_end):
            return "异常"
        
        # 严重异常：当前日期超过计划结束时间（严重滞后）
        elif planned_end and current_date > planned_end:
            return "异常"  # 或者可以返回"严重异常"如果需要区分
        
        # 默认情况
        else:
            return "未开始"
    
    # 其他异常情况
    else:
        return "异常"