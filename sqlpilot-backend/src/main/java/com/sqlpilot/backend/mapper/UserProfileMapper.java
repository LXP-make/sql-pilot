package com.sqlpilot.backend.mapper;

import com.sqlpilot.backend.entity.UserProfile;
import org.apache.ibatis.annotations.*;

@Mapper
public interface UserProfileMapper {
    @Insert("INSERT INTO user_profiles (user_id, preferences, history_summary, rating, total_interactions, created_at, updated_at) VALUES (#{userId}, #{preferences}, #{historySummary}, #{rating}, #{totalInteractions}, NOW(), NOW())")
    void insert(UserProfile profile);

    @Select("SELECT * FROM user_profiles WHERE user_id = #{userId}")
    UserProfile selectByUserId(@Param("userId") String userId);

    @Update("UPDATE user_profiles SET preferences = #{preferences}, history_summary = #{historySummary}, rating = #{rating}, total_interactions = #{totalInteractions}, updated_at = NOW() WHERE user_id = #{userId}")
    void update(UserProfile profile);

    @Delete("DELETE FROM user_profiles WHERE user_id = #{userId}")
    void deleteByUserId(@Param("userId") String userId);
}