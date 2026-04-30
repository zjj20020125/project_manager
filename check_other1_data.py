"""
检查other1字段(新造/检修类型)的数据
"""
import mysql.connector

# 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'zjj520111314',
    'database': 'jgj-project'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # 查询other1字段的所有不同值
    sql = """
    SELECT DISTINCT other1, COUNT(*) as count
    FROM customer_quality
    WHERE other1 IS NOT NULL AND other1 != ''
    GROUP BY other1
    ORDER BY count DESC
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    
    print("=" * 60)
    print("other1字段(新造/检修类型)数据统计")
    print("=" * 60)
    
    if results:
        print(f"\n找到 {len(results)} 种不同的值:\n")
        for row in results:
            print(f"  - '{row['other1']}': {row['count']} 条记录")
    else:
        print("\n⚠️  other1字段没有数据!")
        print("\n建议:")
        print("  1. 检查Excel导入时是否正确映射了该字段")
        print("  2. 查看原始Excel文件中对应的列名")
        print("  3. 可能需要重新导入数据")
    
    # 查看前5条记录的other1值
    print("\n" + "=" * 60)
    print("前5条记录的other1字段值:")
    print("=" * 60)
    sql2 = "SELECT id, product_name, other1 FROM customer_quality LIMIT 5"
    cursor.execute(sql2)
    sample_records = cursor.fetchall()
    
    for record in sample_records:
        print(f"  ID={record['id']}, 产品={record['product_name']}, other1='{record['other1']}'")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
