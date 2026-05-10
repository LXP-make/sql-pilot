# SQL Pilot - AI-Driven SQL Performance Optimization Assistant

A comprehensive SQL performance optimization tool that leverages AI and RAG (Retrieval-Augmented Generation) to analyze and optimize SQL queries.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SQL Pilot Project                        │
├─────────────────────────────────────────────────────────────┤
│  sqlpilot-frontend/   # Vue.js Frontend (待开发)           │
│  sqlpilot-backend/    # Spring Boot Backend (8080)        │
│  ai-service/          # FastAPI RAG Service (8000)        │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **SQL Analysis**: Analyze SQL queries for performance issues
- **AI-Powered Optimization**: RAG-based SQL optimization suggestions
- **Natural Language to SQL**: Convert natural language to SQL queries
- **Rule Engine**: Built-in SQL rule detection (SELECT *, etc.)

## Quick Start

### 1. Start AI Service

```bash
cd ai-service
uvicorn app:app --reload
```

Access: http://localhost:8000/docs

### 2. Start Backend Service

```bash
cd sqlpilot-backend
mvn spring-boot:run
```

Access: http://localhost:8080/api/sql/analyze

## API Endpoints

### AI Service (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/optimize` | POST | SQL optimization with RAG |
| `/ai/natural-to-sql` | POST | Natural language to SQL |
| `/health` | GET | Health check |

### Backend Service (Port 8080)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sql/analyze` | POST | SQL performance analysis |
| `/api/sql/optimize` | POST | SQL optimization |
| `/api/sql/natural-to-sql` | POST | Natural language to SQL |

## Technologies

- **Backend**: Spring Boot 4.0.x, MyBatis
- **AI Service**: FastAPI, ChromaDB, Sentence Transformers
- **AI Model**: Ollama (Qwen2.5)
- **Database**: MySQL

## Project Structure

```
SQLPilot/
├── sqlpilot-backend/
│   ├── src/main/java/com/sqlpilot/backend/
│   │   ├── controller/    # REST API controllers
│   │   ├── service/       # Business logic
│   │   ├── rule/          # SQL rule engine
│   │   ├── dto/           # Data transfer objects
│   │   ├── entity/        # Database entities
│   │   ├── mapper/        # MyBatis mappers
│   │   ├── config/        # Configuration
│   │   └── util/          # Utility classes
│   └── src/main/resources/
│       ├── mapper/        # MyBatis XML
│       └── application.yml
├── ai-service/
│   ├── app.py             # FastAPI application
│   ├── rag_service.py     # RAG core service
│   ├── knowledge/         # Knowledge base
│   └── chroma_db/         # Vector database
└── sqlpilot-frontend/     # Vue.js frontend (待开发)
```

## Configuration

### Database (sqlpilot-backend/src/main/resources/application.yml)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/sqlpilot
    username: root
    password: your_password
```

### AI Service (ai-service/app.py)

```python
# Ollama configuration
ollama_url = "http://127.0.0.1:11434/api/generate"
ollama_model = "qwen2.5:latest"
```

## License

MIT License