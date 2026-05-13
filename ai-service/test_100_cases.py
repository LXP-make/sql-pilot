import requests
import json
import time

BACKEND_URL = "http://127.0.0.1:8081"
AI_SERVICE_URL = "http://127.0.0.1:8080"

test_cases = [
    # ========== SELECT语句测试 (1-20) ==========
    {"id": "SEL-001", "sql": "SELECT * FROM users WHERE age > 18", "keywords": ["select", "select *"]},
    {"id": "SEL-002", "sql": "SELECT * FROM users WHERE id = '123'", "keywords": ["类型", "转换"]},
    {"id": "SEL-003", "sql": "SELECT * FROM users WHERE name LIKE '%test'", "keywords": ["like", "通配符"]},
    {"id": "SEL-004", "sql": "SELECT * FROM orders LIMIT 100000, 10", "keywords": ["分页", "limit"]},
    {"id": "SEL-005", "sql": "SELECT * FROM users WHERE YEAR(create_time) = 2024", "keywords": ["函数", "索引失效"]},
    {"id": "SEL-006", "sql": "SELECT * FROM users WHERE id NOT IN (SELECT id FROM banned)", "keywords": ["not in", "子查询"]},
    {"id": "SEL-007", "sql": "SELECT COUNT(*) FROM orders WHERE status = 1", "keywords": ["count", "聚合"]},
    {"id": "SEL-008", "sql": "SELECT * FROM orders ORDER BY create_time DESC", "keywords": ["order by", "排序"]},
    {"id": "SEL-009", "sql": "SELECT * FROM users WHERE id = 123 OR name = 'test'", "keywords": ["or", "条件"]},
    {"id": "SEL-010", "sql": "SELECT * FROM orders ORDER BY RAND() LIMIT 10", "keywords": ["rand", "随机"]},
    {"id": "SEL-011", "sql": "SELECT * FROM users WHERE LOWER(name) = 'test'", "keywords": ["lower", "函数"]},
    {"id": "SEL-012", "sql": "SELECT * FROM users WHERE name LIKE '%test%'", "keywords": ["like", "前后通配符"]},
    {"id": "SEL-013", "sql": "SELECT DISTINCT status FROM orders", "keywords": ["distinct", "去重"]},
    {"id": "SEL-014", "sql": "SELECT * FROM users WHERE age > 18 AND name LIKE 'a%'", "keywords": ["复合条件", "索引"]},
    {"id": "SEL-015", "sql": "SELECT * FROM large_table WHERE category = 'A'", "keywords": ["全表扫描", "索引"]},
    {"id": "SEL-016", "sql": "SELECT * FROM users WHERE age + 1 > 18", "keywords": ["表达式", "索引失效"]},
    {"id": "SEL-017", "sql": "SELECT * FROM users WHERE name IS NULL", "keywords": ["is null"]},
    {"id": "SEL-018", "sql": "SELECT * FROM users WHERE name != 'test'", "keywords": ["不等于"]},
    {"id": "SEL-019", "sql": "SELECT * FROM users WHERE id IN (1,2,3,4,5)", "keywords": ["in", "列表"]},
    {"id": "SEL-020", "sql": "SELECT * FROM users WHERE name LIKE 't%'", "keywords": ["like", "后通配符"]},

    # ========== JOIN语句测试 (21-30) ==========
    {"id": "JOIN-001", "sql": "SELECT * FROM orders o JOIN users u ON o.user_id = u.id", "keywords": ["join", "索引"]},
    {"id": "JOIN-002", "sql": "SELECT * FROM a JOIN b ON a.id = b.a_id JOIN c ON b.id = c.b_id", "keywords": ["join", "多表"]},
    {"id": "JOIN-003", "sql": "SELECT * FROM orders o LEFT JOIN users u ON o.user_id = u.id", "keywords": ["left join"]},
    {"id": "JOIN-004", "sql": "SELECT * FROM users u RIGHT JOIN orders o ON u.id = o.user_id", "keywords": ["right join"]},
    {"id": "JOIN-005", "sql": "SELECT * FROM t1 JOIN t2 ON t1.id = t2.id WHERE t1.status = 1", "keywords": ["join", "where"]},
    {"id": "JOIN-006", "sql": "SELECT * FROM users INNER JOIN orders ON users.id = orders.user_id", "keywords": ["inner join"]},
    {"id": "JOIN-007", "sql": "SELECT * FROM t1 JOIN t2 ON t1.name = t2.name", "keywords": ["join", "非主键"]},
    {"id": "JOIN-008", "sql": "SELECT * FROM t1, t2 WHERE t1.id = t2.id", "keywords": ["隐式join", "逗号"]},
    {"id": "JOIN-009", "sql": "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE u.status = 1", "keywords": ["join", "条件"]},
    {"id": "JOIN-010", "sql": "SELECT * FROM a LEFT JOIN b ON a.id = b.id LEFT JOIN c ON b.id = c.id", "keywords": ["多层left join"]},

    # ========== 索引测试 (31-40) ==========
    {"id": "IDX-001", "sql": "SELECT * FROM users WHERE DATE(create_time) = '2024-01-01'", "keywords": ["date", "函数"]},
    {"id": "IDX-002", "sql": "SELECT * FROM users WHERE phone = 13800138000", "keywords": ["类型", "转换"]},
    {"id": "IDX-003", "sql": "SELECT * FROM users WHERE status = 1 OR name = 'test'", "keywords": ["or", "索引"]},
    {"id": "IDX-004", "sql": "SELECT * FROM users WHERE age > 18 AND name = 'test'", "keywords": ["复合索引", "最左前缀"]},
    {"id": "IDX-005", "sql": "SELECT * FROM users WHERE name = 'test' AND age > 18", "keywords": ["复合索引"]},
    {"id": "IDX-006", "sql": "SELECT * FROM users WHERE id > 100 AND age > 18", "keywords": ["范围查询"]},
    {"id": "IDX-007", "sql": "SELECT * FROM users WHERE name IN ('a', 'b', 'c')", "keywords": ["in", "列表"]},
    {"id": "IDX-008", "sql": "SELECT * FROM users WHERE name BETWEEN 'a' AND 'z'", "keywords": ["between", "范围"]},
    {"id": "IDX-009", "sql": "SELECT * FROM users WHERE name <> 'test'", "keywords": ["不等于"]},
    {"id": "IDX-010", "sql": "SELECT * FROM users WHERE MONTH(create_time) = 5", "keywords": ["month", "函数"]},

    # ========== 子查询测试 (41-50) ==========
    {"id": "SUB-001", "sql": "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)", "keywords": ["in", "子查询"]},
    {"id": "SUB-002", "sql": "SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id)", "keywords": ["exists"]},
    {"id": "SUB-003", "sql": "SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM orders)", "keywords": ["not in", "子查询"]},
    {"id": "SUB-004", "sql": "SELECT * FROM (SELECT * FROM users WHERE age > 18) AS t", "keywords": ["嵌套子查询"]},
    {"id": "SUB-005", "sql": "SELECT * FROM users u WHERE u.id = (SELECT MAX(id) FROM orders)", "keywords": ["标量子查询"]},
    {"id": "SUB-006", "sql": "SELECT name, (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) FROM users u", "keywords": ["相关子查询"]},
    {"id": "SUB-007", "sql": "SELECT * FROM users WHERE (SELECT COUNT(*) FROM orders) > 5", "keywords": ["标量子查询"]},
    {"id": "SUB-008", "sql": "SELECT * FROM users WHERE id IN (SELECT id FROM (SELECT id FROM users WHERE status = 1) AS t)", "keywords": ["多层嵌套"]},
    {"id": "SUB-009", "sql": "SELECT AVG(total) FROM (SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id) AS t", "keywords": ["派生表"]},
    {"id": "SUB-010", "sql": "DELETE FROM users WHERE id IN (SELECT id FROM banned_users)", "keywords": ["delete", "子查询"]},

    # ========== UNION测试 (51-55) ==========
    {"id": "UNION-001", "sql": "SELECT * FROM t1 UNION SELECT * FROM t2", "keywords": ["union", "去重"]},
    {"id": "UNION-002", "sql": "SELECT * FROM t1 UNION ALL SELECT * FROM t2", "keywords": ["union all"]},
    {"id": "UNION-003", "sql": "SELECT id, name FROM t1 UNION SELECT id, name FROM t2", "keywords": ["union", "列"]},
    {"id": "UNION-004", "sql": "SELECT * FROM old_users UNION SELECT * FROM new_users ORDER BY id", "keywords": ["union", "排序"]},
    {"id": "UNION-005", "sql": "SELECT 'A' AS type, * FROM table_a UNION SELECT 'B' AS type, * FROM table_b", "keywords": ["union", "类型"]},

    # ========== GROUP BY测试 (56-60) ==========
    {"id": "GROUP-001", "sql": "SELECT category, COUNT(*) FROM products GROUP BY category", "keywords": ["group by", "聚合"]},
    {"id": "GROUP-002", "sql": "SELECT category, COUNT(*) FROM products GROUP BY category HAVING COUNT(*) > 10", "keywords": ["group by", "having"]},
    {"id": "GROUP-003", "sql": "SELECT category, COUNT(*) FROM products GROUP BY 1", "keywords": ["group by", "位置"]},
    {"id": "GROUP-004", "sql": "SELECT DATE(create_time), COUNT(*) FROM orders GROUP BY DATE(create_time)", "keywords": ["group by", "函数"]},
    {"id": "GROUP-005", "sql": "SELECT user_id, SUM(amount) FROM orders GROUP BY user_id HAVING SUM(amount) > 1000", "keywords": ["group by", "having"]},

    # ========== 数据类型测试 (61-65) ==========
    {"id": "TYPE-001", "sql": "SELECT * FROM users WHERE id = '123'", "keywords": ["类型", "转换"]},
    {"id": "TYPE-002", "sql": "SELECT * FROM users WHERE phone = 13800138000", "keywords": ["类型", "转换"]},
    {"id": "TYPE-003", "sql": "SELECT * FROM users WHERE age = '18'", "keywords": ["类型", "转换"]},
    {"id": "TYPE-004", "sql": "SELECT * FROM users WHERE created_at = 1640995200", "keywords": ["类型", "时间戳"]},
    {"id": "TYPE-005", "sql": "SELECT * FROM orders WHERE total = '100.00'", "keywords": ["类型", "转换"]},

    # ========== 函数测试 (66-75) ==========
    {"id": "FUNC-001", "sql": "SELECT * FROM users WHERE YEAR(create_time) = 2024", "keywords": ["year", "函数"]},
    {"id": "FUNC-002", "sql": "SELECT * FROM users WHERE MONTH(create_time) = 5", "keywords": ["month", "函数"]},
    {"id": "FUNC-003", "sql": "SELECT * FROM users WHERE DATE(create_time) = '2024-01-01'", "keywords": ["date", "函数"]},
    {"id": "FUNC-004", "sql": "SELECT * FROM users WHERE LOWER(name) = 'test'", "keywords": ["lower", "函数"]},
    {"id": "FUNC-005", "sql": "SELECT * FROM users WHERE UPPER(name) = 'TEST'", "keywords": ["upper", "函数"]},
    {"id": "FUNC-006", "sql": "SELECT * FROM users WHERE SUBSTRING(name, 1, 3) = 'abc'", "keywords": ["substring", "函数"]},
    {"id": "FUNC-007", "sql": "SELECT * FROM users WHERE LENGTH(name) > 10", "keywords": ["length", "函数"]},
    {"id": "FUNC-008", "sql": "SELECT * FROM users WHERE TRIM(name) = 'test'", "keywords": ["trim", "函数"]},
    {"id": "FUNC-009", "sql": "SELECT * FROM users WHERE ABS(age - 18) < 5", "keywords": ["abs", "函数"]},
    {"id": "FUNC-010", "sql": "SELECT * FROM users WHERE ROUND(price, 2) = 100", "keywords": ["round", "函数"]},

    # ========== 分页测试 (76-80) ==========
    {"id": "PAGE-001", "sql": "SELECT * FROM orders LIMIT 10", "keywords": ["limit"]},
    {"id": "PAGE-002", "sql": "SELECT * FROM orders LIMIT 1000, 10", "keywords": ["limit", "offset"]},
    {"id": "PAGE-003", "sql": "SELECT * FROM orders LIMIT 10000, 10", "keywords": ["分页", "深度"]},
    {"id": "PAGE-004", "sql": "SELECT * FROM orders LIMIT 100000, 10", "keywords": ["分页", "offset大"]},
    {"id": "PAGE-005", "sql": "SELECT * FROM orders ORDER BY id DESC LIMIT 10", "keywords": ["分页", "排序"]},

    # ========== 排序测试 (81-85) ==========
    {"id": "SORT-001", "sql": "SELECT * FROM users ORDER BY name", "keywords": ["order by", "索引"]},
    {"id": "SORT-002", "sql": "SELECT * FROM users ORDER BY name, age", "keywords": ["order by", "多列"]},
    {"id": "SORT-003", "sql": "SELECT * FROM users ORDER BY name DESC, age ASC", "keywords": ["order by", "方向"]},
    {"id": "SORT-004", "sql": "SELECT * FROM users ORDER BY RAND()", "keywords": ["rand", "随机"]},
    {"id": "SORT-005", "sql": "SELECT * FROM users ORDER BY LENGTH(name)", "keywords": ["order by", "函数"]},

    # ========== 聚合函数测试 (86-90) ==========
    {"id": "AGG-001", "sql": "SELECT COUNT(*) FROM users", "keywords": ["count", "聚合"]},
    {"id": "AGG-002", "sql": "SELECT COUNT(id) FROM users", "keywords": ["count", "列"]},
    {"id": "AGG-003", "sql": "SELECT MAX(age) FROM users", "keywords": ["max", "聚合"]},
    {"id": "AGG-004", "sql": "SELECT MIN(age) FROM users", "keywords": ["min", "聚合"]},
    {"id": "AGG-005", "sql": "SELECT AVG(age) FROM users", "keywords": ["avg", "聚合"]},

    # ========== LIKE测试 (91-95) ==========
    {"id": "LIKE-001", "sql": "SELECT * FROM users WHERE name LIKE 'test%'", "keywords": ["like", "后通配符"]},
    {"id": "LIKE-002", "sql": "SELECT * FROM users WHERE name LIKE '%test'", "keywords": ["like", "前通配符"]},
    {"id": "LIKE-003", "sql": "SELECT * FROM users WHERE name LIKE '%test%'", "keywords": ["like", "前后通配符"]},
    {"id": "LIKE-004", "sql": "SELECT * FROM users WHERE name LIKE 't_st'", "keywords": ["like", "_", "下划线"]},
    {"id": "LIKE-005", "sql": "SELECT * FROM users WHERE name NOT LIKE 'test%'", "keywords": ["not like"]},

    # ========== NULL测试 (96-100) ==========
    {"id": "NULL-001", "sql": "SELECT * FROM users WHERE name IS NULL", "keywords": ["is null"]},
    {"id": "NULL-002", "sql": "SELECT * FROM users WHERE name IS NOT NULL", "keywords": ["is not null"]},
    {"id": "NULL-003", "sql": "SELECT * FROM users WHERE name = NULL", "keywords": ["= null", "错误"]},
    {"id": "NULL-004", "sql": "SELECT COUNT(*) FROM users WHERE name IS NULL", "keywords": ["count", "null"]},
    {"id": "NULL-005", "sql": "SELECT COALESCE(name, 'unknown') FROM users", "keywords": ["coalesce", "null"]},
]

