import chromadb

from sentence_transformers import SentenceTransformer

# embedding 模型
model = SentenceTransformer(
    'BAAI/bge-small-zh-v1.5'
)

# chroma 数据库
client = chromadb.PersistentClient(
    path="./chroma_db"
)

# 获取 collection
collection = client.get_collection(
    name="sql_rules"
)

# 测试 SQL
query = "select * from user"

# 转向量
query_embedding = model.encode(query).tolist()

# 检索
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2
)

print(results)