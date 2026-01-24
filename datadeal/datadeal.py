import os
import re
import glob

def parse_filename(filename):
    """解析文件名，提取项目名和项目经理"""
    # 去掉扩展名
    name_without_ext = os.path.splitext(filename)[0]
    
    # 尝试匹配 "xxx(项目名)-项目经理姓名" 格式
    match = re.match(r'.*\((.+)\)-(.+)', name_without_ext)
    
    if match:
        project_name = match.group(1).strip()
        manager_name = match.group(2).strip()
        return project_name, manager_name
    
    # 如果不符合上述格式，尝试匹配 "项目名-项目经理姓名" 格式
    last_dash_index = name_without_ext.rfind('-')
    if last_dash_index != -1:
        project_name = name_without_ext[:last_dash_index].strip()
        manager_name = name_without_ext[last_dash_index+1:].strip()
        return project_name, manager_name
    
    # 如果都不符合，返回整个名字作为项目名，项目经理为未知
    return name_without_ext, "未知"

def main():
    # 获取当前目录下的所有Excel文件
    excel_extensions = ['*.xls', '*.xlsx', '*.xlsm', '*.csv']
    excel_files = []
    
    for ext in excel_extensions:
        excel_files.extend(glob.glob(ext))
        excel_files.extend(glob.glob(os.path.join('*', ext)))  # 检查子目录
    
    print("找到的Excel文件及解析结果：")
    print("-" * 60)
    
    for file_path in excel_files:
        filename = os.path.basename(file_path)
        project_name, manager_name = parse_filename(filename)
        
        print(f"表格名: {filename}")
        print(f"  项目名: {project_name}")
        print(f"  项目经理: {manager_name}")
        print("-" * 60)

if __name__ == "__main__":
    main()