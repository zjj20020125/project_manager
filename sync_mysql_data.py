import mysql.connector
from mysql.connector import Error
import sys
import os


def get_remote_connection(host='172.16.100.89', database='ncrdata', user='LCUser', password='LC123456'):
    """获取远程数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            charset='utf8mb4',
            autocommit=False  # 手动控制事务
        )
        return connection
    except Error as e:
        print(f"连接远程数据库失败: {e}")
        return None


def get_local_connection():
    """获取本地数据库连接，使用项目中的配置"""
    try:
        # 尝试从项目配置中读取本地数据库配置
        project_config_path = './project-backend/config/config.py'
        if os.path.exists(project_config_path):
            # 临时添加路径以便导入
            sys.path.insert(0, './project-backend/config')
            import config as project_config
            
            # 使用项目中的数据库配置
            db_config = project_config.DATABASE_CONFIG.copy()
            # 确保使用正确的数据库名
            db_config['database'] = 'jgj-project'
            
            connection = mysql.connector.connect(**db_config)
            return connection
        else:
            # 如果配置文件不存在，使用默认配置
            connection = mysql.connector.connect(
                host='localhost',
                database='jgj-project',  # 根据项目数据源配置使用jgj-project数据库
                user='root',
                password='zjj520111314',  # 使用项目中的默认密码
                charset='utf8mb4'
            )
            return connection
    except ImportError as e:
        print(f"导入配置文件失败: {e}")
        # 如果导入失败，使用默认配置
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='jgj-project',
                user='root',
                password='zjj520111314',
                charset='utf8mb4'
            )
            return connection
        except Error as e:
            print(f"连接本地数据库失败: {e}")
            return None
    except Error as e:
        print(f"连接本地数据库失败: {e}")
        return None


def get_table_structure(connection, table_name):
    """获取表结构"""
    cursor = connection.cursor(buffered=True)  # 使用buffered避免结果未消费的问题
    try:
        # 获取表的字段信息
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns_info = cursor.fetchall()
        
        if not columns_info:
            print(f"表 {table_name} 不存在或没有字段")
            return None
        
        # 构建CREATE TABLE语句
        create_parts = [f"CREATE TABLE `{table_name}` ("]
        column_defs = []
        
        for col in columns_info:
            # col格式: (Field, Type, Null, Key, Default, Extra)
            field = col[0]
            col_type = col[1]
            is_null = col[2]
            key_type = col[3]
            default_val = col[4]
            extra = col[5]
            
            # 构建字段定义
            col_def = f"`{field}` {col_type}"
            
            if is_null == 'NO':
                col_def += " NOT NULL"
            
            if default_val is not None:
                if default_val == '':
                    col_def += " DEFAULT ''"
                else:
                    col_def += f" DEFAULT '{default_val}'"
            
            if extra:
                col_def += f" {extra}"
                
            column_defs.append(col_def)
        
        create_parts.append(',\n  '.join(column_defs))
        create_parts.append("\n)")
        
        return '\n'.join(create_parts)
    except Error as e:
        print(f"获取表结构失败: {e}")
        return None
    finally:
        cursor.close()


def get_table_data(connection, table_name):
    """获取表数据"""
    cursor = connection.cursor(dictionary=True, buffered=True)  # 使用dictionary和buffered
    try:
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"获取表数据失败: {e}")
        return []
    finally:
        cursor.close()


def create_local_table(local_conn, create_statement, new_table_name):
    """在本地数据库创建新表"""
    cursor = local_conn.cursor()
    try:
        # 修改CREATE语句中的表名为新表名
        import re
        # 替换表名为新表名
        new_create_statement = re.sub(
            r'CREATE TABLE [`"]?[^`"\s]+[`"]?',
            f'CREATE TABLE `{new_table_name}`',
            create_statement
        )
        
        # 先删除已存在的表
        cursor.execute(f"DROP TABLE IF EXISTS `{new_table_name}`")
        # 创建新表
        cursor.execute(new_create_statement)
        local_conn.commit()
        print(f"成功创建表 {new_table_name}")
        return True
    except Error as e:
        print(f"创建本地表失败: {e}")
        local_conn.rollback()
        return False
    finally:
        cursor.close()


def insert_data_to_local(local_conn, table_name, data):
    """向本地表插入数据"""
    if not data:
        print("没有数据需要插入")
        return True
        
    cursor = local_conn.cursor(prepared=True)  # 使用prepared语句提高性能
    try:
        if data:
            columns = list(data[0].keys()) if data else []
            if not columns:
                print("没有列数据需要插入")
                return True
                
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join([f'`{col}`' for col in columns])
            insert_query = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
            
            # 准备数据
            values = []
            for row in data:
                value = tuple(row.get(col) for col in columns)  # 使用.get()避免KeyError
                values.append(value)
            
            # 分批插入数据，避免一次性插入过多数据
            batch_size = 1000
            for i in range(0, len(values), batch_size):
                batch = values[i:i + batch_size]
                cursor.executemany(insert_query, batch)
                local_conn.commit()
                print(f"已插入 {min(i + batch_size, len(values))}/{len(values)} 条记录")
            
            print(f"成功插入 {len(data)} 条记录到表 {table_name}")
            return True
    except Error as e:
        print(f"插入数据失败: {e}")
        local_conn.rollback()
        return False
    finally:
        cursor.close()


def main():
    # 参数设置
    remote_host = input("请输入远程MySQL服务器地址 (默认: 172.16.100.89): ").strip() or '172.16.100.89'
    remote_database = input("请输入远程数据库名 (默认: ncrdata): ").strip() or 'ncrdata'
    remote_user = input("请输入远程数据库用户名 (默认: root): ").strip() or 'root'
    remote_password = input("请输入远程数据库密码: ").strip()
    remote_table_name = input("请输入远程表名 (默认: jgjncr): ").strip() or 'jgjncr'
    local_table_name = input("请输入本地新表名 (默认: jgjncr_copy): ").strip() or 'jgjncr_copy'
    
    print("\\n开始同步远程MySQL数据到本地...")
    print(f"远程服务器: {remote_host}")
    print(f"远程数据库: {remote_database}")
    print(f"远程表: {remote_table_name}")
    print(f"本地表: {local_table_name}")
    
    # 连接远程数据库
    remote_conn = get_remote_connection(
        host=remote_host,
        database=remote_database,
        user=remote_user,
        password=remote_password
    )
    if not remote_conn:
        print("无法连接到远程数据库，程序退出")
        return
    
    print("成功连接到远程数据库")
    
    # 连接本地数据库
    local_conn = get_local_connection()
    if not local_conn:
        print("无法连接到本地数据库，程序退出")
        remote_conn.close()
        return
    
    print("成功连接到本地数据库")
    
    try:
        # 获取远程表结构
        print(f"正在获取远程表 {remote_table_name} 的结构...")
        table_structure = get_table_structure(remote_conn, remote_table_name)
        if not table_structure:
            print(f"无法获取远程表 {remote_table_name} 的结构，程序退出")
            return
        
        # 在本地创建新表
        print(f"正在本地创建表 {local_table_name}...")
        if not create_local_table(local_conn, table_structure, local_table_name):
            print(f"创建本地表 {local_table_name} 失败，程序退出")
            return
        
        # 获取远程表数据
        print(f"正在获取远程表 {remote_table_name} 的数据...")
        table_data = get_table_data(remote_conn, remote_table_name)
        if not table_data:
            print(f"获取远程表 {remote_table_name} 数据失败或表中无数据")
            return
        
        print(f"获取到 {len(table_data)} 条记录")
        
        # 插入数据到本地表
        if table_data:
            print("正在向本地表插入数据...")
            if insert_data_to_local(local_conn, local_table_name, table_data):
                print("\\n数据同步完成！")
                print(f"数据已从远程表 {remote_table_name} 同步到本地表 {local_table_name}")
            else:
                print("数据插入失败")
        else:
            print("远程表中没有数据需要同步")
    
    except Exception as e:
        print(f"同步过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭连接
        try:
            if remote_conn and remote_conn.is_connected():
                remote_conn.close()
                print("远程数据库连接已关闭")
        except:
            pass
            
        try:
            if local_conn and local_conn.is_connected():
                local_conn.close()
                print("本地数据库连接已关闭")
        except:
            pass
        
        print("程序执行完毕")


if __name__ == "__main__":
    main()