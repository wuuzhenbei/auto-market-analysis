"""
Excel 导出模块
"""
import sqlite3
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, EXCEL_DIR


class ExcelExporter:
    """Excel 导出器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.output_dir = EXCEL_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_brand_sales(self, year: int = 2024) -> str:
        """
        导出品牌销量数据

        Returns:
            Excel 文件路径
        """
        query = """
        SELECT
            b.name AS 品牌,
            b.category AS 品牌类别,
            b.country AS 国家,
            SUM(s.sales_volume) AS 累计销量,
            ROUND(SUM(s.sales_volume) * 100.0 / (SELECT SUM(sales_volume) FROM sales WHERE year=?), 2) AS 市场份额,
            COUNT(DISTINCT m.id) AS 车型数量
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ?
        GROUP BY b.id
        ORDER BY 累计销量 DESC
        """
        df = pd.read_sql(query, self.conn, params=[year, year])

        filepath = self.output_dir / "品牌销量排名.xlsx"
        df.to_excel(filepath, index=False, sheet_name="品牌销量排名")

        print(f"  - 品牌销量排名: {filepath}")
        return str(filepath)

    def export_model_sales(self, year: int = 2024, top_n: int = 50) -> str:
        """
        导出车型销量数据

        Returns:
            Excel 文件路径
        """
        query = """
        SELECT
            b.name AS 品牌,
            m.name AS 车型,
            m.energy_type AS 能源类型,
            m.body_type AS 车身类型,
            m.guide_price_min AS 最低价,
            m.guide_price_max AS 最高价,
            SUM(s.sales_volume) AS 累计销量
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ?
        GROUP BY m.id
        ORDER BY 累计销量 DESC
        LIMIT ?
        """
        df = pd.read_sql(query, self.conn, params=[year, top_n])

        filepath = self.output_dir / "车型销量排名.xlsx"
        df.to_excel(filepath, index=False, sheet_name="车型销量排名")

        print(f"  - 车型销量排名: {filepath}")
        return str(filepath)

    def export_price_analysis(self) -> str:
        """
        导出价格分析数据

        Returns:
            Excel 文件路径
        """
        # 价格区间分布
        query1 = """
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
            COUNT(*) AS 车型数量
        FROM models
        GROUP BY 价格区间
        ORDER BY MIN(guide_price_min)
        """
        df1 = pd.read_sql(query1, self.conn)

        # 各能源类型价格
        query2 = """
        SELECT
            energy_type AS 能源类型,
            COUNT(*) AS 车型数量,
            ROUND(AVG(guide_price_min), 2) AS 平均最低价,
            ROUND(AVG(guide_price_max), 2) AS 平均最高价,
            ROUND(AVG((guide_price_min + guide_price_max) / 2), 2) AS 平均价格
        FROM models
        GROUP BY energy_type
        ORDER BY 平均价格 DESC
        """
        df2 = pd.read_sql(query2, self.conn)

        # 各品牌类别价格
        query3 = """
        SELECT
            b.category AS 品牌类别,
            COUNT(*) AS 车型数量,
            ROUND(AVG(m.guide_price_min), 2) AS 平均最低价,
            ROUND(AVG(m.guide_price_max), 2) AS 平均最高价,
            ROUND(AVG((m.guide_price_min + m.guide_price_max) / 2), 2) AS 平均价格
        FROM models m
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.category
        ORDER BY 平均价格 DESC
        """
        df3 = pd.read_sql(query3, self.conn)

        filepath = self.output_dir / "价格分析.xlsx"

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df1.to_excel(writer, index=False, sheet_name="价格区间分布")
            df2.to_excel(writer, index=False, sheet_name="能源类型价格")
            df3.to_excel(writer, index=False, sheet_name="品牌类别价格")

        print(f"  - 价格分析: {filepath}")
        return str(filepath)

    def export_energy_analysis(self, year: int = 2024) -> str:
        """
        导出新能源分析数据

        Returns:
            Excel 文件路径
        """
        # 新能源销量
        query1 = """
        SELECT
            m.energy_type AS 能源类型,
            SUM(s.sales_volume) AS 销量,
            COUNT(DISTINCT m.id) AS 车型数量
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year = ?
        GROUP BY m.energy_type
        ORDER BY 销量 DESC
        """
        df1 = pd.read_sql(query1, self.conn, params=[year])

        # 新能源品牌
        query2 = """
        SELECT
            b.name AS 品牌,
            SUM(s.sales_volume) AS 新能源销量,
            COUNT(DISTINCT m.id) AS 车型数量
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ? AND m.energy_type IN ('纯电动', '插电混动', '增程式')
        GROUP BY b.id
        ORDER BY 新能源销量 DESC
        """
        df2 = pd.read_sql(query2, self.conn, params=[year])

        # 新能源车型
        query3 = """
        SELECT
            b.name AS 品牌,
            m.name AS 车型,
            m.energy_type AS 能源类型,
            m.guide_price_min AS 价格,
            s2.range_km AS 续航里程,
            SUM(s.sales_volume) AS 销量
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        LEFT JOIN specs s2 ON m.id = s2.model_id
        WHERE s.year = ? AND m.energy_type IN ('纯电动', '插电混动', '增程式')
        GROUP BY m.id
        ORDER BY 销量 DESC
        """
        df3 = pd.read_sql(query3, self.conn, params=[year])

        filepath = self.output_dir / "新能源分析.xlsx"

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df1.to_excel(writer, index=False, sheet_name="能源类型销量")
            df2.to_excel(writer, index=False, sheet_name="新能源品牌排名")
            df3.to_excel(writer, index=False, sheet_name="新能源车型排名")

        print(f"  - 新能源分析: {filepath}")
        return str(filepath)

    def export_rating_analysis(self) -> str:
        """
        导出口碑评分数据

        Returns:
            Excel 文件路径
        """
        # 品牌评分
        query1 = """
        SELECT
            b.name AS 品牌,
            b.category AS 品牌类别,
            ROUND(AVG(r.overall_score), 2) AS 综合评分,
            ROUND(AVG(r.appearance_score), 2) AS 外观评分,
            ROUND(AVG(r.interior_score), 2) AS 内饰评分,
            ROUND(AVG(r.power_score), 2) AS 动力评分,
            ROUND(AVG(r.space_score), 2) AS 空间评分,
            ROUND(AVG(r.fuel_score), 2) AS 油耗评分,
            ROUND(AVG(r.handling_score), 2) AS 操控评分,
            ROUND(AVG(r.comfort_score), 2) AS 舒适性评分,
            ROUND(AVG(r.value_score), 2) AS 性价比评分,
            COUNT(m.id) AS 车型数量
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.id
        HAVING 车型数量 >= 2
        ORDER BY 综合评分 DESC
        """
        df1 = pd.read_sql(query1, self.conn)

        # 车型评分
        query2 = """
        SELECT
            b.name AS 品牌,
            m.name AS 车型,
            m.energy_type AS 能源类型,
            m.guide_price_min AS 价格,
            r.overall_score AS 综合评分,
            r.appearance_score AS 外观评分,
            r.interior_score AS 内饰评分,
            r.power_score AS 动力评分,
            r.space_score AS 空间评分,
            r.fuel_score AS 油耗评分,
            r.handling_score AS 操控评分,
            r.comfort_score AS 舒适性评分,
            r.value_score AS 性价比评分,
            r.review_count AS 评价数量
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        ORDER BY r.overall_score DESC
        """
        df2 = pd.read_sql(query2, self.conn)

        filepath = self.output_dir / "口碑评分分析.xlsx"

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df1.to_excel(writer, index=False, sheet_name="品牌评分排名")
            df2.to_excel(writer, index=False, sheet_name="车型评分排名")

        print(f"  - 口碑评分分析: {filepath}")
        return str(filepath)

    def export_city_sales(self, year: int = 2024) -> str:
        """
        导出城市销量数据

        Returns:
            Excel 文件路径
        """
        # 城市销量
        query1 = """
        SELECT
            city AS 城市,
            province AS 省份,
            region AS 区域,
            SUM(sales_volume) AS 销量
        FROM city_sales
        WHERE year = ?
        GROUP BY city
        ORDER BY 销量 DESC
        """
        df1 = pd.read_sql(query1, self.conn, params=[year])

        # 区域销量
        query2 = """
        SELECT
            region AS 区域,
            SUM(sales_volume) AS 销量,
            COUNT(DISTINCT city) AS 城市数量
        FROM city_sales
        WHERE year = ?
        GROUP BY region
        ORDER BY 销量 DESC
        """
        df2 = pd.read_sql(query2, self.conn, params=[year])

        filepath = self.output_dir / "城市销量分析.xlsx"

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df1.to_excel(writer, index=False, sheet_name="城市销量排名")
            df2.to_excel(writer, index=False, sheet_name="区域销量分布")

        print(f"  - 城市销量分析: {filepath}")
        return str(filepath)

    def export_comprehensive_data(self, year: int = 2024) -> str:
        """
        导出综合数据（用于数据透视表）

        Returns:
            Excel 文件路径
        """
        query = """
        SELECT
            b.name AS 品牌,
            b.category AS 品牌类别,
            b.country AS 国家,
            m.name AS 车型,
            m.energy_type AS 能源类型,
            m.body_type AS 车身类型,
            m.year AS 年款,
            m.guide_price_min AS 最低价,
            m.guide_price_max AS 最高价,
            (m.guide_price_min + m.guide_price_max) / 2 AS 平均价格,
            s.horsepower AS 马力,
            s.torque AS 扭矩,
            s.fuel_consumption AS 油耗,
            s.range_km AS 续航里程,
            s.length AS 车长,
            s.width AS 车宽,
            s.height AS 车高,
            s.wheelbase AS 轴距,
            r.overall_score AS 综合评分,
            r.value_score AS 性价比评分,
            sl.total_sales AS 累计销量
        FROM models m
        JOIN brands b ON m.brand_id = b.id
        LEFT JOIN specs s ON m.id = s.model_id
        LEFT JOIN ratings r ON m.id = r.model_id
        LEFT JOIN (
            SELECT model_id, SUM(sales_volume) as total_sales
            FROM sales
            WHERE year = ?
            GROUP BY model_id
        ) sl ON m.id = sl.model_id
        ORDER BY sl.total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        filepath = self.output_dir / "综合数据.xlsx"
        df.to_excel(filepath, index=False, sheet_name="综合数据")

        print(f"  - 综合数据: {filepath}")
        return str(filepath)

    def export_all(self, year: int = 2024):
        """导出所有数据"""
        print("\n" + "=" * 60)
        print("导出 Excel 数据")
        print("=" * 60)

        files = []

        print("\n[1/6] 品牌销量数据...")
        files.append(self.export_brand_sales(year))

        print("[2/6] 车型销量数据...")
        files.append(self.export_model_sales(year))

        print("[3/6] 价格分析数据...")
        files.append(self.export_price_analysis())

        print("[4/6] 新能源分析数据...")
        files.append(self.export_energy_analysis(year))

        print("[5/6] 口碑评分数据...")
        files.append(self.export_rating_analysis())

        print("[6/6] 城市销量数据...")
        files.append(self.export_city_sales(year))

        print("\n[额外] 综合数据...")
        files.append(self.export_comprehensive_data(year))

        print(f"\n[[OK]] 共导出 {len(files)} 个 Excel 文件")
        print(f"[[OK]] 保存目录: {self.output_dir}")

        return files

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    exporter = ExcelExporter()
    exporter.export_all()
    exporter.close()
