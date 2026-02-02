import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import mysql.connector
from mysql.connector import Error

# 从config模块导入配置
import config.config
DATABASE_CONFIG = config.config.DATABASE_CONFIG

def get_db_connection():
    """获取数据库连接"""
    connection = None
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
    return connection

def execute_query(query, params=None, fetch_all=False, fetch_one=True):
    """执行SQL查询"""
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(buffered=True, dictionary=True)  # 返回字典格式，并使用buffered参数避免未消费结果
    try:
        cursor.execute(query, params or ())
        
        # 对于SELECT查询，不执行commit
        if query.strip().upper().startswith('SELECT'):
            # 返回查询结果
            if fetch_all:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
            return result
        elif query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            # 对于INSERT, UPDATE, DELETE查询，执行commit
            connection.commit()
            # 对于INSERT查询，如果需要获取LAST_INSERT_ID，则单独处理
            if query.strip().upper().startswith('INSERT'):
                lastrowid = cursor.lastrowid
                return lastrowid
            else:
                # 对于UPDATE, DELETE查询，返回受影响的行数
                return cursor.rowcount
        else:
            # 对于其他查询，执行commit并返回结果
            connection.commit()
            if fetch_all:
                result = cursor.fetchall()
            elif fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            return result
    except Error as e:
        print(f"执行查询错误: {e}")
        if not query.strip().upper().startswith('SELECT'):
            connection.rollback()
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()