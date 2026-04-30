"""
添加测试数据到 problem_category_1 和 supplement_category_2 字段
用于验证前端图表功能
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project-backend'))

from database.database import execute_query

def add_test_data():
    """为现有数据添加问题分类 1 和补充分类 2 的测试数据"""
    
    print("=" * 60)
    print("开始添加测试数据...")
    print("=" * 60)
    
    # 检查表中是否有数据
    count_sql = "SELECT COUNT(*) as count FROM customer_quality"
    result = execute_query(count_sql)
    total_count = result['count'] if result else 0
    
    if total_count == 0:
        print("❌ customer_quality 表中没有数据，请先导入 Excel 数据")
        return False
    
    print(f"✓ 表中共有 {total_count} 条记录")
    
    # 获取所有记录的 ID
    select_sql = "SELECT id FROM customer_quality ORDER BY id"
    records = execute_query(select_sql, fetch_all=True)
    
    if not records:
        print("❌ 未找到任何记录")
        return False
    
    # 定义测试数据分类
    category_1_options = ['设计问题', '工艺问题', '材料问题', '操作问题', '设备问题']
    supplement_2_options = ['原材料', '外协加工', '自主生产', '供应商来料', '客户指定']
    
    # 随机分配测试数据 (按索引取模)
    update_count = 0
    for idx, record in enumerate(records):
        record_id = record['id']
        category_1 = category_1_options[idx % len(category_1_options)]
        supplement_2 = supplement_2_options[idx % len(supplement_2_options)]
        
        update_sql = """
        UPDATE customer_quality 
        SET problem_category_1 = %s, 
            supplement_category_2 = %s 
        WHERE id = %s
        """
        
        result = execute_query(update_sql, (category_1, supplement_2, record_id))
        if result:
            update_count += 1
            print(f"  更新记录 ID={record_id}: problem_category_1='{category_1}', supplement_category_2='{supplement_2}'")
    
    print("\n" + "=" * 60)
    print(f"✓ 成功更新 {update_count} 条记录")
    print("=" * 60)
    
    # 验证更新结果
    print("\n验证更新结果:")
    verify_sql = """
    SELECT problem_category_1, supplement_category_2, COUNT(*) as count 
    FROM customer_quality 
    GROUP BY problem_category_1, supplement_category_2
    ORDER BY count DESC
    """
    result = execute_query(verify_sql, fetch_all=True)
    
    if result:
        print(f"\n{'问题分类 1':<15} {'补充分类 2':<15} {'数量':<10}")
        print("-" * 40)
        for row in result:
            if row['problem_category_1'] and row['supplement_category_2']:
                print(f"{row['problem_category_1']:<15} {row['supplement_category_2']:<15} {row['count']:<10}")
    
    print("\n" + "=" * 60)
    print("测试数据添加完成!")
    print("提示：现在可以刷新前端页面查看图表数据")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = add_test_data()
    if success:
        print("\n✅ 操作成功")
        sys.exit(0)
    else:
        print("\n❌ 操作失败")
        sys.exit(1)
