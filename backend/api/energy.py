"""
新能源分析 API
"""
from fastapi import APIRouter, Query
from backend.database import query_to_dict

router = APIRouter()


@router.get("/types")
def get_energy_type_sales(year: int = Query(2024)):
    """能源类型销量"""
    query = """
    SELECT m.energy_type, SUM(s.sales_volume) as total_sales,
           COUNT(DISTINCT m.id) as model_count
    FROM sales s
    JOIN models m ON s.model_id = m.id
    WHERE s.year = ?
    GROUP BY m.energy_type
    ORDER BY total_sales DESC
    """
    results = query_to_dict(query, [year])
    total = sum(r["total_sales"] for r in results)
    for r in results:
        r["market_share"] = round(r["total_sales"] / total * 100, 2) if total else 0
    return results


@router.get("/penetration")
def get_penetration_trend(start_year: int = Query(2024), end_year: int = Query(2026)):
    """新能源渗透率趋势"""
    query = """
    SELECT s.year, s.month,
           s.year || '-' || printf('%02d', s.month) as year_month,
           SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) as ne_sales,
           SUM(s.sales_volume) as total_sales
    FROM sales s
    JOIN models m ON s.model_id = m.id
    WHERE s.year BETWEEN ? AND ?
    GROUP BY s.year, s.month
    ORDER BY s.year, s.month
    """
    results = query_to_dict(query, [start_year, end_year])
    for r in results:
        r["penetration_rate"] = round(r["ne_sales"] / r["total_sales"] * 100, 2) if r["total_sales"] else 0
    return results


@router.get("/brands")
def get_ne_brands(year: int = Query(2024)):
    """新能源品牌排名"""
    query = """
    SELECT b.name as brand_name, b.category as brand_category,
           SUM(s.sales_volume) as total_sales, COUNT(DISTINCT m.id) as model_count
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE s.year = ? AND m.energy_type IN ('纯电动', '插电混动', '增程式')
    GROUP BY b.id
    ORDER BY total_sales DESC
    """
    results = query_to_dict(query, [year])
    total = sum(r["total_sales"] for r in results)
    for r in results:
        r["market_share"] = round(r["total_sales"] / total * 100, 2) if total else 0
    return results


@router.get("/models")
def get_ne_models(year: int = Query(2024), top_n: int = Query(20)):
    """新能源车型排名"""
    query = """
    SELECT m.name as model_name, b.name as brand_name, m.energy_type,
           m.guide_price_min, m.guide_price_max, sp.range_km,
           SUM(s.sales_volume) as total_sales
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    LEFT JOIN specs sp ON sp.model_id = m.id
    WHERE s.year = ? AND m.energy_type IN ('纯电动', '插电混动', '增程式')
    GROUP BY m.id
    ORDER BY total_sales DESC
    LIMIT ?
    """
    return query_to_dict(query, [year, top_n])


@router.get("/range")
def get_range_analysis():
    """续航分布分析"""
    query = """
    SELECT
        CASE
            WHEN range_km < 300 THEN '300km以下'
            WHEN range_km < 400 THEN '300-400km'
            WHEN range_km < 500 THEN '400-500km'
            WHEN range_km < 600 THEN '500-600km'
            WHEN range_km < 700 THEN '600-700km'
            ELSE '700km以上'
        END as range_group,
        COUNT(*) as model_count,
        AVG(guide_price_min) as avg_price
    FROM specs sp
    JOIN models m ON sp.model_id = m.id
    WHERE m.energy_type = '纯电动' AND sp.range_km > 0
    GROUP BY range_group
    ORDER BY MIN(range_km)
    """
    return query_to_dict(query)


@router.get("/ev-vs-phev")
def get_ev_vs_phev(year: int = Query(2024)):
    """EV vs PHEV 对比"""
    query = """
    SELECT m.energy_type, SUM(s.sales_volume) as total_sales,
           COUNT(DISTINCT m.id) as model_count,
           AVG(m.guide_price_min) as avg_price,
           AVG(sp.range_km) as avg_range,
           AVG(sp.horsepower) as avg_horsepower
    FROM sales s
    JOIN models m ON s.model_id = m.id
    LEFT JOIN specs sp ON sp.model_id = m.id
    WHERE s.year = ? AND m.energy_type IN ('纯电动', '插电混动', '增程式')
    GROUP BY m.energy_type
    """
    return query_to_dict(query, [year])
