package com.sqlpilot.backend.service;

import com.sqlpilot.backend.dto.response.SqlExecuteResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SqlExecutionService {

    @Autowired
    private DataSource dataSource;

    public SqlExecuteResponse execute(String sql, int maxRows) {
        SqlExecuteResponse response = new SqlExecuteResponse();
        long start = System.currentTimeMillis();

        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            boolean hasResultSet = stmt.execute();
            long elapsed = System.currentTimeMillis() - start;

            if (hasResultSet) {
                try (ResultSet rs = stmt.getResultSet()) {
                    ResultSetMetaData meta = rs.getMetaData();
                    int colCount = meta.getColumnCount();
                    List<Map<String, Object>> rows = new ArrayList<>();

                    while (rs.next()) {
                        Map<String, Object> row = new HashMap<>();
                        for (int i = 1; i <= colCount; i++) {
                            row.put(meta.getColumnLabel(i), rs.getObject(i));
                        }
                        rows.add(row);
                    }

                    int totalRows = rows.size();
                    List<Map<String, Object>> limited = totalRows > maxRows
                            ? rows.subList(0, maxRows) : rows;

                    response.setSuccess(true);
                    response.setExecutionTimeMs(elapsed);
                    response.setRowCount(totalRows);
                    response.setRows(limited);
                }
            } else {
                int affected = stmt.getUpdateCount();
                elapsed = System.currentTimeMillis() - start;
                response.setSuccess(true);
                response.setExecutionTimeMs(elapsed);
                response.setRowCount(affected);
            }
        } catch (Exception e) {
            long elapsed = System.currentTimeMillis() - start;
            response.setSuccess(false);
            response.setExecutionTimeMs(elapsed);
            response.setError(e.getMessage());
        }

        return response;
    }
}
