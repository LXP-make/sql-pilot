from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="SQL Pilot AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SqlRequest(BaseModel):
    sql: str

class OptimizeRequest(BaseModel):
    sql: str
    optimization_level: str = "medium"
    include_index_suggestion: bool = True

class NaturalToSqlRequest(BaseModel):
    natural_query: str
    table_schema: dict = None

@app.get("/")
def root():
    return {
        "service": "SQL Pilot AI Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/ai/optimize")
def optimize(req: OptimizeRequest):
    optimized_sql = req.sql
    if "SELECT *" in req.sql.upper():
        optimized_sql = req.sql.replace("*", "id, name")
    
    return {
        "success": True,
        "data": {
            "original_sql": req.sql,
            "optimized_sql": optimized_sql,
            "optimization_suggestions": [
                {"type": "local", "description": "避免使用 SELECT *，指定具体列"},
                {"type": "local", "description": "添加适当的索引"}
            ],
            "problems": ["使用了 SELECT *"]
        }
    }

@app.post("/api/optimize")
def optimize_backward(req: OptimizeRequest):
    return optimize(req)

@app.post("/ai/natural-to-sql")
def natural_to_sql(req: NaturalToSqlRequest):
    sql = "SELECT * FROM table WHERE 1=1"
    if "user" in req.natural_query.lower():
        sql = "SELECT * FROM users WHERE 1=1"
    elif "order" in req.natural_query.lower():
        sql = "SELECT * FROM orders WHERE 1=1"
    
    return {
        "success": True,
        "data": {
            "natural_query": req.natural_query,
            "generated_sql": sql,
            "confidence": 0.6,
            "suggestions": ["请验证生成的SQL"]
        }
    }

@app.post("/api/natural-to-sql")
def natural_to_sql_backward(req: NaturalToSqlRequest):
    return natural_to_sql(req)

if __name__ == "__main__":
    print("="*50)
    print("  SQL Pilot AI Service - SIMPLE MODE")
    print("="*50)
    print("  服务将在 http://localhost:8000 启动")
    print("  Swagger 文档: http://localhost:8000/docs")
    print("="*50)
    print()
    uvicorn.run("app_simple:app", host="0.0.0.0", port=8000, reload=True)