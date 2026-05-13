package com.sqlpilot.backend.rule.impl;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.rule.Rule;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class IndexRule implements Rule {

    private static final String RULE_ID = "RULE_006";
    private static final String RULE_NAME = "索引检测";
    private static final String SEVERITY = "WARN";

    private static final Pattern COMPOSITE_INDEX_PATTERN = 
        Pattern.compile("WHERE\\s+\\w+\\s*[<>]=?\\s*[^']+?\\s+AND\\s+\\w+\\s*=\\s*['\\\"]", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern RANGE_BLOCK_PATTERN = 
        Pattern.compile("WHERE\\s+\\w+\\s*[<>]=?\\s*['\\\"]?[^']*['\\\"]?\\s+AND\\s+\\w+\\s*=\\s*['\\\"]", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern NOT_EQUAL_PATTERN = 
        Pattern.compile("WHERE\\s+\\w+\\s*<>\\s*['\\\"]?[^'\"]*['\\\"]?", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern NOT_EQUAL_ALT_PATTERN = 
        Pattern.compile("WHERE\\s+\\w+\\s*!=\\s*['\\\"]?[^'\"]*['\\\"]?", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern FUNCTION_ON_INDEX_PATTERN = 
        Pattern.compile("WHERE\\s+(YEAR|MONTH|DAY|DATE|LOWER|UPPER|LENGTH|TRIM|SUBSTRING|HOUR|MINUTE|SECOND)\\s*\\(\\s*(\\w+)\\s*\\)", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern OR_ON_DIFF_COLUMNS = 
        Pattern.compile("WHERE\\s+\\w+\\s*=\\s*[^=]+?\\s+OR\\s+\\w+\\s*=\\s*[^=]+?", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern DOUBLE_RANGE_PATTERN = 
        Pattern.compile("WHERE\\s+\\w+\\s*[<>]=?\\s*\\d+\\s+AND\\s+\\w+\\s*[<>]=?\\s*\\d+", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern EXPRESSION_ON_COLUMN = 
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

        if (COMPOSITE_INDEX_PATTERN.matcher(sql).find()) {
            issues.add("复合索引顺序问题 - 范围条件应放在等值条件之后");
        }

        if (RANGE_BLOCK_PATTERN.matcher(sql).find()) {
            issues.add("范围查询阻断 - 范围条件后的列无法使用索引");
        }

        if (NOT_EQUAL_PATTERN.matcher(sql).find() || NOT_EQUAL_ALT_PATTERN.matcher(sql).find()) {
            issues.add("不等于操作(<>) - 可能导致全表扫描");
        }

        if (FUNCTION_ON_INDEX_PATTERN.matcher(sql).find()) {
            issues.add("索引列函数操作 - 导致索引失效");
        }

        if (OR_ON_DIFF_COLUMNS.matcher(sql).find()) {
            issues.add("OR条件连接不同列 - 可能无法使用索引");
        }

        if (DOUBLE_RANGE_PATTERN.matcher(sql).find()) {
            issues.add("双重范围条件 - 只能使用一个范围列的索引");
        }

        Matcher exprMatcher = EXPRESSION_ON_COLUMN.matcher(sql);
        if (exprMatcher.find()) {
            issues.add("列上的表达式计算(" + exprMatcher.group(1) + ") - 导致索引失效");
        }

        if (!issues.isEmpty()) {
            SqlAnalyzeResponse.RuleViolation violation = new SqlAnalyzeResponse.RuleViolation();
            violation.setRuleId(RULE_ID);
            violation.setRuleName(RULE_NAME);
            violation.setSeverity(SEVERITY);
            violation.setDescription("检测到索引问题: " + String.join("; ", issues));
            violations.add(violation);
        }

        return violations;
    }
}