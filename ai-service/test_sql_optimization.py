import requests
import json

def test_sql_optimization(sql, description):
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"{'='*60}")
    print(f"原始SQL:\n{sql}")
    
    try:
        response = requests.post('http://localhost:8080/ai/optimize', json={'sql': sql})
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            data = result['data']
            print(f"\n优化后SQL:\n{data['optimized_sql']}")
            
            if data.get('optimization_suggestions'):
                print("\n优化建议:")
                for i, suggestion in enumerate(data['optimization_suggestions'], 1):
                    print(f"  {i}. {suggestion['description']}")
            
            if data.get('rag_info') and len(data['rag_info']) > 0:
                print("\nRAG检索信息:")
                for doc in data['rag_info']:
                    print(f"  - {doc['filename']} (关键词: {doc['keyword_score']:.2f}, 语义: {doc['semantic_score']:.2f})")
            
            if data.get('problems'):
                print("\n检测到的问题:")
                for problem in data['problems']:
                    print(f"  - {problem}")
                    
            return True
        else:
            print(f"错误: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return False

test_cases = [
    {
        'sql': 'SELECT * FROM users WHERE age > 18',
        'description': 'SELECT * 通配符查询'
    },
    {
        'sql': 'SELECT name FROM student WHERE id IN (SELECT stu_id FROM score WHERE score>90)',
        'description': 'IN子查询'
    },
    {
        'sql': 'SELECT * FROM orders o, users u WHERE o.user_id = u.id AND o.status = "completed"',
        'description': '隐式JOIN查询'
    },
    {
        'sql': 'SELECT COUNT(*), SUM(amount) FROM orders WHERE created_at > "2024-01-01"',
        'description': '聚合函数查询'
    },
    {
        'sql': 'SELECT * FROM products ORDER BY price DESC LIMIT 10 OFFSET 20',
        'description': '排序分页查询'
    },
    {
        'sql': 'SELECT * FROM logs WHERE status=1 AND level="error" AND time > "2024-01-01"',
        'description': '多条件查询'
    },
    {
        'sql': 'SELECT * FROM large_table WHERE name LIKE "%keyword%"',
        'description': '通配符模糊查询'
    },
    {
        'sql': 'SELECT * FROM a JOIN b ON a.id=b.a_id JOIN c ON b.id=c.b_id WHERE a.status=1',
        'description': '多表关联查询'
    },
    {
        'sql': 'SELECT t1.*, t2.* FROM table1 t1 LEFT JOIN table2 t2 ON t1.id = t2.t1_id',
        'description': 'LEFT JOIN查询'
    },
    {
        'sql': 'SELECT department, AVG(salary) as avg_sal FROM employees GROUP BY department HAVING AVG(salary) > 5000',
        'description': 'GROUP BY与HAVING'
    },
    {
        'sql': 'UPDATE users SET status=0 WHERE last_login < "2024-01-01"',
        'description': 'UPDATE语句优化'
    },
    {
        'sql': 'DELETE FROM logs WHERE created_at < "2024-01-01"',
        'description': 'DELETE语句优化'
    }
]

print("SQL优化测试脚本")
print("="*60)
print(f"共 {len(test_cases)} 个测试用例")
print("="*60)

success_count = 0
for test_case in test_cases:
    if test_sql_optimization(test_case['sql'], test_case['description']):
        success_count += 1

print("\n" + "="*60)
print(f"测试结果: {success_count}/{len(test_cases)} 成功")
print("="*60)