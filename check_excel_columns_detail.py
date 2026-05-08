import pandas as pd

# 请修改为你的Excel文件路径
excel_file = r"D:\desktop\项目管理\project manage\datadeal\导入测试2-张衡军.xls"

print("=" * 80)
print(f"检查Excel文件: {excel_file}")
print("=" * 80)

try:
    # 先检查有多少个sheet
    xl = pd.ExcelFile(excel_file)
    print(f"\n📑 Excel文件中的Sheet列表:")
    for i, name in enumerate(xl.sheet_names):
        print(f"   {i}. '{name}'")
    
    # 尝试读取第二个sheet (索引1),如果不存在则读取第一个
    sheet_index = 1 if len(xl.sheet_names) > 1 else 0
    print(f"\n🔍 读取 Sheet 索引 {sheet_index} ('{xl.sheet_names[sheet_index]}')")
    
    df = pd.read_excel(excel_file, sheet_name=sheet_index, header=1, nrows=5)
    
    print(f"\n📋 Sheet索引1的所有列名 (共{len(df.columns)}列):")
    print("-" * 80)
    for i, col in enumerate(df.columns):
        print(f"{i+1:3d}. '{col}'")
    
    print("\n🔍 查找包含'分类'的列:")
    print("-" * 80)
    category_cols = [col for col in df.columns if '分类' in str(col)]
    if category_cols:
        for col in category_cols:
            print(f"   ✓ '{col}'")
    else:
        print("   ❌ 没有找到包含'分类'的列")
    
    print("\n🔍 查找包含'问题'的列:")
    print("-" * 80)
    problem_cols = [col for col in df.columns if '问题' in str(col)]
    if problem_cols:
        for col in problem_cols:
            print(f"   ✓ '{col}'")
    else:
        print("   ❌ 没有找到包含'问题'的列")
    
    print("\n💡 建议:")
    print("-" * 80)
    print("如果Excel中没有这两列,你可以:")
    print("1. 在Excel中添加'问题分类 1'和'补充分类 2'列")
    print("2. 或者修改data.py中的列映射,使用现有的列")
    print("3. 或者从'问题分类'列复制数据到这两个字段")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
