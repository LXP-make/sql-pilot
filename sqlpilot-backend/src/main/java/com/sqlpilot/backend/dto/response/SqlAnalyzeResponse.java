package com.sqlpilot.backend.dto.response;

import java.util.List;

public class SqlAnalyzeResponse {
    private Long analysisId;
    private String originalSql;
    private String databaseType;
    private AnalysisResults analysisResults;
    private List<IndexSuggestion> indexSuggestions;
    private Long executionTime;

    public Long getAnalysisId() {
        return analysisId;
    }

    public void setAnalysisId(Long analysisId) {
        this.analysisId = analysisId;
    }

    public String getOriginalSql() {
        return originalSql;
    }

    public void setOriginalSql(String originalSql) {
        this.originalSql = originalSql;
    }

    public String getDatabaseType() {
        return databaseType;
    }

    public void setDatabaseType(String databaseType) {
        this.databaseType = databaseType;
    }

    public AnalysisResults getAnalysisResults() {
        return analysisResults;
    }

    public void setAnalysisResults(AnalysisResults analysisResults) {
        this.analysisResults = analysisResults;
    }

    public List<IndexSuggestion> getIndexSuggestions() {
        return indexSuggestions;
    }

    public void setIndexSuggestions(List<IndexSuggestion> indexSuggestions) {
        this.indexSuggestions = indexSuggestions;
    }

    public Long getExecutionTime() {
        return executionTime;
    }

    public void setExecutionTime(Long executionTime) {
        this.executionTime = executionTime;
    }

    public static class AnalysisResults {
        private List<RuleViolation> ruleViolations;
        private ExplainResult explainResult;
        private Integer performanceScore;
        private Boolean syntaxValid;

        public List<RuleViolation> getRuleViolations() {
            return ruleViolations;
        }

        public void setRuleViolations(List<RuleViolation> ruleViolations) {
            this.ruleViolations = ruleViolations;
        }

        public ExplainResult getExplainResult() {
            return explainResult;
        }

        public void setExplainResult(ExplainResult explainResult) {
            this.explainResult = explainResult;
        }

        public Integer getPerformanceScore() {
            return performanceScore;
        }

        public void setPerformanceScore(Integer performanceScore) {
            this.performanceScore = performanceScore;
        }

        public Boolean getSyntaxValid() {
            return syntaxValid;
        }

        public void setSyntaxValid(Boolean syntaxValid) {
            this.syntaxValid = syntaxValid;
        }
    }

    public static class RuleViolation {
        private String ruleId;
        private String ruleName;
        private String severity;
        private String description;

        public String getRuleId() {
            return ruleId;
        }

        public void setRuleId(String ruleId) {
            this.ruleId = ruleId;
        }

        public String getRuleName() {
            return ruleName;
        }

        public void setRuleName(String ruleName) {
            this.ruleName = ruleName;
        }

        public String getSeverity() {
            return severity;
        }

        public void setSeverity(String severity) {
            this.severity = severity;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }
    }

    public static class ExplainResult {
        private String selectType;
        private String table;
        private String type;
        private String possibleKeys;
        private String key;
        private String keyLen;
        private String ref;
        private Long rows;
        private String extra;

        public String getSelectType() {
            return selectType;
        }

        public void setSelectType(String selectType) {
            this.selectType = selectType;
        }

        public String getTable() {
            return table;
        }

        public void setTable(String table) {
            this.table = table;
        }

        public String getType() {
            return type;
        }

        public void setType(String type) {
            this.type = type;
        }

        public String getPossibleKeys() {
            return possibleKeys;
        }

        public void setPossibleKeys(String possibleKeys) {
            this.possibleKeys = possibleKeys;
        }

        public String getKey() {
            return key;
        }

        public void setKey(String key) {
            this.key = key;
        }

        public String getKeyLen() {
            return keyLen;
        }

        public void setKeyLen(String keyLen) {
            this.keyLen = keyLen;
        }

        public String getRef() {
            return ref;
        }

        public void setRef(String ref) {
            this.ref = ref;
        }

        public Long getRows() {
            return rows;
        }

        public void setRows(Long rows) {
            this.rows = rows;
        }

        public String getExtra() {
            return extra;
        }

        public void setExtra(String extra) {
            this.extra = extra;
        }
    }

    public static class IndexSuggestion {
        private String tableName;
        private String columnName;
        private String suggestionType;
        private String description;

        public String getTableName() {
            return tableName;
        }

        public void setTableName(String tableName) {
            this.tableName = tableName;
        }

        public String getColumnName() {
            return columnName;
        }

        public void setColumnName(String columnName) {
            this.columnName = columnName;
        }

        public String getSuggestionType() {
            return suggestionType;
        }

        public void setSuggestionType(String suggestionType) {
            this.suggestionType = suggestionType;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }
    }
}