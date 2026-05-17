import json
import os

MEMORY_DIR = "./memory"

os.makedirs(MEMORY_DIR, exist_ok=True)

class MemorySystem:
    def __init__(self):
        self.short_term_memory = {}
        
    def add_short_term_memory(self, user_id: str, content: str, role: str = "user"):
        if user_id not in self.short_term_memory:
            self.short_term_memory[user_id] = []
        
        self.short_term_memory[user_id].append({
            "role": role,
            "content": content,
            "timestamp": len(self.short_term_memory[user_id])
        })
        
        if len(self.short_term_memory[user_id]) > 20:
            self.short_term_memory[user_id] = self.short_term_memory[user_id][-15:]
    
    def get_context_prompt(self, user_id: str) -> str:
        context = ""
        if user_id in self.short_term_memory:
            history = self.short_term_memory[user_id][-5:]
            for item in history:
                role = "用户" if item["role"] == "user" else "助手"
                context += f"{role}: {item['content']}\n"
        
        return context if context else "无对话历史"
    
    def summarize_conversation(self, user_id: str) -> str:
        if user_id not in self.short_term_memory:
            return "暂无对话记录"
        
        history = self.short_term_memory[user_id]
        user_queries = [h["content"] for h in history if h["role"] == "user"]
        return "; ".join(user_queries[-3:]) if user_queries else "暂无对话记录"

class RewardSystem:
    def __init__(self):
        self.feedback_file = os.path.join(MEMORY_DIR, "feedback.json")
        self.profiles_file = os.path.join(MEMORY_DIR, "profiles.json")
        
    def process_feedback(self, user_id: str, conversation_id: str, rating: int, comment: str = "", corrected_answer: str = None) -> dict:
        feedback = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "rating": rating,
            "comment": comment,
            "corrected_answer": corrected_answer,
            "timestamp": len(self._load_feedback()) + 1
        }
        
        feedback_list = self._load_feedback()
        feedback_list.append(feedback)
        self._save_feedback(feedback_list)
        
        self._update_user_profile(user_id, rating)
        
        return {"success": True, "message": "反馈已记录"}
    
    def get_learning_report(self, user_id: str = None) -> dict:
        feedback_list = self._load_feedback()
        
        if user_id:
            user_feedback = [f for f in feedback_list if f["user_id"] == user_id]
        else:
            user_feedback = feedback_list
        
        total_feedback = len(user_feedback)
        if total_feedback == 0:
            return {"total_feedback": 0, "average_rating": 0, "positive_rate": 0}
        
        avg_rating = sum(f["rating"] for f in user_feedback) / total_feedback
        positive_rate = sum(1 for f in user_feedback if f["rating"] >= 4) / total_feedback
        
        return {
            "total_feedback": total_feedback,
            "average_rating": round(avg_rating, 2),
            "positive_rate": round(positive_rate * 100, 2)
        }
    
    def _load_feedback(self):
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_feedback(self, feedback_list):
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_list, f, ensure_ascii=False, indent=2)
    
    def _update_user_profile(self, user_id: str, rating: int):
        profiles = self._load_profiles()
        
        if user_id not in profiles:
            profiles[user_id] = {
                "total_interactions": 0,
                "total_rating": 0,
                "preferences": {}
            }
        
        profiles[user_id]["total_interactions"] += 1
        profiles[user_id]["total_rating"] += rating
        
        self._save_profiles(profiles)
    
    def _load_profiles(self):
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_profiles(self, profiles):
        with open(self.profiles_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)

_memory_system = None
_reward_system = None

def get_memory_system() -> MemorySystem:
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
    return _memory_system

def get_reward_system() -> RewardSystem:
    global _reward_system
    if _reward_system is None:
        _reward_system = RewardSystem()
    return _reward_system
