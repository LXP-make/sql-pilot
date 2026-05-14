import requests
import chromadb
from sentence_transformers import SentenceTransformer
import re

class RagService:
    def __init__(self):
        self.model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection(name="sql_rules")
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.ollama_model = "qwen2.5:latest"

    def embed_query(self, sql: str) -> list:
        return self.model.encode(sql).tolist()

    def retrieve_knowledge(self, sql: str, n_results: int = 3) -> list:
        embedding = self.embed_query(sql)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        return results["documents"][0]

    def call_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"调用 Ollama 失败: {str(e)}"

    def extract_optimized_sql(self, ai_response: str) -> str:
        match = re.search(r"```sql\n(.*?)\n```", ai_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        match = re.search(r"```\n(.*?)\n```", ai_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        lines = ai_response.split("\n")
        for line in lines:
            line = line.strip()
            if line.upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE")):
                return line
        
        return ai_response

    def analyze_sql(self, sql: str) -> dict:
        knowledge = self.retrieve_knowledge(sql)
        knowledge_text = "\n".join(knowledge)

        prompt = f"""你是SQL优化专家。

以下是SQL优化知识：
{knowledge_text}

请分析以下SQL：
{sql}

请返回JSON格式，包含以下字段：
{{
    "problems": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "optimized_sql": "优化后的SQL"
}}
"""

        ai_response = self.call_ollama(prompt)
        
        optimized_sql = self.extract_optimized_sql(ai_response)

        return {
            "original_sql": sql,
            "optimized_sql": optimized_sql,
            "problems": self._extract_list(ai_response, "problems"),
            "suggestions": self._extract_list(ai_response, "suggestions"),
            "raw_ai_response": ai_response
        }

    def _extract_list(self, text: str, key: str) -> list:
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

def analyze_sql(sql: str) -> dict:
    service = get_rag_service()
    return service.analyze_sql(sql)