package com.sqlpilot.backend.service;

import com.sqlpilot.backend.dto.response.NaturalToSqlResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class SqlConverterService {

    private final RestTemplate restTemplate;

    public SqlConverterService() {
        this.restTemplate = new RestTemplate();
    }

    public NaturalToSqlResponse convert(String naturalQuery, Map<String, String[]> tableSchema) {
        long startTime = System.currentTimeMillis();

        NaturalToSqlResponse response = new NaturalToSqlResponse();
        response.setNaturalQuery(naturalQuery);

        String generatedSql = generateLocalSql(naturalQuery);
        response.setGeneratedSql(generatedSql);
        response.setConfidence(0.5);

        List<String> suggestions = new ArrayList<>();
        suggestions.add("Please verify the generated SQL meets your expectations");
        suggestions.add("Consider adding appropriate indexes to improve query performance");
        response.setSuggestions(suggestions);

        long executionTime = System.currentTimeMillis() - startTime;
        response.setExecutionTime(executionTime);

        return response;
    }

    private String generateLocalSql(String naturalQuery) {
        String lowerQuery = naturalQuery.toLowerCase();
        if (lowerQuery.contains("user") || lowerQuery.contains("用户")) {
            return "SELECT * FROM users WHERE 1=1";
        } else if (lowerQuery.contains("order") || lowerQuery.contains("订单")) {
            return "SELECT * FROM orders WHERE 1=1";
        }
        return "-- Cannot generate SQL, please provide more context";
    }
}