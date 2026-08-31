"""
Tableau 数据导出模块
"""
import sqlite3
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, TABLEAU_DIR


class TableauExporter:
    """Tableau 数据导出器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.output_dir = TABLEAU_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_for_tableau(self, year: int = 2024) -> dict:
        """
        导出 Tableau 可用的 CSV 数据

        Returns:
            导出文件路径字典
        """
        files = {}

        # 1. 品牌数据
        print("\n[1/5] 导出品牌数据...")
        query = """
        SELECT
            b.id AS brand_id,
            b.name AS brand_name,
            b.category AS brand_category,
            b.country AS brand_country,
            COUNT(DISTINCT m.id) AS model_count,
            COALESCE(SUM(s.sales_volume), 0) AS total_sales
        FROM brands b
        LEFT JOIN models m ON b.id = m.brand_id
        LEFT JOIN sales s ON m.id = s.model_id AND s.year = ?
        GROUP BY b.id
        """
        df = pd.read_sql(query, self.conn, params=[year])
        filepath = self.output_dir / "brands.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["brands"] = str(filepath)
        print(f"  - brands.csv ({len(df)} 条)")

        # 2. 车型数据
        print("[2/5] 导出车型数据...")
        query = """
        SELECT
            m.id AS model_id,
            m.brand_id,
            b.name AS brand_name,
            b.category AS brand_category,
            m.name AS model_name,
            m.series,
            m.year,
            m.energy_type,
            m.body_type,
            m.guide_price_min,
            m.guide_price_max,
            (m.guide_price_min + m.guide_price_max) / 2 AS avg_price,
            s.horsepower,
            s.torque,
            s.fuel_consumption,
            s.range_km,
            s.length,
            s.width,
            s.height,
            s.wheelbase,
            r.overall_score,
            r.value_score,
            COALESCE(sl.total_sales, 0) AS total_sales
        FROM models m
        JOIN brands b ON m.brand_id = b.id
        LEFT JOIN specs s ON m.id = s.model_id
        LEFT JOIN ratings r ON m.id = r.model_id
        LEFT JOIN (
            SELECT model_id, SUM(sales_volume) as total_sales
            FROM sales WHERE year = ?
            GROUP BY model_id
        ) sl ON m.id = sl.model_id
        """
        df = pd.read_sql(query, self.conn, params=[year])
        filepath = self.output_dir / "models.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["models"] = str(filepath)
        print(f"  - models.csv ({len(df)} 条)")

        # 3. 月度销量数据
        print("[3/5] 导出月度销量数据...")
        query = """
        SELECT
            s.model_id,
            b.name AS brand_name,
            m.name AS model_name,
            m.energy_type,
            m.body_type,
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
        filepath = self.output_dir / "monthly_sales.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["monthly_sales"] = str(filepath)
        print(f"  - monthly_sales.csv ({len(df)} 条)")

        # 4. 城市销量数据
        print("[4/5] 导出城市销量数据...")
        query = """
        SELECT
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
        filepath = self.output_dir / "city_sales.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["city_sales"] = str(filepath)
        print(f"  - city_sales.csv ({len(df)} 条)")

        # 5. 评分数据
        print("[5/5] 导出评分数据...")
        query = """
        SELECT
            r.model_id,
            b.name AS brand_name,
            m.name AS model_name,
            m.energy_type,
            m.guide_price_min AS price,
            r.overall_score,
            r.appearance_score,
            r.interior_score,
            r.power_score,
            r.space_score,
            r.fuel_score,
            r.handling_score,
            r.comfort_score,
            r.value_score,
            r.review_count
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        """
        df = pd.read_sql(query, self.conn)
        filepath = self.output_dir / "ratings.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        files["ratings"] = str(filepath)
        print(f"  - ratings.csv ({len(df)} 条)")

        return files

    def generate_data_dictionary(self) -> str:
        """
        生成数据字典

        Returns:
            数据字典文件路径
        """
        dictionary = """
# Tableau 数据字典

## 数据表说明

### 1. brands.csv - 品牌数据
| 字段名 | 类型 | 说明 |
|--------|------|------|
| brand_id | 整数 | 品牌唯一标识 |
| brand_name | 字符串 | 品牌名称 |
| brand_category | 字符串 | 品牌类别：自主/合资/豪华/新势力 |
| brand_country | 字符串 | 品牌国家 |
| model_count | 整数 | 旗下车型数量 |
| total_sales | 整数 | 年度总销量 |

