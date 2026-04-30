"""
数据管理路由模块
包含数据导入导出相关的 API 接口
"""

import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict
import pandas as pd
import io
import re
import tempfile
from datetime import datetime

# 从database模块导入
from database.database import execute_query

# 创建路由器实例
router = APIRouter(prefix="/v1", tags=["数据管理"])

# 27. 导入项目数据
@router.post("/projects/import")
async def import_projects(file: UploadFile = File(...), overwrite: bool = False):
    """导入项目数据 - 使用统一的处理逻辑"""
    try:
        # 检查文件类型
        if not file.filename.lower().endswith((".xlsx", ".xls", ".csv")):
            raise HTTPException(status_code=400, detail="不支持的文件格式，请上传Excel或CSV文件")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            # 将上传的文件内容写入临时文件
            contents = await file.read()
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name
        
        try:
            # 动态导入datadeal模块
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            datadeal_module_path = os.path.join(project_root, 'datadeal')
            print(f"尝试导入路径: {datadeal_module_path}")
            
            if datadeal_module_path not in sys.path:
                sys.path.insert(0, datadeal_module_path)
                print(f"已添加到sys.path: {datadeal_module_path}")
            
            # 导入simple_datadeal模块
            try:
                import simple_datadeal
                print("成功导入simple_datadeal模块")
            except ImportError as e:
                print(f"导入simple_datadeal模块失败: {e}")
                raise HTTPException(status_code=500, detail=f"无法导入数据处理模块: {str(e)}")
            
            # 保存当前工作目录并切换到临时文件所在目录
            original_cwd = os.getcwd()
            temp_dir = os.path.dirname(tmp_file_path)
            os.chdir(temp_dir)
            print(f"切换工作目录到: {temp_dir}")
            
            try:
                # 调用datadeal的核心处理逻辑，传递原始文件名
                print(f"开始调用process_single_file函数，原始文件名: {file.filename}")
                result = simple_datadeal.process_single_file(tmp_file_path, overwrite=overwrite, original_filename=file.filename)
                print(f"处理结果: {result}")
                
                # 检查处理结果
                if not result:
                    raise HTTPException(status_code=500, detail="处理函数返回空结果")
                
                # 特殊处理查重情况
                existing_count = result.get('existing_count', 0)
                if existing_count > 0 and not overwrite:
                    # 当存在重复数据且未要求覆盖时，返回特殊的响应
                    return {
                        "message": f"项目已存在 {existing_count} 条任务数据",
                        "existing_count": existing_count,
                        "processed_count": 0,
                        "needs_confirmation": True,  # 标记需要用户确认
                        "details": result
                    }
                
                # 正常处理结果
                if not result.get('success', False):
                    error_msg = result.get('message', '未知错误')
                    raise HTTPException(status_code=500, detail=f"数据处理失败: {error_msg}")
                
                # 获取重复数据统计
                processed_count = result.get('data_rows', 0) if 'data_rows' in result else 0
                
                return {
                    "message": f"文件 {file.filename} 导入成功",
                    "existing_count": existing_count,
                    "processed_count": processed_count,
                    "details": result
                }
            except Exception as e:
                print(f"处理文件时出错: {e}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"处理文件时出错: {str(e)}")
            finally:
                # 恢复原来的工作目录
                os.chdir(original_cwd)
                print(f"恢复工作目录到: {original_cwd}")
                
        except HTTPException:
            # 重新抛出HTTP异常
            raise
        except Exception as e:
            print(f"导入过程中出现未预期错误: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                print(f"已清理临时文件: {tmp_file_path}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"导入项目数据出错: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")

def determine_task_status_import(planned_start, planned_end, actual_start, actual_end, lag_days):
    """
    根据新标准判定子任务状态 - 与simple_datadeal.py保持一致，细化状态分类
    
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
    
    # 情况1：已完成的任务（实际开始和结束时间都有数据）
    if actual_start is not None and actual_end is not None:
        # 按时完成：实际时间完全在计划时间范围内
        if (planned_start and planned_end and 
            planned_start <= actual_start <= planned_end and 
            planned_start <= actual_end <= planned_end):
            return "按时完成"
        
        # 延期完成：实际结束时间超过计划结束时间
        elif planned_end and actual_end > planned_end:
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

# 28. 导出项目数据
@router.post("/projects/export")
async def export_projects(request_data: Dict):
    """导出项目数据"""
    try:
        import pandas as pd
        from fastapi.responses import StreamingResponse
        import io
        
        print(f"\n========== 开始导出项目数据 ==========")
        print(f"请求数据：{request_data}")
        
        # 获取要导出的项目ID 列表
        project_ids = request_data.get('project_ids', [])
        print(f"要导出的项目IDs: {project_ids}")

        # 检查 projects 表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            raise HTTPException(status_code=400, detail="数据库中不存在 projects 表")

        # 查询项目数据
        if project_ids:  # 如果指定了项目ID，则导出选中的项目
            placeholders = ','.join(['%s'] * len(project_ids))
            select_sql = f"SELECT * FROM projects WHERE project_id IN ({placeholders}) ORDER BY created_at DESC"
            projects = execute_query(select_sql, tuple(project_ids), fetch_all=True) or []
        else:  # 否则导出所有项目
            select_sql = "SELECT * FROM projects ORDER BY created_at DESC"
            projects = execute_query(select_sql, fetch_all=True) or []

        print(f"✅ 查询到 {len(projects)} 个项目")

        if not projects:
            raise HTTPException(status_code=404, detail="没有找到要导出的项目数据")

        # 将数据转换为 DataFrame，并确保数据类型正确
        processed_projects = []
        for project in projects:
            processed_project = {}
            for key, value in project.items():
                # 处理日期和时间类型
                if isinstance(value, (datetime, type(pd.Timestamp))):
                    processed_project[key] = str(value)
                # 处理十进制类型
                elif hasattr(value, 'quantize'):  # 检查是否为 Decimal 类型
                    processed_project[key] = float(value)
                # 其他类型直接使用
                else:
                    processed_project[key] = value
            processed_projects.append(processed_project)
        
        df = pd.DataFrame(processed_projects)
        print(f"✅ DataFrame 创建成功，形状：{df.shape}")
        
        # 创建内存中的字节流
        output = io.BytesIO()
        
        # 将 DataFrame 写入 Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='项目数据')
        
        # 获取字节流内容
        output.seek(0)
        excel_data = output.getvalue()
        print(f"✅ Excel 文件生成成功，大小：{len(excel_data)} 字节")
                
        # 处理文件名编码问题
        import urllib.parse
        filename = f"项目数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        encoded_filename = urllib.parse.quote(filename, encoding='utf-8')
                
        print(f"📦 准备返回文件：{filename}")
        print(f"Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        print("========== 导出完成 ==========\n")
                        
        return StreamingResponse(
            iter([excel_data]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"导出项目数据出错: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

# 30. 修改项目信息并记录修改日志
@router.put("/projects/{project_id}")
async def update_project_with_log(project_id: int, project_data: dict):
    """修改项目信息并记录修改日志"""
    try:
        # 获取修改人信息
        modifier_name = project_data.get('modifier_name', '')
        modifier_ip = project_data.get('modifier_ip', '')
        remarks = project_data.get('remarks_for_modification', '')
        
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            raise HTTPException(status_code=404, detail="projects表不存在")
        
        # 首先检查项目是否存在
        check_project_sql = "SELECT * FROM projects WHERE project_id = %s"
        old_project = execute_query(check_project_sql, (project_id,))
        if not old_project:
            raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
        
        # 构建更新SQL
        update_fields = []
        update_params = []
        
        # 处理各个字段的更新
        field_mapping = {
            'project_name': project_data.get('project_name'),
            'project_manager': project_data.get('project_manager'),
            'planned_start_date': project_data.get('planned_start_date') or project_data.get('start_date'),
            'planned_end_date': project_data.get('planned_end_date') or project_data.get('end_date'),
            'actual_start_date': project_data.get('actual_start_date'),
            'actual_end_date': project_data.get('actual_end_date'),
            'category': project_data.get('category'),
            'project_status': project_data.get('project_status') or project_data.get('status'),
            'budget': project_data.get('budget'),
            'actual_cost': project_data.get('actual_cost'),
            'remarks': project_data.get('remarks')
        }
        
        for field, value in field_mapping.items():
            if value is not None and value != '':  # 只更新非空值
                update_fields.append(f"{field} = %s")
                update_params.append(value)
        
        # 添加进度字段（特殊处理）
        if 'progress' in project_data and project_data['progress'] is not None:
            update_fields.append("progress = %s")
            update_params.append(float(project_data['progress']))
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供有效的更新字段")
        
        # 更新项目信息
        update_params.append(project_id)
        update_sql = f"UPDATE projects SET {', '.join(update_fields)} WHERE project_id = %s"
        update_result = execute_query(update_sql, tuple(update_params))
        
        if update_result is None or update_result == 0:
            # 如果没有更新任何行，可能是数据与原数据完全相同
            # 这种情况下不抛出错误，而是返回成功消息
            print(f"ℹ️ 项目 {project_id} 的数据未发生变化")
            # 继续执行后续的记录日志和状态刷新逻辑
        
        # 更新成功后，立即重新计算并更新项目状态（基于任务数据）
        try:
            from ..services.project_service import ProjectService
            
            project_name = old_project.get('project_name')
            if project_name:
                print(f"\n========== 开始重新计算项目状态：{project_name} ==========")
                
                # 查询该项目的所有任务，按照 WBS 编码排序（转换为数字后排序）
                last_task_sql = """
                SELECT planned_start_date, planned_end_date, actual_start_date, actual_end_date, wbs_code
                FROM project_tasks
                WHERE project_name = %s
                ORDER BY CAST(wbs_code AS UNSIGNED) DESC
                LIMIT 1
                """
                last_task_result = execute_query(last_task_sql, (project_name,), fetch_all=True)
                
                # 获取最后一个子任务的实际完成时间
                last_actual_end = last_task_result[0].get('actual_end_date') if last_task_result else None
                
                # 汇总所有任务的日期信息（用于计划时间和实际开始时间）
                all_tasks_sql = """
                SELECT planned_start_date, planned_end_date, actual_start_date, actual_end_date
                FROM project_tasks
                WHERE project_name = %s
                """
                all_tasks = execute_query(all_tasks_sql, (project_name,), fetch_all=True) or []
                
                if all_tasks:
                    print(f"找到 {len(all_tasks)} 个任务用于计算项目状态")
                    
                    all_planned_starts = [t['planned_start_date'] for t in all_tasks if t.get('planned_start_date')]
                    all_planned_ends = [t['planned_end_date'] for t in all_tasks if t.get('planned_end_date')]
                    all_actual_starts = [t['actual_start_date'] for t in all_tasks if t.get('actual_start_date')]
                    
                    # 取最早的计划开始时间、最晚的计划结束时间、最早的实际开始时间
                    project_planned_start = min(all_planned_starts) if all_planned_starts else None
                    project_planned_end = max(all_planned_ends) if all_planned_ends else None
                    project_actual_start = min(all_actual_starts) if all_actual_starts else None
                    
                    # 项目的实际完成时间严格取最后一个子任务的实际完成时间
                    project_actual_end = last_actual_end
                    
                    print(f"项目计划时间范围：{project_planned_start} ~ {project_planned_end}")
                    print(f"项目实际时间范围：{project_actual_start} ~ {project_actual_end}")
                    
                    # 使用 ProjectService 计算项目状态
                    if project_planned_start and project_planned_end:
                        new_project_status = ProjectService.calculate_project_status(
                            project_planned_start,
                            project_planned_end,
                            project_actual_start,
                            project_actual_end,
                            project_id  # 传入项目ID以检查异常子任务
                        )
                        
                        # 如果计算出的状态与当前不同，则更新
                        current_status = old_project.get('project_status')
                        if str(new_project_status) != str(current_status):
                            update_status_sql = """
                            UPDATE projects 
                            SET project_status = %s,
                                actual_start_date = %s,
                                actual_end_date = %s,
                                updated_at = NOW()
                            WHERE project_id = %s
                            """
                            
                            execute_query(
                                update_status_sql,
                                (new_project_status, project_actual_start, project_actual_end, project_id)
                            )
                            print(f"✅ 项目 {project_name} 状态已更新：{current_status} -> {new_project_status}")
                        else:
                            print(f"ℹ️ 项目 {project_name} 状态未变化：{current_status}")
                    else:
                        print(f"⚠️ 无法计算项目状态：缺少计划日期")
                else:
                    print(f"⚠️ 项目 {project_name} 没有任务数据，无法计算状态")
        except Exception as e:
            print(f"⚠️ 更新项目状态失败：{e}")
            import traceback
            traceback.print_exc()
            # 不阻断主流程，继续执行
        
        # 记录修改日志（在项目信息和状态都更新完成后）
        log_sql = """
        INSERT INTO project_modifications 
        (project_id, modifier_name, modifier_ip, modification_type, old_values, new_values, remarks)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        # 准备修改前后的值
        old_values = {}
        new_values = {}
        
        for field, new_value in field_mapping.items():
            old_value = old_project.get(field)
            if new_value is not None and new_value != '' and str(new_value) != str(old_value):
                old_values[field] = old_value
                new_values[field] = new_value
        
        # 处理进度字段
        if 'progress' in project_data:
            old_progress = old_project.get('progress')
            new_progress = project_data['progress']
            if str(new_progress) != str(old_progress):
                old_values['progress'] = old_progress
                new_values['progress'] = new_progress
        
        # 插入修改日志
        log_params = (
            project_id,
            modifier_name,
            modifier_ip,
            '项目信息修改',
            json.dumps(old_values, ensure_ascii=False) if old_values else None,
            json.dumps(new_values, ensure_ascii=False) if new_values else None,
            remarks
        )
        
        log_result = execute_query(log_sql, log_params)
        
        # 更新成功后，重新计算并更新项目状态（基于任务数据）
        try:
            from ..services.project_service import ProjectService
            
            project_name = old_project.get('project_name')
            if project_name:
                print(f"开始重新计算项目状态：{project_name}")
                
                # 查询该项目的所有任务，按照 WBS 编码排序（转换为数字后排序）
                last_task_sql = """
                SELECT planned_start_date, planned_end_date, actual_start_date, actual_end_date, wbs_code
                FROM project_tasks
                WHERE project_name = %s
                ORDER BY CAST(wbs_code AS UNSIGNED) DESC
                LIMIT 1
                """
                last_task_result = execute_query(last_task_sql, (project_name,), fetch_all=True)
                
                # 获取最后一个子任务的实际完成时间
                last_actual_end = last_task_result[0].get('actual_end_date') if last_task_result else None
                
                # 汇总所有任务的日期信息（用于计划时间和实际开始时间）
                all_tasks_sql = """
                SELECT planned_start_date, planned_end_date, actual_start_date, actual_end_date
                FROM project_tasks
                WHERE project_name = %s
                """
                all_tasks = execute_query(all_tasks_sql, (project_name,), fetch_all=True) or []
                
                if all_tasks:
                    all_planned_starts = [t['planned_start_date'] for t in all_tasks if t.get('planned_start_date')]
                    all_planned_ends = [t['planned_end_date'] for t in all_tasks if t.get('planned_end_date')]
                    all_actual_starts = [t['actual_start_date'] for t in all_tasks if t.get('actual_start_date')]
                    
                    # 取最早的计划开始时间、最晚的计划结束时间、最早的实际开始时间
                    project_planned_start = min(all_planned_starts) if all_planned_starts else None
                    project_planned_end = max(all_planned_ends) if all_planned_ends else None
                    project_actual_start = min(all_actual_starts) if all_actual_starts else None
                    
                    # 项目的实际完成时间严格取最后一个子任务的实际完成时间
                    project_actual_end = last_actual_end
                    
                    # 使用 ProjectService 计算项目状态
                    if project_planned_start and project_planned_end:
                        new_project_status = ProjectService.calculate_project_status(
                            project_planned_start,
                            project_planned_end,
                            project_actual_start,
                            project_actual_end,
                            project_id  # 传入项目ID以检查异常子任务
                        )
                        
                        # 如果计算出的状态与当前不同，则更新
                        current_status = old_project.get('project_status')
                        if str(new_project_status) != str(current_status):
                            update_status_sql = """
                            UPDATE projects 
                            SET project_status = %s,
                                actual_start_date = %s,
                                actual_end_date = %s,
                                updated_at = NOW()
                            WHERE project_id = %s
                            """
                            
                            execute_query(
                                update_status_sql,
                                (new_project_status, project_actual_start, project_actual_end, project_id)
                            )
                            print(f"✅ 项目 {project_name} 状态已更新为：{new_project_status}")
                        else:
                            print(f"ℹ️ 项目 {project_name} 状态未变化：{current_status}")
                    else:
                        print(f"⚠️ 无法计算项目状态：缺少计划日期")
        except Exception as e:
            print(f"⚠️ 更新项目状态失败：{e}")
            # 不阻断主流程
        
        # 返回成功消息
        return {
            "success": True,
            "message": "项目修改成功" if update_result and update_result > 0 else "项目数据未发生变化",
            "project_id": project_id,
            "modified_fields": list(new_values.keys()),
            "modifier_name": modifier_name,
            "modification_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"修改项目出错: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"修改项目失败: {str(e)}")

# 31. 获取项目列表
@router.get("/projects-list")
async def get_projects_list():
    """获取项目列表"""
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return []

        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return []

        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return []

        # 查询项目列表
        projects_sql = """
        SELECT DISTINCT project_id, project_name
        FROM projects
        ORDER BY project_name
        """

        projects_results = execute_query(projects_sql, fetch_all=True) or []

        # 格式化返回数据
        formatted_results = []
        for result in projects_results:
            if result is not None:
                formatted_results.append({
                    "project_id": result.get('project_id'),
                    "project_name": result.get('project_name', '')
                })

        return formatted_results
    except Exception as e:
        print(f"获取项目列表数据出错: {e}")
        return []

# 32. 批量删除项目
@router.post("/projects/batch-delete")
async def batch_delete_projects(project_ids: List[int]):
    """批量删除项目及其相关数据"""
    try:
        if not project_ids:
            raise HTTPException(status_code=400, detail="请提供要删除的项目ID列表")
        
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            raise HTTPException(status_code=404, detail="projects表不存在")
        
        # 验证所有项目ID都存在
        placeholders = ','.join(['%s'] * len(project_ids))
        check_sql = f"SELECT project_id FROM projects WHERE project_id IN ({placeholders})"
        existing_projects = execute_query(check_sql, tuple(project_ids), fetch_all=True)
        
        if not existing_projects:
            raise HTTPException(status_code=404, detail="指定的项目不存在")
        
        existing_ids = [proj['project_id'] for proj in existing_projects]
        not_found_ids = [pid for pid in project_ids if pid not in existing_ids]
        
        if not_found_ids:
            raise HTTPException(status_code=404, detail=f"以下项目ID不存在: {not_found_ids}")
        
        # 开始事务删除
        deleted_count = 0
        
        # 删除相关的project_tasks数据
        delete_project_tasks_sql = f"DELETE FROM project_tasks WHERE project_id IN ({placeholders})"
        project_tasks_result = execute_query(delete_project_tasks_sql, tuple(project_ids))
        
        # 删除相关的子任务数据
        delete_subtasks_sql = f"DELETE FROM subtasks WHERE project_id IN ({placeholders})"
        subtasks_result = execute_query(delete_subtasks_sql, tuple(project_ids))
        
        # 删除项目数据
        delete_projects_sql = f"DELETE FROM projects WHERE project_id IN ({placeholders})"
        projects_result = execute_query(delete_projects_sql, tuple(project_ids))
        
        if projects_result is not None:
            deleted_count = projects_result
        
        return {
            "success": True,
            "message": f"成功删除 {deleted_count} 个项目及相关数据",
            "deleted_count": deleted_count,
            "deleted_project_ids": project_ids,
            "details": {
                "project_tasks_deleted": project_tasks_result if 'project_tasks_result' in locals() else 0,
                "subtasks_deleted": subtasks_result if 'subtasks_result' in locals() else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"批量删除项目出错: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

# 33. 删除单个项目
@router.delete("/projects/{project_id}")
async def delete_single_project(project_id: int):
    """删除单个项目及其相关数据"""
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            raise HTTPException(status_code=404, detail="projects表不存在")
        
        # 检查项目是否存在
        check_sql = "SELECT project_id FROM projects WHERE project_id = %s"
        project = execute_query(check_sql, (project_id,))
        
        if not project:
            raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
        
        # 开始事务删除
        
        # 删除相关的project_tasks数据
        delete_project_tasks_sql = "DELETE FROM project_tasks WHERE project_id = %s"
        execute_query(delete_project_tasks_sql, (project_id,))
        
        # 删除相关的子任务数据
        delete_subtasks_sql = "DELETE FROM subtasks WHERE project_id = %s"
        execute_query(delete_subtasks_sql, (project_id,))
        
        # 删除项目数据
        delete_project_sql = "DELETE FROM projects WHERE project_id = %s"
        result = execute_query(delete_project_sql, (project_id,))
        
        if result is None or result == 0:
            raise HTTPException(status_code=400, detail="删除项目失败")
        
        return {
            "success": True,
            "message": f"项目 {project_id} 删除成功",
            "deleted_project_id": project_id,
            "details": {
                "project_tasks_deleted": 1,  # 这里可以根据实际情况调整
                "subtasks_deleted": 1
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除项目出错：{e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除失败：{str(e)}")

# 34. 刷新所有项目状态
@router.post("/projects/refresh-status")
async def refresh_projects_status():
    """刷新所有项目状态 - 根据最新的任务数据重新计算并更新项目状态"""
    try:
        from ..services.project_service import ProjectService
        
        print("\n========== 开始刷新所有项目状态 ==========")
        
        # 获取所有项目
        get_all_projects_sql = "SELECT project_id, project_name, project_status FROM projects"
        all_projects = execute_query(get_all_projects_sql, fetch_all=True) or []
        
        if not all_projects:
            return {
                "success": True,
                "message": "没有项目需要更新",
                "updated_count": 0
            }
        
        updated_count = 0
        
        for project in all_projects:
            try:
                project_name = project.get('project_name')
                current_status = project.get('project_status')
                
                if not project_name:
                    continue
                
                # 查询该项目的所有任务，按照 WBS 编码排序（转换为数字后排序）
                all_tasks_sql = """
                SELECT planned_start_date, planned_end_date, actual_start_date, actual_end_date, wbs_code
                FROM project_tasks
                WHERE project_name = %s
                ORDER BY CAST(wbs_code AS UNSIGNED) DESC
                LIMIT 1
                """
                last_task = execute_query(all_tasks_sql, (project_name,), fetch_all=True)
                
                if not last_task:
                    print(f"⚠️ 项目 {project_name} 没有任务数据")
                    continue
                
                # 获取最后一个子任务的实际完成时间
                last_actual_end = last_task[0].get('actual_end_date') if last_task else None
                
                # 汇总所有任务的日期信息（用于计划时间和实际开始时间）
                all_tasks_full_sql = """
                SELECT planned_start_date, planned_end_date, actual_start_date, actual_end_date
                FROM project_tasks
                WHERE project_name = %s
                """
                all_tasks = execute_query(all_tasks_full_sql, (project_name,), fetch_all=True) or []
                
                all_planned_starts = [t['planned_start_date'] for t in all_tasks if t.get('planned_start_date')]
                all_planned_ends = [t['planned_end_date'] for t in all_tasks if t.get('planned_end_date')]
                all_actual_starts = [t['actual_start_date'] for t in all_tasks if t.get('actual_start_date')]
                
                # 取最早的计划开始时间、最晚的计划结束时间、最早的实际开始时间
                project_planned_start = min(all_planned_starts) if all_planned_starts else None
                project_planned_end = max(all_planned_ends) if all_planned_ends else None
                project_actual_start = min(all_actual_starts) if all_actual_starts else None
                
                # 项目的实际完成时间严格取最后一个子任务的实际完成时间
                project_actual_end = last_actual_end
                
                # 使用 ProjectService 计算项目状态
                if project_planned_start and project_planned_end:
                    new_project_status = ProjectService.calculate_project_status(
                        project_planned_start,
                        project_planned_end,
                        project_actual_start,
                        project_actual_end,
                        project['project_id']  # 传入项目ID以检查异常子任务
                    )
                    
                    # 如果计算出的状态与当前不同，则更新
                    if str(new_project_status) != str(current_status):
                        update_status_sql = """
                        UPDATE projects 
                        SET project_status = %s,
                            actual_start_date = %s,
                            actual_end_date = %s,
                            updated_at = NOW()
                        WHERE project_id = %s
                        """
                        
                        execute_query(
                            update_status_sql,
                            (new_project_status, project_actual_start, project_actual_end, project['project_id'])
                        )
                        
                        updated_count += 1
                        print(f"✅ 项目 {project_name} 状态已更新：{current_status} -> {new_project_status}")
                    else:
                        print(f"ℹ️ 项目 {project_name} 状态未变化：{current_status}")
                else:
                    print(f"⚠️ 项目 {project_name} 无法计算状态：缺少计划日期")
                    
            except Exception as e:
                print(f"⚠️ 处理项目 {project_name} 时出错：{e}")
                continue
        
        print(f"\n========== 刷新完成：共更新 {updated_count} 个项目 ==========")
        
        return {
            "success": True,
            "message": f"已刷新 {len(all_projects)} 个项目的状态，其中 {updated_count} 个项目状态发生变化",
            "total_count": len(all_projects),
            "updated_count": updated_count
        }
        
    except Exception as e:
        print(f"❌ 刷新项目状态失败：{e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"刷新项目状态失败：{str(e)}")