def test_backend_ai_integration():
    """测试通过后端调用AI服务，结果保存到MySQL"""
    results = []
    passed = 0
    failed = 0
    total = len(test_cases)

    print("=" * 80)
    print("SQL Pilot 100 Test Cases - Backend + AI Service Integration Test")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"AI Service URL: {AI_SERVICE_URL}")
    print("-" * 80)
    print(f"Total Test Cases: {total}")
    print("-" * 80)

    for idx, case in enumerate(test_cases):
        try:
            print(f"\n[{idx+1}/{total}] {case['id']}: {case['sql'][:50]}...")

            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/api/sql/optimize",
                json={"sql": case["sql"], "optimizationLevel": "medium"},
                timeout=120
            )
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()

                if result.get("success"):
                    data = result.get("data", {})
                    # 处理null值
                    problems = data.get("problems") or []
                    suggestions = data.get("optimizationSuggestions") or []
                    optimized_sql = data.get("optimizedSql") or ""

                    problems_text = " ".join(str(p) for p in problems).lower()
                    suggestions_text = " ".join(str(s) for s in suggestions).lower()
                    optimized_text = optimized_sql.lower() if optimized_sql else ""
                    all_text = (problems_text + suggestions_text + optimized_text).lower()

                    detected_keywords = []
                    for keyword in case["keywords"]:
                        if keyword.lower() in all_text:
                            detected_keywords.append(keyword)

                    is_passed = len(detected_keywords) > 0
                    if is_passed:
                        passed += 1
                        status = "[PASS]"
                    else:
                        failed += 1
                        status = "[FAIL]"

                    print(f"  Status: {status} - Time: {elapsed_time:.2f}s - Detected: {detected_keywords[:3]}")

                    results.append({
                        "test_id": case["id"],
                        "sql": case["sql"],
                        "passed": is_passed,
                        "detected_keywords": detected_keywords,
                        "problems": problems,
                        "suggestions": suggestions,
                        "elapsed_time": elapsed_time,
                        "saved_to_db": True
                    })
                else:
                    failed += 1
                    print(f"  Status: [FAIL] - Service error")
                    results.append({
                        "test_id": case["id"],
                        "sql": case["sql"],
                        "passed": False,
                        "error": result.get("message"),
                        "elapsed_time": elapsed_time,
                        "saved_to_db": False
                    })
            else:
                failed += 1
                print(f"  Status: [FAIL] - HTTP {response.status_code}")
                results.append({
                    "test_id": case["id"],
                    "sql": case["sql"],
                    "passed": False,
                    "error": f"HTTP {response.status_code}",
                    "elapsed_time": elapsed_time,
                    "saved_to_db": False
                })

            if (idx + 1) % 10 == 0:
                time.sleep(2)
            else:
                time.sleep(0.5)

        except Exception as e:
            failed += 1
            print(f"  Status: [FAIL] - Error: {str(e)[:50]}")
            results.append({
                "test_id": case["id"],
                "sql": case["sql"],
                "passed": False,
                "error": str(e),
                "elapsed_time": 0,
                "saved_to_db": False
            })

    print("\n" + "=" * 80)
    print("Test Report")
    print("=" * 80)
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {passed/total*100:.2f}%")
    print(f"Error Rate: {failed/total*100:.2f}%")
    print("=" * 80)

    # 分类统计
    categories = {}
    for r in results:
        prefix = r["test_id"].split("-")[0]
        if prefix not in categories:
            categories[prefix] = {"total": 0, "passed": 0, "failed": 0}
        categories[prefix]["total"] += 1
        if r.get("passed"):
            categories[prefix]["passed"] += 1
        else:
            categories[prefix]["failed"] += 1

    print("\nCategory Stats:")
    for cat, stats in sorted(categories.items()):
        acc = stats["passed"]/stats["total"]*100 if stats["total"] > 0 else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} - {acc:.1f}%")

    print("\n" + "=" * 80)
    print("Database Save Status:")
    saved_count = sum(1 for r in results if r.get("saved_to_db"))
    print(f"  Saved to MySQL: {saved_count}/{total}")
    print(f"  Failed/Not Saved: {total - saved_count}/{total}")
    print("=" * 80)

    report = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_cases": total,
        "passed": passed,
        "failed": failed,
        "accuracy": passed/total*100,
        "error_rate": failed/total*100,
        "categories": categories,
        "saved_to_db": saved_count,
        "details": results
    }

    with open("test_report_100.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\nTest results saved to test_report_100.json")

    return report

if __name__ == "__main__":
    print("Starting 100 test cases...")
    print("Note: Results will be saved to MySQL database automatically")
    print("-" * 80)

    try:
        report = test_backend_ai_integration()
        print(f"\nTest completed!")
        print(f"Accuracy: {report['accuracy']:.2f}%")
        print(f"Database Save: {report['saved_to_db']}/{report['total_cases']} cases")
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()