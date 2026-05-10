package com.sqlpilot.backend.rule;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.rule.impl.SelectStarRule;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class SqlRuleEngine {

    private final List<Rule> rules;

    public SqlRuleEngine() {
        this.rules = new ArrayList<>();
        this.rules.add(new SelectStarRule());
    }

    public List<SqlAnalyzeResponse.RuleViolation> executeRules(String sql) {
        List<SqlAnalyzeResponse.RuleViolation> allViolations = new ArrayList<>();
        for (Rule rule : rules) {
            allViolations.addAll(rule.check(sql));
        }
        return allViolations;
    }
}