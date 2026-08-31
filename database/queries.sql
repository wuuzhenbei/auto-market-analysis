-- ============================================
-- 汽车市场数据分析 - 常用分析查询
-- ============================================

-- 1. 品牌销量排名（2024年累计）
SELECT
    b.name AS 品牌,
    b.category AS 品牌类别,
    b.country AS 国家,
    SUM(s.sales_volume) AS 累计销量,
    ROUND(SUM(s.sales_volume) * 100.0 / (SELECT SUM(sales_volume) FROM sales WHERE year=2024), 2) AS 市场份额
FROM sales s
JOIN models m ON s.model_id = m.id
JOIN brands b ON m.brand_id = b.id
WHERE s.year = 2024
GROUP BY b.id
ORDER BY 累计销量 DESC;

-- 2. 车型销量 TOP 20
SELECT
    b.name AS 品牌,
    m.name AS 车型,
    m.energy_type AS 能源类型,
    m.guide_price_min AS 最低价,
    m.guide_price_max AS 最高价,
    SUM(s.sales_volume) AS 累计销量
FROM sales s
JOIN models m ON s.model_id = m.id
JOIN brands b ON m.brand_id = b.id
WHERE s.year = 2024
GROUP BY m.id
ORDER BY 累计销量 DESC
LIMIT 20;

-- 3. 价格区间分布
SELECT
    CASE
        WHEN guide_price_min < 5 THEN '5万以下'
        WHEN guide_price_min < 10 THEN '5-10万'
        WHEN guide_price_min < 15 THEN '10-15万'
        WHEN guide_price_min < 20 THEN '15-20万'
        WHEN guide_price_min < 30 THEN '20-30万'
        WHEN guide_price_min < 50 THEN '30-50万'
        WHEN guide_price_min < 100 THEN '50-100万'
        ELSE '100万以上'
    END AS 价格区间,
    COUNT(*) AS 车型数量,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM models), 2) AS 占比
FROM models
GROUP BY 价格区间
ORDER BY MIN(guide_price_min);

-- 4. 新能源 vs 燃油车占比
SELECT
    energy_type AS 能源类型,
    COUNT(*) AS 车型数量,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM models), 2) AS 占比
FROM models
GROUP BY energy_type
ORDER BY 车型数量 DESC;

-- 5. 新能源品牌销量排名
SELECT
    b.name AS 品牌,
    SUM(s.sales_volume) AS 新能源销量
FROM sales s
JOIN models m ON s.model_id = m.id
JOIN brands b ON m.brand_id = b.id
WHERE s.year = 2024
AND m.energy_type IN ('纯电动', '插电混动', '增程式')
GROUP BY b.id
ORDER BY 新能源销量 DESC
LIMIT 15;

-- 6. 各品牌平均评分
SELECT
    b.name AS 品牌,
    ROUND(AVG(r.overall_score), 2) AS 平均综合评分,
    ROUND(AVG(r.appearance_score), 2) AS 平均外观评分,
    ROUND(AVG(r.interior_score), 2) AS 平均内饰评分,
    ROUND(AVG(r.power_score), 2) AS 平均动力评分,
    ROUND(AVG(r.value_score), 2) AS 平均性价比评分,
    COUNT(m.id) AS 车型数量
FROM ratings r
JOIN models m ON r.model_id = m.id
JOIN brands b ON m.brand_id = b.id
GROUP BY b.id
HAVING 车型数量 >= 2
ORDER BY 平均综合评分 DESC;

-- 7. 月度销量趋势
SELECT
    month AS 月份,
    SUM(sales_volume) AS 总销量
FROM sales
WHERE year = 2024
GROUP BY month
ORDER BY month;

-- 8. 各能源类型月度销量趋势
SELECT
    m.energy_type AS 能源类型,
    s.month AS 月份,
    SUM(s.sales_volume) AS 销量
FROM sales s
JOIN models m ON s.model_id = m.id
WHERE s.year = 2024
GROUP BY m.energy_type, s.month
ORDER BY m.energy_type, s.month;

-- 9. 城市销量 TOP 20
SELECT
    city AS 城市,
    province AS 省份,
    region AS 区域,
    SUM(sales_volume) AS 总销量
FROM city_sales
WHERE year = 2024
GROUP BY city
ORDER BY 总销量 DESC
LIMIT 20;

-- 10. 区域销量分布
SELECT
    region AS 区域,
    SUM(sales_volume) AS 总销量,
    ROUND(SUM(sales_volume) * 100.0 / (SELECT SUM(sales_volume) FROM city_sales WHERE year=2024), 2) AS 占比
FROM city_sales
WHERE year = 2024
GROUP BY region
ORDER BY 总销量 DESC;

-- 11. 性价比分析（价格 vs 评分）
SELECT
    b.name AS 品牌,
    m.name AS 车型,
    m.guide_price_min AS 最低价,
    r.overall_score AS 综合评分,
    r.value_score AS 性价比评分,
    ROUND(r.overall_score / m.guide_price_min, 4) AS 评分价格比
FROM models m
JOIN brands b ON m.brand_id = b.id
JOIN ratings r ON m.id = r.model_id
WHERE m.guide_price_min > 0
ORDER BY 评分价格比 DESC
LIMIT 20;

-- 12. 车身类型分布
SELECT
    body_type AS 车身类型,
    COUNT(*) AS 车型数量,
    ROUND(AVG(guide_price_min), 2) AS 平均最低价,
    ROUND(AVG(guide_price_max), 2) AS 平均最高价
FROM models
GROUP BY body_type
ORDER BY 车型数量 DESC;

-- 13. 品牌类别销量对比
SELECT
    b.category AS 品牌类别,
    SUM(s.sales_volume) AS 总销量,
    COUNT(DISTINCT m.id) AS 车型数量,
    ROUND(SUM(s.sales_volume) * 1.0 / COUNT(DISTINCT m.id), 0) AS 单车型平均销量
FROM sales s
JOIN models m ON s.model_id = m.id
JOIN brands b ON m.brand_id = b.id
WHERE s.year = 2024
GROUP BY b.category
ORDER BY 总销量 DESC;

-- 14. 高评分低销量车型（潜力车型）
SELECT
    b.name AS 品牌,
    m.name AS 车型,
    r.overall_score AS 综合评分,
    SUM(s.sales_volume) AS 累计销量
FROM models m
JOIN brands b ON m.brand_id = b.id
JOIN ratings r ON m.id = r.model_id
JOIN sales s ON m.id = s.model_id
WHERE s.year = 2024
AND r.overall_score >= 4.5
GROUP BY m.id
HAVING 累计销量 < 50000
ORDER BY r.overall_score DESC;

-- 15. 各价格区间销量占比
SELECT
    CASE
        WHEN m.guide_price_min < 10 THEN '10万以下'
        WHEN m.guide_price_min < 20 THEN '10-20万'
        WHEN m.guide_price_min < 30 THEN '20-30万'
        WHEN m.guide_price_min < 50 THEN '30-50万'
        ELSE '50万以上'
    END AS 价格区间,
    SUM(s.sales_volume) AS 总销量,
    ROUND(SUM(s.sales_volume) * 100.0 / (SELECT SUM(sales_volume) FROM sales WHERE year=2024), 2) AS 市场份额
FROM sales s
JOIN models m ON s.model_id = m.id
WHERE s.year = 2024
GROUP BY 价格区间
ORDER BY MIN(m.guide_price_min);
