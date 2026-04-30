"""检查 Excel 文件中的新责任班组列数据"""
import pandas as pd

excel_file = r"C:\Users\ADMINI~1\AppData\Local\Temp\quality_import_2026 年客户处质量问题台账 - 油箱 - 看板.xlsx"

try:
    # 读取 Excel（与 data.py 相同的参数）
    df = pd.read_excel(excel_file, sheet_name=1, header=1)
    
    print(f"\n=== Excel 文件检查 ===")
    print(f"文件路径：{excel_file}")
    print(f"总列数：{len(df.columns)}")
    print(f"总行数：{len(df)}")
    
    # 查找包含"责任"或"班组"的列
    print(f"\n=== 相关列名 ===")
    for i, col in enumerate(df.columns):
        if '责任' in str(col) or '班组' in str(col):
            print(f"{i+1}. '{col}'")
    
    # 检查"新责任班组"列
    if '新责任班组' in df.columns:
        print(f"\n=== '新责任班组' 列数据 ===")
        team_col = df['新责任班组']
        print(f"非空值数量：{team_col.notna().sum()}")
        print(f"空值数量：{team_col.isna().sum()}")
        
        # 显示前 10 个非空值
        non_empty_values = team_col[team_col.notna() & (team_col != '')].head(10)
        if len(non_empty_values) > 0:
            print(f"\n前 10 个非空值:")
            for idx, val in non_empty_values.items():
                print(f"  行{idx+2}: {val}")
        else:
            print("\n⚠️  该列所有值都为空！")
            
        # 显示前 5 行数据（包括空值）
        print(f"\n前 5 行原始数据:")
        for idx in range(min(5, len(df))):
            val = df.iloc[idx]['新责任班组']
            print(f"  行{idx+2}: {repr(val)}")
    else:
        print(f"\n❌ 未找到'新责任班组'列")
        print(f"\n所有列名列表:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
    
except Exception as e:
    print(f"❌ 读取失败：{e}")
    import traceback
    traceback.print_exc()
