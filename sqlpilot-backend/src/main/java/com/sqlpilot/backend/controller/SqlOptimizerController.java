package com.sqlpilot.backend.controller;

import com.sqlpilot.backend.dto.request.SqlOptimizeRequest;
import com.sqlpilot.backend.dto.response.ApiResponse;
import com.sqlpilot.backend.dto.response.SqlOptimizeResponse;
import com.sqlpilot.backend.service.SqlOptimizeService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/sql")
@CrossOrigin(origins = "*")
public class SqlOptimizerController {

    @Autowired
    private SqlOptimizeService sqlOptimizeService;

    @PostMapping("/optimize")
    public ApiResponse<SqlOptimizeResponse> optimize(@Valid @RequestBody SqlOptimizeRequest request) {
        try {
            SqlOptimizeResponse response = sqlOptimizeService.optimize(
                    request.getSql(),
                    request.getOptimizationLevel(),
                    request.getIncludeIndexSuggestion()
            );
            return ApiResponse.success(response);
        } catch (Exception e) {
            return ApiResponse.error("Optimization failed: " + e.getMessage());
        }
    }
}