"""检查 responsible_team 字段的数据"""
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
    
    # 查询 responsible_team 的所有不同值
    sql = """
    SELECT DISTINCT responsible_team, COUNT(*) as count
    FROM customer_quality
    WHERE responsible_team IS NOT NULL AND TRIM(responsible_team) != ''
    GROUP BY responsible_team
    ORDER BY count DESC
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    print(f"\n=== responsible_team 字段数据统计 ===\n")
    
    if results:
        print(f"共有 {len(results)} 个不同的值:\n")
        for i, row in enumerate(results, 1):
            team = row[0]
            count = row[1]
            print(f"{i}. '{team}' - {count}条记录")
    else:
        print("⚠️  responsible_team 字段中没有非空数据！")
        
        # 检查是否有其他可能的字段
        check_sql = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN responsible_team IS NULL THEN 1 ELSE 0 END) as null_count,
            SUM(CASE WHEN TRIM(responsible_team) = '' THEN 1 ELSE 0 END) as empty_count
        FROM customer_quality
        """
        cursor.execute(check_sql)
        stats = cursor.fetchone()
        
        print(f"\n总记录数：{stats[0]}")
        print(f"NULL 值：{stats[1]}")
        print(f"空字符串：{stats[2]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 查询失败：{e}")
    raise
