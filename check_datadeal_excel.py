"""检查 datadeal 目录下的 Excel 文件"""
import pandas as pd
import os

excel_dir = r"D:\desktop\项目管理\project manage\datadeal"

# 查找可能包含质量问题的文件
possible_files = [
    "导入测试 2-张衡军.xls",
    "导入测试 20260205-阳绪文.xls"
]

for filename in possible_files:
    filepath = os.path.join(excel_dir, filename)
    if os.path.exists(filepath):
        print(f"\n{'='*80}")
        print(f"检查文件：{filename}")
        print(f"{'='*80}\n")
        
        try:
            # 尝试读取第一个 sheet
            df = pd.read_excel(filepath, header=1)  # 假设第 2 行是表头
            
            print(f"列数：{len(df.columns)}")
            print(f"行数：{len(df)}")
            
            # 查找与责任班组相关的列
            print(f"\n相关列名:")
            for i, col in enumerate(df.columns):
                col_str = str(col)
                if '责任' in col_str or '班组' in col_str or '新造' in col_str:
                    print(f"  {i+1}. '{col}'")
            
            # 如果找到"新责任班组"列，显示其数据
            if '新责任班组' in df.columns:
                print(f"\n'新责任班组' 列数据:")
                team_col = df['新责任班组']
                non_empty = team_col[team_col.notna() & (team_col != '')]
                print(f"  非空值数量：{len(non_empty)}")
                if len(non_empty) > 0:
                    print(f"  非空值示例：{non_empty.head(5).tolist()}")
                    
        except Exception as e:
            print(f"❌ 读取失败：{e}")
