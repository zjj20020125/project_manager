# -*- coding: utf-8 -*-
import os
import re
import glob
from datetime import datetime, date
import sys
import json
import mysql.connector

# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入pandas，如果失败则使用xlrd
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    try:
        import xlrd  # 用于读取.xls文件
    except ImportError:
        print("警告: 未安装pandas或xlrd库，将无法读取Excel文件数据")
        xlrd = None

# 从项目配置中获取数据库配置
try:
    import config.config
    DB_CONFIG = config.config.DATABASE_CONFIG
except ImportError:
    # 如果无法导入项目配置，使用默认配置
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
        print(f"数据库连接失败: {e}")
        return None

def get_or_create_project_id(project_name, manager_name, planned_start, planned_end, actual_start, actual_end, status):
    """获取或创建项目ID"""
    connection = connect_to_database()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        # 检查是否已存在相同的项目名称
        check_sql = "SELECT project_id FROM projects WHERE project_name = %s"
        cursor.execute(check_sql, (project_name,))
        existing = cursor.fetchone()
        
        if existing:
            project_id = existing[0]
            print(f"项目 '{project_name}' 已存在，使用现有ID: {project_id}")
        else:
            # 插入项目数据
            insert_sql = """
            INSERT INTO projects (project_name, project_manager, planned_start_date, planned_end_date, 
                                 actual_start_date, actual_end_date, project_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (project_name, manager_name, planned_start, planned_end, actual_start, actual_end, status))
            connection.commit()
            project_id = cursor.lastrowid
            print(f"成功创建项目 '{project_name}'，ID: {project_id}")
        
        return project_id
    except mysql.connector.Error as e:
        print(f"处理项目数据时出错: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def determine_task_status(planned_start, planned_end, actual_start, actual_end, lag_days):
    """
    根据新标准判定子任务状态 - 细化状态分类
    
    状态判断的核心逻辑：
    1. 已完成的任务：实际开始和结束时间都有数据
       - 按时完成：实际时间完全在计划时间范围内
       - 延期完成：实际结束时间超过计划结束时间
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

