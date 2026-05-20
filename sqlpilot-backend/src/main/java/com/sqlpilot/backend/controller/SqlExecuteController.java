package com.sqlpilot.backend.controller;

import com.sqlpilot.backend.dto.request.SqlExecuteRequest;
import com.sqlpilot.backend.dto.response.ApiResponse;
import com.sqlpilot.backend.dto.response.SqlExecuteResponse;
import com.sqlpilot.backend.service.SqlExecutionService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/sql")
@CrossOrigin(origins = "*")
public class SqlExecuteController {

    @Autowired
    private SqlExecutionService sqlExecutionService;

    @PostMapping("/execute")
    public ApiResponse<SqlExecuteResponse> execute(@Valid @RequestBody SqlExecuteRequest request) {
        try {
            SqlExecuteResponse response = sqlExecutionService.execute(request.getSql(), request.getMaxRows());
            return ApiResponse.success(response);
        } catch (Exception e) {
            return ApiResponse.error("Execution failed: " + e.getMessage());
        }
    }
}
