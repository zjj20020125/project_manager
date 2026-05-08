"""
检查NCR数据库中SSCX和问题导向字段的实际数据情况
"""
import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project-backend'))

from database.database import execute_query

def check_database():
    """检查数据库表结构和数据"""
    
    print("=" * 80)
    print("开始检查数据库...")
    print("=" * 80)
    
    # 1. 检查jgjncr_copy表是否存在
    print("\n1. 检查jgjncr_copy表是否存在...")
    check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
    table_exists = execute_query(check_table_sql)
    
    if not table_exists:
        print("❌ jgjncr_copy表不存在")
        
        # 尝试检查jgjncr表
        print("\n尝试检查jgjncr表...")
        check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
        table_exists = execute_query(check_table_sql)
        
        if not table_exists:
            print("❌ jgjncr表也不存在")
            return
        
        table_name = 'jgjncr'
        print(f"✅ 找到表: {table_name}")
    else:
        table_name = 'jgjncr_copy'
        print(f"✅ 找到表: {table_name}")
    
    # 2. 检查表结构
    print(f"\n2. 检查{table_name}表结构...")
    describe_sql = f"DESCRIBE {table_name}"
    columns_result = execute_query(describe_sql, fetch_all=True)
    
    if not columns_result:
        print(f"❌ 无法获取{table_name}表结构")
        return
    
    column_names = [col['Field'] for col in columns_result if 'Field' in col]
    print(f"✅ 表中共有 {len(column_names)} 个字段")
    
    # 3. 检查关键字段
    print("\n3. 检查关键字段是否存在...")
    required_fields = ['sscx', 'cjrq', 'wtdx', 'wtfl', 'wtflxfn']
    
    field_status = {}
    for field in required_fields:
        exists = field in column_names
        field_status[field] = exists
        status_icon = "✅" if exists else "❌"
        print(f"   {status_icon} {field}: {'存在' if exists else '不存在'}")
    
    # 4. 检查SSCX数据统计
    if field_status.get('sscx'):
        print("\n4. 检查SSCX字段数据...")
        
        # 总记录数
        total_sql = f"SELECT COUNT(*) as total FROM {table_name}"
        total_result = execute_query(total_sql, fetch_one=True)
        total_count = total_result['total'] if total_result else 0
        print(f"   总记录数: {total_count}")
        
        # SSCX非空记录数
        sscx_not_null_sql = f"""
        SELECT COUNT(*) as count 
        FROM {table_name} 
        WHERE sscx IS NOT NULL AND TRIM(sscx) != '' AND sscx != 'nan' AND sscx != 'NULL'
        """
        sscx_result = execute_query(sscx_not_null_sql, fetch_one=True)
        sscx_count = sscx_result['count'] if sscx_result else 0
        print(f"   SSCX非空记录数: {sscx_count}")
        
        if sscx_count > 0:
            # SSCX分布统计（前15）
            sscx_dist_sql = f"""
            SELECT 
                sscx as category,
                COUNT(*) as count
            FROM {table_name}
            WHERE sscx IS NOT NULL AND TRIM(sscx) != '' AND sscx != 'nan' AND sscx != 'NULL'
            GROUP BY sscx
            ORDER BY count DESC
            LIMIT 15
            """
            sscx_dist_results = execute_query(sscx_dist_sql, fetch_all=True) or []
            
            print(f"\n   SSCX分布统计（前15名）:")
            for i, record in enumerate(sscx_dist_results, 1):
                print(f"      {i}. {record['category']}: {record['count']}")
        else:
            print("   ⚠️ 没有有效的SSCX数据")
    
    # 5. 检查问题导向字段数据
    if field_status.get('wtdx') and field_status.get('wtfl') and field_status.get('wtflxfn'):
        print("\n5. 检查问题导向字段数据...")
        
        # wtdx统计
        wtdx_sql = f"""
        SELECT 
            COALESCE(NULLIF(TRIM(wtdx), ''), '未知导向') as wtdx,
            COUNT(*) as count
        FROM {table_name}
        WHERE wtdx IS NOT NULL AND TRIM(wtdx) != ''
        GROUP BY wtdx
        ORDER BY count DESC
        """
        wtdx_results = execute_query(wtdx_sql, fetch_all=True) or []
        
        print(f"   wtdx（问题导向）分布:")
        if wtdx_results:
            for i, record in enumerate(wtdx_results, 1):
                print(f"      {i}. {record['wtdx']}: {record['count']}")
        else:
            print("      ⚠️ 没有有效的wtdx数据")
        
        # wtfl统计
        wtfl_sql = f"""
        SELECT 
            COALESCE(NULLIF(TRIM(wtfl), ''), '未知分类') as wtfl,
            COUNT(*) as count
        FROM {table_name}
        WHERE wtfl IS NOT NULL AND TRIM(wtfl) != ''
        GROUP BY wtfl
        ORDER BY count DESC
        LIMIT 10
        """
        wtfl_results = execute_query(wtfl_sql, fetch_all=True) or []
        
        print(f"\n   wtfl（问题分类）分布（前10）:")
        if wtfl_results:
            for i, record in enumerate(wtfl_results, 1):
                print(f"      {i}. {record['wtfl']}: {record['count']}")
        else:
            print("      ⚠️ 没有有效的wtfl数据")
        
        # wtflxfn统计
        wtflxfn_sql = f"""
        SELECT 
            COALESCE(NULLIF(TRIM(wtflxfn), ''), '未知细分') as wtflxfn,
            COUNT(*) as count
        FROM {table_name}
        WHERE wtflxfn IS NOT NULL AND TRIM(wtflxfn) != ''
        GROUP BY wtflxfn
        ORDER BY count DESC
        LIMIT 10
        """
        wtflxfn_results = execute_query(wtflxfn_sql, fetch_all=True) or []
        
        print(f"\n   wtflxfn（问题分类细分）分布（前10）:")
        if wtflxfn_results:
            for i, record in enumerate(wtflxfn_results, 1):
                print(f"      {i}. {record['wtflxfn']}: {record['count']}")
        else:
            print("      ⚠️ 没有有效的wtflxfn数据")
    else:
        print("\n5. ⚠️ 问题导向字段不完整，跳过检查")
    
    # 6. 检查时间字段
    print("\n6. 检查时间字段...")
    time_fields = ['create_time', 'created_at', 'update_time', 'updated_at', 'create_date', 'cjrq']
    found_time_fields = [f for f in time_fields if f in column_names]
    
    if found_time_fields:
        print(f"   ✅ 找到时间字段: {', '.join(found_time_fields)}")
        
        # 如果有cjrq，检查近一年的数据
        if 'cjrq' in column_names:
            from datetime import datetime, timedelta
            one_year_ago = datetime.now() - timedelta(days=365)
            one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')
            
            recent_sql = f"""
            SELECT COUNT(*) as count 
            FROM {table_name} 
            WHERE cjrq >= '{one_year_ago_str}'
            """
            recent_result = execute_query(recent_sql, fetch_one=True)
            recent_count = recent_result['count'] if recent_result else 0
            
            print(f"   近一年内的记录数: {recent_count}")
    else:
        print(f"   ❌ 未找到常见的时间字段")
    
    print("\n" + "=" * 80)
    print("数据库检查完成")
    print("=" * 80)

if __name__ == "__main__":
    try:
        check_database()
    except Exception as e:
        print(f"\n❌ 检查过程中出错: {e}")
        import traceback
        traceback.print_exc()
