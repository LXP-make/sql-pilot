package com.sqlpilot.backend.service;

import com.alibaba.fastjson.JSON;
import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.entity.SqlAnalysisHistory;
import com.sqlpilot.backend.mapper.SqlAnalysisHistoryMapper;
import com.sqlpilot.backend.rule.SqlRuleEngine;
import com.sqlpilot.backend.util.DatabaseUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class SqlAnalysisService {

    @Autowired
    private SqlRuleEngine sqlRuleEngine;

    @Autowired
    private DatabaseUtils databaseUtils;

    @Autowired
    private SqlAnalysisHistoryMapper historyMapper;

    public SqlAnalyzeResponse analyze(String sql, String databaseType) {
        long startTime = System.currentTimeMillis();

        SqlAnalyzeResponse response = new SqlAnalyzeResponse();
        response.setOriginalSql(sql);
        response.setDatabaseType(databaseType);

        SqlAnalyzeResponse.AnalysisResults results = new SqlAnalyzeResponse.AnalysisResults();

        List<SqlAnalyzeResponse.RuleViolation> violations = sqlRuleEngine.executeRules(sql);
        results.setRuleViolations(violations);
        results.setSyntaxValid(violations.isEmpty() || !hasErrorViolation(violations));

        SqlAnalyzeResponse.ExplainResult explainResult = executeExplain(sql);
        results.setExplainResult(explainResult);

        results.setPerformanceScore(calculatePerformanceScore(violations, explainResult));

        response.setAnalysisResults(results);

        List<SqlAnalyzeResponse.IndexSuggestion> indexSuggestions = generateIndexSuggestions(sql);
        response.setIndexSuggestions(indexSuggestions);

        long executionTime = System.currentTimeMillis() - startTime;
        response.setExecutionTime(executionTime);

        Long historyId = saveAnalysisHistory(response);
        response.setAnalysisId(historyId);

        return response;
    }

    private SqlAnalyzeResponse.ExplainResult executeExplain(String sql) {
        try {
            String explainSql = "EXPLAIN " + sql;
            List<Map<String, Object>> result = databaseUtils.executeQuery(explainSql);

            if (!result.isEmpty()) {
                Map<String, Object> row = result.get(0);
                SqlAnalyzeResponse.ExplainResult explainResult = new SqlAnalyzeResponse.ExplainResult();
                explainResult.setSelectType((String) row.get("select_type"));
                explainResult.setTable((String) row.get("table"));
                explainResult.setType((String) row.get("type"));
                explainResult.setPossibleKeys((String) row.get("possible_keys"));
                explainResult.setKey((String) row.get("key"));
                explainResult.setKeyLen((String) row.get("key_len"));
                explainResult.setRef((String) row.get("ref"));
                Object rowsObj = row.get("rows");
                if (rowsObj instanceof Number) {
                    explainResult.setRows(((Number) rowsObj).longValue());
                }
                explainResult.setExtra((String) row.get("Extra"));
                return explainResult;
            }
        } catch (Exception e) {
        }
        return null;
    }

    private boolean hasErrorViolation(List<SqlAnalyzeResponse.RuleViolation> violations) {
        return violations.stream().anyMatch(v -> "ERROR".equals(v.getSeverity()));
    }

    private int calculatePerformanceScore(List<SqlAnalyzeResponse.RuleViolation> violations, SqlAnalyzeResponse.ExplainResult explainResult) {
        int score = 100;

        for (SqlAnalyzeResponse.RuleViolation violation : violations) {
            if ("ERROR".equals(violation.getSeverity())) {
                score -= 20;
            } else if ("WARN".equals(violation.getSeverity())) {
                score -= 10;
            }
        }

        if (explainResult != null && "ALL".equals(explainResult.getType())) {
            score -= 30;
        }

        return Math.max(0, score);
    }

    private List<SqlAnalyzeResponse.IndexSuggestion> generateIndexSuggestions(String sql) {
        List<SqlAnalyzeResponse.IndexSuggestion> suggestions = new ArrayList<>();
        return suggestions;
    }

    private Long saveAnalysisHistory(SqlAnalyzeResponse response) {
        SqlAnalysisHistory history = new SqlAnalysisHistory();
        history.setOriginalSql(response.getOriginalSql());
        history.setDatabaseType(response.getDatabaseType());
        history.setSyntaxValid(response.getAnalysisResults().getSyntaxValid());
        history.setPerformanceScore(response.getAnalysisResults().getPerformanceScore());
        history.setExecutionTime(response.getExecutionTime());
        history.setAnalysisResult(JSON.toJSONString(response.getAnalysisResults()));

        historyMapper.insert(history);
        return history.getId();
    }
}