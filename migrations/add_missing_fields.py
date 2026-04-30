"""添加缺失的字段到 customer_quality 表"""
import pymysql

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "zjj520111314",
    "db_name": "jgj-project"
}

def add_missing_fields():
    """添加 ORM 模型中有但数据库中没有的字段"""
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["db_name"],
            charset="utf8mb4"
        )
        
        cursor = conn.cursor()
        
        # 需要添加的字段列表
        missing_fields = [
            ("product_category", "VARCHAR(50)", "产品归类", "problem_description"),
            ("workshop", "VARCHAR(50)", "所属车间", "assessment_amount"),
            ("inspection员", "VARCHAR(50)", "检验员", "quality_engineer"),
            ("supplier", "VARCHAR(50)", "供应商", "responsible_team"),
            ("closing_date", "DATETIME", "关闭日期", "is_closed"),
            ("other1", "VARCHAR(50)", "预留字段 1", "remark"),
            ("other2", "VARCHAR(50)", "预留字段 2", "other1"),
        ]
        
        for field_name, field_type, comment, after_field in missing_fields:
            # 检查字段是否已存在
            check_sql = """
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
              AND TABLE_NAME = 'customer_quality' 
              AND COLUMN_NAME = %s
            """
            cursor.execute(check_sql, (DB_CONFIG["db_name"], field_name))
            exists = cursor.fetchone()[0]
            
            if exists > 0:
                print(f"✅ 字段 {field_name} 已存在")
            else:
                # 添加字段
                alter_sql = f"""
                ALTER TABLE customer_quality 
                ADD COLUMN {field_name} {field_type} COMMENT '{comment}'
                AFTER {after_field}
                """
                cursor.execute(alter_sql)
                conn.commit()
                print(f"✅ 成功添加字段：{field_name} ({field_type}) - {comment}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 添加字段失败：{e}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("开始执行数据库迁移：添加缺失字段")
    print("="*60)
    add_missing_fields()
    print("="*60)
    print("迁移完成！请重启后端服务")
    print("="*60)
