import requests
import time

print('测试后端+AI服务集成...')
start = time.time()

try:
    response = requests.post(
        'http://127.0.0.1:8081/api/sql/optimize',
        json={'sql': 'SELECT * FROM users WHERE age > 18', 'optimizationLevel': 'medium'},
        timeout=120
    )
    elapsed = time.time() - start
    print(f'状态码: {response.status_code}')
    print(f'耗时: {elapsed:.2f}s')
    result = response.json()
    print(f'Success: {result.get("success")}')
    if result.get('success'):
        data = result.get('data', {})
        print(f'优化SQL: {data.get("optimizedSql", "N/A")[:100]}')
        print(f'问题数: {len(data.get("problems", []))}')
        print(f'建议数: {len(data.get("optimizationSuggestions", []))}')
        print('\n✅ 测试成功！')
    else:
        print(f'Error: {result.get("message")}')
except Exception as e:
    print(f'❌ 测试失败: {e}')