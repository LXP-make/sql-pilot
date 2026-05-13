# MySQL子查询优化指南

## 一、子查询类型

### 1.1 相关子查询（Correlated Subquery）

**定义**：子查询引用外部查询的列，需要为外部查询的每一行执行一次

**示例**：
```sql
SELECT name, (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count
FROM users u
```

**性能问题**：
- 对外部查询的每一行执行子查询
- 当users表很大时，性能会急剧下降

**优化建议**：
- 使用JOIN替代
- 使用窗口函数

**优化后**：
```sql
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name
```

### 1.2 非相关子查询（Non-correlated Subquery）

**定义**：子查询不引用外部查询的列，只执行一次

**示例**：
```sql
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE status = 1)
```

**优化建议**：
- 使用JOIN替代IN子查询
- 对于NOT IN，改用NOT EXISTS避免NULL问题

### 1.3 标量子查询（Scalar Subquery）

**定义**：返回单个值的子查询

**示例**：
```sql
SELECT * FROM users WHERE id = (SELECT MAX(id) FROM orders)
```

**优化建议**：
- 如果可能，使用变量存储结果
- 确保子查询有合适的索引

## 二、子查询优化最佳实践

### 2.1 使用JOIN替代IN子查询

**原查询**：
```sql
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)
```

**优化后**：
```sql
SELECT DISTINCT u.* FROM users u
JOIN orders o ON u.id = o.user_id
```

**性能提升**：避免子查询的额外开销，利用JOIN优化器

### 2.2 使用NOT EXISTS替代NOT IN

**原查询**：
```sql
SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM banned_users)
```

**问题**：如果子查询返回NULL，NOT IN结果为空

**优化后**：
```sql
SELECT * FROM users u
WHERE NOT EXISTS (SELECT 1 FROM banned_users b WHERE b.user_id = u.id)
```

**优势**：
- 正确处理NULL值
- 性能更稳定

### 2.3 避免多层嵌套子查询

**原查询**：
```sql
SELECT * FROM (
    SELECT * FROM (
        SELECT * FROM orders WHERE status = 1
    ) AS t1
) AS t2
```

**优化后**：
```sql
SELECT * FROM orders WHERE status = 1
```

**原则**：尽量扁平化查询结构

### 2.4 使用临时表存储中间结果

**场景**：复杂计算需要多次使用同一结果集

```sql
CREATE TEMPORARY TABLE temp_result AS
SELECT user_id, COUNT(*) as order_count
FROM orders 
WHERE create_time >= '2024-01-01'
GROUP BY user_id;

SELECT u.name, t.order_count
FROM users u
JOIN temp_result t ON u.id = t.user_id;
```

## 三、子查询性能问题检测

### 3.1 检测相关子查询

**特征**：
- 子查询引用外部表的列
- 执行计划中显示"DEPENDENT SUBQUERY"
- 执行时间随外部表行数线性增长

**检测方法**：
```sql
EXPLAIN SELECT name, (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id)
FROM users u;
```

### 3.2 检测NOT IN陷阱

**特征**：
- 使用NOT IN子查询
- 子查询可能返回NULL值
- 意外返回空结果集

**检测方法**：
```sql
-- 检查是否包含NULL
SELECT COUNT(*) FROM banned_users WHERE user_id IS NULL;
```

### 3.3 检测过度嵌套

**特征**：
- 查询包含多层子查询
- 执行计划复杂
- 难以维护

## 四、子查询索引优化

### 4.1 子查询条件列索引

```sql
-- 为子查询条件列创建索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```

### 4.2 覆盖索引优化

```sql
-- 对于IN子查询，创建覆盖索引
CREATE INDEX idx_orders_user_id_status ON orders(user_id, status);
```

## 五、案例分析

### 案例1：相关子查询优化

**问题查询**：
```sql
SELECT 
    name,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id AND o.status = 'completed') as completed_count,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id AND o.status = 'pending') as pending_count
FROM users u
WHERE u.age > 18;
```

**优化后**：
```sql
SELECT 
    u.name,
    SUM(CASE WHEN o.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
    SUM(CASE WHEN o.status = 'pending' THEN 1 ELSE 0 END) as pending_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.age > 18
GROUP BY u.id, u.name;
```

**性能提升**：从O(n*m)降到O(n+m)

### 案例2：NOT IN优化

**问题查询**：
```sql
SELECT * FROM products 
WHERE id NOT IN (SELECT product_id FROM order_items);
```

**优化后**：
```sql
SELECT p.* FROM products p
WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.id);
```

**性能提升**：正确处理NULL，避免意外结果

### 案例3：标量子查询优化

**问题查询**：
```sql
SELECT * FROM orders 
WHERE total_amount > (SELECT AVG(total_amount) FROM orders);
```

**优化后**：
```sql
SET @avg_amount = (SELECT AVG(total_amount) FROM orders);
SELECT * FROM orders WHERE total_amount > @avg_amount;
```

**性能提升**：子查询只执行一次

## 六、总结

| 问题类型 | 检测方法 | 优化策略 |
|---------|---------|---------|
| 相关子查询 | EXPLAIN显示DEPENDENT SUBQUERY | 使用JOIN或窗口函数 |
| NOT IN陷阱 | 检查子查询是否返回NULL | 使用NOT EXISTS |
| 过度嵌套 | 查询结构复杂 | 扁平化查询 |
| 标量子查询 | 多次执行相同子查询 | 使用变量存储结果 |

---

*参考来源：MySQL官方文档、阿里巴巴Java开发手册*

---