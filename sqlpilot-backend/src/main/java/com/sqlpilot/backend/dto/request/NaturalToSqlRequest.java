package com.sqlpilot.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import java.util.Map;

public class NaturalToSqlRequest {
    @NotBlank(message = "Natural query is required")
    private String naturalQuery;
    private Map<String, String[]> tableSchema;

    public String getNaturalQuery() {
        return naturalQuery;
    }

    public void setNaturalQuery(String naturalQuery) {
        this.naturalQuery = naturalQuery;
    }

    public Map<String, String[]> getTableSchema() {
        return tableSchema;
    }

    public void setTableSchema(Map<String, String[]> tableSchema) {
        this.tableSchema = tableSchema;
    }
}