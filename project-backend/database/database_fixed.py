import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling

# 从 config 模块导入配置
import config.config
DATABASE_CONFIG = config.config.DATABASE_CONFIG

# 创建数据库连接池
connection_pool = None

def get_connection_pool():
    """获取或创建数据库连接池"""
    global connection_pool
   if connection_pool is None:
        try:
            connection_pool = pooling.MySQLConnectionPool(
                pool_name="ncr_pool",
                pool_size=5,
                pool_reset_session=True,
                **DATABASE_CONFIG
            )
           print("✅ 数据库连接池创建成功")
        except Error as e:
           print(f"❌ 创建数据库连接池错误：{e}")
            return None
    return connection_pool

def get_db_connection():
    """从连接池获取数据库连接"""
    pool = get_connection_pool()
   if pool:
        try:
            return pool.get_connection()
        except Error as e:
           print(f"从连接池获取连接错误：{e}")
            return None
    return None

def execute_query(query, params=None, fetch_all=False, fetch_one=True):
    """执行 SQL 查询"""
    connection = get_db_connection()
   if not connection:
        return None
    
    cursor = connection.cursor(buffered=True, dictionary=True)
    try:
        cursor.execute(query, params or ())
        
       if query.strip().upper().startswith('SELECT'):
           if fetch_all:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
            return result
        elif query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            connection.commit()
           if query.strip().upper().startswith('INSERT'):
                lastrowid = cursor.lastrowid
                return lastrowid
            else:
                return cursor.rowcount
        else:
            connection.commit()
           if fetch_all:
                result = cursor.fetchall()
            elif fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            return result
    except Error as e:
       print(f"执行查询错误：{e}")
       if not query.strip().upper().startswith('SELECT'):
            connection.rollback()
        return None
    finally:
       if connection.is_connected():
            cursor.close()
            connection.close()
