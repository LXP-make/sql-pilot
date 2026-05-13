import requests
from bs4 import BeautifulSoup
import os
import time
import re

class MySQLDocSpider:
    def __init__(self):
        self.base_url = "https://dev.mysql.com/doc/refman/8.0/en/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def fetch_page(self, url):
        """获取页面内容"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def parse_html_to_markdown(self, html_content, title):
        """将HTML内容转换为Markdown格式"""
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        markdown_content = []
        markdown_content.append(f"# {title}\n")
        markdown_content.append(f"来源: {self.base_url}\n")
        markdown_content.append("---\n")
        
        main_content = soup.find('section', class_='section') or soup.find('div', class_='section')
        if not main_content:
            main_content = soup.find('body')
            
        if main_content:
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'pre', 'ul', 'ol', 'table', 'div']):
                if element.name in ['h1', 'h2', 'h3', 'h4']:
                    level = element.name
                    text = element.get_text(strip=True)
                    if text:
                        prefix = '#' * (int(level[1]) + 1)
                        markdown_content.append(f"\n{prefix} {text}\n")
                        
                elif element.name == 'p':
                    text = element.get_text(strip=True)
                    if text:
                        code_in_p = element.find('code')
                        if code_in_p:
                            text = text.replace(code_in_p.get_text(), f'`{code_in_p.get_text()}`')
                        markdown_content.append(f"{text}\n")
                        
                elif element.name == 'pre':
                    code = element.get_text(strip=True)
                    if code:
                        lang = ''
                        if element.find_parent('div', class_='highlight-sql'):
                            lang = 'sql'
                        markdown_content.append(f"\n```{lang}\n{code}\n```\n")
                        
                elif element.name == 'ul' or element.name == 'ol':
                    for li in element.find_all('li', recursive=False):
                        text = li.get_text(strip=True)
                        if text:
                            markdown_content.append(f"- {text}\n")
                            
                elif element.name == 'table':
                    rows = element.find_all('tr')
                    if rows:
                        markdown_content.append("\n")
                        for tr in rows:
                            cols = tr.find_all(['th', 'td'])
                            row_data = []
                            for col in cols:
                                cell_text = col.get_text(strip=True).replace('|', '\\|')
                                row_data.append(cell_text)
                            markdown_content.append(f"| {' | '.join(row_data)} |\n")
                        markdown_content.append("\n")
        
        return ''.join(markdown_content)
    
    def save_markdown(self, content, filepath):
        """保存Markdown文件"""
        if content:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved: {filepath}")
            return True
        return False
    
    def crawl_mysql_docs(self):
        """爬取MySQL官方文档"""
        docs = {
            'explain.md': 'EXPLAIN Statement',
            'indexes.md': 'MySQL Indexes',
            'limit-optimization.md': 'LIMIT Query Optimization',
            'join.md': 'JOIN Optimization',
            'optimization.md': 'Query Optimization Overview'
        }
        
        for filename, title in docs.items():
            url = f"{self.base_url}{filename}"
            print(f"\nFetching: {url}")
            
            html = self.fetch_page(url)
            if html:
                markdown = self.parse_html_to_markdown(html, title)
                filepath = f"knowledge/mysql/{filename}"
                self.save_markdown(markdown, filepath)
            
            time.sleep(1)
    
    def crawl_blog_content(self):
        """抓取技术博客内容（手动整理版）"""
        blog_content = {
            'slow_sql.md': {
                'title': '慢SQL优化最佳实践',
                'content': '''# 慢SQL优化最佳实践

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
'''
            },
            'filesort.md': {
                'title': 'Filesort详解与优化',
                'content': '''# Filesort详解与优化

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
-- Sort_scan: 200        -- 全表扫描排序次数
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
'''
            },
            'index_fail.md': {
                'title': '索引失效场景详解',
                'content': '''# 索引失效场景详解

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
'''
            }
        }
        
        for filename, data in blog_content.items():
            filepath = f"knowledge/blogs/{filename}"
            content = f"# {data['title']}\n\n{data['content']}"
            self.save_markdown(content, filepath)
        
        return True

def main():
    spider = MySQLDocSpider()
    
    print("=" * 50)
    print("Starting MySQL Documentation Crawler")
    print("=" * 50)
    
    os.makedirs("knowledge/mysql", exist_ok=True)
    os.makedirs("knowledge/blogs", exist_ok=True)
    
    print("\n[1/2] Crawling MySQL official documentation...")
    spider.crawl_mysql_docs()
    
    print("\n[2/2] Creating blog content...")
    spider.crawl_blog_content()
    
    print("\n" + "=" * 50)
    print("Crawling completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()