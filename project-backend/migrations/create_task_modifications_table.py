"""
创建项目任务修改记录表
用于记录所有任务的修改历史
"""

import sys
import os

# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import execute_query

def create_task_modifications_table():
    """创建任务修改记录表"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS project_task_modifications (
        modification_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '修改记录 ID',
        task_id INT NOT NULL COMMENT '任务 ID',
        modifier_name VARCHAR(100) NOT NULL COMMENT '修改人姓名',
        modification_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
        remarks_for_modification TEXT COMMENT '修改说明',
        original_data JSON COMMENT '原始数据',
        modified_data JSON COMMENT '修改后的数据',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        INDEX idx_task_id (task_id),
        INDEX idx_modification_time (modification_time),
        INDEX idx_modifier_name (modifier_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目任务修改记录表';
    """
    
    try:
        print("开始创建任务修改记录表...")
        execute_query(create_table_sql)
        print("✅ 任务修改记录表创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建任务修改记录表失败：{e}")
        return False

if __name__ == "__main__":
    success = create_task_modifications_table()
    if success:
        print("\n迁移完成！")
    else:
        print("\n迁移失败，请检查错误信息")
        sys.exit(1)
