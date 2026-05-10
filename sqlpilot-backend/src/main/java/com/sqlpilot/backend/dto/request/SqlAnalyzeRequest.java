package com.sqlpilot.backend.dto.request;

import jakarta.validation.constraints.NotBlank;

public class SqlAnalyzeRequest {
    @NotBlank(message = "SQL is required")
    private String sql;
    private String databaseType;

    public String getSql() {
        return sql;
    }

    public void setSql(String sql) {
        this.sql = sql;
    }

    public String getDatabaseType() {
        return databaseType;
    }

    public void setDatabaseType(String databaseType) {
        this.databaseType = databaseType;
    }
}