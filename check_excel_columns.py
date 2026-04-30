"""检查 Excel 文件的真实列名"""
import pandas as pd

excel_path = r"D:\desktop\2026年客户处质量问题台账 - 油箱 - 看板.xlsx"

print(f"=== 检查 Excel 文件 ===\n")
print(f"文件路径：{excel_path}\n")

try:
    # 读取所有 sheet 名称
    xl = pd.ExcelFile(excel_path)
    print(f"可用的 Sheet 名称：{xl.sheet_names}\n")
    
    # 读取第二个 sheet（索引 1）
    sheet_name = xl.sheet_names[1]
    print(f"读取第 2 个 Sheet: '{sheet_name}'\n")
    
    # 使用 header=1 读取（第 2 行作为列名）
    df = pd.read_excel(excel_path, sheet_name=1, header=1, dtype=str)
    
    print(f"✅ 读取成功！共 {len(df)} 行数据\n")
    print(f"列名列表 (共 {len(df.columns)} 列):")
    for i, col in enumerate(df.columns):
        print(f"  {i+1}. '{col}'")
    
    if len(df) > 0:
        print(f"\n前 2 行数据预览:")
        print(df.head(2).to_string())
    else:
        print("\n⚠️ 警告：Excel 文件是空的（没有数据行）")
    
    xl.close()
    
except Exception as e:
    print(f"❌ 读取失败：{e}")
    import traceback
    traceback.print_exc()
