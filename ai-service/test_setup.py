import sys

print("1. 测试模块导入...")
try:
    import fastapi
    import uvicorn
    import chromadb
    import sentence_transformers
    print("   ✓ 所有模块导入成功")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    sys.exit(1)

print("\n2. 测试向量数据库...")
try:
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="sql_rules")
    print(f"   ✓ 集合存在，文档数: {collection.count()}")
except Exception as e:
    print(f"   ✗ 向量数据库失败: {e}")
    sys.exit(1)

print("\n3. 测试 Ollama 连接...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    print(f"   ✓ Ollama 响应: {response.status_code}")
except Exception as e:
    print(f"   ✗ Ollama 连接失败: {e}")
    print("   ⚠ 但服务仍可以启动，只是AI功能不可用")

print("\n✅ 环境检查完成，可以启动服务")
print("\n运行命令:")
print("    uvicorn app:app --reload")