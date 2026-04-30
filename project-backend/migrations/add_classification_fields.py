"""
添加问题分类 1 和补充分类 2 字段到 customer_quality 表
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import execute_query

def add_classification_fields():
    """添加问题分类 1 和补充分类 2 字段"""
    
    print("开始添加问题分类字段...")
    
    # 检查表是否存在
    check_table_sql = "SHOW TABLES LIKE 'customer_quality'"
    table_exists = execute_query(check_table_sql)
    
    if not table_exists:
        print("错误：customer_quality 表不存在")
        return False
    
    # 检查字段是否已存在
    describe_sql = "DESCRIBE customer_quality"
    columns_result = execute_query(describe_sql, fetch_all=True)
    
    if not columns_result:
        print("错误：无法获取表结构")
        return False
    
    column_names = [col['Field'] for col in columns_result if 'Field' in col]
    
    # 添加 problem_category_1 字段（问题分类 1）
    if 'problem_category_1' not in column_names:
        add_col_sql = """
        ALTER TABLE customer_quality 
        ADD COLUMN problem_category_1 VARCHAR(100) DEFAULT NULL COMMENT '问题分类 1'
        """
        result = execute_query(add_col_sql, fetch_all=False, fetch_one=False)
        if result is not None:
            print("✓ 成功添加 problem_category_1 字段")
        else:
            print("✗ 添加 problem_category_1 字段失败")
    else:
        print("- problem_category_1 字段已存在，跳过")
    
    # 添加 supplement_category_2 字段（补充分类 2）
    if 'supplement_category_2' not in column_names:
        add_col_sql = """
        ALTER TABLE customer_quality 
        ADD COLUMN supplement_category_2 VARCHAR(100) DEFAULT NULL COMMENT '补充分类 2'
        """
        result = execute_query(add_col_sql, fetch_all=False, fetch_one=False)
        if result is not None:
            print("✓ 成功添加 supplement_category_2 字段")
        else:
            print("✗ 添加 supplement_category_2 字段失败")
    else:
        print("- supplement_category_2 字段已存在，跳过")
    
    print("\n字段添加完成！")
    return True

if __name__ == "__main__":
    success = add_classification_fields()
    if success:
        print("\n迁移执行成功")
        sys.exit(0)
    else:
        print("\n迁移执行失败")
        sys.exit(1)
