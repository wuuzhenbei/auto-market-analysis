"""
价格分析模块
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, PRICE_RANGES


class PriceAnalyzer:
    """价格分析器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))

    def get_price_distribution(self) -> pd.DataFrame:
        """
        价格区间分布

        Returns:
            包含价格区间、车型数量、占比的 DataFrame
        """
        query = """
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
            END AS price_range,
            COUNT(*) AS model_count
        FROM models
        GROUP BY price_range
        ORDER BY MIN(guide_price_min)
        """
        df = pd.read_sql(query, self.conn)

        # 计算占比
        total = df["model_count"].sum()
        df["percentage"] = (df["model_count"] / total * 100).round(2)

        return df

    def get_price_sales_distribution(self, year: int = 2024) -> pd.DataFrame:
        """
        各价格区间销量分布

        Returns:
            包含价格区间、销量、市场份额的 DataFrame
        """
        query = """
        SELECT
            CASE
                WHEN m.guide_price_min < 5 THEN '5万以下'
                WHEN m.guide_price_min < 10 THEN '5-10万'
                WHEN m.guide_price_min < 15 THEN '10-15万'
                WHEN m.guide_price_min < 20 THEN '15-20万'
                WHEN m.guide_price_min < 30 THEN '20-30万'
                WHEN m.guide_price_min < 50 THEN '30-50万'
                WHEN m.guide_price_min < 100 THEN '50-100万'
                ELSE '100万以上'
            END AS price_range,
            SUM(s.sales_volume) AS total_sales,
            COUNT(DISTINCT m.id) AS model_count
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year = ?
        GROUP BY price_range
        ORDER BY MIN(m.guide_price_min)
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算市场份额
        total_sales = df["total_sales"].sum()
        df["market_share"] = (df["total_sales"] / total_sales * 100).round(2)

        # 计算单车型平均销量
        df["avg_sales_per_model"] = (df["total_sales"] / df["model_count"]).round(0).astype(int)

        return df

    def get_price_by_energy_type(self) -> pd.DataFrame:
        """
        各能源类型价格分布

        Returns:
            包含能源类型、平均价格、价格区间的 DataFrame
        """
        query = """
        SELECT
            energy_type,
            COUNT(*) AS model_count,
            ROUND(AVG(guide_price_min), 2) AS avg_min_price,
            ROUND(AVG(guide_price_max), 2) AS avg_max_price,
            ROUND(AVG((guide_price_min + guide_price_max) / 2), 2) AS avg_price,
            MIN(guide_price_min) AS min_price,
            MAX(guide_price_max) AS max_price
        FROM models
        GROUP BY energy_type
        ORDER BY avg_price DESC
        """
        return pd.read_sql(query, self.conn)

    def get_price_by_body_type(self) -> pd.DataFrame:
        """
        各车身类型价格分布

        Returns:
            包含车身类型、平均价格、价格区间的 DataFrame
        """
        query = """
        SELECT
            body_type,
            COUNT(*) AS model_count,
            ROUND(AVG(guide_price_min), 2) AS avg_min_price,
            ROUND(AVG(guide_price_max), 2) AS avg_max_price,
            ROUND(AVG((guide_price_min + guide_price_max) / 2), 2) AS avg_price,
            MIN(guide_price_min) AS min_price,
            MAX(guide_price_max) AS max_price
        FROM models
        GROUP BY body_type
        ORDER BY avg_price DESC
        """
        return pd.read_sql(query, self.conn)

    def get_price_by_brand_category(self) -> pd.DataFrame:
        """
        各品牌类别价格分布

        Returns:
            包含品牌类别、平均价格、价格区间的 DataFrame
        """
        query = """
        SELECT
            b.category AS brand_category,
            COUNT(*) AS model_count,
            ROUND(AVG(m.guide_price_min), 2) AS avg_min_price,
            ROUND(AVG(m.guide_price_max), 2) AS avg_max_price,
            ROUND(AVG((m.guide_price_min + m.guide_price_max) / 2), 2) AS avg_price,
            MIN(m.guide_price_min) AS min_price,
            MAX(m.guide_price_max) AS max_price
        FROM models m
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.category
        ORDER BY avg_price DESC
        """
        return pd.read_sql(query, self.conn)

    def get_price_sales_correlation(self, year: int = 2024) -> pd.DataFrame:
        """
        价格与销量相关性分析

        Returns:
            包含价格、销量的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            m.guide_price_min AS price,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ? AND m.guide_price_min > 0
        GROUP BY m.id
        ORDER BY m.guide_price_min
        """
        return pd.read_sql(query, self.conn, params=[year])

    def get_value_analysis(self, year: int = 2024) -> pd.DataFrame:
        """
        性价比分析（价格 vs 评分）

        Returns:
            包含车型、价格、评分、性价比指数的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            m.guide_price_min AS price,
            r.overall_score,
            r.value_score,
            SUM(s.sales_volume) AS total_sales
        FROM models m
        JOIN brands b ON m.brand_id = b.id
        JOIN ratings r ON m.id = r.model_id
        JOIN sales s ON m.id = s.model_id
        WHERE s.year = ? AND m.guide_price_min > 0
        GROUP BY m.id
        ORDER BY m.guide_price_min
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算性价比指数（评分/价格 * 100）
        df["value_index"] = (df["overall_score"] / df["price"] * 100).round(2)

        return df

    def analyze(self) -> dict:
        """运行价格分析"""
        print("\n" + "=" * 60)
        print("价格分析")
        print("=" * 60)

        results = {}

        # 1. 价格区间分布
        print("\n[1/6] 价格区间分布...")
        results["price_distribution"] = self.get_price_distribution()

        # 2. 各价格区间销量分布
        print("[2/6] 各价格区间销量分布...")
        results["price_sales_distribution"] = self.get_price_sales_distribution()

        # 3. 各能源类型价格分布
        print("[3/6] 各能源类型价格分布...")
        results["price_by_energy_type"] = self.get_price_by_energy_type()

        # 4. 各车身类型价格分布
        print("[4/6] 各车身类型价格分布...")
        results["price_by_body_type"] = self.get_price_by_body_type()

        # 5. 各品牌类别价格分布
        print("[5/6] 各品牌类别价格分布...")
        results["price_by_brand_category"] = self.get_price_by_brand_category()

        # 6. 性价比分析
        print("[6/6] 性价比分析...")
        results["value_analysis"] = self.get_value_analysis()

        # 打印摘要
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """打印分析摘要"""
        print("\n" + "-" * 60)
        print("价格分析摘要")
        print("-" * 60)

        # 价格区间分布
        print("\n车型价格区间分布:")
        for _, row in results["price_distribution"].iterrows():
            print(f"  - {row['price_range']}: {row['model_count']} 个车型 ({row['percentage']}%)")

        # 销量分布
        print("\n各价格区间销量占比:")
        for _, row in results["price_sales_distribution"].iterrows():
            print(f"  - {row['price_range']}: {row['total_sales']:,} 辆 ({row['market_share']}%)")

        # 能源类型价格
        print("\n各能源类型平均价格:")
        for _, row in results["price_by_energy_type"].iterrows():
            print(f"  - {row['energy_type']}: {row['avg_price']:.1f} 万元")

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    analyzer = PriceAnalyzer()
    results = analyzer.analyze()
    analyzer.close()
