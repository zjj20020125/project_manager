"""
检查customer_quality表的字段结构
"""
import mysql.connector

# 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'project_management'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # 查询表结构
    sql = "DESCRIBE customer_quality"
    cursor.execute(sql)
    columns = cursor.fetchall()
    
    print("=" * 80)
    print("customer_quality 表结构")
    print("=" * 80)
    print(f"\n共 {len(columns)} 个字段:\n")
    
    for i, col in enumerate(columns, 1):
        print(f"{i:2d}. {col['Field']:30s} | {col['Type']:20s} | Null: {col['Null']:3s} | Key: {col['Key']:5s}")
    
    # 查找包含repair的字段
    print("\n" + "=" * 80)
    print("包含 'repair' 或 'production' 的字段:")
    print("=" * 80)
    
    repair_fields = [col for col in columns if 'repair' in col['Field'].lower() or 'production' in col['Field'].lower()]
    
    if repair_fields:
        for col in repair_fields:
            print(f"  - {col['Field']} ({col['Type']})")
    else:
        print("  未找到相关字段")
    
    # 检查production_repair_type字段是否有数据
    print("\n" + "=" * 80)
    print("检查 production_repair_type 字段数据:")
    print("=" * 80)
    
    try:
        sql2 = """
        SELECT DISTINCT production_repair_type, COUNT(*) as count
        FROM customer_quality
        WHERE production_repair_type IS NOT NULL AND production_repair_type != ''
        GROUP BY production_repair_type
        ORDER BY count DESC
        """
        cursor.execute(sql2)
        results = cursor.fetchall()
        
        if results:
            print(f"\n找到 {len(results)} 种不同的值:\n")
            for row in results:
                print(f"  - '{row['production_repair_type']}': {row['count']} 条记录")
        else:
            print("\n⚠️  production_repair_type 字段没有数据!")
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
        print("   可能该字段不存在")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
