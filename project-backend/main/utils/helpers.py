"""
通用辅助函数模块
提供项目中常用的工具函数和辅助方法
"""

from typing import List, Dict, Any, Union
from datetime import datetime, date
import re
import json

def format_date(date_value: Union[datetime, date, str, None]) -> str:
    """格式化日期值为字符串"""
    if date_value is None:
        return ""
    
    if isinstance(date_value, (datetime, date)):
        return str(date_value)
    
    if isinstance(date_value, str):
        return date_value
    
    return str(date_value)

def format_decimal(decimal_value: Any) -> str:
    """格式化十进制数值为字符串，去除末尾的0"""
    if decimal_value is None:
        return "0"
    
    if hasattr(decimal_value, 'quantize'):  # Decimal类型
        decimal_str = str(float(decimal_value))
    else:
        decimal_str = str(decimal_value) if decimal_value is not None else "0"
    
    # 清理多余的0
    return decimal_str.rstrip('0').rstrip('.') if '.' in decimal_str else decimal_str

def clean_chinese_text(text: str) -> str:
    """清理中文文本，去除全角空格等特殊字符"""
    if not text:
        return ""
    
    # 去除全角空格和普通空格
    cleaned = text.strip().replace('\u3000', '').replace(' ', '')
    return cleaned

def split_multiple_names(name_string: str, separators: List[str] = None) -> List[str]:
    """
    分割包含多个姓名的字符串
    支持多种分隔符：逗号、分号、顿号等
    """
    if not name_string:
        return []
    
    if separators is None:
        separators = [',', '，', ';', '；', '/', '、', '+']
    
    # 尝试分割多个姓名
    names = [name_string]
    for sep in separators:
        if sep in name_string:
            names = name_string.split(sep)
            break
    
    # 清理每个姓名
    cleaned_names = []
    for name in names:
        clean_name = name.strip()
        if clean_name and clean_name not in ['nan', 'NaN', 'null', 'NULL', '<NULL>', 'None']:
            cleaned_names.append(clean_name)
    
    return cleaned_names

def validate_task_status(planned_start: date = None, planned_end: date = None,
                        actual_start: date = None, actual_end: date = None,
                        lag_days: float = None) -> str:
    """
    根据条件确定任务状态
    完成：滞后度为0，或实际时间早于等于计划时间
    延期完成：实际时间晚于计划时间
    异常：实际开始或完成时间为空
    进行中：当前日期在计划期间内，且只有实际开始时间
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
        # 检查是否为延期完成
        if ((planned_start and actual_start > planned_start) or 
            (planned_end and actual_end > planned_end)):
            return "延期完成"
        # 检查是否为完成
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
    
    # 检查进行中
    if (planned_start and planned_end and 
        planned_start <= current_date <= planned_end and 
        actual_start is not None and actual_end is None):
        return "进行中"
    
    # 默认为异常
    return "异常"

def extract_column_names(columns_result: List[Dict]) -> List[str]:
    """从数据库列描述结果中提取列名"""
    return [col['Field'] for col in columns_result if 'Field' in col]

def check_required_columns(column_names: List[str], required_columns: List[str]) -> List[str]:
    """检查必需列是否存在，返回缺失的列名"""
    return [col for col in required_columns if col not in column_names]

def safe_get_dict_value(dictionary: Dict, key: str, default=None):
    """安全地从字典中获取值"""
    if not dictionary or not isinstance(dictionary, dict):
        return default
    return dictionary.get(key, default)

def convert_to_serializable(obj: Any) -> Any:
    """将对象转换为可序列化的格式"""
    if isinstance(obj, (datetime, date)):
        return str(obj)
    elif hasattr(obj, 'quantize'):  # Decimal类型
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """合并两个字典"""
    result = dict1.copy()
    result.update(dict2)
    return result

def filter_dict_by_keys(dictionary: Dict, keys: List[str]) -> Dict:
    """根据键列表过滤字典"""
    return {k: v for k, v in dictionary.items() if k in keys}

def sort_dict_list(dict_list: List[Dict], sort_key: str, reverse: bool = False) -> List[Dict]:
    """对字典列表按指定键排序"""
    return sorted(dict_list, key=lambda x: x.get(sort_key, 0), reverse=reverse)

def paginate_list(items: List[Any], page: int, limit: int) -> tuple:
    """对列表进行分页"""
    total = len(items)
    offset = (page - 1) * limit
    paginated_items = items[offset:offset + limit]
    return paginated_items, total

def is_valid_date_string(date_string: str) -> bool:
    """检查字符串是否为有效的日期格式"""
    if not date_string:
        return False
    
    try:
        # 尝试解析常见日期格式
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        try:
            datetime.strptime(date_string, '%Y/%m/%d')
            return True
        except ValueError:
            return False

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    # 移除或替换非法字符
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(illegal_chars, '_', filename)
    # 移除首尾的点和空格
    sanitized = sanitized.strip('. ')
    return sanitized if sanitized else "unnamed_file"

def calculate_completion_rate(completed: int, total: int) -> float:
    """计算完成率"""
    if total == 0:
        return 0.0
    return round((completed / total) * 100, 2)

def get_color_palette() -> List[str]:
    """获取预定义的颜色调色板"""
    return [
        '#3498db', '#2ecc71', '#e74c3c', '#9b59b6', 
        '#f1c40f', '#1abc9c', '#d35400', '#34495e', 
        '#7f8c8d', '#e67e22', '#3498db', '#2ecc71'
    ]

def assign_colors_to_items(items: List[str]) -> Dict[str, str]:
    """为项目列表分配颜色"""
    color_palette = get_color_palette()
    color_mapping = {}
    
    for i, item in enumerate(items):
        color_mapping[item] = color_palette[i % len(color_palette)]
    
    return color_mapping