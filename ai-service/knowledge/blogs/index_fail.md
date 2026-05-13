# 索引失效场景详解

---

## 一、索引失效概述

索引是提升数据库查询性能的重要手段，但并不是所有情况都能使用索引。了解索引失效的场景，可以帮助我们编写更高效的SQL。

### 1.1 索引失效的常见原因

1. **对索引列使用函数或表达式**
2. **隐式类型转换**
3. **使用LIKE前置通配符**
4. **OR条件中包含无索引列**
5. **复合索引不遵循最左前缀原则**
6. **使用IS NOT NULL或IS NULL时**

## 二、详细场景分析

### 2.1 场景一：对索引列使用函数

**错误示例**：
```sql
-- 在索引列上使用函数，索引失效
SELECT * FROM users WHERE YEAR(create_time) = 2024;
SELECT * FROM users WHERE DATE(create_time) = '2024-01-01';
SELECT * FROM users WHERE MONTH(create_time) = 6;
SELECT * FROM users WHERE LEFT(name, 3) = 'Tom';
```

**正确示例**：
```sql
-- 使用范围查询保持索引有效
SELECT * FROM users
WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01';
SELECT * FROM users WHERE name LIKE 'Tom%';
```

### 2.2 场景二：隐式类型转换

**错误示例**：
```sql
-- id是INT类型，但传入了字符串
SELECT * FROM users WHERE id = '12345';

-- phone是VARCHAR类型，但传入了数字
SELECT * FROM users WHERE phone = 13800138000;
```

**正确示例**：
```sql
-- 类型保持一致
SELECT * FROM users WHERE id = 12345;
SELECT * FROM users WHERE phone = '13800138000';
```

### 2.3 场景三：LIKE前置通配符

**错误示例**：
```sql
-- 前置%导致索引失效
SELECT * FROM users WHERE name LIKE '%om';
SELECT * FROM users WHERE name LIKE '%Tom%';
```

**正确示例**：
```sql
-- 使用后置通配符，索引有效
SELECT * FROM users WHERE name LIKE 'Tom%';

-- 如果必须使用前置通配符，考虑使用全文索引
ALTER TABLE users ADD FULLTEXT INDEX ft_name(name);
SELECT * FROM users WHERE MATCH(name) AGAINST('Tom');
```

### 2.4 场景四：OR条件使用不当

**错误示例**：
```sql
-- status列有索引，name列无索引，导致全表扫描
SELECT * FROM users WHERE status = 1 OR name = 'Tom';
```

**正确示例**：
```sql
-- 方案1：使用UNION ALL
SELECT * FROM users WHERE status = 1
UNION ALL
SELECT * FROM users WHERE name = 'Tom';

-- 方案2：为name列创建索引
CREATE INDEX idx_name ON users(name);
```

### 2.5 场景五：复合索引不遵循最左前缀

**错误示例**：
```sql
-- 复合索引 INDEX(a, b, c)
-- 以下查询无法使用索引
SELECT * FROM users WHERE b = 2;
SELECT * FROM users WHERE c = 3;
SELECT * FROM users WHERE b = 2 AND c = 3;
```

**正确示例**：
```sql
-- 遵循最左前缀原则
SELECT * FROM users WHERE a = 1;
SELECT * FROM users WHERE a = 1 AND b = 2;
SELECT * FROM users WHERE a = 1 AND b = 2 AND c = 3;

-- WHERE条件的顺序不影响，但必须包含最左列
SELECT * FROM users WHERE a = 1 AND c = 3;  -- 只能使用索引的a列
```

### 2.6 场景六：使用IS NOT NULL

**错误示例**：
```sql
-- 使用IS NOT NULL可能导致索引失效
SELECT * FROM users WHERE email IS NOT NULL;
```

**正确示例**：
```sql
-- 尽量使用IS NULL或BETWEEN
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE email >= '' AND email < '~';

-- 或者为必填字段设置NOT NULL约束
ALTER TABLE users MODIFY email VARCHAR(255) NOT NULL;
```

## 三、特殊情况

### 3.1 使用索引但范围过大

```sql
-- 假设有索引 INDEX(create_time)
-- 使用常量值比使用范围更好
SELECT * FROM users WHERE create_time > '1970-01-01';  -- 可能不使用索引

-- 优化：使用具体范围
SELECT * FROM users
WHERE create_time >= '2020-01-01' AND create_time < '2025-01-01';
```

### 3.2 查询优化器决定不使用索引

MySQL查询优化器会根据统计信息判断是否使用索引：

```sql
-- 当返回数据量超过一定比例时，可能选择全表扫描
SELECT * FROM users WHERE status = 1;  -- 如果status=1的数据超过30%，可能不用索引

-- 强制使用索引（不推荐，可能适得其反）
SELECT * FROM users USE INDEX(idx_status) WHERE status = 1;
```

## 四、索引失效诊断

### 4.1 使用EXPLAIN分析

```sql
EXPLAIN SELECT * FROM users WHERE YEAR(create_time) = 2024;

-- 观察输出：
-- type: ALL (全表扫描)
-- key: NULL (未使用索引)
-- Extra: Using where
```

### 4.2 使用Optimizer Trace

```sql
-- 开启optimizer trace
SET optimizer_trace = 'enabled=on';
SET optimizer_trace_max_mem_size = 1048576;

-- 执行查询
SELECT * FROM users WHERE YEAR(create_time) = 2024;

-- 查看trace结果
SELECT * FROM information_schema.optimizer_trace;
```

## 五、预防措施

### 5.1 编写SQL规范

1. **避免在索引列上使用函数**
2. **保持类型一致**
3. **使用后置通配符**
4. **OR条件确保都有索引**
5. **遵循最左前缀原则**

### 5.2 创建合适的索引

```sql
-- 根据查询创建索引
CREATE INDEX idx_email_status ON users(email, status);
CREATE INDEX idx_create_time_status ON users(create_time, status);
```

## 六、总结

1. **函数和表达式**：避免在索引列上使用
2. **类型转换**：保持比较类型一致
3. **LIKE查询**：优先使用后置通配符
4. **OR条件**：确保所有列都有索引
5. **复合索引**：遵循最左前缀原则
6. **查询优化器**：理解其选择逻辑

来源：MySQL官方文档及京东技术团队实践