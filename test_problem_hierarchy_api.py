"""
测试问题层级详情API接口
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project-backend'))

from database.database import execute_query

def test_problem_hierarchy_api():
    """测试问题层级详情查询"""
    
    print("=" * 80)
    print("🧪 测试问题层级详情API")
    print("=" * 80)
    
    # 检查表是否存在
    check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
    table_exists = execute_query(check_table_sql)
    
    if not table_exists:
        print("❌ jgjncr_copy表不存在")
        return
    
    print("✅ jgjncr_copy表存在")
    
    # 检查字段是否存在
    describe_sql = "DESCRIBE jgjncr_copy"
    columns_result = execute_query(describe_sql, fetch_all=True)
    
    if not columns_result:
        print("❌ 无法获取表结构")
        return
    
    column_names = [col['Field'] for col in columns_result if 'Field' in col]
    print(f"\n📋 表中共有 {len(column_names)} 个字段")
    
    # 检查关键字段
    key_fields = ['wtdx', 'wtfl', 'wtflxf']
    print("\n🔍 检查关键字段:")
    for field in key_fields:
        exists = field in column_names
        status = "✅" if exists else "❌"
        print(f"  {status} {field}: {'存在' if exists else '不存在'}")
    
    # 统计各字段的唯一值数量
    print("\n📊 统计各字段的数据分布:")
    for field in key_fields:
        if field in column_names:
            count_sql = f"""
            SELECT {field}, COUNT(*) as count 
            FROM jgjncr_copy 
            WHERE {field} IS NOT NULL AND TRIM({field}) != ''
            GROUP BY {field}
            ORDER BY count DESC
            LIMIT 5
            """
            results = execute_query(count_sql, fetch_all=True)
            
            if results:
                print(f"\n  📌 {field} (前5条):")
                for row in results:
                    value = row.get(field, 'NULL')
                    count = row.get('count', 0)
                    print(f"     - {value}: {count} 条")
            else:
                print(f"\n  ⚠️  {field}: 无数据")
    
    # 测试具体查询
    print("\n\n🧪 测试具体查询:")
    
    # 先获取一个实际的wtdx值
    sample_sql = """
    SELECT wtdx 
    FROM jgjncr_copy 
    WHERE wtdx IS NOT NULL AND TRIM(wtdx) != ''
    LIMIT 1
    """
    sample_result = execute_query(sample_sql, fetch_one=True)
    
    if sample_result and sample_result.get('wtdx'):
        test_name = sample_result['wtdx']
        print(f"\n  🔍 使用测试值: wtdx = '{test_name}'")
        
        # 执行查询
        query_sql = """
        SELECT * FROM jgjncr_copy 
        WHERE wtdx = %s
        LIMIT 3
        """
        results = execute_query(query_sql, (test_name,), fetch_all=True)
        
        if results:
            print(f"  ✅ 查询成功! 找到 {len(results)} 条记录")
            print(f"\n  📋 第一条记录的字段:")
            first_record = results[0]
            for key, value in list(first_record.items())[:10]:
                print(f"     - {key}: {value}")
        else:
            print(f"  ❌ 未找到记录")
    else:
        print("  ⚠️  没有可用的wtdx数据进行测试")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_problem_hierarchy_api()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
