"""
FastAPI 后端入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.api import brands, models, sales, energy, ratings, overview, import_data

app = FastAPI(
    title="汽车市场数据分析 API",
    description="提供品牌、车型、销量、新能源、口碑等多维度分析数据",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(overview.router, prefix="/api/overview", tags=["市场总览"])
app.include_router(brands.router, prefix="/api/brands", tags=["品牌分析"])
app.include_router(models.router, prefix="/api/models", tags=["车型分析"])
app.include_router(sales.router, prefix="/api/sales", tags=["销量分析"])
app.include_router(energy.router, prefix="/api/energy", tags=["新能源分析"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["口碑分析"])
app.include_router(import_data.router, prefix="/api/import", tags=["数据导入"])


@app.get("/")
def root():
    return {
        "message": "汽车市场数据分析 API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
