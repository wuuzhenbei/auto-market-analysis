"""
销量分析 API
"""
from fastapi import APIRouter, Query
from backend.database import query_to_dict

router = APIRouter()


@router.get("/monthly")
def get_monthly_sales(start_year: int = Query(2024), end_year: int = Query(2026)):
    """月度销量趋势"""
    query = """
    SELECT year, month, SUM(sales_volume) as total_sales,
           year || '-' || printf('%02d', month) as year_month
    FROM sales
    WHERE year BETWEEN ? AND ?
    GROUP BY year, month
    ORDER BY year, month
    """
    return query_to_dict(query, [start_year, end_year])


@router.get("/monthly/by-energy")
def get_monthly_sales_by_energy(start_year: int = Query(2024), end_year: int = Query(2026)):
    """按能源类型月度销量"""
    query = """
    SELECT s.year, s.month, m.energy_type, SUM(s.sales_volume) as total_sales,
           s.year || '-' || printf('%02d', s.month) as year_month
    FROM sales s
    JOIN models m ON s.model_id = m.id
    WHERE s.year BETWEEN ? AND ?
    GROUP BY s.year, s.month, m.energy_type
    ORDER BY s.year, s.month, m.energy_type
    """
    return query_to_dict(query, [start_year, end_year])


@router.get("/yoy")
def get_yoy_growth(year: int = Query(2025)):
    """同比增长"""
    query = """
    SELECT b.name as brand_name,
           SUM(CASE WHEN s.year = ? THEN s.sales_volume ELSE 0 END) as current_sales,
           SUM(CASE WHEN s.year = ? - 1 THEN s.sales_volume ELSE 0 END) as last_sales
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    GROUP BY b.id
    HAVING last_sales > 0
    ORDER BY current_sales DESC
    """
    results = query_to_dict(query, [year, year])
    for r in results:
        r["yoy_growth"] = round((r["current_sales"] - r["last_sales"]) / r["last_sales"] * 100, 1) if r["last_sales"] else 0
    return results


@router.get("/cities")
def get_city_sales(year: int = Query(2024), top_n: int = Query(20)):
    """城市销量"""
    query = """
    SELECT city, province, region, SUM(sales_volume) as sales_volume
    FROM city_sales
    WHERE year = ?
    GROUP BY city
    ORDER BY sales_volume DESC
    LIMIT ?
    """
    return query_to_dict(query, [year, top_n])


@router.get("/regions")
def get_region_sales(year: int = Query(2024)):
    """区域销量"""
    query = """
    SELECT region, SUM(sales_volume) as sales_volume
    FROM city_sales
    WHERE year = ?
    GROUP BY region
    ORDER BY sales_volume DESC
    """
    return query_to_dict(query, [year])


@router.get("/brand-monthly/{brand_name}")
def get_brand_monthly_sales(brand_name: str, start_year: int = Query(2024), end_year: int = Query(2026)):
    """某品牌月度销量"""
    query = """
    SELECT s.year, s.month, SUM(s.sales_volume) as total_sales,
           s.year || '-' || printf('%02d', s.month) as year_month
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    WHERE b.name = ? AND s.year BETWEEN ? AND ?
    GROUP BY s.year, s.month
    ORDER BY s.year, s.month
    """
    return query_to_dict(query, [brand_name, start_year, end_year])
