package com.sqlpilot.backend.mapper;

import com.sqlpilot.backend.entity.SqlConverterHistory;
import org.apache.ibatis.annotations.Param;
import java.util.List;

public interface SqlConverterHistoryMapper {
    void insert(SqlConverterHistory history);
    SqlConverterHistory selectById(@Param("id") Long id);
    List<SqlConverterHistory> selectPage(@Param("offset") int offset, @Param("size") int size);
    Long count();
    void deleteById(@Param("id") Long id);
}