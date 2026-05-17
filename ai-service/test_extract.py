import json
import re

def extract_optimized_sql(ai_response: str) -> str:
    print(f"原始响应: {repr(ai_response[:200])}...")
    
    match = re.search(r"```sql\n(.*?)\n```", ai_response, re.DOTALL)
    if match:
        print("找到 sql 代码块")
        return match.group(1).strip()
    
    match = re.search(r"```\w*\n(.*?)\n```", ai_response, re.DOTALL)
    if match:
        print("找到普通代码块")
        content = match.group(1).strip()
        print(f"代码块内容: {repr(content[:100])}")
        if content.startswith("{"):
            try:
                data = json.loads(content)
                if "optimized_sql" in data:
                    print(f"从JSON中提取: {data['optimized_sql']}")
                    return data["optimized_sql"]
            except Exception as e:
                print(f"JSON解析失败: {e}")
        return content
    
    if ai_response.startswith("{"):
        print("响应是JSON格式")
        try:
            data = json.loads(ai_response)
            if "optimized_sql" in data:
                return data["optimized_sql"]
        except Exception as e:
            print(f"JSON解析失败: {e}")
    
    lines = ai_response.split("\n")
    for line in lines:
        line = line.strip()
        if line.upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE")):
            return line
    
    return ai_response

test_response = """```json
{
    "problems": [
        "SELECT * 使用了通配符，未指定具体字段"
    ],
    "suggestions": [
        "将 SELECT * 改为具体字段列表"
    ],
    "optimized_sql": "SELECT id, name, email FROM users WHERE age > 18;"
}
```"""

result = extract_optimized_sql(test_response)
print(f"最终结果: {result}")
