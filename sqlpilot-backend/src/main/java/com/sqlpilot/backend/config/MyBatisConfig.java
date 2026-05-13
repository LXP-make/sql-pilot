package com.sqlpilot.backend.config;

import com.sqlpilot.backend.mapper.SqlAnalysisHistoryMapper;
import com.sqlpilot.backend.mapper.SqlConverterHistoryMapper;
import com.sqlpilot.backend.mapper.SqlOptimizationHistoryMapper;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.mapper.MapperFactoryBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

import javax.sql.DataSource;

@Configuration
public class MyBatisConfig {

    @Bean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        SqlSessionFactoryBean sessionFactory = new SqlSessionFactoryBean();
        sessionFactory.setDataSource(dataSource);
        sessionFactory.setMapperLocations(new PathMatchingResourcePatternResolver()
            .getResources("classpath:mapper/*.xml"));
        sessionFactory.setTypeAliasesPackage("com.sqlpilot.backend.entity");
        return sessionFactory.getObject();
    }

    @Bean
    public MapperFactoryBean<SqlOptimizationHistoryMapper> sqlOptimizationHistoryMapper(SqlSessionFactory sqlSessionFactory) throws Exception {
        MapperFactoryBean<SqlOptimizationHistoryMapper> factory = new MapperFactoryBean<>(SqlOptimizationHistoryMapper.class);
        factory.setSqlSessionFactory(sqlSessionFactory);
        return factory;
    }

    @Bean
    public MapperFactoryBean<SqlConverterHistoryMapper> sqlConverterHistoryMapper(SqlSessionFactory sqlSessionFactory) throws Exception {
        MapperFactoryBean<SqlConverterHistoryMapper> factory = new MapperFactoryBean<>(SqlConverterHistoryMapper.class);
        factory.setSqlSessionFactory(sqlSessionFactory);
        return factory;
    }

    @Bean
    public MapperFactoryBean<SqlAnalysisHistoryMapper> sqlAnalysisHistoryMapper(SqlSessionFactory sqlSessionFactory) throws Exception {
        MapperFactoryBean<SqlAnalysisHistoryMapper> factory = new MapperFactoryBean<>(SqlAnalysisHistoryMapper.class);
        factory.setSqlSessionFactory(sqlSessionFactory);
        return factory;
    }
}