"""
品牌分析模块
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH


class BrandAnalyzer:
    """品牌分析器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))

    def get_brand_sales_ranking(self, year: int = 2024) -> pd.DataFrame:
        """
        品牌销量排名

        Returns:
            包含品牌名称、销量、市场份额的 DataFrame
        """
        query = """
        SELECT
            b.name AS brand_name,
            b.category AS brand_category,
            b.country AS brand_country,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ?
        GROUP BY b.id
        ORDER BY total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算市场份额
        total_sales = df["total_sales"].sum()
        df["market_share"] = (df["total_sales"] / total_sales * 100).round(2)

        # 计算累计份额
        df["cumulative_share"] = df["market_share"].cumsum().round(2)

        return df

    def get_brand_category_analysis(self, year: int = 2024) -> pd.DataFrame:
        """
        品牌类别分析（自主/合资/豪华/新势力）

        Returns:
            包含品牌类别、销量、车型数量的 DataFrame
        """
        query = """
        SELECT
            b.category AS brand_category,
            SUM(s.sales_volume) AS total_sales,
            COUNT(DISTINCT m.id) AS model_count,
            ROUND(SUM(s.sales_volume) * 1.0 / COUNT(DISTINCT m.id), 0) AS avg_sales_per_model
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ?
        GROUP BY b.category
        ORDER BY total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算市场份额
        total_sales = df["total_sales"].sum()
        df["market_share"] = (df["total_sales"] / total_sales * 100).round(2)

        return df

    def get_brand_country_analysis(self, year: int = 2024) -> pd.DataFrame:
        """
        品牌国家分析

        Returns:
            包含国家、销量、品牌数量的 DataFrame
        """
        query = """
        SELECT
            b.country AS brand_country,
            SUM(s.sales_volume) AS total_sales,
            COUNT(DISTINCT b.id) AS brand_count,
            COUNT(DISTINCT m.id) AS model_count
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ?
        GROUP BY b.country
        ORDER BY total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算市场份额
        total_sales = df["total_sales"].sum()
        df["market_share"] = (df["total_sales"] / total_sales * 100).round(2)

        return df

    def get_brand_model_count(self) -> pd.DataFrame:
        """
        各品牌车型数量

        Returns:
            包含品牌名称、车型数量的 DataFrame
        """
        query = """
        SELECT
            b.name AS brand_name,
            b.category AS brand_category,
            COUNT(m.id) AS model_count
        FROM brands b
        LEFT JOIN models m ON b.id = m.brand_id
        GROUP BY b.id
        ORDER BY model_count DESC
        """
        return pd.read_sql(query, self.conn)

    def get_brand_avg_rating(self) -> pd.DataFrame:
        """
        各品牌平均评分

        Returns:
            包含品牌名称、各维度平均评分的 DataFrame
        """
        query = """
        SELECT
            b.name AS brand_name,
            b.category AS brand_category,
            ROUND(AVG(r.overall_score), 2) AS avg_overall_score,
            ROUND(AVG(r.appearance_score), 2) AS avg_appearance_score,
            ROUND(AVG(r.interior_score), 2) AS avg_interior_score,
            ROUND(AVG(r.power_score), 2) AS avg_power_score,
            ROUND(AVG(r.space_score), 2) AS avg_space_score,
            ROUND(AVG(r.fuel_score), 2) AS avg_fuel_score,
            ROUND(AVG(r.handling_score), 2) AS avg_handling_score,
            ROUND(AVG(r.comfort_score), 2) AS avg_comfort_score,
            ROUND(AVG(r.value_score), 2) AS avg_value_score,
            COUNT(m.id) AS model_count
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.id
        HAVING model_count >= 2
        ORDER BY avg_overall_score DESC
        """
        return pd.read_sql(query, self.conn)

    def get_top_models_by_brand(self, brand_name: str, year: int = 2024, top_n: int = 5) -> pd.DataFrame:
        """
        指定品牌的热销车型

        Args:
            brand_name: 品牌名称
            year: 年份
            top_n: 返回数量

        Returns:
            包含车型名称、销量的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            m.energy_type,
            m.guide_price_min,
            m.guide_price_max,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE b.name = ? AND s.year = ?
        GROUP BY m.id
        ORDER BY total_sales DESC
        LIMIT ?
        """
        return pd.read_sql(query, self.conn, params=[brand_name, year, top_n])

    def analyze(self) -> dict:
        """运行品牌分析"""
        print("\n" + "=" * 60)
        print("品牌分析")
        print("=" * 60)

        results = {}

        # 1. 品牌销量排名
        print("\n[1/5] 品牌销量排名...")
        results["brand_sales_ranking"] = self.get_brand_sales_ranking()
        print(f"  - 共 {len(results['brand_sales_ranking'])} 个品牌")

        # 2. 品牌类别分析
        print("[2/5] 品牌类别分析...")
        results["brand_category_analysis"] = self.get_brand_category_analysis()

        # 3. 品牌国家分析
        print("[3/5] 品牌国家分析...")
        results["brand_country_analysis"] = self.get_brand_country_analysis()

        # 4. 品牌车型数量
        print("[4/5] 品牌车型数量...")
        results["brand_model_count"] = self.get_brand_model_count()

        # 5. 品牌平均评分
        print("[5/5] 品牌平均评分...")
        results["brand_avg_rating"] = self.get_brand_avg_rating()

        # 打印摘要
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """打印分析摘要"""
        print("\n" + "-" * 60)
        print("品牌分析摘要")
        print("-" * 60)

        # 销量 TOP 10
        print("\n销量 TOP 10 品牌:")
        top10 = results["brand_sales_ranking"].head(10)
        for i, row in top10.iterrows():
            print(f"  {i+1}. {row['brand_name']}: {row['total_sales']:,} 辆 ({row['market_share']}%)")

        # 品牌类别分布
        print("\n品牌类别分布:")
        for _, row in results["brand_category_analysis"].iterrows():
            print(f"  - {row['brand_category']}: {row['total_sales']:,} 辆 ({row['market_share']}%)")

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    analyzer = BrandAnalyzer()
    results = analyzer.analyze()
    analyzer.close()
