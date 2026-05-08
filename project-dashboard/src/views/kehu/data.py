import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv  # 加载环境变量（避免硬编码敏感信息）
import os
from orm_model import Base, CustomerQualityIssue  # 导入 ORM 模型

# --------------------------
# 1. 加载配置（建议用.env文件管理）
# --------------------------
load_dotenv()  # 加载.env文件中的配置

# 数据库连接配置（从.env 文件读取，或直接修改此处）
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),  # 数据库地址（默认：localhost）
    "port": os.getenv("DB_PORT", "3306"),       # 端口（默认：3306）
    "user": os.getenv("DB_USER", "root"),       # 用户名（默认：root）
    "password": os.getenv("DB_PASSWORD", "zjj520111314"),  # 密码（与后端一致）
    "db_name": os.getenv("DB_NAME", "jgj-project")    # 数据库名（与后端一致）
}

# Excel 文件配置
EXCEL_CONFIG = {
    "file_path": None,  # Excel 文件路径（可通过命令行参数或函数参数传入）
    "sheet_index": 1,  # Sheet 索引（从 0 开始，1 表示第二个 sheet：2026 客户处反馈问题）
    "header_row": 1,  # 列名所在行号（从 0 开始，1 表示第 2 行作为列名，第 1 行是标题说明）
    "date_columns": ["发生日期", "关闭日期"]  # 需要转换为日期类型的列
}

# --------------------------
# 2. 数据库连接初始化
# --------------------------
def init_db():
    """创建数据库引擎和会话，若表不存在则创建表"""
    # 构建数据库连接 URL（MySQL 格式）
    db_url = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db_name']}?charset=utf8mb4"

    # 创建引擎（控制数据库连接池）
    engine = create_engine(db_url, echo=False)  # echo=True 会打印 SQL 语句（调试用）

    # 创建所有表（若表不存在）：基于 ORM 模型自动生成表结构
    Base.metadata.create_all(engine)

    # 创建会话（用于数据库操作）
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"数据库连接成功：{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db_name']}")
    print("表结构已初始化（若不存在则创建）")
    return engine, session

