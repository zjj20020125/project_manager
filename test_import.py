import requests
import os

# 测试文件路径
file_path = r"D:\desktop\项目管理\project manage\测试导入数据.csv"

# 检查文件是否存在
if not os.path.exists(file_path):
    print(f"文件不存在: {file_path}")
    exit(1)

# 准备文件上传
files = {'file': open(file_path, 'rb')}
data = {'overwrite': 'false'}

try:
    # 发送POST请求
    response = requests.post(
        'http://localhost:8001/v1/projects/import',
        files=files,
        data=data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("导入成功!")
    else:
        print("导入失败!")
        
except Exception as e:
    print(f"请求出错: {e}")
finally:
    files['file'].close()