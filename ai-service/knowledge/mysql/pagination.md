# MySQL分页查询优化

来源: https://dev.mysql.com/doc/refman/8.0/en/limit-optimization.html

---

## 一、LIMIT分页问题

### 1.1 深分页性能问题

当OFFSET值很大时，MySQL必须扫描并丢弃前面大量的行。

```sql
-- 深分页问题
SELECT * FROM orders ORDER BY id LIMIT 1000000, 10;

-- 问题：
-- 1. MySQL必须扫描前1000010行
-- 2. 只返回最后10行
-- 3. 随着OFFSET增大，性能急剧下降
```

### 1.2 性能对比

| 查询 | 预计扫描行数 | 执行时间 |
|------|-------------|---------|
| LIMIT 0, 10 | 10 | 0.001s |
| LIMIT 10000, 10 | 10010 | 0.05s |
| LIMIT 100000, 10 | 100010 | 0.5s |
| LIMIT 1000000, 10 | 1000010 | 5s+ |

## 二、解决方案

### 2.1 方案一：游标分页（推荐）

使用上一页的最后一条记录的ID作为起点：

```sql
-- 第一页
SELECT * FROM orders ORDER BY id LIMIT 10;

-- 第二页（已知上一页最后ID为100）
SELECT * FROM orders WHERE id > 100 ORDER BY id LIMIT 10;

-- 第三页（已知上一页最后ID为200）
SELECT * FROM orders WHERE id > 200 ORDER BY id LIMIT 10;
```

**前提条件**：
- 必须有单调递增的主键或唯一索引
- 不支持跳页
- 需要前端保存上一页的最后一条记录ID

### 2.2 方案二：延迟关联（Deferred Join）

先查询ID，再关联获取完整数据：

```sql
-- 原始深分页（慢）
SELECT * FROM orders ORDER BY create_time DESC LIMIT 1000000, 10;

-- 优化：延迟关联
SELECT * FROM orders o
INNER JOIN (
    SELECT id FROM orders
    ORDER BY create_time DESC
    LIMIT 1000000, 10
) t ON o.id = t.id;
```

**原理**：
- 子查询只查询ID，覆盖索引即可满足
- 避免回表扫描大量数据
- 性能提升显著

### 2.3 方案三：条件过滤 + LIMIT

在WHERE中添加过滤条件：

```sql
-- 原始分页
SELECT * FROM orders LIMIT 1000000, 10;

-- 优化：添加有效过滤条件
SELECT * FROM orders
WHERE create_time >= '2024-01-01'
ORDER BY create_time DESC
LIMIT 10;
```

### 2.4 方案四：记录总数估算

不查询总数，使用估算：

```sql
-- 获取近似总数（快）
SELECT TABLE_ROWS FROM information_schema.tables
WHERE TABLE_SCHEMA = 'db_name' AND TABLE_NAME = 'orders';

-- 使用ID范围分页
SELECT * FROM orders WHERE id BETWEEN 1000000 AND 1000010;
```

### 2.5 方案五：分段查询

使用BETWEEN进行分段：

```sql
-- 分段1
SELECT * FROM orders WHERE id BETWEEN 1 AND 1000;

-- 分段2
SELECT * FROM orders WHERE id BETWEEN 1001 AND 2000;

-- 分段3
SELECT * FROM orders WHERE id BETWEEN 2001 AND 3000;
```

## 三、Java实现示例

### 3.1 游标分页实现

```java
// 实体类
public class Order {
    private Long id;
    private String orderNo;
    private LocalDateTime createTime;
}

// 游标分页查询
public List<Order> selectOrdersCursor(Long lastId, int pageSize) {
    String sql = "SELECT * FROM orders WHERE id > ? ORDER BY id LIMIT ?";
    return jdbcTemplate.query(sql, (rs, rowNum) -> {
        Order order = new Order();
        order.setId(rs.getLong("id"));
        order.setOrderNo(rs.getString("order_no"));
        order.setCreateTime(rs.getTimestamp("create_time").toLocalDateTime());
        return order;
    }, lastId, pageSize);
}
```

### 3.2 延迟关联实现

```java
public List<Order> selectOrdersDeferredJoin(int offset, int limit) {
    String sql = "SELECT o.* FROM orders o " +
                 "INNER JOIN (SELECT id FROM orders " +
                 "ORDER BY create_time DESC LIMIT ?, ?) t ON o.id = t.id " +
                 "ORDER BY o.create_time DESC";
    return jdbcTemplate.query(sql, offset, limit, (rs, rowNum) -> {
        Order order = new Order();
        order.setId(rs.getLong("id"));
        order.setOrderNo(rs.getString("order_no"));
        order.setCreateTime(rs.getTimestamp("create_time").toLocalDateTime());
        return order;
    });
}
```

## 四、性能测试对比

### 4.1 测试环境

- MySQL 8.0
- orders表：1000万条数据
- 测试机：8核CPU，16GB内存

### 4.2 测试结果

| 分页方式 | 偏移量100万 | 偏移量500万 |
|---------|-----------|------------|
| 原始LIMIT | 5.2s | 25.8s |
| 游标分页 | 0.01s | 0.01s |
| 延迟关联 | 0.8s | 0.9s |

### 4.3 优化建议

1. **优先使用游标分页**：性能最优
2. **使用延迟关联**：当无法使用游标分页时
3. **避免深分页**：限制最大OFFSET值
4. **使用覆盖索引**：确保分页查询使用索引

## 五、总结

### 5.1 优化策略对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| 游标分页 | 性能最优 | 不支持跳页 | 有单调递增ID |
| 延迟关联 | 支持跳页 | 需改写SQL | 复杂排序分页 |
| 条件过滤 | 实现简单 | 场景有限 | 有过滤条件 |
| 估算总数 | 快速 | 不精确 | 无需精确总数 |

### 5.2 最佳实践

1. **避免深分页**：使用游标分页替代OFFSET分页
2. **使用覆盖索引**：减少回表查询
3. **限制最大页数**：禁止查询过深的分页
4. **使用延迟关联**：处理复杂排序分页
5. **预计算热点数据**：缓存热门分页数据

来源：MySQL 8.0 Reference Manual 及美团技术团队实践