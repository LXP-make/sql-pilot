import requests
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque

class MemorySystem:
    def __init__(self, backend_url="http://localhost:8081"):
        self.backend_url = backend_url
        self.max_short_term = 10
        self.short_term_memory: Dict[str, deque] = {}

    def _api_post(self, endpoint: str, data: dict) -> dict:
        try:
            response = requests.post(f"{self.backend_url}{endpoint}", data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API调用失败 {endpoint}: {e}")
            return {"success": False, "error": str(e)}

    def _api_get(self, endpoint: str, params: dict = None) -> dict:
        try:
            response = requests.get(f"{self.backend_url}{endpoint}", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API调用失败 {endpoint}: {e}")
            return {"success": False, "error": str(e)}

    def add_short_term_memory(self, user_id: str, content: str, role: str = "user", metadata: Dict = None):
        if user_id not in self.short_term_memory:
            self.short_term_memory[user_id] = deque(maxlen=self.max_short_term)
        
        memory_item = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": content,
            "role": role,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        
        self.short_term_memory[user_id].append(memory_item)
        
        self._api_post("/api/memory/conversation", {
            "userId": user_id,
            "content": content,
            "role": role
        })

    def get_short_term_memory(self, user_id: str, limit: int = None) -> List[Dict]:
        if user_id not in self.short_term_memory:
            return []
        
        items = list(self.short_term_memory[user_id])
        if limit:
            return items[-limit:]
        return items

    def get_context_prompt(self, user_id: str) -> str:
        result = self._api_get(f"/api/memory/context/{user_id}")
        if result.get("success"):
            return result.get("context", "")
        
        memories = self.get_short_term_memory(user_id)
        if not memories:
            return ""
        
        context = "对话历史:\n"
        for item in memories:
            role = "用户" if item["role"] == "user" else "助手"
            context += f"{role}: {item['content']}\n"
        return context

    def get_or_create_user_profile(self, user_id: str) -> Dict:
        result = self._api_get(f"/api/memory/profile/{user_id}")
        if result.get("success"):
            return result.get("data", {})
        return {"user_id": user_id, "preferences": {}, "rating": 0.0, "total_interactions": 0}

    def update_user_preference(self, user_id: str, key: str, value: Any):
        self._api_post("/api/memory/preference", {
            "userId": user_id,
            "key": key,
            "value": str(value)
        })

    def record_feedback(self, conversation_id: str, user_id: str, rating: int, comment: str = "", corrected_answer: str = None) -> float:
        result = self._api_post("/api/memory/feedback", {
            "conversationId": conversation_id,
            "userId": user_id,
            "rating": rating,
            "comment": comment,
            "correctedAnswer": corrected_answer
        })
        
        if result.get("success"):
            return result.get("reward", 0.0)
        return 0.0

    def should_update_knowledge(self, conversation_id: str) -> bool:
        return False

    def get_knowledge_update_candidates(self) -> List[Dict[str, Any]]:
        result = self._api_get("/api/memory/learning-report")
        if result.get("success"):
            return result.get("data", {}).get("knowledgeUpdateCandidates", [])
        return []

    def summarize_conversation(self, user_id: str) -> str:
        result = self._api_get(f"/api/memory/summary/{user_id}")
        if result.get("success"):
            return result.get("summary", "")
        
        memories = self.get_short_term_memory(user_id)
        if not memories:
            return ""
        
        user_messages = [m['content'] for m in memories if m['role'] == 'user']
        assistant_messages = [m['content'] for m in memories if m['role'] == 'assistant']
        
        summary = f"用户对话摘要:\n"
        summary += f"- 用户提问次数: {len(user_messages)}\n"
        summary += f"- 助手回复次数: {len(assistant_messages)}\n"
        
        if user_messages:
            summary += f"- 主要关注点: {'; '.join(user_messages[-3:])}\n"
        
        return summary

    def clear_short_term_memory(self, user_id: str):
        if user_id in self.short_term_memory:
            self.short_term_memory[user_id].clear()

class RewardPenaltySystem:
    def __init__(self, memory_system: MemorySystem):
        self.memory_system = memory_system
        self.reward_history: List[Dict[str, Any]] = []
        self.thresholds = {
            "positive": 4,
            "negative": 2,
            "update_knowledge": 3
        }

    def process_feedback(self, user_id: str, conversation_id: str, rating: int, comment: str = "", corrected_answer: str = None):
        reward = self.memory_system.record_feedback(conversation_id, user_id, rating, comment, corrected_answer)
        
        self.reward_history.append({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "rating": rating,
            "reward": reward,
            "timestamp": datetime.now().isoformat()
        })
        
        if rating >= self.thresholds["positive"]:
            return self._handle_positive_feedback(user_id, conversation_id, reward)
        elif rating <= self.thresholds["negative"]:
            return self._handle_negative_feedback(user_id, conversation_id, corrected_answer)
        else:
            return {"status": "neutral", "reward": reward}

    def _handle_positive_feedback(self, user_id: str, conversation_id: str, reward: float) -> Dict[str, Any]:
        profile = self.memory_system.get_or_create_user_profile(user_id)
        
        return {
            "status": "positive",
            "reward": reward,
            "message": "感谢您的好评！",
            "user_rating": profile.get('rating', 0.0),
            "suggestion": "继续保持高质量回答"
        }

    def _handle_negative_feedback(self, user_id: str, conversation_id: str, corrected_answer: str) -> Dict[str, Any]:
        needs_update = self.memory_system.should_update_knowledge(conversation_id)
        
        actions = []
        if corrected_answer:
            actions.append("已记录修正答案，将用于知识库更新")
        if needs_update:
            actions.append("建议更新相关知识文档")
        
        return {
            "status": "negative",
            "reward": -0.5,
            "message": "抱歉未能满足您的需求，我们会持续改进",
            "needs_knowledge_update": needs_update,
            "actions": actions
        }

    def get_learning_report(self, user_id: str = None) -> Dict[str, Any]:
        params = {"userId": user_id} if user_id else {}
        result = self.memory_system._api_get("/api/memory/learning-report", params)
        
        if result.get("success"):
            return result.get("data", {})
        return {"error": "无法获取学习报告"}

_memory_system = None
_reward_system = None

def get_memory_system() -> MemorySystem:
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
    return _memory_system

def get_reward_system() -> RewardPenaltySystem:
    global _reward_system
    if _reward_system is None:
        _reward_system = RewardPenaltySystem(get_memory_system())
    return _reward_system