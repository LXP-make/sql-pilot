# SQL Pilot

AI驱动的SQL性能优化助手，基于RAG技术和大厂SQL规范知识库，提供SQL分析、智能优化、自然语言转SQL等功能。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     SQL Pilot                                │
├─────────────────────────────────────────────────────────────┤
│  sqlpilot-frontend/     Vue 3 + Element Plus 前端            │
│  sqlpilot-backend/      Spring Boot 4.0 后端服务            │
│  ai-service/            FastAPI + ChromaDB RAG服务           │
└─────────────────────────────────────────────────────────────┘
```

## 功能特性

- **SQL 分析** — 解析SQL查询，使用JSqlParser检测SELECT *、隐式类型转换、索引失效等15+种性能问题
- **AI 优化** — 基于RAG检索大厂SQL规范知识库，通过Qwen2.5生成精准优化建议
- **自然语言转SQL** — 用中文描述查询需求，自动生成对应SQL语句
- **EXPLAIN 分析** — 解析执行计划，从type/rows/Extra多维度评分并定位性能瓶颈
- **对话记忆** — 记录分析历史，支持用户反馈评分，优化建议持续迭代

## 技术栈

| 模块 | 技术 |
|------|------|
| 后端 | Spring Boot 4.0, MyBatis, MySQL |
| AI服务 | FastAPI, ChromaDB, BAAI/bge-small-zh, Qwen2.5 |
| 前端 | Vue 3, Element Plus, Axios |
| 规则引擎 | JSqlParser 4.9（解析+验证） |

## 快速开始

### 1. 启动 Ollama

```bash
ollama run qwen2.5
```

### 2. 启动 AI 服务

```bash
cd ai-service
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

### 3. 启动后端

```bash
cd sqlpilot-backend
mvn spring-boot:run
```

### 4. 启动前端

```bash
cd sqlpilot-frontend
npm install
npm run dev
```

## 项目结构

```
SQLPilot/
├── sqlpilot-backend/                 # Spring Boot 后端
│   └── src/main/java/com/sqlpilot/backend/
│       ├── controller/               # REST API（分析/优化/NL2SQL/记忆）
│       ├── service/                  # 业务逻辑
│       ├── rule/impl/                # 规则引擎（SelectStarRule, JoinRule等）
│       ├── mapper/                   # MyBatis 数据访问
│       └── entity/                   # 实体类
├── ai-service/                       # RAG AI服务
│   ├── app.py                        # FastAPI 入口
│   ├── rag_service.py                # 向量检索+关键字混合检索
│   ├── memory_system.py              # 记忆与奖惩系统
│   ├── build_vector_db.py            # 知识库向量化
│   └── knowledge/                    # SQL规范知识库（JSON）
└── sqlpilot-frontend/                # Vue 3 前端
    └── src/views/                    # 页面：Home, SqlOptimize, NaturalToSql, History, Feedback
```

## 接口概览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/sql/analyze` | POST | SQL 性能分析 |
| `/api/sql/optimize` | POST | 获取 AI 优化建议 |
| `/api/sql/natural-to-sql` | POST | 自然语言转 SQL |
| `/ai/optimize` | POST | RAG SQL 优化 |
| `/ai/natural-to-sql` | POST | NL2SQL |
