"""
检查customer_quality表的字段 - 使用项目配置
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project-backend'))

from database.database import get_db_connection

conn = get_db_connection()
if not conn:
    print("数据库连接失败")
    sys.exit(1)

try:
    cursor = conn.cursor(dictionary=True)
    
    # 查询表结构
    cursor.execute("DESCRIBE customer_quality")
    columns = cursor.fetchall()
    
    print("=" * 80)
    print("customer_quality 表结构")
    print("=" * 80)
    print(f"\n共 {len(columns)} 个字段:\n")
    
    for i, col in enumerate(columns, 1):
        print(f"{i:2d}. {col['Field']:35s} | {col['Type']:20s}")
    
    # 查找包含repair或production的字段
    print("\n" + "=" * 80)
    print("包含 'repair' 或 'production' 的字段:")
    print("=" * 80)
    
    repair_fields = [col for col in columns if 'repair' in col['Field'].lower() or 'production' in col['Field'].lower()]
    
    if repair_fields:
        for col in repair_fields:
            print(f"  ✅ {col['Field']} ({col['Type']})")
    else:
        print("  ❌ 未找到相关字段")
    
    # 如果找到production_repair_type字段,检查数据
    has_production_repair = any(col['Field'] == 'production_repair_type' for col in columns)
    
    if has_production_repair:
        print("\n" + "=" * 80)
        print("production_repair_type 字段数据统计:")
        print("=" * 80)
        
        sql = """
        SELECT DISTINCT production_repair_type, COUNT(*) as count
        FROM customer_quality
        WHERE production_repair_type IS NOT NULL AND production_repair_type != ''
        GROUP BY production_repair_type
        ORDER BY count DESC
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        
        if results:
            print(f"\n找到 {len(results)} 种不同的值:\n")
            for row in results:
                print(f"  - '{row['production_repair_type']}': {row['count']} 条记录")
        else:
            print("\n⚠️  production_repair_type 字段没有数据!")
    
    cursor.close()
finally:
    conn.close()
