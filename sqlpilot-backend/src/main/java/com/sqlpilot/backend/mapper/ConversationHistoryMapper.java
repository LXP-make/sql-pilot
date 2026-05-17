package com.sqlpilot.backend.mapper;

import com.sqlpilot.backend.entity.ConversationHistory;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface ConversationHistoryMapper {
    @Insert("INSERT INTO conversation_history (id, user_id, conversation_id, content, role, timestamp, metadata) VALUES (#{id}, #{userId}, #{conversationId}, #{content}, #{role}, #{timestamp}, #{metadata})")
    void insert(ConversationHistory history);

    @Select("SELECT * FROM conversation_history WHERE id = #{id}")
    ConversationHistory selectById(@Param("id") String id);

    @Select("SELECT id, user_id as userId, conversation_id as conversationId, content, role, timestamp, metadata FROM conversation_history WHERE user_id = #{userId} ORDER BY timestamp DESC")
    List<ConversationHistory> selectByUserId(@Param("userId") String userId);

    @Select("SELECT * FROM conversation_history WHERE conversation_id = #{conversationId} ORDER BY timestamp DESC")
    List<ConversationHistory> selectByConversationId(@Param("conversationId") String conversationId);

    @Select("SELECT conversation_id FROM conversation_history WHERE user_id = #{userId} ORDER BY timestamp DESC LIMIT 1")
    String selectRecentConversationId(@Param("userId") String userId);

    @Delete("DELETE FROM conversation_history WHERE id = #{id}")
    void deleteById(@Param("id") String id);

    @Delete("DELETE FROM conversation_history WHERE conversation_id = #{conversationId}")
    void deleteByConversationId(@Param("conversationId") String conversationId);
}