package com.sqlpilot.backend.dto.request;

import jakarta.validation.constraints.NotBlank;

public class SqlOptimizeRequest {
    @NotBlank(message = "SQL is required")
    private String sql;
    private String optimizationLevel;
    private Boolean includeIndexSuggestion;

    public String getSql() {
        return sql;
    }

    public void setSql(String sql) {
        this.sql = sql;
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
}