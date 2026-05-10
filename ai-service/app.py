from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_service import analyze_sql
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
def home():
    return {
        "service": "SQL Pilot AI Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            {"POST /ai/optimize": "SQL优化"},
            {"POST /api/optimize": "SQL优化(兼容)"},
            {"POST /ai/natural-to-sql": "自然语言转SQL"},
            {"POST /api/natural-to-sql": "自然语言转SQL(兼容)"},
            {"GET /health": "健康检查"}
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/ai/optimize")
def optimize(req: OptimizeRequest):
    try:
        result = analyze_sql(req.sql)
        
        return {
            "success": True,
            "data": {
                "original_sql": result["original_sql"],
                "optimized_sql": result["optimized_sql"],
                "optimization_suggestions": [
                    {"type": "rag", "description": s} 
                    for s in result["suggestions"]
                ],
                "problems": result["problems"]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": None
        }

@app.post("/api/optimize")
def optimize_backward(req: OptimizeRequest):
    return optimize(req)

@app.post("/ai/natural-to-sql")
def natural_to_sql(req: NaturalToSqlRequest):
    try:
        prompt = f"根据以下描述生成SQL语句：{req.natural_query}"
        result = analyze_sql(prompt)
        
        return {
            "success": True,
            "data": {
                "natural_query": req.natural_query,
                "generated_sql": result["optimized_sql"],
                "confidence": 0.7,
                "suggestions": result["suggestions"]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": None
        }

@app.post("/api/natural-to-sql")
def natural_to_sql_backward(req: NaturalToSqlRequest):
    return natural_to_sql(req)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)