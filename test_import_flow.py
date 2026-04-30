"""测试导入流程，查看实际列名"""
import sys
import os

# 添加 data.py 所在目录到路径
kehu_dir = r"D:\desktop\项目管理\project manage\project-dashboard\src\views\kehu"
if kehu_dir not in sys.path:
    sys.path.insert(0, kehu_dir)

# 动态加载 data.py
import importlib.util
spec = importlib.util.spec_from_file_location("data_module", os.path.join(kehu_dir, "data.py"))
data_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_module)

# 测试文件路径（使用绝对路径）
base_dir = os.path.dirname(os.path.abspath(__file__))
test_files = [
    os.path.join(base_dir, "datadeal", "导入测试 2-张衡军.xls"),
    os.path.join(base_dir, "datadeal", "导入测试 20260205-阳绪文.xls"),
]

for test_file in test_files:
    if os.path.exists(test_file):
        print(f"\n{'='*80}")
        print(f"测试文件：{test_file}")
        print('='*80)
        
        try:
            # 读取 Excel 数据
            df = data_module.read_excel_data(test_file)
            print(f"✅ 读取成功！共 {len(df)} 条记录")
            print(f"\n列名列表:")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}. {col}")
        except Exception as e:
            print(f"❌ 读取失败：{e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n⚠️  文件不存在：{test_file}")
