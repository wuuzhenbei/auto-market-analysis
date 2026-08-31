
# Power BI 数据关系模型指南

## 数据模型结构

本数据采用星型模型（Star Schema）设计，包含以下表：

### 事实表（Fact Tables）

1. **fact_sales** - 销量事实表
   - 主键: sales_id
   - 外键: model_id
   - 度量: sales_volume, yoy_growth, mom_growth

2. **fact_city_sales** - 城市销量事实表
   - 主键: city_sales_id
   - 外键: model_id
   - 度量: sales_volume

### 维度表（Dimension Tables）

1. **dim_brands** - 品牌维度表
   - 主键: brand_id
   - 属性: brand_name, brand_category, brand_country

2. **dim_models** - 车型维度表
   - 主键: model_id
   - 外键: brand_id
   - 属性: model_name, series, year, energy_type, body_type, price

3. **dim_specs** - 参数维度表
   - 主键: model_id
   - 属性: horsepower, torque, fuel_consumption, range_km 等

4. **dim_ratings** - 评分维度表
   - 主键: model_id
   - 属性: overall_score, appearance_score 等

## 关系设置

在 Power BI 中设置以下关系：

```
fact_sales[model_id] ──→ dim_models[model_id] (多对一)
fact_sales[model_id] ──→ dim_specs[model_id] (多对一)
fact_sales[model_id] ──→ dim_ratings[model_id] (多对一)
dim_models[brand_id] ──→ dim_brands[brand_id] (多对一)
fact_city_sales[model_id] ──→ dim_models[model_id] (多对一)
```

## 导入步骤

1. 打开 Power BI Desktop
2. 获取数据 → 文本/CSV
3. 依次导入所有 CSV 文件
4. 在"模型视图"中设置关系
5. 创建度量值和计算列

## 推荐度量值

```DAX
// 总销量
Total Sales = SUM(fact_sales[sales_volume])

// 市场份额
Market Share =
DIVIDE(
    SUM(fact_sales[sales_volume]),
    CALCULATE(SUM(fact_sales[sales_volume]), ALL(dim_brands))
)

// 同比增长率
YoY Growth = AVERAGE(fact_sales[yoy_growth])

// 新能源渗透率
NE Penetration =
DIVIDE(
    CALCULATE(SUM(fact_sales[sales_volume]), dim_models[energy_type] IN {"纯电动", "插电混动", "增程式"}),
    SUM(fact_sales[sales_volume])
)

// 平均评分
Avg Rating = AVERAGE(dim_ratings[overall_score])
```

## 推荐可视化

1. **品牌市场份额** - 饼图/树状图
2. **价格区间分布** - 柱状图
3. **新能源渗透率趋势** - 折线图
4. **城市销量分布** - 地图
5. **车型参数对比** - 散点图/雷达图
6. **评分分布** - 箱线图
