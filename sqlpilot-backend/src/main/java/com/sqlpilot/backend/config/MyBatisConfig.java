package com.sqlpilot.backend.config;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Configuration;

@Configuration
@MapperScan("com.sqlpilot.backend.mapper")
public class MyBatisConfig {
}