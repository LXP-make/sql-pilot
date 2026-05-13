# MySQL复杂查询优化指南

## 一、复杂查询特征识别

### 1.1 多表JOIN查询

**定义**：涉及3个及以上表的JOIN操作

**示例**：
```sql
SELECT 
    u.name,
    o.order_no,
    p.product_name,
    c.category_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
WHERE u.age > 18
  AND o.create_time >= '2024-01-01';
```

**性能问题**：
- JOIN顺序影响性能
- 缺少索引导致全表扫描
- 数据量大时笛卡尔积爆炸

**优化建议**：
- 确保所有JOIN列有索引
- 控制JOIN表数量（建议不超过5表）
- 使用小表驱动大表

### 1.2 嵌套子查询

**定义**：子查询嵌套在其他子查询中

**示例**：
```sql
SELECT * FROM (
    SELECT 
        user_id,
        COUNT(*) as order_count
    FROM (
        SELECT * FROM orders WHERE status = 1
    ) AS valid_orders
    GROUP BY user_id
    HAVING COUNT(*) > 5
) AS active_users;
```

**优化建议**：
- 使用WITH子句简化
- 考虑使用临时表
- 扁平化查询结构

### 1.3 复杂条件组合

**定义**：包含多个AND/OR条件、子查询、函数操作的查询

**示例**：
```sql
SELECT * FROM orders
WHERE status = 1
  AND create_time >= '2024-01-01'
  AND total_amount > (SELECT AVG(total_amount) FROM orders)
  AND (user_id IN (SELECT id FROM vip_users) OR discount > 0);
```

## 二、复杂查询优化策略

### 2.1 索引优化

**确保JOIN列有索引**：
```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_products_category_id ON products(category_id);
```

**创建复合索引**：
```sql
CREATE INDEX idx_orders_status_create_time ON orders(status, create_time);
```

### 2.2 JOIN顺序优化

**原则**：小表驱动大表

**手动指定JOIN顺序**（如果优化器选择不佳）：
```sql
SELECT STRAIGHT_JOIN
    u.name, o.order_no
FROM small_table s
JOIN large_table l ON s.id = l.small_id;
```

### 2.3 使用WITH子句

**原查询**：
```sql
SELECT * FROM (
    SELECT user_id, COUNT(*) as cnt FROM orders GROUP BY user_id
) AS t1
WHERE cnt > 10;
```

**优化后**：
```sql
WITH order_counts AS (
    SELECT user_id, COUNT(*) as cnt 
    FROM orders 
    GROUP BY user_id
)
SELECT * FROM order_counts WHERE cnt > 10;
```

**优势**：
- 提高可读性
- 优化器可以更好地处理

### 2.4 拆分复杂查询

**场景**：一个查询做太多事情

**原查询**：
```sql
SELECT 
    user_id,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count,
    (SELECT SUM(amount) FROM payments p WHERE p.user_id = u.id) as total_paid,
    (SELECT COUNT(*) FROM reviews r WHERE r.user_id = u.id) as review_count
FROM users u;
```

**优化后**：
```sql
-- 分别查询然后合并
SELECT u.id, u.name, COALESCE(o.cnt, 0) as order_count
FROM users u
LEFT JOIN (SELECT user_id, COUNT(*) as cnt FROM orders GROUP BY user_id) o 
    ON u.id = o.user_id;
```

### 2.5 使用临时表或物化视图

**场景**：复杂计算需要多次使用

```sql
CREATE TEMPORARY TABLE monthly_stats AS
SELECT 
    DATE_FORMAT(create_time, '%Y-%m') as month,
    COUNT(*) as order_count,
    SUM(total_amount) as total_sales
FROM orders
WHERE create_time >= '2024-01-01'
GROUP BY DATE_FORMAT(create_time, '%Y-%m');

-- 多次使用临时表
SELECT * FROM monthly_stats WHERE month = '2024-01';
SELECT SUM(order_count) FROM monthly_stats;
```

## 三、复杂查询性能检测

### 3.1 使用EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT 
    u.name, COUNT(o.id) as order_count
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

**关注指标**：
- type: 访问类型（ALL表示全表扫描）
- key: 使用的索引
- rows: 扫描行数
- Extra: Using filesort, Using temporary等

### 3.2 识别性能瓶颈

**常见问题**：
1. **ALL**：全表扫描
2. **Using filesort**：文件排序
3. **Using temporary**：临时表
4. **Range checked for each record**：逐行范围检查

### 3.3 检测JOIN顺序问题

```sql
EXPLAIN FORMAT=JSON
SELECT * FROM a JOIN b JOIN c ON ...;
```

**查看JSON输出中的join_execution字段**

## 四、案例分析

### 案例1：多表JOIN优化

**问题查询**：
```sql
SELECT 
    u.name, o.order_no, p.product_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.status = 1;
```

**问题**：缺少索引，全表扫描

**优化后**：
```sql
-- 添加索引
CREATE INDEX idx_orders_user_id_status ON orders(user_id, status);
CREATE INDEX idx_order_items_order_id_product_id ON order_items(order_id, product_id);

SELECT 
    u.name, o.order_no, p.product_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.status = 1;
```

**性能提升**：从全表扫描变为索引扫描

### 案例2：嵌套子查询优化

**问题查询**：
```sql
SELECT * FROM (
    SELECT * FROM (
        SELECT * FROM orders WHERE status = 1
    ) AS t1
    WHERE total_amount > 100
) AS t2
ORDER BY create_time DESC;
```

**优化后**：
```sql
SELECT * FROM orders 
WHERE status = 1 AND total_amount > 100
ORDER BY create_time DESC;
```

**性能提升**：简化查询结构

### 案例3：复杂条件优化

**问题查询**：
```sql
SELECT * FROM orders
WHERE status = 1
  AND YEAR(create_time) = 2024
  AND (user_id IN (1, 2, 3) OR discount > 0);
```

**优化后**：
```sql
SELECT * FROM orders
WHERE status = 1
  AND create_time >= '2024-01-01' 
  AND create_time < '2025-01-01'
  AND (user_id IN (1, 2, 3) OR discount > 0);
```

**性能提升**：避免函数操作索引列

## 五、最佳实践总结

| 优化策略 | 适用场景 | 预期收益 |
|---------|---------|---------|
| 添加索引 | JOIN列、WHERE条件列 | 显著提升 |
| 控制JOIN数量 | 多表查询 | 复杂度降低 |
| 使用WITH子句 | 嵌套子查询 | 可读性提升 |
| 拆分查询 | 一个查询多任务 | 可维护性提升 |
| 使用临时表 | 重复计算 | 性能提升 |

---

*参考来源：MySQL官方文档、美团技术团队博客*

---