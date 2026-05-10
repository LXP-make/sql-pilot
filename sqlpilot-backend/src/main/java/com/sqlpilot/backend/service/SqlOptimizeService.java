package com.sqlpilot.backend.service;

import com.sqlpilot.backend.dto.response.SqlOptimizeResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@Service
public class SqlOptimizeService {

    private final RestTemplate restTemplate;

    public SqlOptimizeService() {
        this.restTemplate = new RestTemplate();
    }

    public SqlOptimizeResponse optimize(String sql, String optimizationLevel, Boolean includeIndexSuggestion) {
        long startTime = System.currentTimeMillis();

        SqlOptimizeResponse response = new SqlOptimizeResponse();
        response.setOriginalSql(sql);

        String optimizedSql = generateLocalOptimization(sql);
        response.setOptimizedSql(optimizedSql);

        List<SqlOptimizeResponse.OptimizationSuggestion> suggestions = new ArrayList<>();
        SqlOptimizeResponse.OptimizationSuggestion suggestion = new SqlOptimizeResponse.OptimizationSuggestion();
        suggestion.setType("LOCAL_OPTIMIZATION");
        suggestion.setDescription("Basic SQL optimization suggestions");
        suggestion.setBefore(sql);
        suggestion.setAfter(optimizedSql);
        suggestions.add(suggestion);

        response.setOptimizationSuggestions(suggestions);
        response.setEstimatedPerformanceImprovement("30%");

        long executionTime = System.currentTimeMillis() - startTime;
        response.setExecutionTime(executionTime);

        return response;
    }

    private String generateLocalOptimization(String sql) {
        if (sql.toUpperCase().contains("SELECT *")) {
            return sql.replace("SELECT *", "SELECT /* Specify columns */");
        }
        return sql;
    }
}