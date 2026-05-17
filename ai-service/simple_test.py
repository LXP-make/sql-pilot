import requests
import json

def test_ai_service():
    base_url = "http://127.0.0.1:8000"
    
    test_sql = "SELECT * FROM users WHERE age > 18"
    
    print(f"测试AI服务: {base_url}/ai/optimize")
    print(f"SQL: {test_sql}")
    
    try:
        response = requests.post(
            f"{base_url}/ai/optimize",
            json={"sql": test_sql},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n状态码: {response.status_code}")
            print(f"成功: {result.get('success')}")
            
            if result.get('success'):
                data = result.get('data', {})
                print(f"问题列表: {data.get('problems', [])}")
                suggestions = data.get('optimization_suggestions', [])
                print(f"优化建议数: {len(suggestions)}")
                if suggestions:
                    for i, s in enumerate(suggestions[:3], 1):
                        print(f"  {i}. {s.get('description', '')[:80]}")
                print(f"优化后SQL: {data.get('optimized_sql', '')[:100]}")
            else:
                print(f"错误信息: {result.get('message')}")
        else:
            print(f"HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"异常: {str(e)}")

if __name__ == "__main__":
    test_ai_service()