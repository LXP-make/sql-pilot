# MySQL索引详解

来源: https://dev.mysql.com/doc/refman/8.0/en/mysql-indexes.html

---

## 一、索引概述

索引是用于加速数据检索的数据结构。MySQL使用B+树作为默认索引结构。

### 1.1 索引的优点

- 加速数据检索
- 减少I/O操作
- 加速排序和分组
- 唯一性约束

### 1.2 索引的代价

- 占用磁盘空间
- 增加写操作成本（INSERT/UPDATE/DELETE）
- 降低批量导入性能

## 二、索引类型

### 2.1 B+树索引（默认）

适用于所有存储引擎（InnoDB、MyISAM等）。

```sql
CREATE INDEX idx_name ON users(name);
```

### 2.2 HASH索引

仅MEMORY存储引擎支持。

```sql
CREATE TABLE users (
    id INT,
    name VARCHAR(50),
    INDEX idx_name USING HASH (name)
) ENGINE=MEMORY;
```

### 2.3 空间索引（R-Tree）

用于地理空间数据类型。

```sql
CREATE TABLE locations (
    id INT,
    position POINT,
    SPATIAL INDEX pos_idx (position)
) ENGINE=MyISAM;
```

### 2.4 全文索引

用于文本搜索。

```sql
ALTER TABLE articles ADD FULLTEXT INDEX ft_title_content(title, content);
SELECT * FROM articles WHERE MATCH(title, content) AGAINST('MySQL');
```

## 三、复合索引

### 3.1 复合索引结构

复合索引是包含多个列的索引，遵循最左前缀原则。

```sql
CREATE INDEX idx_user_status ON users(user_id, status, create_time);
```

### 3.2 最左前缀原则

索引`INDEX(a, b, c)`可用于：
- `WHERE a = 1`
- `WHERE a = 1 AND b = 2`
- `WHERE a = 1 AND b = 2 AND c = 3`

索引`INDEX(a, b, c)`不可用于：
- `WHERE b = 2`
- `WHERE c = 3`
- `WHERE b = 2 AND c = 3`

### 3.3 列顺序选择

将区分度高的列放在前面：

```sql
-- user_id区分度高，放前面
CREATE INDEX idx_user_status ON users(user_id, status);

-- 查询：WHERE user_id = 1 AND status = 2
```

## 四、覆盖索引

### 4.1 什么是覆盖索引

查询的所有列都包含在索引中，无需回表。

```sql
-- 创建覆盖索引
CREATE INDEX idx_name_email ON users(name, email);

-- 查询可以直接使用索引
SELECT name, email FROM users WHERE name = 'John';
-- Extra: Using index（覆盖索引）
```

### 4.2 覆盖索引优势

- 减少数据访问次数
- 避免回表查询
- 减少I/O操作

## 五、索引使用规则

### 5.1 适用于索引的条件

```sql
-- 等值比较
WHERE name = 'John'
WHERE id IN (1, 2, 3)

-- 范围查询
WHERE age > 18
WHERE create_time BETWEEN '2024-01-01' AND '2024-12-31'

-- 前缀匹配
WHERE name LIKE 'John%'

-- 排序
ORDER BY create_time
```

### 5.2 不适用于索引的条件

```sql
-- 函数操作
WHERE YEAR(create_time) = 2024

-- 前置通配符
WHERE name LIKE '%John'

-- 类型转换
WHERE id = '123'  -- id是INT类型

-- OR条件无索引列
WHERE name = 'John' OR email = 'john@example.com'
```

## 六、索引优化策略

### 6.1 选择性优化

选择性和区分度高的列创建索引：

```sql
-- 计算列的选择性
SELECT COUNT(DISTINCT column_name) / COUNT(*) FROM table_name;

-- 性别列选择性低，不适合建索引
-- 用户ID列选择性强，适合建索引
```

### 6.2 前缀索引

对于VARCHAR类型的长字段，使用前缀索引：

```sql
-- 创建10字符前缀索引
CREATE INDEX idx_email ON users(email(10));
```

### 6.3 多列索引 vs 单列索引

```sql
-- 多列索引（推荐用于组合查询）
CREATE INDEX idx_status_time ON orders(status, create_time);
SELECT * FROM orders WHERE status = 1 AND create_time > '2024-01-01';

-- 多个单列索引（OR查询时可能更优）
CREATE INDEX idx_status ON orders(status);
CREATE INDEX idx_time ON orders(create_time);
```

## 七、索引维护

### 7.1 查看索引

```sql
SHOW INDEX FROM users;
SHOW INDEX FROM orders\G
```

### 7.2 删除索引

```sql
DROP INDEX idx_name ON users;
ALTER TABLE users DROP INDEX idx_name;
```

### 7.3 重建索引

```sql
OPTIMIZE TABLE users;  -- 重建表和索引
```

### 7.4 查找未使用的索引

```sql
SELECT * FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL 
AND count_star = 0;
```

## 八、索引设计原则

1. **独立列**：避免在列上使用函数或表达式
2. **前缀索引**：长字符串列使用前缀索引
3. **覆盖索引**：尽量让查询使用覆盖索引
4. **控制数量**：单表索引不超过5个
5. **遵循最左前缀**：复合索引要遵循最左前缀原则
6. **区分度优先**：区分度高的列放在复合索引前面

## 九、常见问题

### 9.1 索引失效原因

1. 对索引列使用函数
2. 隐式类型转换
3. OR条件中包含无索引列
4. 不遵循最左前缀原则
5. 使用LIKE前置通配符

### 9.2 索引与外键

```sql
-- 外键列应建立索引
ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users(id);
CREATE INDEX idx_user_id ON orders(user_id);
```

来源：MySQL 8.0 Reference Manual