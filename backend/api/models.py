"""
车型分析 API
"""
from fastapi import APIRouter, Query
from backend.database import query_to_dict

router = APIRouter()


@router.get("/ranking")
def get_model_ranking(year: int = Query(2024), top_n: int = Query(20)):
    """车型销量排名"""
    query = """
    SELECT m.name as model_name, b.name as brand_name, m.energy_type, m.body_type,
           m.guide_price_min, m.guide_price_max,
           SUM(s.sales_volume) as total_sales
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE s.year = ?
    GROUP BY m.id
    ORDER BY total_sales DESC
    LIMIT ?
    """
    return query_to_dict(query, [year, top_n])


@router.get("/detail/{model_name}")
def get_model_detail(model_name: str):
    """车型详情"""
    query = """
    SELECT m.*, b.name as brand_name, b.category as brand_category,
           s.horsepower, s.torque, s.acceleration_100, s.displacement,
           s.fuel_consumption, s.range_km, s.battery_capacity,
           s.length, s.width, s.height, s.wheelbase,
           r.overall_score, r.appearance_score, r.interior_score, r.power_score,
           r.space_score, r.fuel_score, r.handling_score, r.comfort_score, r.value_score
    FROM models m
    JOIN brands b ON m.brand_id = b.id
    LEFT JOIN specs s ON s.model_id = m.id
    LEFT JOIN ratings r ON r.model_id = m.id
    WHERE m.name = ?
    """
    results = query_to_dict(query, [model_name])
    return results[0] if results else {"error": "车型未找到"}


@router.get("/search")
def search_models(q: str = Query(..., description="搜索关键词")):
    """搜索车型"""
    query = """
    SELECT m.name as model_name, b.name as brand_name, m.energy_type, m.body_type,
           m.guide_price_min, m.guide_price_max
    FROM models m
    JOIN brands b ON m.brand_id = b.id
    WHERE m.name LIKE ? OR b.name LIKE ?
    LIMIT 20
    """
    keyword = f"%{q}%"
    return query_to_dict(query, [keyword, keyword])
