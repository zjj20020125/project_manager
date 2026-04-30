"""测试质量问题列表 API 返回的字段完整性"""
import requests

BASE_URL = "http://localhost:8001"

def test_problem_list_fields():
    """测试问题列表接口返回的字段"""
    url = f"{BASE_URL}/v1/feedback/problem/list?page=1&limit=5"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API 调用成功！\n")
        
        if data.get('list') and len(data['list']) > 0:
            problem = data['list'][0]
            
            print("=" * 80)
            print("📋 质量问题列表 - 字段检查")
            print("=" * 80)
            
            # 需要检查的12个筛选条件字段
            required_fields = {
                'market_category': '市场分类',
                'occurrence_unit': '发生单位',
                'vehicle_model': '车型',
                'production_repair_type': '新造/检修',
                'problem_category': '问题分类',
                'problem_category_1': '问题分类1',
                'supplement_category_2': '补充分类2',
                'product_type': '产品类型',
                'month': '月份',
                'week': '周数',
                'problem_type': '问题定性',
                'department': '新责任班组'
            }
            
            print("\n🔍 检查12个筛选条件字段:\n")
            all_ok = True
            
            for field, label in required_fields.items():
                value = problem.get(field)
                status = "✅" if value is not None else "❌"
                
                if value is None:
                    all_ok = False
                    print(f"{status} {label:12s} ({field:30s}): 缺失")
                else:
                    display_value = str(value)[:40]
                    print(f"{status} {label:12s} ({field:30s}): {display_value}")
            
            print("\n" + "=" * 80)
            
            if all_ok:
                print("✅ 所有字段都正常返回！")
            else:
                print("❌ 部分字段缺失，请检查后端 API")
            
            print("\n📊 完整数据示例:")
            print("-" * 80)
            for key, value in problem.items():
                if value is not None:
                    display_val = str(value)[:60]
                    print(f"  {key:30s}: {display_val}")
            
        else:
            print("⚠️ 暂无数据")
    else:
        print(f"❌ API 调用失败：{response.status_code}")
        print(f"错误信息：{response.text}")

if __name__ == "__main__":
    try:
        test_problem_list_fields()
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
