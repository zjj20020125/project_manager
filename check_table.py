"""检查 customer_quality 表结构"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project-backend'))

from database.database import get_db_connection

conn = get_db_connection()
if not conn:
    print("数据库连接失败")
    sys.exit(1)

try:
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute('SHOW TABLES LIKE "customer_quality"')
    tables = cursor.fetchall()
    
    if not tables:
        print("❌ customer_quality 表不存在！")
        sys.exit(1)
    
    print("✅ customer_quality 表存在\n")
    
    # 显示表结构
    print("=== 表结构 ===")
    cursor.execute('DESCRIBE customer_quality')
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]:<30} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL':<10}")
    
    # 检查数据量
    cursor.execute('SELECT COUNT(*) FROM customer_quality')
    count = cursor.fetchone()[0]
    print(f"\n=== 数据统计 ===")
    print(f"总记录数：{count}")
    
finally:
    conn.close()
