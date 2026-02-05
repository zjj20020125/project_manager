"""
数据验证工具模块
提供数据校验和验证功能
"""

from typing import List, Dict, Any, Union, Optional
from datetime import datetime, date
import re

class DataValidator:
    """数据验证器类"""
    
    @staticmethod
    def validate_project_name(project_name: str) -> bool:
        """验证项目名称"""
        if not project_name or not isinstance(project_name, str):
            return False
        return len(project_name.strip()) > 0
    
    @staticmethod
    def validate_task_name(task_name: str) -> bool:
        """验证任务名称"""
        if not task_name or not isinstance(task_name, str):
            return False
        return len(task_name.strip()) > 0
    
    @staticmethod
    def validate_date_range(start_date: Union[date, datetime, str], 
                          end_date: Union[date, datetime, str]) -> bool:
        """验证日期范围的有效性"""
        if not start_date or not end_date:
            return False
        
        try:
            # 转换为date对象进行比较
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            elif isinstance(start_date, datetime):
                start_date = start_date.date()
                
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            elif isinstance(end_date, datetime):
                end_date = end_date.date()
            
            return start_date <= end_date
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_progress(progress: Union[float, int, str]) -> bool:
        """验证进度值（0-100之间）"""
        try:
            if isinstance(progress, str):
                progress = float(progress.replace('%', ''))
            
            progress_float = float(progress)
            return 0 <= progress_float <= 100
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_wbs_code(wbs_code: str) -> bool:
        """验证WBS编码格式"""
        if not wbs_code or not isinstance(wbs_code, str):
            return False
        
        # WBS编码应该是数字或数字.数字的格式
        pattern = r'^\d+(\.\d+)*$'
        return bool(re.match(pattern, wbs_code.strip()))
    
    @staticmethod
    def validate_task_status(status: str) -> bool:
        """验证任务状态值"""
        if not status or not isinstance(status, str):
            return False
        
        valid_statuses = ['未开始', '进行中', '已完成', '已验收', '异常', '延期完成', '完成']
        return status.strip() in valid_statuses
    
    @staticmethod
    def validate_person_name(name: str) -> bool:
        """验证人员姓名"""
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        # 姓名不应该包含明显的非法字符
        illegal_patterns = [r'[0-9]', r'[^\u4e00-\u9fff\u0041-\u005a\u0061-\u007a\s\-\.]']
        
        for pattern in illegal_patterns:
            if re.search(pattern, name):
                return False
        
        return len(name) > 0
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证电话号码格式"""
        if not phone or not isinstance(phone, str):
            return False
        
        # 支持多种电话格式
        patterns = [
            r'^1[3-9]\d{9}$',  # 中国手机号
            r'^\d{3,4}-\d{7,8}$',  # 固话格式 xxx-xxxxxxx
            r'^\d{10,11}$'  # 纯数字格式
        ]
        
        phone_clean = phone.strip().replace('-', '').replace(' ', '')
        return any(bool(re.match(pattern, phone_clean)) for pattern in patterns)

class DatabaseValidator:
    """数据库相关验证器"""
    
    @staticmethod
    def validate_table_exists(table_name: str, execute_query_func) -> bool:
        """验证表是否存在"""
        try:
            check_sql = f"SHOW TABLES LIKE '{table_name}'"
            result = execute_query_func(check_sql)
            return result is not None
        except Exception:
            return False
    
    @staticmethod
    def validate_columns_exist(table_name: str, required_columns: List[str], 
                             execute_query_func) -> List[str]:
        """验证必需列是否存在，返回缺失的列"""
        try:
            describe_sql = f"DESCRIBE {table_name}"
            columns_result = execute_query_func(describe_sql, fetch_all=True)
            if not columns_result:
                return required_columns
            
            existing_columns = [col['Field'] for col in columns_result if 'Field' in col]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            return missing_columns
        except Exception:
            return required_columns

class FileValidator:
    """文件相关验证器"""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """验证文件扩展名"""
        if not filename or not isinstance(filename, str):
            return False
        
        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return file_extension in [ext.lower().lstrip('.') for ext in allowed_extensions]
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
        """验证文件大小（默认10MB限制）"""
        if not isinstance(file_size, int) or file_size < 0:
            return False
        
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def validate_excel_file(filename: str, file_size: int) -> tuple:
        """验证Excel文件"""
        allowed_extensions = ['.xlsx', '.xls']
        extension_valid = FileValidator.validate_file_extension(filename, allowed_extensions)
        size_valid = FileValidator.validate_file_size(file_size, 50)  # Excel文件最大50MB
        
        errors = []
        if not extension_valid:
            errors.append("文件格式不支持，请上传.xlsx或.xls文件")
        if not size_valid:
            errors.append("文件过大，请上传小于50MB的文件")
            
        return len(errors) == 0, errors

def validate_api_request_data(data: Dict, required_fields: List[str]) -> tuple:
    """验证API请求数据"""
    errors = []
    
    # 检查必需字段
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"缺少必需字段: {field}")
        elif isinstance(data[field], str) and not data[field].strip():
            errors.append(f"字段 {field} 不能为空")
    
    return len(errors) == 0, errors

def sanitize_input(input_data: Any, data_type: type = str) -> Any:
    """清理输入数据"""
    if input_data is None:
        return None
    
    if data_type == str:
        if isinstance(input_data, str):
            return input_data.strip()
        else:
            return str(input_data).strip()
    elif data_type == int:
        try:
            return int(input_data)
        except (ValueError, TypeError):
            return None
    elif data_type == float:
        try:
            return float(input_data)
        except (ValueError, TypeError):
            return None
    else:
        return input_data