"""直接查询数据库验证 responsible_team 字段的数据"""
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "zjj520111314",
    "database": "jgj-project",
    "charset": "utf8mb4"
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 查询所有记录的 responsible_team 字段
    sql = """
    SELECT 
        id,
        serial_number,
        product_name,
        responsible_team,
        LENGTH(responsible_team) as team_length,
        TRIM(responsible_team) as team_trimmed
    FROM customer_quality
    LIMIT 10
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    print(f"\n=== customer_quality 表数据抽样（前 10 条）===\n")
    print(f"{'ID':<4} {'序号':<6} {'产品名称':<15} {'responsible_team':<20} {'长度':<6} {'TRIM 后':<20}")
    print("-" * 90)
    
    for row in results:
        id_val = row[0]
        serial = row[1]
        product = row[2][:12] if row[2] else ""
        team = row[3] if row[3] else "(NULL)"
        length = row[4]
        trimmed = row[5] if row[5] else "(空)"
        
        print(f"{id_val:<4} {serial:<6} {product:<15} {team:<20} {length:<6} {trimmed:<20}")
    
    # 统计非空数据
    count_sql = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN responsible_team IS NULL THEN 1 ELSE 0 END) as null_count,
        SUM(CASE WHEN TRIM(responsible_team) = '' THEN 1 ELSE 0 END) as empty_count,
        SUM(CASE WHEN TRIM(responsible_team) != '' THEN 1 ELSE 0 END) as non_empty_count
    FROM customer_quality
    """
    
    cursor.execute(count_sql)
    stats = cursor.fetchone()
    
    print(f"\n\n=== 统计数据 ===")
    print(f"总记录数：{stats[0]}")
    print(f"NULL 值：{stats[1]}")
    print(f"空字符串：{stats[2]}")
    print(f"非空数据：{stats[3]}")
    
    if stats[3] > 0:
        # 获取所有不同的非空值
        distinct_sql = """
        SELECT DISTINCT responsible_team, COUNT(*) as count
        FROM customer_quality
        WHERE TRIM(responsible_team) != ''
        GROUP BY responsible_team
        ORDER BY count DESC
        """
        cursor.execute(distinct_sql)
        distinct_values = cursor.fetchall()
        
        print(f"\n\n=== 非空值列表（共 {len(distinct_values)} 种）===")
        for i, val in enumerate(distinct_values, 1):
            print(f"{i}. '{val[0]}' - {val[1]}条记录")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 查询失败：{e}")
    raise