def insert_tasks_to_db(project_id, project_name, manager_name, excel_data, overwrite=False):
    """将任务信息插入到project_tasks表"""
    if not excel_data:
        return False, 0  # 返回(成功状态, 现有数据条数)
    
    connection = connect_to_database()
    if not connection:
        return False, 0
    
    cursor = connection.cursor()
    try:
        # 检查该项目是否已经有任务数据
        check_sql = "SELECT COUNT(*) FROM project_tasks WHERE project_name = %s AND project_id = %s"
        cursor.execute(check_sql, (project_name, project_id))
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0 and not overwrite:
            print(f"项目 '{project_name}' (ID: {project_id}) 已有 {existing_count} 条任务数据，需要确认是否覆盖")
            # 返回现有数据条数，让前端决定是否覆盖
            return False, existing_count
        elif existing_count > 0 and overwrite:
            # 如果需要覆盖，先清空现有数据
            delete_sql = "DELETE FROM project_tasks WHERE project_id = %s AND project_name = %s"
            cursor.execute(delete_sql, (project_id, project_name))
            connection.commit()
            deleted_count = cursor.rowcount
            print(f"已清空项目 '{project_name}' 的 {deleted_count} 条旧任务数据")
            existing_count = 0  # 重置计数
        
        print(f"开始处理项目 '{project_name}' 的 {len(excel_data)} 行数据")
        
        # 识别可能的列名 - 增强版本
        task_name_cols = ['任务名称', 'task_name', 'task', '工作内容', '任务描述', 'task_description', '任务', 'name', '工作项', '活动名称']
        wbs_code_cols = ['WBS编码', 'wbs_code', 'wbs', 'WBS', '工作分解结构', 'work_breakdown_structure', '编码', '工作包']
        task_owner_cols = ['负责人', 'task_owner', 'owner', '责任人', 'task_responsible', 'person_in_charge', '执行人', '担当者', '负责人员']
        planned_start_cols = ['计划开始时间', '计划开始日期', 'planned_start', 'planned_start_date', 'start_date_plan', '计划开始', '计划开工', '预计开始', '计划启动']
        planned_end_cols = ['计划结束时间', '计划结束日期', 'planned_end', 'planned_end_date', 'end_date_plan', '计划结束', '计划完工', '预计结束', '计划完成']
        actual_start_cols = ['实际开始时间', '实际开始日期', 'actual_start', 'actual_start_date', 'start_date_actual', '实际开始', '实际开工', '真实开始']
        actual_end_cols = ['实际结束时间', '实际结束日期', 'actual_end', 'actual_end_date', 'end_date_actual', '实际结束', '实际完工', '真实结束']
        progress_cols = ['进度', 'progress', '完成度', 'completion_rate', 'percentage', '完成百分比', '进展']
        lag_days_cols = ['滞后度(天)', 'lag_days', 'delay_days', 'delay', '延期天数', '延迟天数']
        task_status_cols = ['状态', 'task_status', 'status', '任务状态', '工作状态', '执行状态', '完成状态']
        
        inserted_count = 0
        
        for i, row in enumerate(excel_data):
            task_name = None
            wbs_code = None
            task_owner = None
            planned_start = None
            planned_end = None
            actual_start = None
            actual_end = None
            progress = None
            lag_days = None
            task_status = None
            
            print(f"  处理第 {i+1} 行数据: {row}")  # 调试信息
            
            # 遍历行中的每一列，查找匹配的字段 - 增强版本
            print(f"    处理行数据，列名: {list(row.keys())}")
            
            for col_name, col_value in row.items():
                col_name_clean = col_name.strip().replace('\u3000', '').replace(' ', '')  # 去除全角空格和普通空格
                col_name_lower = col_name_clean.lower()
                
                # 增强的任务名称匹配
                if not task_name and (
                    any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower 
                        for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_name_cols]) or
                    ('任务' in col_name_clean and '名称' in col_name_clean) or
                    ('工作' in col_name_clean and '内容' in col_name_clean)
                ):
                    task_name = str(col_value) if col_value else None
                    print(f"    找到任务名称: {task_name} (列名: {col_name})")
                
                # 增强的WBS编码匹配
                elif not wbs_code and (
                    any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower 
                        for keyword in [c.replace('\u3000', '').replace(' ', '') for c in wbs_code_cols]) or
                    ('wbs' in col_name_lower) or ('编码' in col_name_clean and 'wbs' in col_name_lower)
                ):
                    wbs_code = str(col_value) if col_value else None
                    print(f"    找到WBS编码: {wbs_code} (列名: {col_name})")
                
                # 增强的负责人匹配
                elif not task_owner and (
                    any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower 
                        for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_owner_cols]) or
                    ('负责' in col_name_clean and ('人' in col_name_clean or '者' in col_name_clean)) or
                    ('担当' in col_name_clean) or ('执行' in col_name_clean and '人' in col_name_clean)
                ):
                    task_owner = str(col_value) if col_value else None
                    print(f"    找到负责人: {task_owner} (列名: {col_name})")
                
                # 日期字段匹配保持原样但添加更多调试信息
                elif not planned_start and any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_start_cols]):
                    planned_start = extract_date_from_cell(col_value)
                    print(f"    找到计划开始: {planned_start} (列名: {col_name}, 原始值: {col_value})")
                elif not planned_end and any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_end_cols]):
                    planned_end = extract_date_from_cell(col_value)
                    print(f"    找到计划结束: {planned_end} (列名: {col_name}, 原始值: {col_value})")
                elif not actual_start and any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_start_cols]):
                    actual_start = extract_date_from_cell(col_value)
                    print(f"    找到实际开始: {actual_start} (列名: {col_name}, 原始值: {col_value})")
                elif not actual_end and any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_end_cols]):
                    actual_end = extract_date_from_cell(col_value)
                    print(f"    找到实际结束: {actual_end} (列名: {col_name}, 原始值: {col_value})")
                
                # 进度匹配保持原样
                elif not progress and any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in progress_cols]):
                    if col_value is not None:
                        try:
                            val_str = str(col_value).replace('%', '')
                            if val_str.replace('.', '').isdigit():
                                progress = float(val_str)
                            else:
                                progress = None
                            print(f"    找到进度: {progress} (列名: {col_name})")
                        except:
                            progress = None
                
                # 滞后天数匹配保持原样
                elif not lag_days and any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in lag_days_cols]):
                    if col_value is not None:
                        try:
                            lag_days = float(str(col_value)) if str(col_value).replace('-', '').replace('.', '').isdigit() else None
                            print(f"    找到滞后天数: {lag_days} (列名: {col_name})")
                        except:
                            lag_days = None
                
                # 状态匹配保持原样
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_status_cols]):
                    task_status = str(col_value) if col_value else None
                    print(f"    找到状态: {task_status} (列名: {col_name})")
            
            # 只有当至少有任务名称时才插入记录
            if task_name and task_name.strip() != '':
                print(f"    准备插入任务: {task_name}")
                
                # 如果task_status未明确指定或为空值，则根据条件计算
                if not task_status or task_status == 'None' or task_status == '' or task_status.lower() == 'none':
                    task_status = determine_task_status(planned_start, planned_end, actual_start, actual_end, lag_days)
                    print(f"    根据条件计算状态: {task_status}")
                else:
                    print(f"    使用Excel中的状态: {task_status}")
                
                # 计算工期和延期信息
                planned_duration = None
                actual_duration = None
                delay_days = None
                delay_reason = None
                
                if planned_start and planned_end:
                    planned_duration = (planned_end - planned_start).days
                if actual_start and actual_end:
                    actual_duration = (actual_end - actual_start).days
                
                # 判断是否延期
                if planned_end and actual_end and actual_end > planned_end:
                    delay_days = (actual_end - planned_end).days
                    delay_reason = "实际结束时间晚于计划结束时间"
                
                # 根据实际的数据库结构插入任务数据，包括project_id
                insert_task_sql = """
                INSERT INTO project_tasks (
                    project_id, project_name, project_manager, task_name, wbs_code, 
                    planned_start_date, planned_end_date, actual_start_date, actual_end_date,
                    progress, task_owner, task_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                try:
                    cursor.execute(insert_task_sql, (
                        project_id, project_name, manager_name, task_name, wbs_code,
                        planned_start, planned_end, actual_start, actual_end,
                        progress, task_owner, task_status
                    ))
                    inserted_count += 1
                    print(f"    成功插入任务: {task_name}，状态: {task_status}")
                except mysql.connector.Error as e:
                    print(f"    插入任务 '{task_name}' 时出错: {e}")
        
        connection.commit()
        if inserted_count > 0:
            print(f"成功插入 {inserted_count} 个任务到项目 '{project_name}' (ID: {project_id})")
        else:
            print(f"项目 '{project_name}' 没有找到有效的任务数据或插入失败")
        return True, existing_count
    except mysql.connector.Error as e:
        print(f"插入任务数据时出错: {e}")
        return False, existing_count
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def parse_filename(filename):
    """解析文件名，提取项目名和项目经理 - 改进版本"""
    print(f"开始解析文件名: {filename}")
    
    # 去掉扩展名
    name_without_ext = os.path.splitext(filename)[0]
    print(f"去掉扩展名后: {name_without_ext}")
    
    # 检查是否为临时文件名
    temp_patterns = [
        r'^tmp[a-zA-Z0-9]+$',      # tmp开头的随机字符串
        r'^tmp[a-zA-Z0-9]+_$',     # tmp开头带下划线结尾
        r'^temp_[a-zA-Z0-9]+$',    # temp_开头的随机字符串
        r'^[a-zA-Z0-9]{8,}$',      # 纯随机字符（8位以上）
        r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'  # UUID格式
    ]
    
    for pattern in temp_patterns:
        if re.match(pattern, name_without_ext):
            print(f"检测到临时文件名: {name_without_ext}，将使用默认项目名")
            return "未命名项目", "未知负责人"
    
    # 尝试多种格式匹配
    
    # 格式1: "xxx(项目名)-项目经理姓名"
    match1 = re.match(r'.*\((.+)\)(?:-|_)(.+)', name_without_ext)
    if match1:
        project_name = match1.group(1).strip()
        manager_name = match1.group(2).strip()
        print(f"格式1匹配成功 - 项目名: {project_name}, 项目经理: {manager_name}")
        return project_name, manager_name
    
    # 格式2: "项目名-项目经理姓名" (最常见的格式)
    last_dash_index = name_without_ext.rfind('-')
    if last_dash_index != -1 and last_dash_index > 0:
        project_name = name_without_ext[:last_dash_index].strip()
        manager_name = name_without_ext[last_dash_index+1:].strip()
        # 验证项目经理姓名合理性（中文姓名2-4个字符）
        if project_name and manager_name and re.match(r'^[\u4e00-\u9fff]{2,4}$', manager_name):
            print(f"格式2匹配成功 - 项目名: {project_name}, 项目经理: {manager_name}")
            return project_name, manager_name
    
    # 格式3: "项目名_项目经理姓名"
    last_underscore_index = name_without_ext.rfind('_')
    if last_underscore_index != -1 and last_underscore_index > 0:
        project_name = name_without_ext[:last_underscore_index].strip()
        manager_name = name_without_ext[last_underscore_index+1:].strip()
        # 验证项目经理姓名合理性
        if project_name and manager_name and re.match(r'^[\u4e00-\u9fff]{2,4}$', manager_name):
            print(f"格式3匹配成功 - 项目名: {project_name}, 项目经理: {manager_name}")
            return project_name, manager_name
    
    # 格式4: 尝试从文件名中智能提取（适用于没有明确分隔符的情况）
    # 假设文件名中包含中文且最后一个中文词是项目经理
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', name_without_ext)
    if len(chinese_chars) >= 2:
        # 取最后一个中文词作为项目经理，其余作为项目名
        manager_candidate = chinese_chars[-1]
        project_candidate = ''.join(chinese_chars[:-1])
        if len(manager_candidate) >= 2 and len(project_candidate) >= 2:
            print(f"格式4匹配成功 - 项目名: {project_candidate}, 项目经理: {manager_candidate}")
            return project_candidate, manager_candidate
    
    # 如果都不符合，返回整个名字作为项目名，项目经理为未知
    print(f"无法识别格式，使用默认值 - 项目名: {name_without_ext}, 项目经理: 未知")
    return name_without_ext, "未知"

def extract_date_from_cell(cell_value):
    """从单元格值中提取日期"""
    if cell_value is None:
        return None
    
    # 如果已经是日期对象，直接返回
    if isinstance(cell_value, datetime):
        # 检查是否为NaT
        if str(cell_value) == 'NaT':
            return None
        return cell_value.date()
    elif isinstance(cell_value, date):
        # 检查是否为NaT
        if str(cell_value) == 'NaT':
            return None
        return cell_value
    
    # 如果是字符串，尝试解析
    if isinstance(cell_value, str):
        # 移除可能的空白字符
        cell_value = cell_value.strip()
        
        # 尝试不同的日期格式
        date_formats = [
            '%Y-%m-%d',      # 2023-01-15
            '%Y/%m/%d',      # 2023/01/15
            '%m/%d/%Y',      # 01/15/2023
            '%d/%m/%Y',      # 15/01/2023
            '%Y年%m月%d日',   # 2023年01月15日
            '%m月%d日',      # 01月15日
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(cell_value, fmt)
                return parsed_date.date()
            except ValueError:
                continue
        
        return None
    
    # 如果是数值（在Excel中日期通常存储为浮点数）
    if isinstance(cell_value, (int, float)):
        try:
            # Excel日期是从1900年1月1日开始的天数
            # 处理可能的NaN值
            if str(cell_value) == 'nan' or cell_value != cell_value:  # NaN检查
                return None
            date_from_serial = datetime.fromordinal(int(693594 + cell_value))  # 693594是datetime(1900, 1, 1).toordinal()
            return date_from_serial.date()
        except:
            return None
    
    return None

def read_excel_data(file_path):
    """读取Excel文件的数据并返回一个包含所有数据的列表"""
    if PANDAS_AVAILABLE:
        try:
            # 根据文件扩展名选择合适的引擎
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in ['.xls']:
                df = pd.read_excel(file_path, engine='xlrd')
            elif file_extension in ['.xlsx', '.xlsm']:
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_extension in ['.csv']:
                df = pd.read_csv(file_path)
            else:
                # 默认尝试用openpyxl读取
                df = pd.read_excel(file_path)
                
            # 将DataFrame转换为字典列表，每行是一个字典
            data_list = df.to_dict('records')
            return data_list
        except Exception as e:
            print(f"使用pandas读取文件 {file_path} 时出错: {str(e)}")
            return []
    else:
        # 使用xlrd库读取Excel文件
        if xlrd is None:
            print(f"无法读取文件 {file_path}，因为没有可用的Excel读取库")
            return []
        
        try:
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheets()[0]  # 取第一个工作表
            
            # 读取所有数据
            data_list = []
            for row_idx in range(sheet.nrows):
                row_data = {}
                for col_idx in range(sheet.ncols):
                    cell_value = sheet.cell_value(row_idx, col_idx)
                    # 使用列索引作为键，或者如果第一行是标题，则使用标题名称
                    if row_idx == 0:  # 如果是标题行，保存标题
                        column_name = str(cell_value) if cell_value else f"Column_{col_idx}"
                        row_data[column_name] = cell_value
                    else:  # 如果不是标题行，使用之前保存的标题作为键
                        if row_idx == 1:  # 初始化列名
                            column_name = str(sheet.cell_value(0, col_idx)) if sheet.cell_value(0, col_idx) else f"Column_{col_idx}"
                        else:
                            column_name = str(sheet.cell_value(0, col_idx)) if sheet.cell_value(0, col_idx) else f"Column_{col_idx}"
                        
                        row_data[column_name] = cell_value
                
                data_list.append(row_data)
            
            return data_list
        except Exception as e:
            print(f"使用xlrd读取文件 {file_path} 时出错: {str(e)}")
            return []

def analyze_excel_data(data_list):
    """分析Excel数据，提取关键信息"""
    if not data_list:
        return None, None, None, None, "未计划"
    
    # 查找可能的日期列名
    planned_start_cols = ['计划开始时间', '计划开始日期', 'planned_start', 'planned_start_date', 'start_date_plan', '计划开始', '计划开工']
    planned_end_cols = ['计划结束时间', '计划结束日期', 'planned_end', 'planned_end_date', 'end_date_plan', '计划结束', '计划完工']
    actual_start_cols = ['实际开始时间', '实际开始日期', 'actual_start', 'actual_start_date', 'start_date_actual', '实际开始', '实际开工']
    actual_end_cols = ['实际结束时间', '实际结束日期', 'actual_end', 'actual_end_date', 'end_date_actual', '实际结束', '实际完工']
    
    # 收集所有日期值
    planned_starts = []
    planned_ends = []
    actual_starts = []
    actual_ends = []
    
    for row in data_list:
        for col_name, col_value in row.items():
            col_name_clean = col_name.strip().replace('\u3000', '').replace(' ', '')  # 去除全角空格和普通空格
            col_name_lower = col_name_clean.lower()
            
            # 检查列名是否匹配计划开始日期
            if any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_start_cols]):
                date_val = extract_date_from_cell(col_value)
                if date_val:
                    planned_starts.append(date_val)
            
            # 检查列名是否匹配计划结束日期
            elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_end_cols]):
                date_val = extract_date_from_cell(col_value)
                if date_val:
                    planned_ends.append(date_val)
            
            # 检查列名是否匹配实际开始日期
            elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_start_cols]):
                date_val = extract_date_from_cell(col_value)
                if date_val:
                    actual_starts.append(date_val)
            
            # 检查列名是否匹配实际结束日期
            elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_end_cols]):
                date_val = extract_date_from_cell(col_value)
                if date_val:
                    actual_ends.append(date_val)
    
    # 计算最早的计划开始时间和最晚的计划结束时间
    # 过滤掉NaT值后再进行比较
    filtered_planned_starts = [d for d in planned_starts if d is not None and str(d) != 'NaT']
    filtered_planned_ends = [d for d in planned_ends if d is not None and str(d) != 'NaT']
    filtered_actual_starts = [d for d in actual_starts if d is not None and str(d) != 'NaT']
    filtered_actual_ends = [d for d in actual_ends if d is not None and str(d) != 'NaT']
    
    earliest_planned_start = min(filtered_planned_starts) if filtered_planned_starts else None
    latest_planned_end = max(filtered_planned_ends) if filtered_planned_ends else None
    earliest_actual_start = min(filtered_actual_starts) if filtered_actual_starts else None
    
    # 修改：项目实际结束时间严格取最后一个子任务的实际完成时间
    # 如果最后一个子任务的实际完成时间为空，则认定为空，不再向前查找其他任务
    latest_actual_end = None
    if data_list:
        # 直接取最后一行数据（按照 WBS 顺序，最后一个子任务代表项目的最终交付物）
        last_row = data_list[-1]
            
        # 遍历最后一行的所有列，找出所有实际结束时间相关的字段
        actual_end_fields = []
        for col_name, col_value in last_row.items():
            col_name_clean = col_name.strip().replace('\u3000', '').replace(' ', '')
            col_name_lower = col_name_clean.lower()
                
            # 检查是否为实际结束时间列
            if any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower 
                   for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_end_cols]):
                actual_end_fields.append((col_name, col_value))
            
        # 如果找到了实际结束时间字段，取最后一个字段的值（包括 None）
        if actual_end_fields:
            # 取最后一个实际结束时间字段的值
            last_field_name, last_field_value = actual_end_fields[-1]
            latest_actual_end = extract_date_from_cell(last_field_value)
            # 注意：即使提取结果为 None，也保持为 None，不再查找其他行或其他字段
        # 如果最后一行没有任何实际结束时间字段，则 latest_actual_end 保持为 None
    
    # 根据新的状态判断逻辑确定项目状态
    current_date = datetime.now().date()
    
    # 情况 1：已完成的任务（实际开始和结束时间都有数据）
    if latest_actual_end and latest_actual_end <= current_date:
        # 检查是否延期完成
        if latest_planned_end and latest_actual_end > latest_planned_end:
            status = "延期完成"
        else:
            status = "完成"
    
    # 情况2：进行中的任务（只有实际开始时间，没有实际结束时间）
    elif earliest_actual_start and not latest_actual_end:
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
    
    # 情况3：未启动的任务（实际开始和结束时间都没有数据）
    elif not earliest_actual_start and not latest_actual_end:
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
    
    # 其他情况
    else:
        status = "异常"
    
    return earliest_planned_start, latest_planned_end, earliest_actual_start, latest_actual_end, status

def extract_project_info_from_excel(file_data):
    """从Excel数据中智能提取项目信息 - 简化版本"""
    if not file_data:
        return None, None
    
    print("开始从Excel内容中提取项目信息...")
    
    # 查找可能包含项目信息的列名
    project_name_indicators = ['项目', '工程', '任务', '工作', 'project', 'proj']
    manager_indicators = ['负责', '担当', '执行', '管理', '主管', 'manager', 'owner']
    
    # 收集所有可能的项目相关信息
    potential_project_names = []
    potential_managers = []
    
    # 检查第一行（通常是标题行）寻找线索
    if file_data:
        first_row = file_data[0]
        for col_name, col_value in first_row.items():
            col_name_str = str(col_name).strip()
            col_value_str = str(col_value).strip() if col_value else ""
            
            # 检查列名是否暗示项目信息
            if any(indicator in col_name_str.lower() for indicator in project_name_indicators):
                if col_value_str and len(col_value_str) > 2:
                    potential_project_names.append(col_value_str)
                    print(f"  发现潜在项目名: {col_value_str} (来自列: {col_name_str})")
            
            # 检查列名是否暗示负责人信息
            if any(indicator in col_name_str.lower() for indicator in manager_indicators):
                if col_value_str and len(col_value_str) > 1:
                    potential_managers.append(col_value_str)
                    print(f"  发现潜在负责人: {col_value_str} (来自列: {col_name_str})")
    
    # 从任务数据中收集负责人信息
    task_owners = []
    for row in file_data:
        for col_name, col_value in row.items():
            col_name_clean = str(col_name).strip().replace('\u3000', '').replace(' ', '')
            col_value_str = str(col_value).strip() if col_value else ""
            
            # 匹配负责人列
            task_owner_cols = ['负责人', 'task_owner', 'owner', '责任人', 'task_responsible', 'person_in_charge', '执行人', '担当者', '负责人员']
            if any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_clean.lower() 
                   for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_owner_cols]):
                if col_value_str and len(col_value_str) > 1 and col_value_str not in task_owners:
                    # 验证是否为合理的中文姓名
                    if re.match(r'^[\u4e00-\u9fff]{2,4}$', col_value_str):
                        task_owners.append(col_value_str)
                        print(f"  从任务数据发现负责人: {col_value_str}")
    
    # 决策项目名称
    project_name = None
    if potential_project_names:
        # 选择最长的有效项目名
        project_name = max(potential_project_names, key=len)
    elif file_data:
        # 从任务内容中提取项目主题
        task_contents = []
        for row in file_data:
            for col_name, col_value in row.items():
                col_name_clean = str(col_name).strip().replace('\u3000', '').replace(' ', '')
                col_value_str = str(col_value).strip() if col_value else ""
                
                # 匹配任务名称列
                task_name_cols = ['任务名称', 'task_name', 'task', '工作内容', '任务描述', 'task_description', '任务', 'name', '工作项', '活动名称']
                if any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_clean.lower() 
                       for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_name_cols]):
                    if col_value_str and len(col_value_str) > 3:
                        task_contents.append(col_value_str)
        
        # 从任务内容中提取共同主题
        if task_contents:
            first_task = task_contents[0]
            # 移除常见的编号前缀
            prefixes_to_remove = ['0100', '0101', '0102', '0200', '0300', '0400', '0500', '0501', '0502']
            for prefix in prefixes_to_remove:
                if first_task.startswith(prefix):
                    first_task = first_task[len(prefix):].strip()
                    break
            
            if first_task:
                project_name = f"{first_task}项目"
            else:
                project_name = "项目管理系统"
        elif task_owners:
            project_name = f"{task_owners[0]}的项目"
        else:
            project_name = "未命名项目"
    else:
        project_name = "未命名项目"
    
    # 决策负责人
    manager_name = None
    if potential_managers:
        # 优先选择符合中文姓名格式的
        chinese_managers = [mgr for mgr in potential_managers 
                           if re.match(r'^[\u4e00-\u9fff]{2,4}$', mgr)]
        if chinese_managers:
            manager_name = chinese_managers[0]
        else:
            manager_name = potential_managers[0]
    elif task_owners:
        # 统计出现频率最高的负责人
        from collections import Counter
        owner_counts = Counter(task_owners)
        if owner_counts:
            manager_name = owner_counts.most_common(1)[0][0]
        else:
            manager_name = "未知负责人"
    else:
        manager_name = "未知负责人"
    
    print(f"智能提取结果 - 项目名: {project_name}, 负责人: {manager_name}")
    return project_name, manager_name

def process_single_file(file_path, overwrite=False, original_filename=None):
    """处理单个Excel文件并导入到数据库"""
    # 优先使用传入的原始文件名，如果没有则使用文件路径中的文件名
    filename = original_filename if original_filename else os.path.basename(file_path)
    print(f"使用文件名进行解析: {filename}")
    project_name, manager_name = parse_filename(filename)
    
    print(f"\n处理表格: {filename}")
    print(f"  初步解析项目名: {project_name}")
    print(f"  初步解析项目经理: {manager_name}")
    
    # 读取文件数据
    file_data = read_excel_data(file_path)
    
    # 如果初步解析结果不佳（临时文件名或默认值），尝试从Excel内容中智能提取
    if (project_name.startswith("tmp") or project_name in ["未命名项目", filename.replace('.xlsx', '').replace('.xls', '')]) and \
       (manager_name in ["未知", "未知负责人"]):
        print("检测到默认值，尝试从Excel内容中智能提取项目信息...")
        smart_project_name, smart_manager_name = extract_project_info_from_excel(file_data)
        if smart_project_name and smart_manager_name:
            project_name = smart_project_name
            manager_name = smart_manager_name
            print(f"  智能提取成功 - 项目名: {project_name}, 负责人: {manager_name}")
        else:
            print("  智能提取失败，继续使用默认值")
    
    if not file_data:
        print(f"  警告: 无法读取文件 {file_path} 的数据")
        return {"success": False, "message": "无法读取文件数据"}
    
    # 分析数据，提取关键信息
    planned_start, planned_end, actual_start, actual_end, status = analyze_excel_data(file_data)
    
    # 获取或创建项目ID
    project_id = get_or_create_project_id(
        project_name, 
        manager_name, 
        planned_start, 
        planned_end, 
        actual_start, 
        actual_end, 
        status
    )
    
    if project_id is None:
        print(f"  ✗ 无法获取或创建项目ID，跳过此文件")
        return {"success": False, "message": "无法创建项目"}
    
    # 如果需要覆盖，先清空现有数据
    if overwrite:
        clear_existing_project_tasks(project_id, project_name)
    
    # 将任务信息插入到project_tasks表
    success, existing_count = insert_tasks_to_db(
        project_id,
        project_name,
        manager_name,
        file_data,
        overwrite
    )
    
    result = {
        "success": success,
        "filename": filename,
        "project_name": project_name,
        "manager_name": manager_name,
        "project_id": project_id,
        "data_rows": len(file_data),
        "existing_count": existing_count,  # 添加现有数据条数
        "planned_start": planned_start,
        "planned_end": planned_end,
        "actual_start": actual_start,
        "actual_end": actual_end,
        "status": status
    }
    
    if success:
        print(f"  ✓ 项目任务信息已成功导入数据库")
        result["message"] = "导入成功"
    else:
        if existing_count > 0:
            print(f"  ⚠ 项目 '{project_name}' 已有 {existing_count} 条任务数据，需要确认是否覆盖")
            result["message"] = f"项目已存在 {existing_count} 条任务数据"
        else:
            print(f"  ✗ 项目任务信息导入数据库失败")
            result["message"] = "导入失败"
    
    return result

def clear_existing_project_tasks(project_id, project_name):
    """清空指定项目的现有任务数据"""
    connection = connect_to_database()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        # 清空该项目的任务数据
        delete_sql = "DELETE FROM project_tasks WHERE project_id = %s AND project_name = %s"
        cursor.execute(delete_sql, (project_id, project_name))
        connection.commit()
        deleted_count = cursor.rowcount
        print(f"  已清空项目 '{project_name}' 的 {deleted_count} 条任务数据")
        return True
    except mysql.connector.Error as e:
        print(f"  清空项目任务数据时出错: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    print("开始处理Excel文件并导入到数据库...")
    
    # 获取当前目录下的所有Excel文件
    excel_extensions = ['*.xls', '*.xlsx', '*.xlsm', '*.csv']
    excel_files = []
    
    for ext in excel_extensions:
        excel_files.extend(glob.glob(ext))
    
    if not excel_files:
        print("在当前目录下未找到任何Excel文件")
        return
    
    print(f"找到 {len(excel_files)} 个Excel文件:")
    for f in excel_files:
        print(f"  - {f}")
    print("-" * 60)
    
    # 存储所有文件的数据
    all_files_data = []
    
    for file_path in excel_files:
        filename = os.path.basename(file_path)
        project_name, manager_name = parse_filename(filename)
        
        print(f"\n处理表格: {filename}")
        print(f"  解析项目名: {project_name}")
        print(f"  解析项目经理: {manager_name}")
        
        # 读取文件数据
        file_data = read_excel_data(file_path)
        
        if not file_data:
            print(f"  警告: 无法读取文件 {file_path} 的数据")
            continue
        
        # 分析数据，提取关键信息
        planned_start, planned_end, actual_start, actual_end, status = analyze_excel_data(file_data)
        
        # 获取或创建项目ID
        project_id = get_or_create_project_id(
            project_name, 
            manager_name, 
            planned_start, 
            planned_end, 
            actual_start, 
            actual_end, 
            status
        )
        
        if project_id is None:
            print(f"  ✗ 无法获取或创建项目ID，跳过此文件")
            continue
        
        # 将任务信息插入到project_tasks表
        success = insert_tasks_to_db(
            project_id,
            project_name,
            manager_name,
            file_data
        )
        
        if success:
            print(f"  ✓ 项目任务信息已成功导入数据库")
        else:
            print(f"  ✗ 项目任务信息导入数据库失败")
        
        # 创建文件数据记录
        file_record = {
            'filename': filename,
            'project_name': project_name,
            'manager_name': manager_name,
            'project_id': project_id,
            'data': file_data,
            'planned_start': planned_start,
            'planned_end': planned_end,
            'actual_start': actual_start,
            'actual_end': actual_end,
            'status': status
        }
        
        all_files_data.append(file_record)
        
        print(f"  数据行数: {len(file_data)}")
        print(f"  计划开始时间: {planned_start}")
        print(f"  计划结束时间: {planned_end}")
        print(f"  实际开始时间: {actual_start}")
        print(f"  实际结束时间: {actual_end}")
        print(f"  项目状态: {status}")
        print("-" * 60)
    
    # 打印所有文件的数据摘要
    print(f"\n\n处理完成! 总共处理了 {len(all_files_data)} 个项目文件")
    print("=" * 60)
    
    for i, file_record in enumerate(all_files_data):
        print(f"\n--- 文件 {i+1}: {file_record['filename']} ---")
        print(f"项目ID: {file_record['project_id']}")
        print(f"项目名: {file_record['project_name']}")
        print(f"项目经理: {file_record['manager_name']}")
        print(f"计划开始: {file_record['planned_start']}")
        print(f"计划结束: {file_record['planned_end']}")
        print(f"实际开始: {file_record['actual_start']}")
        print(f"实际结束: {file_record['actual_end']}")
        print(f"状态: {file_record['status']}")
        print(f"数据行数: {len(file_record['data'])}")

if __name__ == "__main__":
    main()