# --------------------------
# 3. Excel数据读取与预处理
# --------------------------
def read_excel_data(file_path=None):
    """读取 Excel 表二数据，进行预处理（日期转换、空值处理）"""
    try:
        # 如果传入了 file_path，使用传入的路径
        excel_file_path = file_path if file_path else EXCEL_CONFIG["file_path"]
        
        # 1. 读取 Excel 表二数据（跳过第 1 行标题说明，从第 2 行开始读取列名）
        df = pd.read_excel(
            excel_file_path,
            sheet_name=EXCEL_CONFIG["sheet_index"],  # 使用 sheet 索引而不是名称，避免编码问题
            header=EXCEL_CONFIG["header_row"],  # 第 2 行作为列名（第 1 行是标题说明）
            dtype=str  # 先统一读为字符串，避免自动类型转换错误
        )
        
        # 打印调试信息
        print(f"\n=== Excel 读取调试信息 ===")
        print(f"文件路径：{excel_file_path}")
        print(f"Sheet 索引：{EXCEL_CONFIG['sheet_index']}")
        print(f"Header 行：{EXCEL_CONFIG['header_row']}")
        print(f"读取到的列名（全部 {len(df.columns)} 列）:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. '{col}'")
        print(f"数据行数：{len(df)}")
        
        # 特别检查“新责任班组”列
        if '新责任班组' in df.columns:
            team_col = df['新责任班组']
            non_empty_count = team_col.notna().sum()
            empty_count = (~team_col.notna()).sum()
            print(f"\n【新责任班组】列统计:")
            print(f"  非空值：{non_empty_count}条")
            print(f"  空值：{empty_count}条")
            if non_empty_count > 0:
                print(f"  前 5 个非空值：{team_col[team_col.notna()].head(5).tolist()}")
        else:
            print(f"\n⚠️  未找到【新责任班组】列")
                
        # 特别检查“问题分类 1”和“补充分类 2”列
        if '问题分类 1' in df.columns:
            cat1_col = df['问题分类 1']
            non_empty = cat1_col.notna().sum()
            empty = (~cat1_col.notna()).sum()
            print(f"\n【问题分类 1】列统计:")
            print(f"  非空值：{non_empty}条")
            print(f"  空值：{empty}条")
            if non_empty > 0:
                print(f"  前 5 个非空值：{cat1_col[cat1_col.notna()].head(5).tolist()}")
        else:
            print(f"\n⚠️  未找到【问题分类 1】列")
                
        if '补充分类 2' in df.columns:
            cat2_col = df['补充分类 2']
            non_empty = cat2_col.notna().sum()
            empty = (~cat2_col.notna()).sum()
            print(f"\n【补充分类 2】列统计:")
            print(f"  非空值：{non_empty}条")
            print(f"  空值：{empty}条")
            if non_empty > 0:
                print(f"  前 5 个非空值：{cat2_col[cat2_col.notna()].head(5).tolist()}")
        else:
            print(f"\n⚠️  未找到【补充分类 2】列")
        
        print(f"==========================\n")

        # 2. 重命名列名（确保与 ORM 模型字段名一致，Excel 列名→模型字段名）
        # 注意：Excel 列名需与下方字典的 key 完全匹配（含空格）
        column_mapping = {
            "序号": "serial_number",
            "OA 编号": "oa_number",  # OA 系统编号
            "月份": "month",
            "市场分类": "market_category",
            "发生日期": "occurrence_date",
            "发生单位": "occurrence_unit",
            "车型": "vehicle_model",
            "车号": "vehicle_number",
            "产品名称": "product_name",
            "图号": "drawing_number",
            "产品数量": "product_quantity",
            "产品归类": "product_category",
            "新造/检修类型": "production_repair_type",  # 新造/检修类型
            "问题描述": "problem_description",
            "问题分类 1": "problem_category_1",  # 新增
            "补充分类 2": "supplement_category_2",  # 新增
            "问题分类": "problem_category",
            "问题定性": "problem_nature",
            "原因分析（逐条分析）": "cause_analysis",
            "纠正措施": "corrective_measures",
            "措施执行情况": "measure_implementation",
            "考核单": "assessment_form",
            "考核金额": "assessment_amount",
            "所属车间": "workshop",
            "质量工程师": "quality_engineer",
            "检验员": "inspector",
            "责任班组": "responsible_team",  # Excel 中可能是"新责任班组"
            "新责任班组": "responsible_team",  # 添加这个映射
            "供应商": "supplier",
            "责任人": "responsible_person",
            "二维码导入状态": "qrcode_import_status",
            "是否关闭": "is_closed",
            "关闭日期": "closing_date",
            "备注": "remark",
            "Unnamed: 30": "other1",  # Excel 中未命名的预留列 1
            "Unnamed: 31": "other2"   # Excel 中未命名的预留列 2
        }

        # 只保留 Excel 中存在的列，并改名（避免列不存在时报错）
        existing_columns = [col for col in column_mapping.keys() if col in df.columns]
        missing_columns = [col for col in column_mapping.keys() if col not in df.columns]
        
        # 检查是否有必要的列缺失
        required_columns = ["序号", "月份", "市场分类", "发生日期", "发生单位", "产品名称", "问题描述"]
        missing_required = [col for col in required_columns if col not in df.columns]
        
        if missing_required:
            error_msg = f"Excel 文件中缺少必要的列：{', '.join(missing_required)}\n\n"
            error_msg += f"当前 Excel 文件中的列名：\n"
            error_msg += "\n".join([f"  - {col}" for col in df.columns])
            raise ValueError(error_msg)
        
        df = df[existing_columns].rename(columns=column_mapping)
                
        # 为缺失的列添加空值
        for col_name in column_mapping.values():
            if col_name not in df.columns:
                df[col_name] = ""
        
        # 特殊处理：如果 problem_category_1 或 supplement_category_2 为空，从 problem_category 复制
        if 'problem_category' in df.columns:
            # 如果 problem_category_1 列为空（全为空字符串），使用 problem_category 的值
            if 'problem_category_1' in df.columns:
                mask_cat1 = (df['problem_category_1'].isna()) | (df['problem_category_1'] == '')
                if mask_cat1.any():
                    df.loc[mask_cat1, 'problem_category_1'] = df.loc[mask_cat1, 'problem_category']
                    print(f"\n✅ 已将 {mask_cat1.sum()} 条空的 problem_category_1 从 problem_category 复制")
            
            # 如果 supplement_category_2 列为空（全为空字符串），使用 problem_category 的值
            if 'supplement_category_2' in df.columns:
                mask_cat2 = (df['supplement_category_2'].isna()) | (df['supplement_category_2'] == '')
                if mask_cat2.any():
                    df.loc[mask_cat2, 'supplement_category_2'] = df.loc[mask_cat2, 'problem_category']
                    print(f"✅ 已将 {mask_cat2.sum()} 条空的 supplement_category_2 从 problem_category 复制")
        
        # 3. 数据预处理
        # 3.1 日期列转换（处理 Excel 日期格式）- 使用 ORM 字段名而不是 Excel 列名
        orm_date_columns = ["occurrence_date", "closing_date"]  # 对应 ORM 模型中的字段名
        for date_col in orm_date_columns:
            if date_col in df.columns:  # 确保列存在
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")  # 无效日期转为 NaT

        # 3.2 数值列转换（产品数量、考核金额）
        df["product_quantity"] = pd.to_numeric(df["product_quantity"], errors="coerce").fillna(0).astype(int)
        df["assessment_amount"] = pd.to_numeric(df["assessment_amount"], errors="coerce").fillna(0.0)

        # 3.3 空值处理（字符串列空值转为空字符串，避免数据库NULL问题）
        str_columns = df.select_dtypes(include=["object"]).columns
        df[str_columns] = df[str_columns].fillna("")

        # 4. 重置索引（避免导入时索引异常）
        df = df.reset_index(drop=True)

        print(f"Excel数据读取成功，共{len(df)}条记录")
        return df

    except Exception as e:
        print(f"Excel数据读取失败：{str(e)}")
        raise  # 抛出异常，终止程序

