"""
Power BI 数据导出模块
"""
import sqlite3
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, TABLEAU_DIR


class PowerBIExporter:
    """Power BI 数据导出器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.output_dir = TABLEAU_DIR / "powerbi"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_for_powerbi(self, year: int = 2024) -> dict:
        """
        导出 Power BI 可用的 CSV 数据

        Returns:
            导出文件路径字典
        """
        files = {}

        # 1. 事实表：销量数据
        print("\n[1/6] 导出销量事实表...")
        query = """
        SELECT
            s.id AS sales_id,
            s.model_id,
            b.name AS brand_name,
            m.name AS model_name,
            m.energy_type,
            m.body_type,
            b.category AS brand_category,
            b.country AS brand_country,
            m.guide_price_min AS price,
            s.year,
            s.month,
            s.sales_volume,
            s.yoy_growth,
            s.mom_growth,
            s.ranking
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ?
        """
        df = pd.read_sql(query, self.conn, params=[year])
        filepath = self.output_dir / "fact_sales.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["fact_sales"] = str(filepath)
        print(f"  - fact_sales.csv ({len(df)} 条)")

        # 2. 事实表：城市销量
        print("[2/6] 导出城市销量事实表...")
        query = """
        SELECT
            cs.id AS city_sales_id,
            cs.model_id,
            b.name AS brand_name,
            m.name AS model_name,
            m.energy_type,
            cs.city,
            cs.province,
            cs.region,
            cs.sales_volume,
            cs.year,
            cs.month
        FROM city_sales cs
        JOIN models m ON cs.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE cs.year = ?
        """
        df = pd.read_sql(query, self.conn, params=[year])
        filepath = self.output_dir / "fact_city_sales.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["fact_city_sales"] = str(filepath)
        print(f"  - fact_city_sales.csv ({len(df)} 条)")

        # 3. 维度表：品牌
        print("[3/6] 导出品牌维度表...")
        query = """
        SELECT
            id AS brand_id,
            name AS brand_name,
            category AS brand_category,
            country AS brand_country
        FROM brands
        """
        df = pd.read_sql(query, self.conn)
        filepath = self.output_dir / "dim_brands.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["dim_brands"] = str(filepath)
        print(f"  - dim_brands.csv ({len(df)} 条)")

        # 4. 维度表：车型
        print("[4/6] 导出车型维度表...")
        query = """
        SELECT
            m.id AS model_id,
            m.brand_id,
            b.name AS brand_name,
            m.name AS model_name,
            m.series,
            m.year,
            m.energy_type,
            m.body_type,
            m.guide_price_min,
            m.guide_price_max,
            (m.guide_price_min + m.guide_price_max) / 2 AS avg_price
        FROM models m
        JOIN brands b ON m.brand_id = b.id
        """
        df = pd.read_sql(query, self.conn)
        filepath = self.output_dir / "dim_models.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["dim_models"] = str(filepath)
        print(f"  - dim_models.csv ({len(df)} 条)")

        # 5. 维度表：参数
        print("[5/6] 导出参数维度表...")
        query = """
        SELECT
            model_id,
            engine_type,
            displacement,
            horsepower,
            torque,
            transmission,
            drive_type,
            length,
            width,
            height,
            wheelbase,
            curb_weight,
            fuel_consumption,
            battery_capacity,
            range_km,
            acceleration_100,
            top_speed
        FROM specs
        """
        df = pd.read_sql(query, self.conn)
        filepath = self.output_dir / "dim_specs.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["dim_specs"] = str(filepath)
        print(f"  - dim_specs.csv ({len(df)} 条)")

        # 6. 维度表：评分
        print("[6/6] 导出评分维度表...")
        query = """
        SELECT
            model_id,
            overall_score,
            appearance_score,
            interior_score,
            power_score,
            space_score,
            fuel_score,
            handling_score,
            comfort_score,
            value_score,
            review_count
        FROM ratings
        """
        df = pd.read_sql(query, self.conn)
        filepath = self.output_dir / "dim_ratings.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["dim_ratings"] = str(filepath)
        print(f"  - dim_ratings.csv ({len(df)} 条)")

        return files

    def generate_relationship_guide(self) -> str:
        """
        生成关系模型指南

        Returns:
            指南文件路径
        """
        guide = """
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
"""

        filepath = self.output_dir / "PowerBI关系模型指南.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(guide)

        print(f"\n[[OK]] 关系模型指南: {filepath}")
        return str(filepath)

    def export_all(self, year: int = 2024):
        """导出所有 Power BI 数据"""
        print("\n" + "=" * 60)
        print("导出 Power BI 数据")
        print("=" * 60)

        # 导出数据
        files = self.export_for_powerbi(year)

        # 生成关系模型指南
        self.generate_relationship_guide()

        print(f"\n[[OK]] 共导出 {len(files)} 个 CSV 文件")
        print(f"[[OK]] 保存目录: {self.output_dir}")

        return files

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    exporter = PowerBIExporter()
    exporter.export_all()
    exporter.close()
