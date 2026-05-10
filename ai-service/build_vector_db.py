import json
import chromadb

from sentence_transformers import SentenceTransformer

# 加载 embedding 模型
model = SentenceTransformer(
    'BAAI/bge-small-zh-v1.5'
)

# 创建 chroma 数据库
client = chromadb.PersistentClient(
    path="./chroma_db"
)

# 创建 collection
collection = client.get_or_create_collection(
    name="sql_rules"
)

# 读取知识库
with open(
    "knowledge/sql_rules.json",
    "r",
    encoding="utf-8"
) as f:

    rules = json.load(f)

# 写入向量数据库
for rule in rules:

    text = f"""
    问题: {rule['problem']}
    原因: {rule['reason']}
    解决方案: {rule['solution']}
    示例: {rule['example']}
    """

    embedding = model.encode(text).tolist()

    collection.add(
        ids=[rule['id']],
        documents=[text],
        embeddings=[embedding]
    )

print("向量数据库构建完成")