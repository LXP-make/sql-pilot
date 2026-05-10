import chromadb

# 加载数据库
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("sql_rules")

print(f"数据库中有 {collection.count()} 条知识\n")

# 测试查询
query = "SELECT * FROM users WHERE age > 18"
print(f"查询: {query}")
print("="*50)

results = collection.query(
    query_texts=[query],
    n_results=3
)

print("\n找到的相关知识:")
for i, doc in enumerate(results["documents"][0], 1):
    print(f"\n{i}. {doc[:200]}...")

print("\n" + "="*50)
print("知识库测试成功！")