# --------------------------
# 4. 批量导入数据库
# --------------------------
def batch_import_to_db(session, df):
    """将DataFrame数据批量导入数据库"""
    try:
        # 1. 将 DataFrame 转换为 ORM 模型实例列表（批量创建）
        issue_instances = []
        for _, row in df.iterrows():
            # 将每行数据转为字典，过滤空值（NaT/NaN 转为 None）
            row_dict = row.to_dict()
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = None
        
            # 创建模型实例（CustomerQualityIssue 对应 customer_quality 表）
            # 与后端接口使用的表名完全一致
            issue = CustomerQualityIssue(**row_dict)
            issue_instances.append(issue)

        # 2. 批量添加到数据库（bulk_save_objects效率高于add_all）
        session.bulk_save_objects(issue_instances)

        # 3. 提交事务（确认写入数据库）
        session.commit()

        print(f"数据批量导入成功，共导入{len(issue_instances)}条记录")

    except Exception as e:
        # 若出错，回滚事务（避免数据不一致）
        session.rollback()
        print(f"数据导入失败，已回滚：{str(e)}")
        raise
    finally:
        # 关闭会话（释放数据库连接）
        session.close()
        print("数据库会话已关闭")

# --------------------------
# 5. 主执行函数
# --------------------------
def main():
    """主流程：初始化数据库→读取 Excel→批量导入"""
    print("="*60)
    print("开始执行 Excel 数据导入数据库流程")
    print(f"目标数据库：{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db_name']}")
    print(f"目标表：customer_quality (CustomerQualityIssue ORM 模型映射)")
    print("="*60)

    # 步骤 1：初始化数据库
    engine, session = init_db()

    # 步骤 2：读取 Excel 数据
    df = read_excel_data()

    # 步骤 3：批量导入数据库
    batch_import_to_db(session, df)

    print("="*60)
    print("数据导入流程执行完成")
    print("提示：请检查 customer_quality 表中是否已有数据")
    print("可通过访问 /api/v1/feedback/problem/filters 接口验证筛选条件")
    print("="*60)

# 执行主函数（仅当脚本直接运行时生效）
if __name__ == "__main__":
    import sys
    
    # 如果提供了命令行参数，使用第一个参数作为文件路径
    if len(sys.argv) > 1:
        EXCEL_CONFIG["file_path"] = sys.argv[1]
        print(f"使用命令行参数指定的文件：{sys.argv[1]}")
    else:
        print("使用方法：python data.py <Excel 文件路径>")
        print("例如：python data.py C:\\Users\\example\\质量问题台账.xlsx")
        print("\n未指定文件路径，退出程序")
        sys.exit(1)
    
    main()