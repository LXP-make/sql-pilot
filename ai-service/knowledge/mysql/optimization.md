# MySQL查询优化概述

来源: https://dev.mysql.com/doc/refman/8.0/en/optimize.html

---

## 一、查询优化概述

MySQL查询优化器会自动选择最优执行计划，但开发者仍需了解优化原理以编写高效SQL。

### 1.1 查询优化过程

1. **语法解析**：将SQL解析为解析树
2. **预处理**：检查语义和权限
3. **成本优化**：计算各执行计划的成本
4. **计划执行**：按照最优计划执行

### 1.2 优化器可做的优化

- 选择最合适的索引
- 选择最优的表连接顺序
- 选择最优的连接算法
- 重写子查询
- 简化表达式
- 常量折叠

## 二、EXPLAIN使用指南

### 2.1 查看执行计划

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;

EXPLAIN FORMAT=JSON SELECT * FROM users WHERE id = 1\G

EXPLAIN FORMAT=TREE SELECT * FROM users WHERE id = 1;
```

### 2.2 估算成本

```sql
EXPLAIN FORMAT=JSON SELECT * FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.create_time > '2024-01-01'\G

-- 查看query_cost（查询成本）
-- 成本越低越好
```

## 三、索引优化

### 3.1 索引设计原则

1. **独立列原则**：避免在索引列上使用函数
2. **最左前缀原则**：复合索引遵循顺序
3. **覆盖索引原则**：减少回表查询
4. **选择性原则**：区分度高的列优先

### 3.2 常见索引问题

```sql
-- 问题：索引列使用函数
SELECT * FROM users WHERE YEAR(create_time) = 2024;

-- 解决：改写为范围查询
SELECT * FROM users WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01';

-- 问题：隐式类型转换
SELECT * FROM users WHERE id = '123';  -- id是INT

-- 解决：保持类型一致
SELECT * FROM users WHERE id = 123;
```

## 四、SQL编写优化

### 4.1 SELECT优化

```sql
-- 避免SELECT *
SELECT id, name, email FROM users WHERE id = 1;

-- 使用 LIMIT 限制返回行数
SELECT * FROM orders LIMIT 100;

-- 使用 ORDER BY LIMIT 限制排序范围
SELECT * FROM orders ORDER BY create_time DESC LIMIT 10;
```

### 4.2 WHERE优化

```sql
-- 避免OR条件无索引
SELECT * FROM users WHERE id = 1 OR email = 'test@example.com';

-- 改写为UNION
SELECT * FROM users WHERE id = 1
UNION
SELECT * FROM users WHERE email = 'test@example.com';

-- 避免NOT IN子查询
SELECT * FROM products WHERE id NOT IN (SELECT product_id FROM orders);

-- 改写为NOT EXISTS
SELECT p.* FROM products p WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.product_id = p.id
);
```

### 4.3 JOIN优化

```sql
-- 确保连接列有索引
CREATE INDEX idx_user_id ON orders(user_id);

-- 小表驱动大表
SELECT * FROM small_table s JOIN large_table l ON s.id = l.small_id;
```

## 五、配置优化

### 5.1 关键参数

```sql
-- 查看优化器配置
SHOW VARIABLES LIKE 'optimizer_switch';

-- 启用MRR（多范围读）优化
SET optimizer_switch = 'mrr=on,mrr_cost_based=on';

-- 启用BKA（批量键访问）优化
SET optimizer_switch = 'batched_key_access=on';

-- 设置索引深度
SET max_seeks_for_key = 100;
```

### 5.2 缓存配置

```sql
-- 查询缓存（MySQL 8.0已移除）
-- MySQL 8.0使用查询结果缓存替代

-- 重新连接缓存
SET optimizer_switch = 'reuse_connections=on';
```

## 六、性能分析工具

### 6.1 EXPLAIN ANALYZE（MySQL 8.0.21+）

```sql
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.create_time > '2024-01-01';

-- 输出包含：
-- 预估成本 vs 实际成本
-- 预估行数 vs 实际行数
-- 执行时间
```

### 6.2 Optimizer Trace

```sql
-- 开启optimizer trace
SET optimizer_trace = 'enabled=on';
SET optimizer_trace_max_mem_size = 1048576;

-- 执行查询
SELECT * FROM users WHERE id = 1;

-- 查看trace
SELECT * FROM information_schema.optimizer_trace;
```

### 6.3 Performance Schema

```sql
-- 查看语句事件
SELECT * FROM performance_schema.events_statements_history
ORDER BY TIMER_WAIT DESC LIMIT 10;

-- 查看阶段事件
SELECT * FROM performance_schema.events_stages_history;
```

## 七、慢查询优化

### 7.1 开启慢查询日志

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
SET GLOBAL long_query_time = 1;
SET GLOBAL log_queries_not_using_indexes = 'ON';
```

### 7.2 分析慢查询

```sql
-- 使用mysqldumpslow分析
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log

-- 参数说明：
-- -s: 排序方式 (c:次数, t:时间, l:锁定)
-- -t: 返回前N条
```

### 7.3 pt-query-digest工具

```bash
# 安装Percona Toolkit
# 分析慢查询
pt-query-digest /var/log/mysql/slow.log

# 输出包含：
# 查询响应时间分布
# 查询执行次数
# 查询优化建议
```

## 八、常见优化场景

### 8.1 COUNT(*)优化

```sql
-- 使用COUNT(*)统计行数
SELECT COUNT(*) FROM orders WHERE status = 1;

-- 避免COUNT(列名)
SELECT COUNT(id) FROM orders;  -- 会忽略NULL值

-- 使用EXPLAIN检查
EXPLAIN SELECT COUNT(*) FROM orders;
```

### 8.2 GROUP BY优化

```sql
-- 确保GROUP BY列有索引
CREATE INDEX idx_status ON orders(status);

-- 使用LIMIT获取分组后的一部分数据
SELECT status, COUNT(*) as cnt
FROM orders
GROUP BY status
LIMIT 10;
```

### 8.3 ORDER BY优化

```sql
-- 确保ORDER BY列有索引
CREATE INDEX idx_create_time ON orders(create_time);

-- 避免filesort
EXPLAIN SELECT * FROM orders ORDER BY create_time DESC LIMIT 10;
-- Extra: Using index condition (好)
```

### 8.4 DISTINCT优化

```sql
-- 使用DISTINCT获取唯一值
SELECT DISTINCT status FROM orders;

-- 确保列有索引
CREATE INDEX idx_status ON orders(status);

-- EXPLAIN检查
EXPLAIN SELECT DISTINCT status FROM orders;
```

## 九、总结

### 9.1 优化检查清单

1. [ ] 使用EXPLAIN检查执行计划
2. [ ] 确保type不是ALL（全表扫描）
3. [ ] 确保key不为NULL（使用了索引）
4. [ ] Extra避免Using filesort和Using temporary
5. [ ] rows值尽量小
6. [ ] 使用覆盖索引减少回表

### 9.2 优化优先级

1. **SQL优化**：改写低效SQL
2. **索引优化**：创建合适索引
3. **表结构优化**：合理设计表结构
4. **配置优化**：调整MySQL参数
5. **硬件优化**：升级硬件资源

来源：MySQL 8.0 Reference Manual 及阿里巴巴数据库规范