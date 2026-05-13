package com.sqlpilot.backend.dto.response;

import java.util.List;

public class SqlOptimizeResponse {
    private String originalSql;
    private String optimizedSql;
    private List<String> problems;
    private List<OptimizationSuggestion> optimizationSuggestions;
    private String estimatedPerformanceImprovement;
    private Long executionTime;

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

    public List<String> getProblems() {
        return problems;
    }

    public void setProblems(List<String> problems) {
        this.problems = problems;
    }

    public List<OptimizationSuggestion> getOptimizationSuggestions() {
        return optimizationSuggestions;
    }

    public void setOptimizationSuggestions(List<OptimizationSuggestion> optimizationSuggestions) {
        this.optimizationSuggestions = optimizationSuggestions;
    }

    public String getEstimatedPerformanceImprovement() {
        return estimatedPerformanceImprovement;
    }

    public void setEstimatedPerformanceImprovement(String estimatedPerformanceImprovement) {
        this.estimatedPerformanceImprovement = estimatedPerformanceImprovement;
    }

    public Long getExecutionTime() {
        return executionTime;
    }

    public void setExecutionTime(Long executionTime) {
        this.executionTime = executionTime;
    }

    public static class OptimizationSuggestion {
        private String type;
        private String description;
        private String before;
        private String after;

        public String getType() {
            return type;
        }

        public void setType(String type) {
            this.type = type;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }

        public String getBefore() {
            return before;
        }

        public void setBefore(String before) {
            this.before = before;
        }

        public String getAfter() {
            return after;
        }

        public void setAfter(String after) {
            this.after = after;
        }
    }
}