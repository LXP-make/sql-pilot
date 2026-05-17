package com.sqlpilot.backend.mapper;

import com.sqlpilot.backend.entity.SqlAnalysisHistory;
import org.apache.ibatis.annotations.Param;
import java.util.List;

public interface SqlAnalysisHistoryMapper {
    void insert(SqlAnalysisHistory history);
    SqlAnalysisHistory selectById(@Param("id") Long id);
    List<SqlAnalysisHistory> selectPage(@Param("offset") int offset, @Param("size") int size);
    Long count();
    void deleteById(@Param("id") Long id);
    
    List<SqlAnalysisHistory> selectByDatabaseType(@Param("databaseType") String databaseType);
    List<SqlAnalysisHistory> selectRecentByDatabaseType(@Param("databaseType") String databaseType, @Param("limit") int limit);
    List<SqlAnalysisHistory> selectAll();
}