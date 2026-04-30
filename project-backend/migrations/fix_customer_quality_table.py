"""
修复 customer_quality 表结构，添加缺失的字段
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import get_db_connection


def fix_customer_quality_table():
    """修复客户质量反馈表，添加缺失字段"""
    conn = get_db_connection()
    if not conn:
        print("❌ 数据库连接失败")
        return
    
    try:
        cursor = conn.cursor()
        
        # 检查哪些字段已经存在
        cursor.execute('DESCRIBE customer_quality')
        existing_columns = [col[0] for col in cursor.fetchall()]
        
        print("=== 开始修复 customer_quality 表 ===\n")
        print(f"当前已有字段：{existing_columns}\n")
        
        # 需要添加的字段列表
        columns_to_add = []
        
        # 市场类别
        if 'market_category' not in existing_columns:
            columns_to_add.append({
                'name': 'market_category',
                'definition': "VARCHAR(100) DEFAULT NULL COMMENT '市场类别'",
                'after': 'company_name'
            })
        
        # 发生单位
        if 'occurrence_unit' not in existing_columns:
            columns_to_add.append({
                'name': 'occurrence_unit',
                'definition': "VARCHAR(200) DEFAULT NULL COMMENT '发生单位'",
                'after': 'market_category'
            })
        
        # 问题定性（核心字段）
        if 'problem_nature' not in existing_columns:
            columns_to_add.append({
                'name': 'problem_nature',
                'definition': "VARCHAR(50) NOT NULL DEFAULT '其他' COMMENT '问题定性（设计问题/工艺问题/材料问题/操作问题/设备问题/其他）'",
                'after': 'quality_issue_type'
            })
        
        # 责任部门（核心字段）
        if 'responsible_team' not in existing_columns:
            columns_to_add.append({
                'name': 'responsible_team',
                'definition': "VARCHAR(100) DEFAULT NULL COMMENT '责任部门/责任团队'",
                'after': 'problem_nature'
            })
        
        # 产品类型/车型
        if 'vehicle_model' not in existing_columns:
            columns_to_add.append({
                'name': 'vehicle_model',
                'definition': "VARCHAR(200) DEFAULT NULL COMMENT '产品类型/车型'",
                'after': 'product_name'
            })
        
        # 考核金额（核心字段）
        if 'assessment_amount' not in existing_columns:
            columns_to_add.append({
                'name': 'assessment_amount',
                'definition': "DECIMAL(10,2) DEFAULT 0 COMMENT '考核金额'",
                'after': 'priority'
            })
        
        # 是否关闭（核心字段）
        if 'is_closed' not in existing_columns:
            columns_to_add.append({
                'name': 'is_closed',
                'definition': "VARCHAR(10) NOT NULL DEFAULT '否' COMMENT '是否关闭（是/否）'",
                'after': 'status'
            })
        
        # 责任人
        if 'responsible_person' not in existing_columns:
            columns_to_add.append({
                'name': 'responsible_person',
                'definition': "VARCHAR(100) DEFAULT NULL COMMENT '责任人'",
                'after': 'handler'
            })
        
        # 纠正措施
        if 'corrective_measures' not in existing_columns:
            columns_to_add.append({
                'name': 'corrective_measures',
                'definition': "TEXT DEFAULT NULL COMMENT '纠正措施'",
                'after': 'solution'
            })
        
        # 问题描述（详细）
        if 'problem_description' not in existing_columns:
            columns_to_add.append({
                'name': 'problem_description',
                'definition': "TEXT DEFAULT NULL COMMENT '问题详细描述'",
                'after': 'issue_description'
            })
        
        # 问题类别
        if 'problem_category' not in existing_columns:
            columns_to_add.append({
                'name': 'problem_category',
                'definition': "VARCHAR(50) DEFAULT NULL COMMENT '问题类别'",
                'after': 'severity'
            })
        
        # 措施实施
        if 'measure_implementation' not in existing_columns:
            columns_to_add.append({
                'name': 'measure_implementation',
                'definition': "VARCHAR(200) DEFAULT NULL COMMENT '措施实施'",
                'after': 'problem_category'
            })
        
        # 备注
        if 'remark' not in existing_columns:
            columns_to_add.append({
                'name': 'remark',
                'definition': "TEXT DEFAULT NULL COMMENT '备注'",
                'after': 'remarks'
            })
        
        # 更新时间
        if 'updated_time' not in existing_columns:
            columns_to_add.append({
                'name': 'updated_time',
                'definition': "DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'",
                'after': 'update_time'
            })
        
        # 创建时间（用于发现日期）
        if 'created_time' not in existing_columns:
            columns_to_add.append({
                'name': 'created_time',
                'definition': "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（发现日期）'",
                'after': 'discovery_date'
            })
        
        # 执行 ALTER TABLE 语句添加缺失的字段
        if columns_to_add:
            for col in columns_to_add:
                after_field = col.get('after')
                if after_field and after_field in existing_columns:
                    sql = f"ALTER TABLE customer_quality ADD COLUMN {col['name']} {col['definition']} AFTER {after_field}"
                else:
                    sql = f"ALTER TABLE customer_quality ADD COLUMN {col['name']} {col['definition']}"
                
                print(f"添加字段：{col['name']}")
                cursor.execute(sql)
                print(f"✅ {col['name']} 添加成功\n")
            
            conn.commit()
            print("\n✅ 所有缺失字段添加成功！")
        else:
            print("✅ 表结构完整，无需添加字段")
        
        # 显示最终表结构
        cursor.execute('DESCRIBE customer_quality')
        final_columns = cursor.fetchall()
        
        print("\n=== 修复后的表结构 ===\n")
        for col in final_columns:
            print(f"{col[0]:<25} {col[1]:<20} NULL:{col[2]:<5} Key:{col[3]:<5} Default:{str(col[4]):<15}")
        
    except Exception as e:
        print(f"❌ 修复失败：{e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("开始修复 customer_quality 表结构")
    print("=" * 80)
    fix_customer_quality_table()
    print("\n完成！")
