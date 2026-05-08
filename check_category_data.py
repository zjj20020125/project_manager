import sys
sys.path.insert(0, 'project-backend')
from database.database import execute_query

print("=" * 80)
print("检查问题分类1和补充分类2的数据")
print("=" * 80)

# 检查 problem_category_1
sql1 = """
SELECT DISTINCT problem_category_1, COUNT(*) as count
FROM customer_quality
WHERE problem_category_1 IS NOT NULL AND TRIM(problem_category_1) != ''
GROUP BY problem_category_1
ORDER BY count DESC
"""

print("\n📊 problem_category_1 (问题分类1) 分布:")
result1 = execute_query(sql1, fetch_all=True)
if result1:
    for row in result1:
        print(f"   - {row['problem_category_1']}: {row['count']}条")
else:
    print("   ❌ 没有数据")

# 检查 supplement_category_2
sql2 = """
SELECT DISTINCT supplement_category_2, COUNT(*) as count
FROM customer_quality
WHERE supplement_category_2 IS NOT NULL AND TRIM(supplement_category_2) != ''
GROUP BY supplement_category_2
ORDER BY count DESC
"""

print("\n📊 supplement_category_2 (补充分类2) 分布:")
result2 = execute_query(sql2, fetch_all=True)
if result2:
    for row in result2:
        print(f"   - {row['supplement_category_2']}: {row['count']}条")
else:
    print("   ❌ 没有数据")

# 检查总记录数
total_sql = "SELECT COUNT(*) as total FROM customer_quality"
total_result = execute_query(total_sql, fetch_one=True)
print(f"\n📋 总记录数: {total_result['total']}")

print("\n" + "=" * 80)
