"""重命名数据库列以匹配 ORM 模型"""
import pymysql

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "zjj520111314",
    "db_name": "jgj-project"
}

def rename_columns():
    """将数据库中的列名改为与 ORM 模型一致"""
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
        
        # 需要重命名的列：旧列名 -> (新列名，类型，注释)
        columns_to_rename = {
            "assessment_form_number": ("assessment_form", "VARCHAR(50)", "考核单（编号）"),
            "qrcode_imported": ("qrcode_import_status", "VARCHAR(20)", "二维码导入状态"),
        }
        
        for old_name, (new_name, col_type, comment) in columns_to_rename.items():
            # 检查旧列是否存在
            check_sql = """
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
              AND TABLE_NAME = 'customer_quality' 
              AND COLUMN_NAME = %s
            """
            cursor.execute(check_sql, (DB_CONFIG["db_name"], old_name))
            exists = cursor.fetchone()[0]
            
            if exists > 0:
                # 重命名列
                alter_sql = f"""
                ALTER TABLE customer_quality 
                CHANGE COLUMN {old_name} {new_name} {col_type} COMMENT '{comment}'
                """
                cursor.execute(alter_sql)
                conn.commit()
                print(f"✅ 成功重命名：{old_name} → {new_name}")
            else:
                print(f"⚠️  列 {old_name} 不存在，跳过")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 重命名列失败：{e}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("开始执行数据库迁移：重命名列")
    print("="*60)
    rename_columns()
    print("="*60)
    print("迁移完成！请重启后端服务")
    print("="*60)
