package com.sqlpilot.backend.rule.impl;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.rule.Rule;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ImplicitTypeConversionRule implements Rule {

    private static final String RULE_ID = "RULE_002";
    private static final String RULE_NAME = "隐式类型转换检测";
    private static final String SEVERITY = "WARN";

    private static final Pattern STRING_COL_COMPARE_NUM = 
        Pattern.compile("WHERE\\s+(phone|mobile|email|name|address|code|status|type|phone_number)\\s*=\\s*\\d+", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern DATE_COL_COMPARE_NUM = 
        Pattern.compile("WHERE\\s+(create_time|created_at|update_time|modify_time|start_time|end_time|date)\\s*=\\s*\\d{10,13}", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern NUM_COL_COMPARE_STR = 
        Pattern.compile("WHERE\\s+(age|id|total|amount|price|count|score|level)\\s*=\\s*['\"]([^'\"]*)['\"]", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern DECIMAL_COL_COMPARE_STR = 
        Pattern.compile("WHERE\\s+(balance|salary|cost|discount|rate)\\s*=\\s*['\"](\\d+\\.?\\d*)['\"]", Pattern.CASE_INSENSITIVE);

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

        if (STRING_COL_COMPARE_NUM.matcher(sql).find()) {
            issues.add("字符串列与数字比较 - 可能导致隐式类型转换");
        }

        if (DATE_COL_COMPARE_NUM.matcher(sql).find()) {
            issues.add("日期列与时间戳比较 - 可能导致隐式类型转换");
        }

        Matcher numMatcher = NUM_COL_COMPARE_STR.matcher(sql);
        while (numMatcher.find()) {
            String value = numMatcher.group(1);
            if (value != null && !value.matches("\\d+")) {
                issues.add("数值列与非数字字符串比较 - 可能导致隐式类型转换");
            }
        }

        if (DECIMAL_COL_COMPARE_STR.matcher(sql).find()) {
            issues.add("小数列与字符串比较 - 可能导致隐式类型转换");
        }

        if (!issues.isEmpty()) {
            SqlAnalyzeResponse.RuleViolation violation = new SqlAnalyzeResponse.RuleViolation();
            violation.setRuleId(RULE_ID);
            violation.setRuleName(RULE_NAME);
            violation.setSeverity(SEVERITY);
            violation.setDescription("检测到隐式类型转换: " + String.join("; ", issues));
            violations.add(violation);
        }

        return violations;
    }
}