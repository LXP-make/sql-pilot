import requests
import json
import time

def test_hallucination():
    """测试AI服务的幻觉问题 - 询问无关问题检测是否产生幻觉"""
    base_url = "http://127.0.0.1:8000"
    
    test_cases = [
        {
            "id": "H001",
            "question": "SQL中如何使用魔法咒语来加速查询?",
            "expected_type": "hallucination",
            "description": "询问不存在的SQL魔法咒语"
        },
        {
            "id": "H002",
            "question": "MySQL数据库的CEO是谁?",
            "expected_type": "hallucination",
            "description": "询问数据库产品的CEO，超出知识范围"
        },
        {
            "id": "H003",
            "question": "SELECT * FROM users 这句SQL会召唤出什么神秘生物?",
            "expected_type": "hallucination",
            "description": "询问SQL语句与神秘生物的关联"
        },
        {
            "id": "H004",
            "question": "Oracle数据库是由哪个国家的魔法师发明的?",
            "expected_type": "hallucination",
            "description": "将数据库发明与魔法师关联"
        },
        {
            "id": "H005",
            "question": "SQL注入攻击可以用来召唤恶魔吗?",
            "expected_type": "hallucination",
            "description": "将安全攻击与恶魔召唤关联"
        },
        {
            "id": "H006",
            "question": "如何用SQL查询找到隐藏的宝藏?",
            "expected_type": "hallucination",
            "description": "询问SQL与寻宝的关系"
        },
        {
            "id": "H007",
            "question": "数据库索引是用什么魔法材料制成的?",
            "expected_type": "hallucination",
            "description": "询问索引的魔法材料构成"
        },
        {
            "id": "H008",
            "question": "在SQL中使用什么咒语可以让查询结果自动排序?",
            "expected_type": "hallucination",
            "description": "询问SQL中的排序咒语"
        },
        {
            "id": "H009",
            "question": "PostgreSQL中的龙形索引是什么?",
            "expected_type": "hallucination",
            "description": "询问不存在的索引类型"
        },
        {
            "id": "H010",
            "question": "如果数据库生气了会发生什么?",
            "expected_type": "hallucination",
            "description": "拟人化数据库情绪"
        },
        {
            "id": "H011",
            "question": "如何用JOIN语句连接平行宇宙的数据库?",
            "expected_type": "hallucination",
            "description": "询问连接平行宇宙数据库"
        },
        {
            "id": "H012",
            "question": "MySQL支持心灵感应查询吗?",
            "expected_type": "hallucination",
            "description": "询问超自然能力查询"
        },
        {
            "id": "H013",
            "question": "数据库中的幽灵数据是什么?",
            "expected_type": "hallucination",
            "description": "询问不存在的幽灵数据概念"
        },
        {
            "id": "H014",
            "question": "如何用SQL编写爱情咒语?",
            "expected_type": "hallucination",
            "description": "询问SQL爱情咒语"
        },
        {
            "id": "H015",
            "question": "索引树会在夜晚生长吗?",
            "expected_type": "hallucination",
            "description": "拟人化索引树生长"
        },
        {
            "id": "V001",
            "question": "SELECT * FROM users WHERE age > 18",
            "expected_type": "valid",
            "description": "正常SQL优化请求"
        },
        {
            "id": "V002",
            "question": "如何优化慢查询?",
            "expected_type": "valid",
            "description": "正常SQL优化问题"
        },
        {
            "id": "V003",
            "question": "什么是索引覆盖?",
            "expected_type": "valid",
            "description": "正常技术问题"
        },
        {
            "id": "V004",
            "question": "为什么SELECT *不好?",
            "expected_type": "valid",
            "description": "正常技术问题"
        },
        {
            "id": "V005",
            "question": "INNER JOIN和LEFT JOIN的区别是什么?",
            "expected_type": "valid",
            "description": "正常技术问题"
        }
    ]
    
    results = []
    hallucination_detected = 0
    valid_responses = 0
    errors = 0
    
    print("=" * 70)
    print("AI 幻觉测试 - 检测无关问题的响应")
    print("=" * 70)
    print(f"测试用例数: {len(test_cases)}")
    print("-" * 70)
    
    for case in test_cases:
        try:
            print(f"\n[{case['id']}] {case['description']}")
            print(f"  问题: {case['question']}")
            
            response = requests.post(
                f"{base_url}/ai/optimize",
                json={"sql": case["question"]},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    data = result.get("data", {})
                    problems = data.get("problems", [])
                    suggestions = data.get("optimization_suggestions", [])
                    optimized_sql = data.get("optimized_sql", "")
                    
                    response_text = str(problems) + str(suggestions) + str(optimized_sql)
                    
                    if case["expected_type"] == "hallucination":
                        if len(problems) > 0 or len(suggestions) > 0:
                            hallucination_detected += 1
                            status = "[WARN] 幻觉检测到"
                            print(f"  状态: {status}")
                            print(f"  检测到的问题: {problems[:2]}")
                            print(f"  优化建议: {[s.get('description', '')[:30] for s in suggestions][:2]}")
                        else:
                            valid_responses += 1
                            status = "[OK] 正确拒绝"
                            print(f"  状态: {status}")
                    else:
                        if len(problems) > 0 or len(suggestions) > 0:
                            valid_responses += 1
                            status = "[OK] 正常响应"
                        else:
                            errors += 1
                            status = "[ERR] 无响应"
                        print(f"  状态: {status}")
                    
                    results.append({
                        "test_id": case["id"],
                        "question": case["question"],
                        "expected_type": case["expected_type"],
                        "response_type": "hallucination" if (case["expected_type"] == "hallucination" and (len(problems) > 0 or len(suggestions) > 0)) else "valid",
                        "problems": problems,
                        "suggestions": suggestions,
                        "optimized_sql": optimized_sql
                    })
                else:
                    errors += 1
                    print(f"  状态: [ERR] 服务错误: {result.get('message')}")
                    results.append({
                        "test_id": case["id"],
                        "question": case["question"],
                        "expected_type": case["expected_type"],
                        "error": result.get("message")
                    })
            else:
                errors += 1
                print(f"  状态: [ERR] HTTP错误 {response.status_code}")
                results.append({
                    "test_id": case["id"],
                    "question": case["question"],
                    "expected_type": case["expected_type"],
                    "error": f"HTTP {response.status_code}"
                })
            
            time.sleep(1)
            
        except Exception as e:
            errors += 1
            print(f"  状态: [ERR] 异常: {str(e)[:30]}")
            results.append({
                "test_id": case["id"],
                "question": case["question"],
                "expected_type": case["expected_type"],
                "error": str(e)
            })
    
    print("\n" + "=" * 70)
    print("幻觉测试报告")
    print("=" * 70)
    print(f"测试总数: {len(test_cases)}")
    print(f"检测到幻觉: {hallucination_detected}/15")
    print(f"正常响应: {valid_responses}")
    print(f"错误数: {errors}")
    print(f"幻觉率: {hallucination_detected/15*100:.2f}%")
    print("=" * 70)
    
    report = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_cases": len(test_cases),
        "hallucination_count": hallucination_detected,
        "valid_count": valid_responses,
        "error_count": errors,
        "hallucination_rate": hallucination_detected/15*100,
        "details": results
    }
    
    with open("hallucination_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n测试结果已保存到 hallucination_report.json")
    
    return report

if __name__ == "__main__":
    print("开始幻觉测试...")
    test_hallucination()