# -*- coding: utf-8 -*-
import os
import re
import glob
from datetime import datetime
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
    根据条件确定任务状态
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
        planned_start <= current_date <= planned_end and 
        actual_start is not None and actual_end is None):
        return "进行中"
    
    # 默认为异常
    return "异常"

def insert_tasks_to_db(project_id, project_name, manager_name, excel_data):
    """将任务信息插入到project_tasks表"""
    if not excel_data:
        return False
    
    connection = connect_to_database()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        # 检查该项目是否已经有任务数据
        check_sql = "SELECT COUNT(*) FROM project_tasks WHERE project_name = %s AND project_id = %s"
        cursor.execute(check_sql, (project_name, project_id))
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"项目 '{project_name}' (ID: {project_id}) 已有 {count} 条任务数据，跳过重复导入")
            return True  # 返回True表示不需要导入，但操作成功
        
        print(f"开始处理项目 '{project_name}' 的 {len(excel_data)} 行数据")
        
        # 识别可能的列名
        task_name_cols = ['任务名称', 'task_name', 'task', '工作内容', '任务描述', 'task_description', '任务', 'name']
        wbs_code_cols = ['WBS编码', 'wbs_code', 'wbs', 'WBS', '工作分解结构', 'work_breakdown_structure']
        task_owner_cols = ['负责人', 'task_owner', 'owner', '责任人', 'task_responsible', 'person_in_charge']
        planned_start_cols = ['计划开始时间', '计划开始日期', 'planned_start', 'planned_start_date', 'start_date_plan', '计划开始', '计划开工']
        planned_end_cols = ['计划结束时间', '计划结束日期', 'planned_end', 'planned_end_date', 'end_date_plan', '计划结束', '计划完工']
        actual_start_cols = ['实际开始时间', '实际开始日期', 'actual_start', 'actual_start_date', 'start_date_actual', '实际开始', '实际开工']
        actual_end_cols = ['实际结束时间', '实际结束日期', 'actual_end', 'actual_end_date', 'end_date_actual', '实际结束', '实际完工']
        progress_cols = ['进度', 'progress', '完成度', 'completion_rate', 'percentage']
        lag_days_cols = ['滞后度(天)', 'lag_days', 'delay_days', 'delay']
        task_status_cols = ['状态', 'task_status', 'status', '任务状态', '工作状态']
        
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
            
            # 遍历行中的每一列，查找匹配的字段
            for col_name, col_value in row.items():
                col_name_clean = col_name.strip().replace('\u3000', '').replace(' ', '')  # 去除全角空格和普通空格
                col_name_lower = col_name_clean.lower()
                
                if any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_name_cols]) and not task_name:
                    task_name = str(col_value) if col_value else None
                    print(f"    找到任务名称: {task_name}")
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in wbs_code_cols]) and not wbs_code:
                    wbs_code = str(col_value) if col_value else None
                    print(f"    找到WBS编码: {wbs_code}")
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_owner_cols]) and not task_owner:
                    task_owner = str(col_value) if col_value else None
                    print(f"    找到负责人: {task_owner}")
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_start_cols]) and not planned_start:
                    planned_start = extract_date_from_cell(col_value)
                    print(f"    找到计划开始: {planned_start}")
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_end_cols]) and not planned_end:
                    planned_end = extract_date_from_cell(col_value)
                    print(f"    找到计划结束: {planned_end}")
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_start_cols]) and not actual_start:
                    actual_start = extract_date_from_cell(col_value)
                    print(f"    找到实际开始: {actual_start}")
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_end_cols]) and not actual_end:
                    actual_end = extract_date_from_cell(col_value)
                    print(f"    找到实际结束: {actual_end}")
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in progress_cols]) and not progress:
                    if col_value is not None:
                        try:
                            # 处理百分比格式
                            val_str = str(col_value).replace('%', '')
                            if val_str.replace('.', '').isdigit():
                                progress = float(val_str)
                            else:
                                progress = None
                            print(f"    找到进度: {progress}")
                        except:
                            progress = None
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in lag_days_cols]) and not lag_days:
                    if col_value is not None:
                        try:
                            lag_days = float(str(col_value)) if str(col_value).replace('-', '').replace('.', '').isdigit() else None
                            print(f"    找到滞后天数: {lag_days}")
                        except:
                            lag_days = None
                elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower for keyword in [c.replace('\u3000', '').replace(' ', '') for c in task_status_cols]):
                    task_status = str(col_value) if col_value else None
                    print(f"    找到状态: {task_status}")
            
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
        return True
    except mysql.connector.Error as e:
        print(f"插入任务数据时出错: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def parse_filename(filename):
    """解析文件名，提取项目名和项目经理"""
    # 去掉扩展名
    name_without_ext = os.path.splitext(filename)[0]
    
    # 尝试匹配 "xxx(项目名)-项目经理姓名" 格式
    match = re.match(r'.*\((.+)\)-(.+)', name_without_ext)
    
    if match:
        project_name = match.group(1).strip()
        manager_name = match.group(2).strip()
        return project_name, manager_name
    
    # 如果不符合上述格式，尝试匹配 "项目名-项目经理姓名" 格式
    last_dash_index = name_without_ext.rfind('-')
    if last_dash_index != -1:
        project_name = name_without_ext[:last_dash_index].strip()
        manager_name = name_without_ext[last_dash_index+1:].strip()
        return project_name, manager_name
    
    # 如果都不符合，返回整个名字作为项目名，项目经理为未知
    return name_without_ext, "未知"

def extract_date_from_cell(cell_value):
    """从单元格值中提取日期"""
    if cell_value is None:
        return None
    
    # 如果已经是日期对象，直接返回
    if isinstance(cell_value, (datetime)):
        return cell_value.date()
    
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
    earliest_planned_start = min(planned_starts) if planned_starts else None
    latest_planned_end = max(planned_ends) if planned_ends else None
    earliest_actual_start = min(actual_starts) if actual_starts else None
    latest_actual_end = max(actual_ends) if actual_ends else None
    
    # 根据数据确定项目状态
    if latest_actual_end and latest_actual_end < datetime.now().date():
        status = "已完成"
    elif earliest_actual_start:
        status = "进行中"
    elif earliest_planned_start and earliest_planned_start > datetime.now().date():
        status = "未开始"
    else:
        status = "已计划"
    
    return earliest_planned_start, latest_planned_end, earliest_actual_start, latest_actual_end, status

def process_single_file(file_path, overwrite=False):
    """处理单个Excel文件并导入到数据库"""
    filename = os.path.basename(file_path)
    project_name, manager_name = parse_filename(filename)
    
    print(f"\n处理表格: {filename}")
    print(f"  解析项目名: {project_name}")
    print(f"  解析项目经理: {manager_name}")
    
    # 读取文件数据
    file_data = read_excel_data(file_path)
    
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
    success = insert_tasks_to_db(
        project_id,
        project_name,
        manager_name,
        file_data
    )
    
    result = {
        "success": success,
        "filename": filename,
        "project_name": project_name,
        "manager_name": manager_name,
        "project_id": project_id,
        "data_rows": len(file_data),
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