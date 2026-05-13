package com.sqlpilot.backend.service;

import com.alibaba.fastjson.JSON;
import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.dto.response.SqlOptimizeResponse;
import com.sqlpilot.backend.entity.SqlOptimizationHistory;
import com.sqlpilot.backend.mapper.SqlOptimizationHistoryMapper;
import com.sqlpilot.backend.rule.SqlRuleEngine;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class SqlOptimizeService {

    private final RestTemplate restTemplate;

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    @Value("${ai.service.optimize-path}")
    private String aiOptimizePath;

    @Value("${ai.timeout}")
    private int timeout;

    @Autowired
    private SqlOptimizationHistoryMapper optimizationHistoryMapper;

    @Autowired
    private SqlRuleEngine sqlRuleEngine;

    public SqlOptimizeService() {
        this.restTemplate = new RestTemplate();
    }

    public SqlOptimizeResponse optimize(String sql, String optimizationLevel, Boolean includeIndexSuggestion) {
        long startTime = System.currentTimeMillis();

        SqlOptimizeResponse response = new SqlOptimizeResponse();
        response.setOriginalSql(sql);
        String source = "LOCAL";

        List<String> detectedProblems = new ArrayList<>();

        List<SqlAnalyzeResponse.RuleViolation> ruleViolations = sqlRuleEngine.executeRules(sql);
        for (SqlAnalyzeResponse.RuleViolation violation : ruleViolations) {
            detectedProblems.add(violation.getRuleName() + ": " + violation.getDescription());
        }

        try {
            Map<String, Object> aiResponse = callAiService(sql, optimizationLevel, includeIndexSuggestion);

            if (aiResponse != null && (Boolean) aiResponse.get("success")) {
                Map<String, Object> data = (Map<String, Object>) aiResponse.get("data");

                if (data != null) {
                    source = "AI";
                    if (data.containsKey("optimized_sql")) {
                        response.setOptimizedSql((String) data.get("optimized_sql"));
                    } else {
                        response.setOptimizedSql(sql);
                    }

                    if (data.containsKey("problems")) {
                        List<String> aiProblems = (List<String>) data.get("problems");
                        if (aiProblems != null) {
                            detectedProblems.addAll(aiProblems);
                        }
                    }

                    List<SqlOptimizeResponse.OptimizationSuggestion> suggestions = new ArrayList<>();
                    if (data.containsKey("optimization_suggestions")) {
                        List<Map<String, Object>> aiSuggestions = (List<Map<String, Object>>) data.get("optimization_suggestions");
                        for (Map<String, Object> aiSuggestion : aiSuggestions) {
                            SqlOptimizeResponse.OptimizationSuggestion suggestion = new SqlOptimizeResponse.OptimizationSuggestion();
                            suggestion.setType((String) aiSuggestion.get("type"));
                            suggestion.setDescription((String) aiSuggestion.get("description"));
                            suggestions.add(suggestion);
                        }
                    }
                    response.setOptimizationSuggestions(suggestions);
                    response.setEstimatedPerformanceImprovement("AI分析结果");
                }
            } else {
                applyLocalOptimization(response, sql, detectedProblems);
            }
        } catch (Exception e) {
            applyLocalOptimization(response, sql, detectedProblems);
        }

        if (response.getOptimizationSuggestions() == null || response.getOptimizationSuggestions().isEmpty()) {
            applyLocalOptimization(response, sql, detectedProblems);
        }

        response.setProblems(detectedProblems);

        long executionTime = System.currentTimeMillis() - startTime;
        response.setExecutionTime(executionTime);

        saveOptimizationHistory(response, optimizationLevel, includeIndexSuggestion, source, executionTime);

        return response;
    }

    private void applyLocalOptimization(SqlOptimizeResponse response, String sql, List<String> detectedProblems) {
        String optimizedSql = generateLocalOptimization(sql);
        response.setOptimizedSql(optimizedSql);

        List<SqlOptimizeResponse.OptimizationSuggestion> suggestions = new ArrayList<>();

        for (String problem : detectedProblems) {
            SqlOptimizeResponse.OptimizationSuggestion suggestion = new SqlOptimizeResponse.OptimizationSuggestion();
            suggestion.setType("RULE_DETECTION");
            suggestion.setDescription(problem);
            suggestion.setBefore(sql);
            suggestion.setAfter(optimizedSql);
            suggestions.add(suggestion);
        }

        if (sql.toUpperCase().contains("SELECT *")) {
            SqlOptimizeResponse.OptimizationSuggestion suggestion = new SqlOptimizeResponse.OptimizationSuggestion();
            suggestion.setType("LOCAL_OPTIMIZATION");
            suggestion.setDescription("Avoid using SELECT *, specify columns explicitly for better performance");
            suggestion.setBefore(sql);
            suggestion.setAfter(optimizedSql);
            suggestions.add(suggestion);
        }

        if (!suggestions.isEmpty()) {
            response.setOptimizationSuggestions(suggestions);
        }

        response.setEstimatedPerformanceImprovement("30%");
    }

    private void saveOptimizationHistory(SqlOptimizeResponse response, String optimizationLevel, Boolean includeIndexSuggestion, String source, long executionTime) {
        try {
            SqlOptimizationHistory history = new SqlOptimizationHistory();
            history.setOriginalSql(response.getOriginalSql());
            history.setOptimizedSql(response.getOptimizedSql());
            history.setOptimizationLevel(optimizationLevel);
            history.setIncludeIndexSuggestion(includeIndexSuggestion);
            history.setOptimizationSuggestions(JSON.toJSONString(response.getOptimizationSuggestions()));
            history.setProblems(response.getProblems() != null ? JSON.toJSONString(response.getProblems()) : null);
            history.setEstimatedImprovement(response.getEstimatedPerformanceImprovement());
            history.setExecutionTime(executionTime);
            history.setSource(source);

            optimizationHistoryMapper.insert(history);
        } catch (Exception e) {
            System.err.println("Failed to save optimization history: " + e.getMessage());
        }
    }

    private Map<String, Object> callAiService(String sql, String optimizationLevel, Boolean includeIndexSuggestion) {
        try {
            String url = aiServiceUrl + aiOptimizePath;

            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("sql", sql);
            if (optimizationLevel != null) {
                requestBody.put("optimization_level", optimizationLevel);
            }
            if (includeIndexSuggestion != null) {
                requestBody.put("include_index_suggestion", includeIndexSuggestion);
            }

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);

            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                request,
                Map.class
            );

            return response.getBody();
        } catch (Exception e) {
            return null;
        }
    }

    private String generateLocalOptimization(String sql) {
        if (sql.toUpperCase().contains("SELECT *")) {
            return sql.replace("SELECT *", "SELECT /* Specify columns */");
        }
        return sql;
    }
}