package com.sqlpilot.backend.rule.impl;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.rule.Rule;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.statement.Statement;
import net.sf.jsqlparser.statement.select.PlainSelect;
import net.sf.jsqlparser.statement.select.Select;
import net.sf.jsqlparser.statement.select.SelectItem;

import java.util.ArrayList;
import java.util.List;

public class SelectStarRule implements Rule {

    private static final String RULE_ID = "RULE_001";
    private static final String RULE_NAME = "SELECT * Detection";
    private static final String SEVERITY = "WARN";

    @Override
    public String getRuleId() {
        return RULE_ID;
    }

    @Override
    public String getRuleName() {
        return RULE_NAME;
    }

    @Override
    public String getSeverity() {
        return SEVERITY;
    }

    @Override
    public List<SqlAnalyzeResponse.RuleViolation> check(String sql) {
        List<SqlAnalyzeResponse.RuleViolation> violations = new ArrayList<>();

        try {
            Statement statement = CCJSqlParserUtil.parse(sql);

            if (statement instanceof Select) {
                Select select = (Select) statement;

                if (select.getSelectBody() instanceof PlainSelect) {
                    PlainSelect plainSelect = (PlainSelect) select.getSelectBody();

                    for (SelectItem item : plainSelect.getSelectItems()) {
                        String itemStr = item.toString();
                        if (itemStr.equals("*") || itemStr.contains(".*")) {
                            SqlAnalyzeResponse.RuleViolation violation = new SqlAnalyzeResponse.RuleViolation();
                            violation.setRuleId(RULE_ID);
                            violation.setRuleName(RULE_NAME);
                            violation.setSeverity(SEVERITY);
                            violation.setDescription("Consider explicitly specifying columns instead of using SELECT *");
                            violations.add(violation);
                            break;
                        }
                    }
                }
            }
        } catch (Exception e) {
        }

        return violations;
    }
}