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
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SelectStarRule implements Rule {

    private static final String RULE_ID = "RULE_001";
    private static final String RULE_NAME = "SELECT检测";
    private static final String SEVERITY = "WARN";

    private static final Pattern LARGE_TABLE_PATTERN = 
        Pattern.compile("FROM\\s+(large_|big_|huge_|massive_|giant_)\\w+", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern COLUMN_EXPRESSION_PATTERN = 
        Pattern.compile("WHERE\\s+(\\w+)\\s*([+\\-*/%])\\s*\\d+\\s*[<>]=?", Pattern.CASE_INSENSITIVE);

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
        List<String> issues = new ArrayList<>();

        try {
            Statement statement = CCJSqlParserUtil.parse(sql);

            if (statement instanceof Select) {
                Select select = (Select) statement;

                if (select.getSelectBody() instanceof PlainSelect) {
                    PlainSelect plainSelect = (PlainSelect) select.getSelectBody();

                    for (SelectItem item : plainSelect.getSelectItems()) {
                        String itemStr = item.toString();
                        if (itemStr.equals("*") || itemStr.contains(".*")) {
                            issues.add("SELECT * - 建议明确指定需要的列");
                            break;
                        }
                    }
                }
            }
        } catch (Exception e) {
            if (sql.contains("SELECT *")) {
                issues.add("SELECT * - 建议明确指定需要的列");
            }
        }

        if (LARGE_TABLE_PATTERN.matcher(sql).find()) {
            issues.add("查询大表 - 注意性能影响");
        }

        Matcher exprMatcher = COLUMN_EXPRESSION_PATTERN.matcher(sql);
        if (exprMatcher.find()) {
            issues.add("列上的表达式计算(" + exprMatcher.group(1) + exprMatcher.group(2) + ") - 可能导致索引失效");
        }

        if (!issues.isEmpty()) {
            SqlAnalyzeResponse.RuleViolation violation = new SqlAnalyzeResponse.RuleViolation();
            violation.setRuleId(RULE_ID);
            violation.setRuleName(RULE_NAME);
            violation.setSeverity(SEVERITY);
            violation.setDescription("检测到SELECT问题: " + String.join("; ", issues));
            violations.add(violation);
        }

        return violations;
    }
}