package com.sqlpilot.backend.entity;

import java.time.LocalDateTime;

public class SqlOptimizationHistory {
    private Long id;
    private String originalSql;
    private String optimizedSql;
    private String optimizationLevel;
    private Boolean includeIndexSuggestion;
    private String optimizationSuggestions;
    private String problems;
    private String estimatedImprovement;
    private Long executionTime;
    private String source;
    private LocalDateTime createdAt;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getOriginalSql() {
        return originalSql;
    }

    public void setOriginalSql(String originalSql) {
        this.originalSql = originalSql;
    }

    public String getOptimizedSql() {
        return optimizedSql;
    }

    public void setOptimizedSql(String optimizedSql) {
        this.optimizedSql = optimizedSql;
    }

    public String getOptimizationLevel() {
        return optimizationLevel;
    }

    public void setOptimizationLevel(String optimizationLevel) {
        this.optimizationLevel = optimizationLevel;
    }

    public Boolean getIncludeIndexSuggestion() {
        return includeIndexSuggestion;
    }

    public void setIncludeIndexSuggestion(Boolean includeIndexSuggestion) {
        this.includeIndexSuggestion = includeIndexSuggestion;
    }

    public String getOptimizationSuggestions() {
        return optimizationSuggestions;
    }

    public void setOptimizationSuggestions(String optimizationSuggestions) {
        this.optimizationSuggestions = optimizationSuggestions;
    }

    public String getProblems() {
        return problems;
    }

    public void setProblems(String problems) {
        this.problems = problems;
    }

    public String getEstimatedImprovement() {
        return estimatedImprovement;
    }

    public void setEstimatedImprovement(String estimatedImprovement) {
        this.estimatedImprovement = estimatedImprovement;
    }

    public Long getExecutionTime() {
        return executionTime;
    }

    public void setExecutionTime(Long executionTime) {
        this.executionTime = executionTime;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}