"""
口碑分析 API
"""
from fastapi import APIRouter, Query
from backend.database import query_to_dict

router = APIRouter()


@router.get("/distribution")
def get_rating_distribution():
    """评分分布"""
    query = """
    SELECT
        CASE
            WHEN overall_score < 3.5 THEN '3.5以下'
            WHEN overall_score < 4.0 THEN '3.5-4.0'
            WHEN overall_score < 4.5 THEN '4.0-4.5'
            ELSE '4.5以上'
        END as rating_range,
        COUNT(*) as model_count
    FROM ratings
    GROUP BY rating_range
    ORDER BY rating_range
    """
    results = query_to_dict(query)
    total = sum(r["model_count"] for r in results)
    for r in results:
        r["percentage"] = round(r["model_count"] / total * 100, 2) if total else 0
    return results


@router.get("/brands")
def get_brand_ratings():
    """品牌评分排名"""
    query = """
    SELECT b.name as brand_name, b.category as brand_category,
           AVG(r.overall_score) as overall_score,
           AVG(r.appearance_score) as appearance_score,
           AVG(r.interior_score) as interior_score,
           AVG(r.power_score) as power_score,
           AVG(r.space_score) as space_score,
           AVG(r.fuel_score) as fuel_score,
           AVG(r.handling_score) as handling_score,
           AVG(r.comfort_score) as comfort_score,
           AVG(r.value_score) as value_score,
           COUNT(*) as model_count
    FROM ratings r
    JOIN models m ON r.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    GROUP BY b.id
    HAVING model_count >= 2
    ORDER BY overall_score DESC
    """
    return query_to_dict(query)


@router.get("/models")
def get_model_ratings(top_n: int = Query(20)):
    """车型评分排名"""
    query = """
    SELECT m.name as model_name, b.name as brand_name, m.energy_type,
           (m.guide_price_min + m.guide_price_max) / 2 as price,
           r.overall_score, r.appearance_score, r.interior_score, r.power_score,
           r.space_score, r.fuel_score, r.handling_score, r.comfort_score, r.value_score,
           r.review_count
    FROM ratings r
    JOIN models m ON r.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    ORDER BY r.overall_score DESC
    LIMIT ?
    """
    return query_to_dict(query, [top_n])


@router.get("/radar/{brand_name}")
def get_brand_radar(brand_name: str):
    """品牌雷达图数据"""
    query = """
    SELECT AVG(r.appearance_score) as appearance,
           AVG(r.interior_score) as interior,
           AVG(r.power_score) as power,
           AVG(r.space_score) as space,
           AVG(r.fuel_score) as fuel,
           AVG(r.handling_score) as handling,
           AVG(r.comfort_score) as comfort,
           AVG(r.value_score) as value
    FROM ratings r
    JOIN models m ON r.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE b.name = ?
    """
    return query_to_dict(query, [brand_name])


@router.get("/dimension-analysis")
def get_dimension_analysis():
    """各维度评分分析"""
    query = """
    SELECT '外观' as dimension, AVG(appearance_score) as avg_score,
           MIN(appearance_score) as min_score, MAX(appearance_score) as max_score
    FROM ratings
    UNION ALL
    SELECT '内饰', AVG(interior_score), MIN(interior_score), MAX(interior_score) FROM ratings
    UNION ALL
    SELECT '动力', AVG(power_score), MIN(power_score), MAX(power_score) FROM ratings
    UNION ALL
    SELECT '空间', AVG(space_score), MIN(space_score), MAX(space_score) FROM ratings
    UNION ALL
    SELECT '油耗', AVG(fuel_score), MIN(fuel_score), MAX(fuel_score) FROM ratings
    UNION ALL
    SELECT '操控', AVG(handling_score), MIN(handling_score), MAX(handling_score) FROM ratings
    UNION ALL
    SELECT '舒适性', AVG(comfort_score), MIN(comfort_score), MAX(comfort_score) FROM ratings
    UNION ALL
    SELECT '性价比', AVG(value_score), MIN(value_score), MAX(value_score) FROM ratings
    """
    return query_to_dict(query)
