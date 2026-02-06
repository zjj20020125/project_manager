"""
数据管理路由模块
包含数据导入导出相关的API接口
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

# 28. 导出项目数据
@router.post("/projects/export")
async def export_projects(request_data: Dict):
    """导出项目数据"""
    try:
        import pandas as pd
        from fastapi.responses import StreamingResponse
        import io
        
        # 获取要导出的项目ID列表
        project_ids = request_data.get('project_ids', [])

        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            raise HTTPException(status_code=400, detail="数据库中不存在projects表")

        # 查询项目数据
        if project_ids:  # 如果指定了项目ID，则导出选中的项目
            placeholders = ','.join(['%s'] * len(project_ids))
            select_sql = f"SELECT * FROM projects WHERE project_id IN ({placeholders}) ORDER BY created_at DESC"
            projects = execute_query(select_sql, tuple(project_ids), fetch_all=True) or []
        else:  # 否则导出所有项目
            select_sql = "SELECT * FROM projects ORDER BY created_at DESC"
            projects = execute_query(select_sql, fetch_all=True) or []

        if not projects:
            raise HTTPException(status_code=404, detail="没有找到要导出的项目数据")

        # 将数据转换为DataFrame，并确保数据类型正确
        processed_projects = []
        for project in projects:
            processed_project = {}
            for key, value in project.items():
                # 处理日期和时间类型
                if isinstance(value, (datetime, type(pd.Timestamp))):
                    processed_project[key] = str(value)
                # 处理十进制类型
                elif hasattr(value, 'quantize'):  # 检查是否为Decimal类型
                    processed_project[key] = float(value)
                # 其他类型直接使用
                else:
                    processed_project[key] = value
            processed_projects.append(processed_project)

        df = pd.DataFrame(processed_projects)

        # 创建内存中的字节流
        output = io.BytesIO()

        # 将DataFrame写入Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='项目数据')

        # 获取字节流内容
        output.seek(0)

        # 创建StreamingResponse返回Excel文件
        def iterfile():
            yield output.getvalue()

        return StreamingResponse(
            iterfile(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=\"项目数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx\""}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"导出项目数据出错: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")