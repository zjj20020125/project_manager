#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建项目修改记录表的数据库迁移脚本
用于存储项目信息的修改历史
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import execute_query


def create_modification_table():
    """创建项目修改记录表"""
    try:
        # 创建项目修改记录表的SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS project_modifications (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
            project_id INT NOT NULL COMMENT '项目ID',
            modifier_name VARCHAR(100) NOT NULL COMMENT '修改人姓名',
            modifier_ip VARCHAR(45) COMMENT '修改人IP地址',
            modification_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
            modification_type VARCHAR(50) NOT NULL COMMENT '修改类型',
            old_values TEXT COMMENT '修改前的值',
            new_values TEXT COMMENT '修改后的值',
            remarks TEXT COMMENT '修改备注',
            INDEX idx_project_id (project_id),
            INDEX idx_modifier_name (modifier_name),
            INDEX idx_modification_time (modification_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目修改记录表';
        """
        
        # 执行创建表的SQL
        result = execute_query(create_table_sql)
        
        if result is not None:
            print("✅ 项目修改记录表创建成功！")
            
            # 验证表是否创建成功
            verify_sql = "SHOW TABLES LIKE 'project_modifications';"
            table_exists = execute_query(verify_sql)
            
            if table_exists:
                print("📋 表结构信息:")
                print("-" * 50)
                desc_sql = "DESCRIBE project_modifications;"
                columns = execute_query(desc_sql, fetch_all=True)
                if columns:
                    for column in columns:
                        print(f"  {column['Field']}: {column['Type']} ({'必填' if column['Null'] == 'NO' else '可选'})")
            else:
                print("❌ 表创建验证失败")
        else:
            print("❌ 创建表时发生错误")
            
    except Exception as e:
        print(f"❌ 创建表时发生错误: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始创建项目修改记录表...")
    create_modification_table()
    print("🎉 数据库迁移完成！")