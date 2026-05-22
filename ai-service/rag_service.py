import json
import re
import os
import chromadb
from sentence_transformers import SentenceTransformer
from memory_system import get_memory_system, get_reward_system

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "sql_rules"
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
TOP_K = 5


class ChromaRetriever:
    """Retrieves relevant knowledge from ChromaDB using semantic search."""

    def __init__(self):
        self._model = None
        self._collection = None
        self._keyword_cache = {}

    def _get_model(self):
        if self._model is None:
            self._model = SentenceTransformer(EMBEDDING_MODEL)
        return self._model

    def _get_collection(self):
        if self._collection is None:
            try:
                client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
                self._collection = client.get_or_create_collection(name=COLLECTION_NAME)
            except Exception as e:
                print(f"ChromaDB init failed: {e}, falling back to no-RAG mode")
                return None
        return self._collection

    def _keyword_boost(self, query: str, documents: list[str]) -> list[float]:
        """Compute a simple keyword match boost for re-ranking."""
        query_lower = query.lower()
        keywords = re.findall(r"[a-zA-Z_]+", query_lower)

        boosts = []
        for doc in documents:
            doc_lower = doc.lower()
            score = sum(2 for kw in keywords if len(kw) > 2 and kw in doc_lower)
            boosts.append(score)
        return boosts

    def retrieve(self, query: str, n_results: int = 3) -> list[dict]:
        """Search ChromaDB with semantic + keyword hybrid scoring."""
        collection = self._get_collection()
        if collection is None:
            return []

        model = self._get_model()

        query_embedding = model.encode(query).tolist()

        n_query = max(n_results * 3, TOP_K)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_query,
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        semantic_scores = [1 - d for d in distances]
        keyword_boosts = self._keyword_boost(query, documents)

        combined = []
        for i in range(len(ids)):
            combined_score = semantic_scores[i] * 0.7 + min(keyword_boosts[i] * 0.05, 0.3)
            combined.append({
                "filename": metadatas[i].get("source", "unknown"),
                "content": documents[i][:2000],
                "score": round(combined_score, 4),
                "semantic_score": round(semantic_scores[i], 4),
                "keyword_score": keyword_boosts[i],
            })

        combined.sort(key=lambda x: -x["score"])
        return combined[:n_results]


class RagService:
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.ollama_model = "qwen2.5"
        self.retriever = ChromaRetriever()
        self.memory_system = get_memory_system()
        self.reward_system = get_reward_system()

    def call_ollama(self, prompt: str) -> str:
        try:
            from urllib.parse import urlparse
            import json as _json
            from http.client import HTTPConnection

            parsed = urlparse(self.ollama_url)
            conn = HTTPConnection(parsed.hostname, parsed.port, timeout=120)
            body = _json.dumps({"model": self.ollama_model, "prompt": prompt, "stream": False})
            conn.request("POST", parsed.path, body=body, headers={"Content-Type": "application/json"})
            resp = conn.getresponse()
            data = resp.read().decode()
            conn.close()

            if resp.status != 200:
                return f"调用 Ollama 失败: HTTP {resp.status}"

            return _json.loads(data)["response"]
        except Exception as e:
            return f"调用 Ollama 失败: {str(e)}"

    def extract_optimized_sql(self, ai_response: str) -> str:
        match = re.search(r"```sql\n(.*?)\n```", ai_response, re.DOTALL)
        if match:
            return match.group(1).strip()

        match = re.search(r"```\w*\n(.*?)\n```", ai_response, re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content.startswith("{"):
                try:
                    data = json.loads(content)
                    if "optimized_sql" in data:
                        return data["optimized_sql"]
                except json.JSONDecodeError:
                    pass
            return content

        if ai_response.startswith("{"):
            try:
                data = json.loads(ai_response)
                if "optimized_sql" in data:
                    return data["optimized_sql"]
            except json.JSONDecodeError:
                pass

        lines = ai_response.split("\n")
        for line in lines:
            line = line.strip()
            if line.upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE")):
                return line

        return ai_response

    def analyze_sql(self, sql: str, user_id: str = "default_user", conversation_id: str = "default_conv") -> dict:
        self.memory_system.add_short_term_memory(user_id, sql, role="user")

        knowledge = self.retriever.retrieve(sql, n_results=3)

        knowledge_text = ""
        retrieved_info = []
        for item in knowledge:
            knowledge_text += f"【{item['filename']}】\n{item['content'][:1000]}\n\n---\n\n"
            retrieved_info.append({
                "filename": item["filename"],
                "score": item["score"],
                "keyword_score": item["keyword_score"],
                "semantic_score": item["semantic_score"]
            })

        if not knowledge_text:
            knowledge_text = "无相关知识"

        context = self.memory_system.get_context_prompt(user_id)

        prompt = f"""你是SQL优化专家。

{context}

以下是相关的SQL优化知识：
{knowledge_text}

请基于以上知识分析以下SQL：
{sql}

优化规则：
1. 必须将SELECT *改为具体字段列表
2. 对于LIKE '%xxx%'查询，建议使用全文索引或其他优化方式
3. 检查WHERE条件中的字段是否需要索引
4. 优化JOIN语句，确保ON条件使用索引字段
5. 避免不必要的DISTINCT和ORDER BY
6. 使用LIMIT限制返回行数
7. 将IN子查询转换为JOIN语句，提高查询效率
8. 使用表别名简化SQL语句

请返回JSON格式，包含以下字段：
{{
    "problems": ["问题1", "问题2", ...],
    "suggestions": ["建议1", "建议2", ...],
    "optimized_sql": "优化后的SQL语句"
}}

如果是无关问题或非SQL内容，请返回：
{{
    "problems": ["非SQL内容或无关问题"],
    "suggestions": ["请提供有效的SQL语句进行优化分析"],
    "optimized_sql": ""
}}
"""

        ai_response = self.call_ollama(prompt)
        self.memory_system.add_short_term_memory(user_id, ai_response, role="assistant")

        optimized_sql = self.extract_optimized_sql(ai_response)

        return {
            "original_sql": sql,
            "optimized_sql": optimized_sql,
            "problems": self._extract_list(ai_response, "problems"),
            "suggestions": self._extract_list(ai_response, "suggestions"),
            "raw_ai_response": ai_response,
            "retrieved_knowledge": retrieved_info,
            "conversation_id": conversation_id
        }

    def submit_feedback(self, user_id: str, conversation_id: str, rating: int, comment: str = "", corrected_answer: str = None) -> dict:
        return self.reward_system.process_feedback(user_id, conversation_id, rating, comment, corrected_answer)

    def get_learning_report(self, user_id: str = None) -> dict:
        return self.reward_system.get_learning_report(user_id)

    def summarize_conversation(self, user_id: str) -> str:
        return self.memory_system.summarize_conversation(user_id)

    def _extract_list(self, text: str, key: str) -> list:
        try:
            text = text.strip()
            if text.startswith("{") and text.endswith("}"):
                data = json.loads(text)
                if key in data:
                    return data[key]
        except json.JSONDecodeError:
            pass

        pattern = rf'"{key}":\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items_str = match.group(1)
            items = re.findall(r'"(.*?)"', items_str)
            if items:
                return items

        lines = text.split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if line.startswith(("-", "1.", "2.", "3.", "•")):
                result.append(line.lstrip("-•0123456789. "))
        return result


_rag_service = None


def get_rag_service() -> RagService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RagService()
    return _rag_service


def analyze_sql(sql: str, user_id: str = "default_user", conversation_id: str = "default_conv") -> dict:
    service = get_rag_service()
    return service.analyze_sql(sql, user_id, conversation_id)
