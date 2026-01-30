#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
# 添加项目backend目录到模块搜索路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'project-backend'))

# 导入配置
try:
    import config.config as config
except ImportError:
    # 如果直接导入失败，尝试添加路径后导入
    backend_path = os.path.join(os.path.dirname(__file__), 'project-backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    import config.config as config

import mysql.connector

def check_jgjncr_tables():
    """检查jgjncr和jgjncr_copy表结构"""
    try:
        # 连接数据库
        db_config = config.DATABASE_CONFIG
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 检查jgjncr_copy表是否存在
        cursor.execute("SHOW TABLES LIKE 'jgjncr_copy'")
        result = cursor.fetchone()
        if result:
            print('jgjncr_copy表存在')
            # 查看表结构
            cursor.execute('DESCRIBE jgjncr_copy')
            columns = cursor.fetchall()
            print('jgjncr_copy表结构:')
            for col in columns:
                print(f'  {col[0]}: {col[1]}')
        else:
            print('jgjncr_copy表不存在')

        print()

        # 检查jgjncr表
        cursor.execute("SHOW TABLES LIKE 'jgjncr'")
        result = cursor.fetchone()
        if result:
            print('jgjncr表存在')
            # 查看表结构
            cursor.execute('DESCRIBE jgjncr')
            columns = cursor.fetchall()
            print('jgjncr表结构:')
            for col in columns:
                print(f'  {col[0]}: {col[1]}')
        else:
            print('jgjncr表不存在')

        conn.close()
    except Exception as e:
        print(f"连接数据库时出错: {e}")

if __name__ == "__main__":
    check_jgjncr_tables()