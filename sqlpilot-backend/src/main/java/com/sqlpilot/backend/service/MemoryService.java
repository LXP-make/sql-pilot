package com.sqlpilot.backend.service;

import com.sqlpilot.backend.entity.SqlAnalysisHistory;
import com.sqlpilot.backend.mapper.SqlAnalysisHistoryMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class MemoryService {

    @Autowired
    private SqlAnalysisHistoryMapper analysisHistoryMapper;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public void addConversation(String userId, String content, String role) {
        SqlAnalysisHistory history = new SqlAnalysisHistory();
        history.setOriginalSql(content);
        history.setOptimizedSql(role);
        history.setDatabaseType(userId);
        history.setAnalysisResult("{}");
        history.setCreatedAt(LocalDateTime.now());
        history.setUpdatedAt(LocalDateTime.now());
        
        analysisHistoryMapper.insert(history);
    }

    public List<SqlAnalysisHistory> getConversationHistory(String userId) {
        return analysisHistoryMapper.selectByDatabaseType(userId);
    }

    public String getContextPrompt(String userId) {
        List<SqlAnalysisHistory> histories = analysisHistoryMapper.selectByDatabaseType(userId);
        if (histories.isEmpty()) {
            return "";
        }
        
        StringBuilder context = new StringBuilder("对话历史:\n");
        for (SqlAnalysisHistory history : histories) {
            String role = "user".equals(history.getOptimizedSql()) ? "用户" : "助手";
            context.append(role).append(": ").append(history.getOriginalSql()).append("\n");
        }
        return context.toString();
    }

    @org.springframework.transaction.annotation.Transactional
    public void updateUserPreference(String userId, String key, String value) {
        try {
            jdbcTemplate.execute(
                "INSERT INTO index_suggestion (history_id, table_name, column_names, index_type) " +
                "VALUES (1, '" + escapeSql(userId) + "', '" + escapeSql(key) + "', '" + escapeSql(value) + "')"
            );
        } catch (Exception e) {
            System.err.println("Failed to insert into index_suggestion: " + e.getMessage());
        }
    }

    public Map<String, Object> getUserProfile(String userId) {
        Map<String, Object> profile = new HashMap<>();
        
        List<SqlAnalysisHistory> histories = analysisHistoryMapper.selectByDatabaseType(userId);
        long userCount = histories.stream().filter(h -> "user".equals(h.getOptimizedSql())).count();
        long assistantCount = histories.stream().filter(h -> "assistant".equals(h.getOptimizedSql())).count();
        
        profile.put("userId", userId);
        profile.put("userMessageCount", userCount);
        profile.put("assistantMessageCount", assistantCount);
        profile.put("preferences", new HashMap<String, String>());
        
        return profile;
    }

    @org.springframework.transaction.annotation.Transactional
    public Map<String, Object> recordFeedback(String conversationId, String userId, Integer rating, String comment, String correctedAnswer) {
        double reward = calculateReward(rating, comment, correctedAnswer);
        
        try {
            jdbcTemplate.execute(
                "INSERT INTO optimization_suggestion (history_id, suggestion_type, severity, description) " +
                "VALUES (1, 'FEEDBACK', '" + (rating >= 4 ? "INFO" : rating <= 2 ? "HIGH" : "MEDIUM") + "', '" + escapeSql("user=" + userId + ",rating=" + rating + ",comment=" + (comment != null ? comment : "")) + "')"
            );
        } catch (Exception e) {
            System.err.println("Failed to insert into optimization_suggestion: " + e.getMessage());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("reward", reward);
        result.put("needsUpdate", false);
        return result;
    }

    private double calculateReward(Integer rating, String comment, String correctedAnswer) {
        double baseReward = rating * 0.2;
        
        if (comment != null && comment.length() > 10) {
            baseReward += 0.1;
        }
        if (correctedAnswer != null && correctedAnswer.length() > 20) {
            baseReward += 0.2;
        }
        
        return Math.max(-1.0, Math.min(1.0, baseReward));
    }

    public String summarizeConversation(String userId) {
        List<SqlAnalysisHistory> histories = analysisHistoryMapper.selectByDatabaseType(userId);
        if (histories.isEmpty()) {
            return "";
        }
        
        long userCount = histories.stream().filter(h -> "user".equals(h.getOptimizedSql())).count();
        long assistantCount = histories.stream().filter(h -> "assistant".equals(h.getOptimizedSql())).count();
        
        StringBuilder summary = new StringBuilder("用户对话摘要:\n");
        summary.append("- 用户提问次数: ").append(userCount).append("\n");
        summary.append("- 助手回复次数: ").append(assistantCount).append("\n");
        
        List<String> recentUserMessages = histories.stream()
                .filter(h -> "user".equals(h.getOptimizedSql()))
                .map(SqlAnalysisHistory::getOriginalSql)
                .collect(Collectors.toList());
        if (!recentUserMessages.isEmpty()) {
            int start = Math.max(0, recentUserMessages.size() - 3);
            summary.append("- 主要关注点: ").append(String.join("; ", recentUserMessages.subList(start, recentUserMessages.size()))).append("\n");
        }
        
        return summary.toString();
    }

    public Map<String, Object> getLearningReport(String userId) {
        Map<String, Object> report = new HashMap<>();
        report.put("totalFeedbacks", 0);
        report.put("averageRating", 0);
        report.put("positiveCount", 0);
        report.put("negativeCount", 0);
        report.put("improvementNeeded", false);
        return report;
    }

    public Map<String, Object> getTableStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("sql_analysis_history", analysisHistoryMapper.count());
        
        try {
            Long optCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM optimization_suggestion", Long.class);
            stats.put("optimization_suggestion", optCount);
        } catch (Exception e) {
            stats.put("optimization_suggestion", 0);
        }
        
        try {
            Long idxCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM index_suggestion", Long.class);
            stats.put("index_suggestion", idxCount);
        } catch (Exception e) {
            stats.put("index_suggestion", 0);
        }
        
        return stats;
    }

    private String escapeSql(String str) {
        if (str == null) {
            return "";
        }
        return str.replace("'", "''");
    }

    public Map<String, Object> getTableStructure() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            List<Map<String, Object>> optColumns = jdbcTemplate.queryForList(
                "DESCRIBE optimization_suggestion"
            );
            result.put("optimization_suggestion", optColumns);
        } catch (Exception e) {
            result.put("optimization_suggestion_error", e.getMessage());
        }
        
        try {
            List<Map<String, Object>> idxColumns = jdbcTemplate.queryForList(
                "DESCRIBE index_suggestion"
            );
            result.put("index_suggestion", idxColumns);
        } catch (Exception e) {
            result.put("index_suggestion_error", e.getMessage());
        }
        
        try {
            List<Map<String, Object>> sqlColumns = jdbcTemplate.queryForList(
                "DESCRIBE sql_analysis_history"
            );
            result.put("sql_analysis_history", sqlColumns);
        } catch (Exception e) {
            result.put("sql_analysis_history_error", e.getMessage());
        }
        
        return result;
    }
}
