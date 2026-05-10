import json
import requests
import chromadb

from sentence_transformers import SentenceTransformer

# embedding 模型
embedding_model = SentenceTransformer(
    'BAAI/bge-small-zh-v1.5'
)

# chroma
client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="sql_rules"
)

# 用户 SQL
sql = "select * from user"

# 转向量
query_embedding = embedding_model.encode(sql).tolist()

# 相似检索
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2
)

# 检索知识
knowledge = "\n".join(
    results["documents"][0]
)

# Prompt
prompt = f"""
你是SQL优化专家。

以下是SQL优化知识：

{knowledge}

请分析以下SQL：

{sql}

请返回：

1. SQL存在的问题
2. 优化建议
3. 优化后的SQL
"""

# session
session = requests.Session()

# 禁用代理（关键）
session.trust_env = False

# 调用 Ollama
response = session.post(
    "http://127.0.0.1:11434/api/generate",
    headers={
        "Content-Type": "application/json"
    },
    data=json.dumps({
        "model": "qwen2.5",
        "prompt": prompt,
        "stream": False
    }),
    timeout=600
)

# 输出
result = response.json()

print(result["response"])