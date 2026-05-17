package com.sqlpilot.backend.mapper;

import com.sqlpilot.backend.entity.Feedback;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface FeedbackMapper {
    @Insert("INSERT INTO feedback (id, conversation_id, user_id, rating, comment, corrected_answer, reward, timestamp) VALUES (#{id}, #{conversationId}, #{userId}, #{rating}, #{comment}, #{correctedAnswer}, #{reward}, #{timestamp})")
    void insert(Feedback feedback);

    @Select("SELECT * FROM feedback WHERE id = #{id}")
    Feedback selectById(@Param("id") String id);

    @Select("SELECT * FROM feedback WHERE user_id = #{userId} ORDER BY timestamp DESC")
    List<Feedback> selectByUserId(@Param("userId") String userId);

    @Select("SELECT * FROM feedback WHERE conversation_id = #{conversationId} ORDER BY timestamp DESC")
    List<Feedback> selectByConversationId(@Param("conversationId") String conversationId);

    @Select("SELECT * FROM feedback WHERE conversation_id = #{conversationId} ORDER BY timestamp DESC LIMIT #{limit}")
    List<Feedback> selectRecentByConversationId(@Param("conversationId") String conversationId, @Param("limit") int limit);

    @Select("SELECT * FROM feedback ORDER BY timestamp DESC")
    List<Feedback> selectAll();

    @Select("SELECT conversation_id, corrected_answer, comment, timestamp FROM feedback WHERE corrected_answer IS NOT NULL AND rating < 3 ORDER BY timestamp DESC LIMIT 10")
    List<Feedback> selectKnowledgeUpdateCandidates();

    @Delete("DELETE FROM feedback WHERE id = #{id}")
    void deleteById(@Param("id") String id);
}