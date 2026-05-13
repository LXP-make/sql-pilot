package com.sqlpilot.backend.rule;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.rule.impl.ImplicitTypeConversionRule;
import com.sqlpilot.backend.rule.impl.IndexRule;
import com.sqlpilot.backend.rule.impl.JoinRule;
import com.sqlpilot.backend.rule.impl.PaginationRule;
import com.sqlpilot.backend.rule.impl.SelectStarRule;
import com.sqlpilot.backend.rule.impl.SubqueryRule;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class SqlRuleEngine {

    private final List<Rule> rules;

    public SqlRuleEngine() {
        this.rules = new ArrayList<>();
        this.rules.add(new SelectStarRule());
        this.rules.add(new ImplicitTypeConversionRule());
        this.rules.add(new SubqueryRule());
        this.rules.add(new PaginationRule());
        this.rules.add(new JoinRule());
        this.rules.add(new IndexRule());
    }

    public List<SqlAnalyzeResponse.RuleViolation> executeRules(String sql) {
        List<SqlAnalyzeResponse.RuleViolation> allViolations = new ArrayList<>();
        for (Rule rule : rules) {
            allViolations.addAll(rule.check(sql));
        }
        return allViolations;
    }
}