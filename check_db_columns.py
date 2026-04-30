"""检查 customer_quality 表的字段"""
import pymysql

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "zjj520111314",
    "db_name": "jgj-project"
}

try:
    # 连接数据库
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["db_name"],
        charset="utf8mb4"
    )
    
    cursor = conn.cursor()
    
    # 查询表的所有列
    sql = """
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_COMMENT
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = %s 
      AND TABLE_NAME = 'customer_quality'
    ORDER BY ORDINAL_POSITION
    """
    
    cursor.execute(sql, (DB_CONFIG["db_name"]))
    columns = cursor.fetchall()
    
    print(f"\n=== customer_quality 表结构（共 {len(columns)} 列）===\n")
    print(f"{'序号':<4} {'列名':<30} {'类型':<15} {'长度':<6} {'可空':<6} {'注释'}")
    print("-" * 100)
    
    for i, col in enumerate(columns, 1):
        col_name = col[0]
        data_type = col[1]
        max_length = col[2] if col[2] else '-'
        is_nullable = col[3]
        comment = col[4] if col[4] else '-'
        
        print(f"{i:<4} {col_name:<30} {data_type:<15} {str(max_length):<6} {is_nullable:<6} {comment}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 查询失败：{e}")
    raise
