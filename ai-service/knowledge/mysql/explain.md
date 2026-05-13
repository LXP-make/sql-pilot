# MySQL EXPLAIN执行计划详解

来源: https://dev.mysql.com/doc/refman/8.0/en/explain.html

---

## 一、EXPLAIN概述

EXPLAIN语句用于获取MySQL如何执行SELECT、TABLE、DELETE、INSERT、REPLACE、UPDATE语句的执行计划信息。

### 1.1 基本语法

```sql
EXPLAIN [explain_type] {explainable_stmt | FOR CONNECTION connection_id}

explain_type: {
    FORMAT = format_name
}

format_name: {
    TRADITIONAL
  | JSON
  | TREE
}

explainable_stmt: {
    SELECT statement
  | TABLE statement
  | DELETE statement
  | INSERT statement
  | REPLACE statement
  | UPDATE statement
}
```

## 二、EXPLAIN输出字段详解

### 2.1 id列

查询编号，标识每个SELECT或操作所在的层级。

| id值 | 含义 |
|------|------|
| 1 | 最外层SELECT |
| 2 | 子查询中的SELECT |
| 3 | 联合查询中的第二个SELECT |

### 2.2 select_type列

查询类型，区分简单查询和复杂查询。

| select_type值 | 含义 |
|---------------|------|
| SIMPLE | 简单SELECT，不使用UNION或子查询 |
| PRIMARY | 最外层SELECT |
| UNION | UNION中的第二个或后面的SELECT |
| DEPENDENT UNION | UNION中的第二个或后面的SELECT，依赖于外部查询 |
| SUBQUERY | 子查询中的第一个SELECT |
| DEPENDENT SUBQUERY | 子查询中的第一个SELECT，依赖于外部查询 |
| DERIVED | 派生表（FROM子句中的子查询） |
| MATERIALIZED | 物化子查询 |
| UNCACHEABLE SUBQUERY | 结果不能被缓存的子查询 |
| UNCACHEABLE UNION | 属于不可缓存子查询的UNION |

### 2.3 type列（重要）

表连接类型，从优到差排序：

| type值 | 含义 | 性能 |
|--------|------|------|
| system | 表只有一行（系统表） | 最好 |
| const | 通过索引一次命中 | 很好 |
| eq_ref | 唯一索引扫描 | 好 |
| ref | 非唯一索引扫描 | 一般 |
| ref_or_null | 类似于ref，但包含NULL查询 | 一般 |
| index_merge | 索引合并 | 较好 |
| unique_subquery | 子查询返回唯一值 | 较好 |
| index_subquery | 子查询返回非唯一值 | 一般 |
| range | 索引范围扫描 | 一般 |
| index | 全索引扫描 | 较差 |
| ALL | 全表扫描 | 最差 |

**最佳实践**：确保查询至少达到range级别，避免ALL。

### 2.4 possible_keys列

MySQL可能使用的索引列表（仅供参考）。

### 2.5 key列（重要）

实际使用的索引。如果为NULL，表示未使用索引。

### 2.6 key_len列

实际使用的索引长度。可用于判断复合索引使用了多少列。

### 2.7 ref列

与索引比较的列或常量。

### 2.8 rows列（重要）

MySQL估计需要检查的行数。数值越小越好。

### 2.9 filtered列

按条件过滤后，保留的行的百分比（0-100）。

### 2.10 Extra列（非常重要）

包含额外的优化信息。

| Extra值 | 含义 | 说明 |
|---------|------|------|
| Using index | 使用覆盖索引 | 性能好 |
| Using index condition | 使用索引条件 | 性能较好 |
| Using where | 使用WHERE过滤 | 正常 |
| Using temporary | 使用临时表 | 性能差 |
| Using filesort | 使用文件排序 | 性能差 |
| Using join buffer | 使用连接缓存 | 性能差 |
| Nested loop | 嵌套循环连接 | 正常 |
| Batched key access | 批量键访问 | 性能好 |
| Memory bypass | 内存旁路 | 特殊优化 |

## 三、JSON格式输出

```sql
EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE id = 1\G
```

JSON格式包含更详细的信息，如成本估算、访问条件等。

## 四、TREE格式输出（MySQL 8.0.16+）

```sql
EXPLAIN FORMAT=TREE SELECT * FROM orders WHERE id = 1
```

树状格式更直观地展示查询执行逻辑。

## 五、EXPLAIN ANALYZE（MySQL 8.0.21+）

EXPLAIN ANALYZE会实际执行查询并返回统计分析：

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE id = 1
```

输出包含：
- 实际执行时间
- 每步实际返回的行数
- 迭代器成本估算

## 六、实战案例

### 6.1 案例一：全表扫描

```sql
EXPLAIN SELECT * FROM users WHERE age > 18;
```

输出：
- type: ALL（全表扫描）
- rows: 1000000（扫描大量行）
- Extra: Using where

优化：添加索引
```sql
CREATE INDEX idx_age ON users(age);
```

### 6.2 案例二：使用索引

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;
```

输出：
- type: const（常量查找）
- key: PRIMARY（使用主键索引）
- rows: 1（只检查1行）

### 6.3 案例三：文件排序

```sql
EXPLAIN SELECT * FROM users ORDER BY create_time DESC;
```

输出：
- type: ALL
- Extra: Using filesort（性能差）

优化：添加索引
```sql
CREATE INDEX idx_create_time ON users(create_time);
```

## 七、最佳实践

1. **定期使用EXPLAIN检查慢查询**
2. **确保type不是ALL（全表扫描）**
3. **确保key不为NULL（使用了索引）**
4. **关注Extra列，避免Using filesort和Using temporary**
5. **rows值越小越好**
6. **优先使用覆盖索引（Using index）**

来源：MySQL 8.0 Reference Manual