package com.sqlpilot.backend.mapper;

import com.sqlpilot.backend.entity.SqlOptimizationHistory;
import org.apache.ibatis.annotations.Param;
import java.util.List;

public interface SqlOptimizationHistoryMapper {
    void insert(SqlOptimizationHistory history);
    SqlOptimizationHistory selectById(@Param("id") Long id);
    List<SqlOptimizationHistory> selectPage(@Param("offset") int offset, @Param("size") int size);
    Long count();
    void deleteById(@Param("id") Long id);
}