# MySQL JOIN优化

来源: https://dev.mysql.com/doc/refman/8.0/en/optimization.html

---

## 一、JOIN执行原理

### 1.1 嵌套循环连接（NLJ）

MySQL默认使用嵌套循环算法执行JOIN：

```sql
SELECT * FROM orders o JOIN users u ON o.user_id = u.id;
```

执行过程：
1. 遍历驱动表（外表）
2. 对每一行，根据连接条件查询被驱动表（内表）
3. 组合结果返回

### 1.2 块嵌套循环连接（BNL）

当连接缓冲区足够大时，MySQL使用BNL算法：

```sql
-- 启用块嵌套循环
SET optimizer_switch = 'block_nested_loop=on';

SELECT * FROM orders o JOIN users u ON o.user_id = u.id;
```

## 二、JOIN类型优化

### 2.1 INNER JOIN优化

确保连接列有索引：

```sql
-- 优化前（无索引）
EXPLAIN SELECT * FROM orders o INNER JOIN users u ON o.user_id = u.id;

-- 结果：
-- type: ALL (全表扫描)
-- 性能差

-- 优化：为user_id添加索引
CREATE INDEX idx_user_id ON orders(user_id);

-- 优化后
-- type: ref (索引查找)
-- 性能好
```

### 2.2 LEFT JOIN优化

**原则**：小表驱动大表

```sql
-- 优化策略：将小表作为驱动表
SELECT * FROM small_table s LEFT JOIN large_table l ON s.id = l.small_id;

-- 验证：小表有100行，大表有1000万行
-- 使用小表驱动，减少循环次数
```

### 2.3 多表JOIN优化

控制JOIN表的数量和顺序：

```sql
-- 优化前：5表JOIN
SELECT * FROM a,b,c,d,e WHERE a.id=b.a_id AND b.id=c.b_id...;

-- 优化后：拆分为多个简单查询
SELECT * FROM a WHERE ...;
SELECT * FROM b WHERE a_id IN (...);
SELECT * FROM c WHERE b_id IN (...);
```

## 三、JOIN优化策略

### 3.1 为JOIN列创建索引

```sql
-- 为连接列创建索引
CREATE INDEX idx_a_id ON a(id);
CREATE INDEX idx_b_a_id ON b(a_id);

-- 确保连接列类型一致
ALTER TABLE orders MODIFY user_id BIGINT NOT NULL;  -- 与users.id类型一致
```

### 3.2 使用STRAIGHT_JOIN强制顺序

```sql
-- 强制按书写顺序执行JOIN
SELECT STRAIGHT_JOIN * FROM orders o
STRAIGHT_JOIN users u ON o.user_id = u.id
STRAIGHT_JOIN products p ON o.product_id = p.id;
```

### 3.3 启用Batched Key Access

```sql
-- 启用BKA优化
SET optimizer_switch = 'batched_key_access=on';

EXPLAIN SELECT * FROM orders o JOIN users u ON o.user_id = u.id;
-- Extra: Using join buffer (Batched Key Access)
```

### 3.4 优化Buffer配置

```sql
-- 查看JOIN缓冲区大小
SHOW VARIABLES LIKE 'join_buffer_size';

-- 默认256KB，建议根据数据量调整
SET GLOBAL join_buffer_size = 1048576;  -- 1MB
```

## 四、JOIN类型选择

### 4.1 小表JOIN大表

```sql
-- 小表（前1000条）JOIN大表
SELECT * FROM small_customers c
INNER JOIN orders o ON c.id = o.customer_id;

-- 确保小表有合适索引
CREATE INDEX idx_customer_id ON orders(customer_id);
```

### 4.2 大表JOIN大表

```sql
-- 使用分步查询
-- 步骤1：从表A获取需要的ID
SELECT id INTO @ids FROM a WHERE ... LIMIT 1000;

-- 步骤2：用ID查询表B
SELECT * FROM b WHERE id IN (@ids);
```

### 4.3 多表JOIN顺序

**原则**：
1. 驱动表选择数据量小的表
2. 优先连接有索引的表
3. 尽量减少中间结果集大小

```sql
-- 优化前：未考虑表大小
SELECT * FROM large_table1 t1
JOIN small_table t2 ON t1.id = t2.t1_id
JOIN medium_table t3 ON t2.id = t3.t2_id;

-- 优化后：调整JOIN顺序
SELECT * FROM small_table t2
JOIN medium_table t3 ON t2.id = t3.t2_id
JOIN large_table1 t1 ON t3.t1_id = t1.id;
```

## 五、实战案例

### 5.1 案例一：优化多表连接

**问题SQL**：
```sql
SELECT o.id, o.order_no, u.name, p.product_name
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
WHERE o.create_time > '2024-01-01';
```

**优化方案**：
```sql
-- 1. 确保连接列有索引
CREATE INDEX idx_user_id ON orders(user_id);
CREATE INDEX idx_product_id ON orders(product_id);

-- 2. 添加查询条件索引
CREATE INDEX idx_create_time ON orders(create_time);

-- 3. 使用覆盖索引
CREATE INDEX idx_time_user_product ON orders(create_time, user_id, product_id);
```

### 5.2 案例二：优化OR条件连接

**问题SQL**：
```sql
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id OR o.creator_id = u.id;
```

**优化方案**：
```sql
-- 改写为UNION
SELECT * FROM orders o JOIN users u ON o.user_id = u.id
UNION
SELECT * FROM orders o JOIN users u ON o.creator_id = u.id;
```

## 六、JOIN性能监控

### 6.1 查看JOIN执行计划

```sql
EXPLAIN FORMAT=JSON
SELECT * FROM orders o JOIN users u ON o.user_id = u.id\G
```

### 6.2 检查慢查询

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- 分析JOIN相关慢查询
SHOW GLOBAL STATUS LIKE 'Slow_queries';
```

### 6.3 使用Performance Schema

```sql
-- 查看JOIN缓冲区使用情况
SELECT * FROM performance_schema.memory_summary_global_by_event_name
WHERE EVENT_NAME LIKE 'memory/sql/join%';
```

## 七、JOIN最佳实践

1. **小表驱动大表**：减少循环次数
2. **为JOIN列创建索引**：加速连接查找
3. **避免全表扫描**：确保连接列有索引
4. **控制JOIN数量**：不超过3-4个表
5. **使用EXPLAIN分析**：检查执行计划
6. **适当增加Buffer**：提升BNL性能

来源：MySQL 8.0 Reference Manual 及字节跳动技术团队实践