import requests
import json
import time

def test_ai_service():
    """测试AI服务接口"""
    base_url = "http://127.0.0.1:8080"
    
    # 测试用例
    test_cases = [
        {"id": "S001", "sql": "SELECT * FROM users WHERE age > 18", "expected_problems": ["SELECT *"]},
        {"id": "S002", "sql": "SELECT * FROM users WHERE id = '123'", "expected_problems": ["类型转换"]},
        {"id": "S003", "sql": "SELECT * FROM users WHERE name LIKE '%test'", "expected_problems": ["LIKE"]},
        {"id": "S004", "sql": "SELECT * FROM orders LIMIT 100000, 10", "expected_problems": ["分页"]},
        {"id": "S005", "sql": "SELECT * FROM users WHERE YEAR(create_time) = 2024", "expected_problems": ["函数"]},
        {"id": "S006", "sql": "SELECT * FROM users WHERE id NOT IN (SELECT id FROM banned)", "expected_problems": ["NOT IN"]},
        {"id": "S007", "sql": "SELECT COUNT(*) FROM orders WHERE status = 1", "expected_problems": ["索引"]},
        {"id": "S008", "sql": "SELECT * FROM orders ORDER BY create_time DESC", "expected_problems": ["排序"]},
        {"id": "J001", "sql": "SELECT * FROM orders o JOIN users u ON o.user_id = u.id", "expected_problems": ["JOIN"]},
        {"id": "I001", "sql": "SELECT * FROM users WHERE DATE(create_time) = '2024-01-01'", "expected_problems": ["函数"]},
        {"id": "I002", "sql": "SELECT * FROM users WHERE phone = 13800138000", "expected_problems": ["类型转换"]},
        {"id": "I003", "sql": "SELECT * FROM users WHERE status = 1 OR name = 'test'", "expected_problems": ["OR"]},
        {"id": "P001", "sql": "SELECT * FROM large_table WHERE category = 'A'", "expected_problems": ["全表扫描"]},
        {"id": "P002", "sql": "SELECT * FROM orders ORDER BY RAND() LIMIT 10", "expected_problems": ["随机"]},
        {"id": "P003", "sql": "SELECT DISTINCT status FROM orders", "expected_problems": ["DISTINCT"]},
    ]
    
    results = []
    passed = 0
    failed = 0
    total = len(test_cases)
    
    print("=" * 60)
    print("SQL Pilot AI服务测试")
    print("=" * 60)
    print(f"测试用例数: {total}")
    print("-" * 60)
    
    for case in test_cases:
        try:
            print(f"\n测试 {case['id']}: {case['sql']}")
            
            response = requests.post(
                f"{base_url}/ai/optimize", 
                json={"sql": case["sql"]},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    problems = result.get("data", {}).get("problems", [])
                    suggestions = result.get("data", {}).get("optimization_suggestions", [])
                    optimized_sql = result.get("data", {}).get("optimized_sql", "")
                    
                    # 验证是否检测到预期问题
                    detected_expected = False
                    problems_text = " ".join(problems).lower()
                    for expected in case["expected_problems"]:
                        if expected.lower() in problems_text:
                            detected_expected = True
                            break
                    
                    if detected_expected:
                        passed += 1
                        status = "✅ 通过"
                    else:
                        failed += 1
                        status = "❌ 未检测到预期问题"
                    
                    print(f"  状态: {status}")
                    if problems:
                        print(f"  检测到的问题: {problems}")
                    if suggestions:
                        print(f"  优化建议: {[s.get('description', '') for s in suggestions]}")
                    
                    results.append({
                        "test_id": case["id"],
                        "sql": case["sql"],
                        "success": True,
                        "detected_expected": detected_expected,
                        "problems": problems,
                        "suggestions": suggestions
                    })
                else:
                    failed += 1
                    print(f"  状态: ❌ 服务返回失败: {result.get('message')}")
                    results.append({
                        "test_id": case["id"],
                        "sql": case["sql"],
                        "success": False,
                        "error": result.get("message")
                    })
            else:
                failed += 1
                print(f"  状态: ❌ HTTP错误 {response.status_code}")
                results.append({
                    "test_id": case["id"],
                    "sql": case["sql"],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
            
            # 避免请求过快
            time.sleep(1)
            
        except Exception as e:
            failed += 1
            print(f"  状态: ❌ 异常: {str(e)}")
            results.append({
                "test_id": case["id"],
                "sql": case["sql"],
                "success": False,
                "error": str(e)
            })
    
    # 生成报告
    print("\n" + "=" * 60)
    print("测试报告")
    print("=" * 60)
    print(f"测试总数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"准确率: {passed/total*100:.2f}%")
    print(f"错误率: {failed/total*100:.2f}%")
    print("=" * 60)
    
    # 保存结果到文件
    report = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_cases": total,
        "passed": passed,
        "failed": failed,
        "accuracy": passed/total*100,
        "error_rate": failed/total*100,
        "details": results
    }
    
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n测试结果已保存到 test_results.json")
    
    return report

if __name__ == "__main__":
    # 先启动服务
    print("请确保AI服务已在 http://127.0.0.1:8080 运行")
    input("按回车键开始测试...")
    test_ai_service()