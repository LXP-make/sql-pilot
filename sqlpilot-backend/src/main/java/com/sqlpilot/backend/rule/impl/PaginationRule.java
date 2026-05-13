package com.sqlpilot.backend.rule.impl;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.rule.Rule;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PaginationRule implements Rule {

    private static final String RULE_ID = "RULE_004";
    private static final String RULE_NAME = "分页检测";
    private static final String SEVERITY = "WARN";

    private static final Pattern LARGE_OFFSET_PATTERN = 
        Pattern.compile("LIMIT\\s+(\\d{5,}|\\d{4,}),\\s*\\d+", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern MEDIUM_OFFSET_PATTERN = 
        Pattern.compile("LIMIT\\s+(\\d{4}),\\s*\\d+", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern ORDER_BY_DESC_LIMIT = 
        Pattern.compile("ORDER\\s+BY\\s+\\w+\\s+DESC\\s+LIMIT\\s+\\d+", Pattern.CASE_INSENSITIVE);
    
    private static final Pattern HIGH_LIMIT_PATTERN = 
        Pattern.compile("LIMIT\\s+(\\d{4,})", Pattern.CASE_INSENSITIVE);

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

        Matcher largeOffsetMatcher = LARGE_OFFSET_PATTERN.matcher(sql);
        if (largeOffsetMatcher.find()) {
            issues.add("大偏移量分页(LIMIT " + largeOffsetMatcher.group(1) + ", N) - 建议使用游标分页");
        }

        Matcher mediumOffsetMatcher = MEDIUM_OFFSET_PATTERN.matcher(sql);
        if (mediumOffsetMatcher.find() && !largeOffsetMatcher.find()) {
            issues.add("中等偏移量分页(LIMIT " + mediumOffsetMatcher.group(1) + ", N) - 注意性能");
        }

        if (ORDER_BY_DESC_LIMIT.matcher(sql).find()) {
            issues.add("倒序分页模式 - 确认是否需要ORDER BY DESC");
        }

        Matcher highLimitMatcher = HIGH_LIMIT_PATTERN.matcher(sql);
        if (highLimitMatcher.find()) {
            issues.add("大结果集查询(LIMIT " + highLimitMatcher.group(1) + ") - 考虑分批处理");
        }

        if (!issues.isEmpty()) {
            SqlAnalyzeResponse.RuleViolation violation = new SqlAnalyzeResponse.RuleViolation();
            violation.setRuleId(RULE_ID);
            violation.setRuleName(RULE_NAME);
            violation.setSeverity(SEVERITY);
            violation.setDescription("检测到分页问题: " + String.join("; ", issues));
            violations.add(violation);
        }

        return violations;
    }
}