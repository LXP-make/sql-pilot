package com.sqlpilot.backend.controller;

import com.sqlpilot.backend.dto.request.NaturalToSqlRequest;
import com.sqlpilot.backend.dto.response.ApiResponse;
import com.sqlpilot.backend.dto.response.NaturalToSqlResponse;
import com.sqlpilot.backend.service.SqlConverterService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/sql")
@CrossOrigin(origins = "*")
public class SqlConverterController {

    @Autowired
    private SqlConverterService sqlConverterService;

    @PostMapping("/natural-to-sql")
    public ApiResponse<NaturalToSqlResponse> convert(@Valid @RequestBody NaturalToSqlRequest request) {
        try {
            NaturalToSqlResponse response = sqlConverterService.convert(
                    request.getNaturalQuery(),
                    request.getTableSchema()
            );
            return ApiResponse.success(response);
        } catch (Exception e) {
            return ApiResponse.error("Conversion failed: " + e.getMessage());
        }
    }
}