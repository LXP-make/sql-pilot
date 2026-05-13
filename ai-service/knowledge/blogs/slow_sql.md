# 慢SQL优化最佳实践

---

## 一、慢查询定义

MySQL慢查询日志是MySQL提供的一种日志记录，用来记录在MySQL中响应时间超过阈值的SQL语句。

### 1.1 慢查询配置参数

```sql
-- 查看慢查询相关配置
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 设置阈值时间为1秒

-- 设置慢查询日志文件路径
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
```

### 1.2 慢查询分析工具

```bash
# 使用 mysqldumpslow 工具分析慢查询日志
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log

# 参数说明：
# -s: 排序方式 (c:次数, t:时间, l:锁定时间)
# -t: 返回前N条记录
```

## 二、慢查询原因分析

### 2.1 常见原因

1. **全表扫描**：没有合适的索引
2. **索引失效**：查询条件导致索引无法使用
3. **深度分页**：LIMIT offset过大
4. **复杂查询**：多表JOIN、子查询
5. **函数操作**：在索引列上使用函数

### 2.2 优化策略

#### 策略一：使用覆盖索引

```sql
-- 避免回表查询
SELECT id, name FROM users WHERE name = 'John';
-- 创建覆盖索引
CREATE INDEX idx_name_id ON users(name, id);
```

#### 策略二：优化深度分页

```sql
-- 原始慢查询
SELECT * FROM orders LIMIT 1000000, 10;

-- 优化方案1：使用游标分页
SELECT * FROM orders WHERE id > #{last_id} LIMIT 10;

-- 优化方案2：延迟关联
SELECT * FROM orders o
INNER JOIN (SELECT id FROM orders LIMIT 1000000, 10) t
ON o.id = t.id;
```

#### 策略三：避免索引失效

```sql
-- 错误示例：索引失效
SELECT * FROM users WHERE YEAR(create_time) = 2024;

-- 正确示例：索引生效
SELECT * FROM users
WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01';
```

## 三、实战案例

### 3.1 案例一：全表扫描优化

**问题SQL**：
```sql
SELECT * FROM orders WHERE status = 'completed' AND create_time >= '2024-01-01';
```

**优化方案**：
```sql
-- 创建复合索引
CREATE INDEX idx_status_create_time ON orders(status, create_time);
```

**优化效果**：
- 优化前：查询时间 5s（全表扫描100万行）
- 优化后：查询时间 50ms（索引扫描）

### 3.2 案例二：深度分页优化

**问题SQL**：
```sql
SELECT * FROM products ORDER BY create_time DESC LIMIT 100000, 20;
```

**优化方案**：
```sql
-- 使用延迟关联
SELECT p.* FROM products p
INNER JOIN (
    SELECT id FROM products
    ORDER BY create_time DESC
    LIMIT 100000, 20
) t ON p.id = t.id;
```

**优化效果**：
- 优化前：查询时间 3s
- 优化后：查询时间 80ms

## 四、监控与预防

### 4.1 定期检查慢查询

```sql
-- 查看最近一次的慢查询分析
SHOW GLOBAL STATUS LIKE 'Slow_queries';

-- 查看有多少查询超过阈值
SELECT * FROM mysql.slow_log
ORDER BY start_time DESC
LIMIT 10;
```

### 4.2 索引优化建议

```sql
-- 分析查询使用到的索引
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 查看表的索引情况
SHOW INDEX FROM users;

-- 查找未使用的索引
SELECT * FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL
AND count_star = 0;
```

## 五、总结

1. **预防为主**：编写SQL时注意索引设计
2. **监控为辅**：开启慢查询日志，及时发现问题
3. **优化有道**：根据EXPLAIN分析结果针对性优化
4. **定期巡检**：定期检查和优化慢查询

来源：MySQL官方文档及美团技术团队实践