### 2. models.csv - 车型数据
| 字段名 | 类型 | 说明 |
|--------|------|------|
| model_id | 整数 | 车型唯一标识 |
| brand_id | 整数 | 所属品牌ID |
| brand_name | 字符串 | 品牌名称 |
| brand_category | 字符串 | 品牌类别 |
| model_name | 字符串 | 车型名称 |
| series | 字符串 | 车系 |
| year | 整数 | 年款 |
| energy_type | 字符串 | 能源类型：纯电动/插电混动/增程式/燃油/油电混动 |
| body_type | 字符串 | 车身类型：轿车/SUV/MPV |
| guide_price_min | 浮点数 | 最低指导价（万元） |
| guide_price_max | 浮点数 | 最高指导价（万元） |
| avg_price | 浮点数 | 平均价格（万元） |
| horsepower | 整数 | 马力（ps） |
| torque | 整数 | 扭矩（N·m） |
| fuel_consumption | 浮点数 | 综合油耗（L/100km） |
| range_km | 整数 | 纯电续航（km） |
| length | 浮点数 | 车长（mm） |
| width | 浮点数 | 车宽（mm） |
| height | 浮点数 | 车高（mm） |
| wheelbase | 浮点数 | 轴距（mm） |
| overall_score | 浮点数 | 综合评分（1-5分） |
| value_score | 浮点数 | 性价比评分（1-5分） |
| total_sales | 整数 | 年度累计销量 |

### 3. monthly_sales.csv - 月度销量数据
| 字段名 | 类型 | 说明 |
|--------|------|------|
| model_id | 整数 | 车型ID |
| brand_name | 字符串 | 品牌名称 |
| model_name | 字符串 | 车型名称 |
| energy_type | 字符串 | 能源类型 |
| body_type | 字符串 | 车身类型 |
| price | 浮点数 | 最低指导价 |
| year | 整数 | 年份 |
| month | 整数 | 月份 |
| sales_volume | 整数 | 月销量 |
| yoy_growth | 浮点数 | 同比增长率（%） |
| mom_growth | 浮点数 | 环比增长率（%） |
| ranking | 整数 | 排名 |

### 4. city_sales.csv - 城市销量数据
| 字段名 | 类型 | 说明 |
|--------|------|------|
| model_id | 整数 | 车型ID |
| brand_name | 字符串 | 品牌名称 |
| model_name | 字符串 | 车型名称 |
| energy_type | 字符串 | 能源类型 |
| city | 字符串 | 城市 |
| province | 字符串 | 省份 |
| region | 字符串 | 区域：华东/华南/华北/华中/西南/西北/东北 |
| sales_volume | 整数 | 销量 |
| year | 整数 | 年份 |
| month | 整数 | 月份 |

### 5. ratings.csv - 评分数据
| 字段名 | 类型 | 说明 |
|--------|------|------|
| model_id | 整数 | 车型ID |
| brand_name | 字符串 | 品牌名称 |
| model_name | 字符串 | 车型名称 |
| energy_type | 字符串 | 能源类型 |
| price | 浮点数 | 最低指导价 |
| overall_score | 浮点数 | 综合评分 |
| appearance_score | 浮点数 | 外观评分 |
| interior_score | 浮点数 | 内饰评分 |
| power_score | 浮点数 | 动力评分 |
| space_score | 浮点数 | 空间评分 |
| fuel_score | 浮点数 | 油耗评分 |
| handling_score | 浮点数 | 操控评分 |
| comfort_score | 浮点数 | 舒适性评分 |
| value_score | 浮点数 | 性价比评分 |
| review_count | 整数 | 评价数量 |

## 数据关系

```
brands (1) ──→ (N) models
models (1) ──→ (1) specs
models (1) ──→ (N) sales
models (1) ──→ (1) ratings
models (1) ──→ (N) city_sales
```

## Tableau 连接建议

1. 使用 `model_id` 作为主键连接各表
2. 日期字段建议使用 `year` + `month` 组合
3. 地理字段使用 `city`、`province`、`region`
4. 数值字段可直接用于度量
5. 分类字段（品牌、能源类型、车身类型等）用于维度
"""

        filepath = self.output_dir / "数据字典.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(dictionary)

        print(f"\n[[OK]] 数据字典: {filepath}")
        return str(filepath)

    def export_all(self, year: int = 2024):
        """导出所有 Tableau 数据"""
        print("\n" + "=" * 60)
        print("导出 Tableau 数据")
        print("=" * 60)

        # 导出数据
        files = self.export_for_tableau(year)

        # 生成数据字典
        self.generate_data_dictionary()

        print(f"\n[[OK]] 共导出 {len(files)} 个 CSV 文件")
        print(f"[[OK]] 保存目录: {self.output_dir}")

        return files

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    exporter = TableauExporter()
    exporter.export_all()
    exporter.close()
