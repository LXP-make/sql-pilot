import requests
import json
import re
from collections import OrderedDict
from memory_system import get_memory_system, get_reward_system

class HybridRetriever:
    def __init__(self):
        self.ollama_embedding_url = "http://127.0.0.1:11434/api/embeddings"
        self.ollama_model = "qwen2.5"
        self.knowledge_base = self._load_knowledge_base()
        self.document_embeddings = {}

    def _load_knowledge_base(self):
        import os
        knowledge = []
        knowledge_dir = "./knowledge"
        
        if os.path.exists(knowledge_dir):
            for root, dirs, files in os.walk(knowledge_dir):
                for file in files:
                    if file.endswith(".md"):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                content = f.read()
                                knowledge.append({
                                    "filename": file,
                                    "content": content[:3000],
                                    "short_content": content[:500]
                                })
                        except Exception as e:
                            print(f"加载文件失败 {file}: {e}")
        return knowledge

    def _generate_embedding(self, text: str) -> list:
        try:
            response = requests.post(
                self.ollama_embedding_url,
                json={"model": self.ollama_model, "prompt": text},
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
        except Exception as e:
            print(f"嵌入生成失败: {str(e)}")
            return []

    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        if not vec1 or not vec2:
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def _keyword_match_score(self, query: str, doc: dict) -> float:
        query_lower = query.lower()
        content_lower = doc["content"].lower()
        score = 0.0
        
        keywords = {
            'select *': 5, 'select': 2,
            'join': 4, 'inner join': 4, 'left join': 4, 'right join': 4,
            'index': 4, '索引': 4,
            'where': 1,
            'like': 3, 'like %': 3,
            'limit': 2, 'offset': 2,
            'order by': 2, 'group by': 2,
            'subquery': 3, '子查询': 3,
            'union': 2,
            'distinct': 2,
            'count': 1, 'sum': 1, 'avg': 1, 'max': 1, 'min': 1,
            'optimize': 3, '优化': 3,
            'performance': 3, '性能': 3,
            'slow': 3, '慢查询': 3
        }
        
        for keyword, weight in keywords.items():
            if keyword in query_lower and keyword in content_lower:
                score += weight
        
        return score

    def _semantic_match_score(self, query_embedding: list, doc: dict) -> float:
        doc_key = doc["filename"]
        
        if doc_key not in self.document_embeddings:
            doc_embedding = self._generate_embedding(doc["short_content"])
            self.document_embeddings[doc_key] = doc_embedding
        else:
            doc_embedding = self.document_embeddings[doc_key]
        
        return self._cosine_similarity(query_embedding, doc_embedding)

    def retrieve(self, query: str, n_results: int = 3, keyword_weight: float = 0.4, semantic_weight: float = 0.6) -> list:
        if not self.knowledge_base:
            return []
        
        query_embedding = self._generate_embedding(query)
        results = []
        
        for doc in self.knowledge_base:
            keyword_score = self._keyword_match_score(query, doc)
            semantic_score = self._semantic_match_score(query_embedding, doc)
            
            max_keyword = max(self._keyword_match_score(q, doc) for q in ["select *", "join", "index", "where"] + [query])
            if max_keyword > 0:
                keyword_score = keyword_score / max_keyword
            
            combined_score = (keyword_score * keyword_weight) + (semantic_score * semantic_weight)
            
            if combined_score > 0.01:
                results.append({
                    "score": combined_score,
                    "keyword_score": keyword_score,
                    "semantic_score": semantic_score,
                    "filename": doc["filename"],
                    "content": doc["content"]
                })
        
        results.sort(key=lambda x: -x["score"])
        
        return [{
            "content": r["content"],
            "filename": r["filename"],
            "score": r["score"],
            "keyword_score": r["keyword_score"],
            "semantic_score": r["semantic_score"]
        } for r in results[:n_results]]

class RagService:
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.ollama_model = "qwen2.5"
        self.retriever = HybridRetriever()
        self.memory_system = get_memory_system()
        self.reward_system = get_reward_system()

    def call_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
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
        except:
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