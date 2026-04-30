"""添加 oa_number 字段到 customer_quality 表"""
import pymysql

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "zjj520111314",
    "db_name": "jgj-project"
}

def add_oa_number_field():
    """在 customer_quality 表中添加 oa_number 字段"""
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["db_name"],
            charset="utf8mb4"
        )
        
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        check_sql = """
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
          AND TABLE_NAME = 'customer_quality' 
          AND COLUMN_NAME = 'oa_number'
        """
        cursor.execute(check_sql, (DB_CONFIG["db_name"]))
        exists = cursor.fetchone()[0]
        
        if exists > 0:
            print("✅ customer_quality 表中已存在 oa_number 字段")
        else:
            # 添加字段
            alter_sql = """
            ALTER TABLE customer_quality 
            ADD COLUMN oa_number VARCHAR(50) COMMENT 'OA 编号（OA 系统编号）'
            AFTER serial_number
            """
            cursor.execute(alter_sql)
            conn.commit()
            print("✅ 成功添加 oa_number 字段到 customer_quality 表")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 添加字段失败：{e}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("开始执行数据库迁移：添加 OA 编号字段")
    print("="*60)
    add_oa_number_field()
    print("="*60)
    print("迁移完成！请重启后端服务以应用更改")
    print("="*60)
