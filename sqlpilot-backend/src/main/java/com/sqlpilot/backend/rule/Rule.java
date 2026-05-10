package com.sqlpilot.backend.rule;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import java.util.List;

public interface Rule {
    String getRuleId();
    String getRuleName();
    String getSeverity();
    List<SqlAnalyzeResponse.RuleViolation> check(String sql);
}