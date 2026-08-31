"""
品牌分析 API
"""
from fastapi import APIRouter, Query
from backend.database import query_to_dict

router = APIRouter()


@router.get("/ranking")
def get_brand_ranking(year: int = Query(2024, description="年份")):
    """品牌销量排名"""
    query = """
    SELECT b.name as brand_name, b.category as brand_category, b.country as brand_country,
           SUM(s.sales_volume) as total_sales
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE s.year = ?
    GROUP BY b.id
    ORDER BY total_sales DESC
    """
    results = query_to_dict(query, [year])
    total = sum(r["total_sales"] for r in results)
    for r in results:
        r["market_share"] = round(r["total_sales"] / total * 100, 2) if total else 0
    return results


@router.get("/categories")
def get_brand_categories(year: int = Query(2024, description="年份")):
    """品牌分类分析"""
    query = """
    SELECT b.category as brand_category, SUM(s.sales_volume) as total_sales,
           COUNT(DISTINCT m.id) as model_count
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE s.year = ?
    GROUP BY b.category
    ORDER BY total_sales DESC
    """
    results = query_to_dict(query, [year])
    total = sum(r["total_sales"] for r in results)
    for r in results:
        r["market_share"] = round(r["total_sales"] / total * 100, 2) if total else 0
    return results


@router.get("/countries")
def get_brand_countries(year: int = Query(2024, description="年份")):
    """品牌国别分析"""
    query = """
    SELECT b.country as brand_country, SUM(s.sales_volume) as total_sales,
           COUNT(DISTINCT b.id) as brand_count, COUNT(DISTINCT m.id) as model_count
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE s.year = ?
    GROUP BY b.country
    ORDER BY total_sales DESC
    """
    results = query_to_dict(query, [year])
    total = sum(r["total_sales"] for r in results)
    for r in results:
        r["market_share"] = round(r["total_sales"] / total * 100, 2) if total else 0
    return results


@router.get("/{brand_name}/models")
def get_brand_models(brand_name: str, year: int = Query(2024, description="年份"), top_n: int = Query(5)):
    """某品牌车型列表"""
    query = """
    SELECT m.name as model_name, m.energy_type, m.guide_price_min, m.guide_price_max,
           SUM(s.sales_volume) as total_sales
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE b.name = ? AND s.year = ?
    GROUP BY m.id
    ORDER BY total_sales DESC
    LIMIT ?
    """
    return query_to_dict(query, [brand_name, year, top_n])


@router.get("/{brand_name}/ratings")
def get_brand_ratings(brand_name: str):
    """某品牌评分详情"""
    query = """
    SELECT m.name as model_name, m.energy_type,
           r.overall_score, r.appearance_score, r.interior_score, r.power_score,
           r.space_score, r.fuel_score, r.handling_score, r.comfort_score, r.value_score,
           r.review_count
    FROM ratings r
    JOIN models m ON r.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE b.name = ?
    ORDER BY r.overall_score DESC
    """
    return query_to_dict(query, [brand_name])
