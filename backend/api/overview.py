"""
市场总览 API
"""
from fastapi import APIRouter, Query
from backend.database import query_to_dict, query_to_dataframe

router = APIRouter()


@router.get("")
def get_market_overview(year: int = Query(None, description="年份")):
    """获取市场总览 KPI"""
    overview = {}

    # 总销量
    if year:
        result = query_to_dict("SELECT SUM(sales_volume) as total FROM sales WHERE year = ?", [year])
    else:
        result = query_to_dict("SELECT SUM(sales_volume) as total FROM sales")
    overview["total_sales"] = result[0]["total"] if result and result[0]["total"] else 0

    # 品牌数量
    result = query_to_dict("SELECT COUNT(*) as cnt FROM brands")
    overview["brand_count"] = result[0]["cnt"]

    # 车型数量
    result = query_to_dict("SELECT COUNT(*) as cnt FROM models")
    overview["model_count"] = result[0]["cnt"]

    # 新能源渗透率
    if year:
        query = """
        SELECT SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) * 100.0 / SUM(s.sales_volume) as rate
        FROM sales s JOIN models m ON s.model_id = m.id WHERE s.year = ?
        """
        result = query_to_dict(query, [year])
    else:
        query = """
        SELECT SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) * 100.0 / SUM(s.sales_volume) as rate
        FROM sales s JOIN models m ON s.model_id = m.id
        """
        result = query_to_dict(query)
    overview["new_energy_penetration"] = round(result[0]["rate"], 2) if result and result[0]["rate"] else 0

    # 平均售价
    result = query_to_dict("SELECT AVG((guide_price_min + guide_price_max) / 2) as avg FROM models WHERE guide_price_min > 0")
    overview["avg_price"] = round(result[0]["avg"], 2) if result and result[0]["avg"] else 0

    # 平均评分
    result = query_to_dict("SELECT AVG(overall_score) as avg FROM ratings")
    overview["avg_rating"] = round(result[0]["avg"], 2) if result and result[0]["avg"] else 0

    return overview


@router.get("/insights")
def get_insights():
    """获取分析洞察"""
    insights = []

    # 市场集中度
    query = """
    SELECT b.name, SUM(s.sales_volume) as total_sales
    FROM sales s JOIN models m ON s.model_id = m.id JOIN brands b ON m.brand_id = b.id
    GROUP BY b.id ORDER BY total_sales DESC LIMIT 5
    """
    top5 = query_to_dict(query)
    total = query_to_dict("SELECT SUM(sales_volume) as total FROM sales")
    total_sales = total[0]["total"] if total else 0
    top5_sales = sum(r["total_sales"] for r in top5)
    top5_share = top5_sales / total_sales * 100 if total_sales else 0

    insights.append({
        "category": "市场集中度",
        "insight": f"TOP 5 品牌市场份额合计 {top5_share:.1f}%",
        "detail": f"前五名: {', '.join(r['name'] for r in top5)}"
    })

    return insights
