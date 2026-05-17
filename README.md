# SQL Pilot - AI驱动的SQL性能优化助手

一个利用AI和RAG（检索增强生成）技术分析和优化SQL查询的综合性工具。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    SQL Pilot 项目                           │
├─────────────────────────────────────────────────────────────┤
│  sqlpilot-frontend/   # Vue.js 前端 (待开发)               │
│  sqlpilot-backend/    # Spring Boot 后端 (8081)            │
│  ai-service/          # FastAPI RAG 服务 (8080)            │
└─────────────────────────────────────────────────────────────┘
```

## 功能特性

- **SQL分析**: 分析SQL查询的性能问题
- **AI优化**: 基于RAG的SQL优化建议
- **自然语言转SQL**: 将自然语言转换为SQL查询
- **规则引擎**: 内置SQL规则检测（如 SELECT * 等）
- **记忆系统**: 对话历史管理和用户偏好设置
- **奖惩机制**: 用户反馈收集用于持续学习
- **混合检索**: 结合关键词和语义搜索的RAG

## 快速开始

### 1. 启动 Ollama（必需）

```bash
ollama run qwen2.5
```

### 2. 启动 AI 服务

```bash
cd ai-service
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

访问: http://localhost:8080/docs

### 3. 启动后端服务

```bash
cd sqlpilot-backend
mvn spring-boot:run
```

访问: http://localhost:8081/api/sql/analyze

## API 接口

### AI 服务（端口 8080）

| 接口 | 方法 | 描述 |
|------|------|------|
| `/ai/optimize` | POST | RAG SQL优化 |
| `/ai/natural-to-sql` | POST | 自然语言转SQL |
| `/health` | GET | 健康检查 |

### 后端服务（端口 8081）

#### SQL 分析
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/sql/analyze` | POST | SQL性能分析 |
| `/api/sql/optimize` | POST | SQL优化 |
| `/api/sql/natural-to-sql` | POST | 自然语言转SQL |

#### 记忆系统
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/memory/conversation` | POST | 添加对话记录 |
| `/api/memory/conversation/{userId}` | GET | 获取对话历史 |
| `/api/memory/context/{userId}` | GET | 获取AI上下文提示 |
| `/api/memory/preference` | POST | 更新用户偏好 |
| `/api/memory/feedback` | POST | 提交反馈（奖惩机制） |
| `/api/memory/profile/{userId}` | GET | 获取用户画像 |
| `/api/memory/summary/{userId}` | GET | 获取对话摘要 |
| `/api/memory/table-stats` | GET | 获取数据库表统计 |

## 技术栈

- **后端**: Spring Boot 4.0.x, MyBatis
- **AI服务**: FastAPI, ChromaDB, Ollama Embeddings
- **AI模型**: Ollama (Qwen2.5)
- **数据库**: MySQL（三个表：index_suggestion, optimization_suggestion, sql_analysis_history）
- **记忆系统**: 基于JDBC的数据持久化

## 项目结构

```
SQLPilot/
├── sqlpilot-backend/
│   ├── src/main/java/com/sqlpilot/backend/
│   │   ├── controller/    # REST API 控制器 (MemoryController, SqlController)
│   │   ├── service/       # 业务逻辑 (MemoryService, SqlAnalysisService)
│   │   ├── rule/          # SQL规则引擎
│   │   ├── dto/           # 数据传输对象
│   │   ├── entity/        # 数据库实体
│   │   ├── mapper/        # MyBatis 映射器
│   │   ├── config/        # 配置类
│   │   └── util/          # 工具类
│   └── src/main/resources/
│       ├── mapper/        # MyBatis XML
│       └── application.yml
├── ai-service/
│   ├── app.py             # FastAPI 应用
│   ├── rag_service.py     # RAG核心服务（含混合检索）
│   ├── knowledge/         # 知识库
│   └── chroma_db/         # 向量数据库
└── sqlpilot-frontend/     # Vue.js 前端 (待开发)
```

## 配置说明

### 数据库配置 (sqlpilot-backend/src/main/resources/application.yml)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/sqlpilot?serverTimezone=Asia/Shanghai
    username: root
    password: your_password
    driver-class-name: com.mysql.cj.jdbc.Driver
```

### AI 服务配置 (ai-service/app.py)

```python
# Ollama 配置
ollama_url = "http://127.0.0.1:11434/api/generate"
ollama_model = "qwen2.5:latest"
```

## 记忆系统设计

### 数据库表结构

记忆系统使用三个现有表进行数据持久化：

1. **sql_analysis_history**: 存储对话历史和SQL分析记录
2. **optimization_suggestion**: 存储用户反馈和奖惩记录
3. **index_suggestion**: 存储用户偏好和设置

### 奖惩机制

- **评分奖励**: 1-5分转换为奖励值 (-1.0 到 1.0)
- **评论奖励**: 详细评论额外奖励（超过10字符）
- **修正奖励**: 提供修正答案额外奖励（超过20字符）

## 许可证

MIT License
