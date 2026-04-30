"""
测试周数筛选功能
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_week_filter():
    """测试周数筛选功能"""
    print("=" * 60)
    print("测试周数筛选功能")
    print("=" * 60)
    
    # 先获取所有数据（无筛选）
    print("\n1️⃣ 获取所有数据（无筛选）...")
    response = requests.get(f"{BASE_URL}/v1/feedback/problem/list?page=1&limit=5")
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', 0)
        print(f"   ✅ 总记录数: {total}")
        if data.get('list'):
            first_item = data['list'][0]
            print(f"   📅 第一条记录的日期: {first_item.get('occur_date')}")
    else:
        print(f"   ❌ 请求失败: {response.status_code}")
        return
    
    # 获取可用的周数列表
    print("\n2️⃣ 获取可用周数列表...")
    response = requests.get(f"{BASE_URL}/v1/feedback/problem/filters")
    if response.status_code == 200:
        filters = response.json().get('data', {})
        weeks = filters.get('weeks', [])
        print(f"   ✅ 可用周数数量: {len(weeks)}")
        print(f"   📅 前5个周数: {weeks[:5]}")
        
        if len(weeks) > 0:
            # 测试单选周数
            test_week = weeks[0]
            print(f"\n3️⃣ 测试单选周数: {test_week}")
            response = requests.get(
                f"{BASE_URL}/v1/feedback/problem/list",
                params={"page": 1, "limit": 5, "week": test_week}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 筛选后记录数: {data.get('total', 0)}")
                if data.get('list'):
                    for item in data['list'][:2]:
                        print(f"      - {item.get('product_name')}: {item.get('occur_date')}")
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
            
            # 测试多选周数
            if len(weeks) > 1:
                test_weeks = ','.join(weeks[:2])
                print(f"\n4️⃣ 测试多选周数: {test_weeks}")
                response = requests.get(
                    f"{BASE_URL}/v1/feedback/problem/list",
                    params={"page": 1, "limit": 5, "week": test_weeks}
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 筛选后记录数: {data.get('total', 0)}")
                    if data.get('list'):
                        for item in data['list'][:2]:
                            print(f"      - {item.get('product_name')}: {item.get('occur_date')}")
                else:
                    print(f"   ❌ 请求失败: {response.status_code}")
                    print(f"      错误信息: {response.text}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_week_filter()
