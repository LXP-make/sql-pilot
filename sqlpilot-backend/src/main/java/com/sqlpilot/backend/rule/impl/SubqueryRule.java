package com.sqlpilot.backend.rule.impl;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.rule.Rule;
import net.sf.jsqlparser.JSQLParserException;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.statement.Statement;
import net.sf.jsqlparser.statement.select.FromItem;
import net.sf.jsqlparser.statement.select.PlainSelect;
import net.sf.jsqlparser.statement.select.Select;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SubqueryRule implements Rule {

    private static final String RULE_ID = "RULE_003";
    private static final String RULE_NAME = "子查询检测";
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
        List<String> issues = new ArrayList<>();
        
        String upperSql = sql.toUpperCase();
        
        if (upperSql.contains("IN (SELECT") || upperSql.contains("IN(SELECT")) {
            issues.add("IN子查询 - 考虑使用JOIN替代");
        }

        if (upperSql.contains("EXISTS (")) {
            issues.add("EXISTS子查询");
        }

        if (upperSql.contains("NOT EXISTS (")) {
            issues.add("NOT EXISTS子查询");
        }

        if (upperSql.contains("NOT IN (SELECT") || upperSql.contains("NOT IN(SELECT")) {
            issues.add("NOT IN子查询 - NULL值可能导致意外结果");
        }

        Pattern derivedTablePattern = Pattern.compile("FROM\\s*\\(\\s*SELECT", Pattern.CASE_INSENSITIVE);
        Matcher derivedMatcher = derivedTablePattern.matcher(sql);
        if (derivedMatcher.find()) {
            issues.add("派生表（FROM子句中的子查询）");
        }

        Pattern scalarPattern = Pattern.compile("=\\s*\\(\\s*SELECT", Pattern.CASE_INSENSITIVE);
        Matcher scalarMatcher = scalarPattern.matcher(sql);
        if (scalarMatcher.find()) {
            issues.add("标量子查询 - 可能影响性能");
        }

        Pattern columnSubqueryPattern = Pattern.compile(",\\s*\\(\\s*SELECT", Pattern.CASE_INSENSITIVE);
        Matcher columnMatcher = columnSubqueryPattern.matcher(sql);
        if (columnMatcher.find()) {
            issues.add("SELECT列表中的相关子查询");
        }

        Pattern nestedPattern = Pattern.compile("\\(\\s*SELECT.*\\(\\s*SELECT", Pattern.CASE_INSENSITIVE | Pattern.DOTALL);
        Matcher nestedMatcher = nestedPattern.matcher(sql);
        if (nestedMatcher.find()) {
            issues.add("嵌套子查询 - 可能导致性能问题");
        }

        int selectCount = countOccurrences(upperSql, "SELECT");
        if (selectCount > 2) {
            issues.add("深层嵌套子查询(" + (selectCount - 1) + "层)");
        }

        if (!issues.isEmpty()) {
            SqlAnalyzeResponse.RuleViolation violation = new SqlAnalyzeResponse.RuleViolation();
            violation.setRuleId(RULE_ID);
            violation.setRuleName(RULE_NAME);
            violation.setSeverity(SEVERITY);
            violation.setDescription("检测到子查询: " + String.join("; ", issues));
            violations.add(violation);
        }

        return violations;
    }

    private int countOccurrences(String str, String sub) {
        int count = 0;
        int idx = 0;
        while ((idx = str.indexOf(sub, idx)) != -1) {
            count++;
            idx += sub.length();
        }
        return count;
    }
}