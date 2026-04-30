"""检查问题定性数据"""
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "zjj520111314",
    "database": "jgj-project",
    "charset": "utf8mb4"
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# 查询问题定性数据
sql = """
SELECT DISTINCT problem_nature 
FROM customer_quality 
WHERE problem_nature IS NOT NULL AND TRIM(problem_nature) != ''
ORDER BY problem_nature
LIMIT 10
"""

cursor.execute(sql)
results = cursor.fetchall()

print("\n=== 数据库中的问题定性数据 ===")
if results:
    print(f"共找到 {len(results)} 种问题定性类型:")
    for i, row in enumerate(results, 1):
        print(f"  {i}. {row[0]}")
else:
    print("⚠️  未找到任何问题定性数据！")
    print("   请检查数据库中 customer_quality 表的 problem_nature 字段是否有值。")

conn.close()
