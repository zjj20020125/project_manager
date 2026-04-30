"""测试质量问题详情 API"""
import requests

BASE_URL = "http://localhost:8001"

def test_problem_detail():
    """测试质量问题详情接口"""
    # 先获取列表，找到一个存在的 ID
    list_url = f"{BASE_URL}/v1/feedback/problem/list?page=1&limit=1"
    
    response = requests.get(list_url)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ 获取列表成功！\n")
        
        if data.get('list') and len(data['list']) > 0:
            problem_id = data['list'][0]['problem_id']
            print(f"找到问题 ID: {problem_id}")
            
            # 获取详情
            detail_url = f"{BASE_URL}/v1/feedback/problem/detail/{problem_id}"
            detail_response = requests.get(detail_url)
            
            print(f"\n详情 API 状态码：{detail_response.status_code}")
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print("\n✅ 详情数据获取成功！")
                print("=" * 60)
                for key, value in detail_data.items():
                    print(f"{key}: {value}")
            else:
                print(f"\n❌ 详情获取失败：{detail_response.text}")
        else:
            print("暂无数据")
    else:
        print(f"❌ 列表获取失败：{response.text}")

if __name__ == "__main__":
    try:
        test_problem_detail()
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
