# Filesort详解与优化

---

## 一、什么是Filesort

Filesort是MySQL在无法利用索引的有序性进行排序时，采用的一种外部排序算法。虽然名字中包含"file"，但Filesort并不一定使用文件进行排序，当排序数据量较小时，MySQL会在内存中完成排序（使用sort_buffer）。

### 1.1 Filesort触发条件

```sql
-- 查看SQL是否使用了Filesort
EXPLAIN SELECT * FROM users ORDER BY create_time DESC;
-- Extra列显示：Using filesort
```

### 1.2 触发Filesort的情况

1. **ORDER BY列没有索引**
2. **ORDER BY的列与WHERE条件不匹配索引最左前缀**
3. **同时有ORDER BY和GROUP BY，但列不同**
4. **ORDER BY中使用了表达式或函数**

## 二、Filesort实现机制

### 2.1 两种排序算法

#### 1. 两次扫描算法（Two-pass）
- 第一次扫描：读取行指针和排序列，排序后写入临时文件
- 第二次扫描：根据排序结果读取完整行数据
- 内存使用：sort_buffer_size

#### 2. 一次扫描算法（Single-pass）
- 一次读取所有需要的列（排序列+SELECT所需的列）
- 直接在内存中完成排序
- MySQL 4.1之后默认使用此算法

### 2.2 sort_buffer_size参数

```sql
-- 查看sort_buffer_size大小
SHOW VARIABLES LIKE 'sort_buffer_size';

-- 设置sort_buffer_size（建议256KB-2MB）
SET GLOBAL sort_buffer_size = 262144;  -- 256KB
```

## 三、Filesort优化策略

### 3.1 策略一：为ORDER BY列创建索引

```sql
-- 创建合适的索引
CREATE INDEX idx_create_time ON users(create_time DESC);

-- 现在查询将使用索引排序，不再需要Filesort
SELECT * FROM users ORDER BY create_time DESC LIMIT 10;
-- Extra列显示：Using index condition
```

### 3.2 策略二：优化排序字段顺序

确保ORDER BY与索引顺序一致：

```sql
-- 假设索引为 INDEX idx_a_b_c(a, b, c)
-- 有效使用索引的ORDER BY
ORDER BY a;              -- 使用索引a列
ORDER BY a, b;           -- 使用索引a,b列
ORDER BY a, b, c;       -- 使用索引a,b,c列

-- 无效使用索引的ORDER BY
ORDER BY b;              -- 跳跃a列，无法使用索引
ORDER BY c;              -- 跳跃a,b列，无法使用索引
ORDER BY b, c;           -- 跳跃a列，无法使用索引
```

### 3.3 策略三：覆盖索引优化Filesort

```sql
-- 创建覆盖索引避免回表
CREATE INDEX idx_create_time_covering ON users(create_time DESC, id, name, email);

-- 查询直接使用覆盖索引，无需Filesort
SELECT id, name, email FROM users ORDER BY create_time DESC LIMIT 10;
```

### 3.4 策略四：减少排序数据量

```sql
-- 添加WHERE条件减少排序数据量
SELECT * FROM orders WHERE status = 'completed' ORDER BY create_time DESC;

-- 添加LIMIT限制排序范围
SELECT * FROM orders ORDER BY create_time DESC LIMIT 100;
```

## 四、实战案例

### 4.1 案例一：优化多字段排序

**问题SQL**：
```sql
SELECT * FROM orders
WHERE status = 1
ORDER BY create_time DESC, order_id DESC
LIMIT 100;
```

**优化方案**：
```sql
-- 创建复合索引
CREATE INDEX idx_status_time_id ON orders(status, create_time DESC, order_id DESC);

-- 验证优化效果
EXPLAIN SELECT * FROM orders
WHERE status = 1
ORDER BY create_time DESC, order_id DESC
LIMIT 100;
-- type: range
-- key: idx_status_time_id
-- Extra: Using index condition
```

### 4.2 案例二：优化随机排序

**问题SQL**：
```sql
SELECT * FROM products ORDER BY RAND() LIMIT 10;
```

**优化方案**：
```sql
-- 方案1：使用主键排序代替随机
SELECT * FROM products
WHERE id >= (SELECT FLOOR(RAND() * (SELECT MAX(id) FROM products)))
ORDER BY id LIMIT 10;

-- 方案2：应用层生成随机ID列表
SELECT * FROM products WHERE id IN (1, 5, 8, 23, 67);
```

## 五、Filesort监控

### 5.1 检查Filesort使用情况

```sql
-- 查看排序相关状态
SHOW GLOBAL STATUS LIKE 'Sort%';

-- 结果示例：
-- Sort_range: 1000    -- 索引范围内排序次数
-- Sort_merge_passes: 5 -- 归并排序次数（应接近0）
-- Sort_rows: 50000     -- 排序总行数
-- Sort_scan: 200      -- 全表扫描排序次数
```

### 5.2 慢查询日志中的Filesort

```sql
-- 在慢查询日志中查看是否使用Filesort
SHOW VARIABLES LIKE 'log_queries_not_using_indexes';
SET GLOBAL log_queries_not_using_indexes = 'ON';
```

## 六、总结

1. **优先使用索引排序**：确保ORDER BY与索引匹配
2. **使用覆盖索引**：减少回表和Filesort
3. **合理设置sort_buffer_size**：根据数据量调整
4. **监控排序性能**：关注Sort_merge_passes值
5. **避免随机排序**：使用确定性的排序方式

来源：MySQL官方文档及美团技术团队实践