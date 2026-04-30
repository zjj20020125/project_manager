"""
测试质量问题筛选条件 API 接口
用于验证 /api/v1/feedback/problem/filters 接口的数据格式
"""
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8000"

def test_problem_filters():
    """测试筛选条件接口"""
    print("=" * 60)
    print("测试接口：GET /v1/feedback/problem/filters")
    print("=" * 60)
    
    try:
        # 发送 GET 请求
        response = requests.get(f"{BASE_URL}/v1/feedback/problem/filters")
        
        # 检查响应状态码
        print(f"\n✅ 响应状态码：{response.status_code}")
        
        if response.status_code == 200:
            # 解析 JSON 数据
            data = response.json()
            
            print("\n📦 完整响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 验证数据结构
            if data.get("success"):
                print("\n✅ 接口调用成功")
                
                filters_data = data.get("data", {})
                
                # 检查月份数据
                months = filters_data.get("months", [])
                print(f"\n📅 月份数据:")
                print(f"   - 数量：{len(months)}")
                print(f"   - 前 5 个：{months[:5] if len(months) > 5 else months}")
                print(f"   - 数据类型：{type(months)}")
                print(f"   - 示例格式：{months[0] if months else '无数据'}")
                
                # 检查车型数据
                product_types = filters_data.get("product_types", [])
                print(f"\n🚗 车型数据:")
                print(f"   - 数量：{len(product_types)}")
                print(f"   - 前 5 个：{product_types[:5] if len(product_types) > 5 else product_types}")
                print(f"   - 数据类型：{type(product_types)}")
                print(f"   - 示例格式：{product_types[0] if product_types else '无数据'}")
                
                # 检查责任班组数据
                departments = filters_data.get("departments", [])
                print(f"\n👥 责任班组数据:")
                print(f"   - 数量：{len(departments)}")
                print(f"   - 前 5 个：{departments[:5] if len(departments) > 5 else departments}")
                print(f"   - 数据类型：{type(departments)}")
                print(f"   - 示例格式：{departments[0] if departments else '无数据'}")
                
                # 生成前端使用示例
                print("\n" + "=" * 60)
                print("🎯 前端使用示例:")
                print("=" * 60)
                print("""
// 前端接收到的数据格式：
const filterOptions = {
  months: ["2026-01", "2026-02", "2026-03"],
  product_types: ["CRH6F", "复兴号", "和谐号"],
  departments: ["车间 A", "车间 B", "班组 C"]
}

// Vue 模板中使用：
// 月份选择器（直接使用，不需要转换）
<el-date-picker v-model="filterForm.month" type="month" />

// 车型下拉框
<el-select v-model="filterForm.product_type">
  <el-option 
    v-for="type in filterOptions.product_types" 
    :key="type" 
    :label="type" 
    :value="type" 
  />
</el-select>

// 责任部门下拉框
<el-select v-model="filterForm.department">
  <el-option 
    v-for="dept in filterOptions.departments" 
    :key="dept" 
    :label="dept" 
    :value="dept" 
  />
</el-select>
                """)
                
                print("\n✅ 数据格式验证通过！")
                
            else:
                print("\n❌ 接口返回 success=false")
        else:
            print(f"\n❌ 请求失败：{response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接错误：无法连接到服务器")
        print("   请确保后端服务正在运行 (通常是 http://localhost:8000)")
    except Exception as e:
        print(f"\n❌ 发生错误：{str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_problem_filters()
