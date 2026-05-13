package com.sqlpilot.backend.rule.impl;

import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.rule.Rule;
import net.sf.jsqlparser.JSQLParserException;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.schema.Table;
import net.sf.jsqlparser.statement.Statement;
import net.sf.jsqlparser.statement.select.FromItem;
import net.sf.jsqlparser.statement.select.Join;
import net.sf.jsqlparser.statement.select.PlainSelect;
import net.sf.jsqlparser.statement.select.Select;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class JoinRule implements Rule {

    private static final String RULE_ID = "RULE_005";
    private static final String RULE_NAME = "JOIN检测";
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
        
        if (upperSql.contains("FROM") && upperSql.contains(",") && upperSql.contains("WHERE")) {
            int fromIdx = upperSql.indexOf("FROM");
            int whereIdx = upperSql.indexOf("WHERE");
            if (fromIdx < whereIdx) {
                String between = upperSql.substring(fromIdx, whereIdx);
                if (between.contains(",") && countOccurrences(between, "FROM") == 1) {
                    issues.add("隐式JOIN（逗号分隔）- 建议使用显式JOIN语法");
                }
            }
        }
        
        int joinCount = countOccurrences(upperSql, "JOIN");
        if (joinCount > 2) {
            issues.add("多层JOIN(" + joinCount + "层) - 可能导致性能问题");
        }
        
        int leftJoinCount = countOccurrences(upperSql, "LEFT JOIN");
        if (leftJoinCount > 1) {
            issues.add("连续LEFT JOIN(" + leftJoinCount + "个) - 注意结果集膨胀");
        }
        
        if (hasSelfJoin(sql)) {
            issues.add("自连接 - 确保在连接列上有索引");
        }
        
        if (!issues.isEmpty()) {
            SqlAnalyzeResponse.RuleViolation violation = new SqlAnalyzeResponse.RuleViolation();
            violation.setRuleId(RULE_ID);
            violation.setRuleName(RULE_NAME);
            violation.setSeverity(SEVERITY);
            violation.setDescription("检测到JOIN问题: " + String.join("; ", issues));
            violations.add(violation);
        }
        
        return violations;
    }

    private boolean hasSelfJoin(String sql) {
        try {
            Statement stmt = CCJSqlParserUtil.parse(sql);
            if (stmt instanceof Select) {
                Select select = (Select) stmt;
                Object body = select.getSelectBody();
                if (body instanceof PlainSelect) {
                    PlainSelect plainSelect = (PlainSelect) body;
                    Map<String, Integer> tableCount = new HashMap<>();
                    
                    FromItem fromItem = plainSelect.getFromItem();
                    if (fromItem instanceof Table) {
                        Table table = (Table) fromItem;
                        String tableName = table.getName().toLowerCase();
                        tableCount.put(tableName, 1);
                    }
                    
                    List<Join> joins = plainSelect.getJoins();
                    if (joins != null) {
                        for (Join join : joins) {
                            FromItem rightItem = join.getRightItem();
                            if (rightItem instanceof Table) {
                                Table table = (Table) rightItem;
                                String tableName = table.getName().toLowerCase();
                                int count = tableCount.getOrDefault(tableName, 0) + 1;
                                tableCount.put(tableName, count);
                                if (count > 1) {
                                    return true;
                                }
                            }
                        }
                    }
                }
            }
        } catch (JSQLParserException e) {
            // 解析失败，跳过
        }
        
        return false;
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