#!/usr/bin/env python3
"""测试 AI Memory 系统和奖惩机制"""

from memory_system import get_memory_system, get_reward_system
from rag_service import get_rag_service
import uuid

def test_memory_system():
    print("=" * 60)
    print("AI Memory 系统 + 奖惩机制 测试")
    print("=" * 60)
    
    memory = get_memory_system()
    reward = get_reward_system()
    rag = get_rag_service()
    
    user_id = "test_user_001"
    conversation_id = str(uuid.uuid4())
    
    print(f"\n[测试1] 用户对话记忆")
    print("-" * 40)
    
    queries = [
        "SELECT * FROM users WHERE age > 18",
        "这个查询有什么问题？",
        "如何优化？"
    ]
    
    for i, query in enumerate(queries):
        print(f"\n用户提问 {i+1}: {query}")
        result = rag.analyze_sql(query, user_id, conversation_id)
        print(f"助手回复: {result['problems']}")
    
    print(f"\n[测试2] 对话历史上下文")
    print("-" * 40)
    context = memory.get_context_prompt(user_id)
    print(f"上下文内容:\n{context}")
    
    print(f"\n[测试3] 用户画像摘要")
    print("-" * 40)
    summary = memory.summarize_conversation(user_id)
    print(f"对话摘要:\n{summary}")
    
    print(f"\n[测试4] 提交正向反馈")
    print("-" * 40)
    feedback1 = reward.process_feedback(
        user_id=user_id,
        conversation_id=conversation_id,
        rating=5,
        comment="回答非常有帮助，优化建议很实用！",
        corrected_answer=None
    )
    print(f"正向反馈处理结果:\n{json.dumps(feedback1, indent=2, ensure_ascii=False)}")
    
    print(f"\n[测试5] 提交负向反馈")
    print("-" * 40)
    feedback2 = reward.process_feedback(
        user_id=user_id,
        conversation_id=conversation_id,
        rating=1,
        comment="回答不准确，没有解决我的问题",
        corrected_answer="正确的优化方法应该是添加索引到age字段，使用SELECT具体字段而非SELECT *"
    )
    print(f"负向反馈处理结果:\n{json.dumps(feedback2, indent=2, ensure_ascii=False)}")
    
    print(f"\n[测试6] 学习报告")
    print("-" * 40)
    report = reward.get_learning_report()
    print(f"学习报告:\n{json.dumps(report, indent=2, ensure_ascii=False)}")
    
    print(f"\n[测试7] 用户偏好设置")
    print("-" * 40)
    memory.update_user_preference(user_id, "favorite_database", "MySQL")
    memory.update_user_preference(user_id, "preferred_format", "JSON")
    profile = memory.get_or_create_user_profile(user_id)
    print(f"用户偏好: {profile.get('preferences', '{}')}")
    print(f"用户评分: {profile.get('rating', 0.0)}")
    print(f"交互次数: {profile.get('total_interactions', 0)}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    import json
    test_memory_system()