package com.sqlpilot.backend;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.sqlpilot.backend.mapper")
public class SqlPilotApplication {

    public static void main(String[] args) {
        SpringApplication.run(SqlPilotApplication.class, args);
    }

}