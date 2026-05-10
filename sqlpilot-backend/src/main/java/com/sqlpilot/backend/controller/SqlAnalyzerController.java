package com.sqlpilot.backend.controller;

import com.sqlpilot.backend.dto.request.SqlAnalyzeRequest;
import com.sqlpilot.backend.dto.response.ApiResponse;
import com.sqlpilot.backend.dto.response.SqlAnalyzeResponse;
import com.sqlpilot.backend.service.SqlAnalysisService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/sql")
@CrossOrigin(origins = "*")
public class SqlAnalyzerController {

    @Autowired
    private SqlAnalysisService sqlAnalysisService;

    @PostMapping("/analyze")
    public ApiResponse<SqlAnalyzeResponse> analyze(@Valid @RequestBody SqlAnalyzeRequest request) {
        try {
            SqlAnalyzeResponse response = sqlAnalysisService.analyze(
                    request.getSql(),
                    request.getDatabaseType()
            );
            return ApiResponse.success(response);
        } catch (Exception e) {
            return ApiResponse.error("Analysis failed: " + e.getMessage());
        }
    }
}