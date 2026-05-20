package com.sqlpilot.backend.dto.request;

import jakarta.validation.constraints.NotBlank;

public class SqlExecuteRequest {
    @NotBlank(message = "SQL is required")
    private String sql;
    private int maxRows = 100;

    public String getSql() {
        return sql;
    }

    public void setSql(String sql) {
        this.sql = sql;
    }

    public int getMaxRows() {
        return maxRows;
    }

    public void setMaxRows(int maxRows) {
        this.maxRows = maxRows;
    }
}
