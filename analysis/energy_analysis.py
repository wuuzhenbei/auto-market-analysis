"""
新能源分析模块
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH


class EnergyAnalyzer:
    """新能源分析器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))

    def get_energy_type_distribution(self) -> pd.DataFrame:
        """
        能源类型分布

        Returns:
            包含能源类型、车型数量、占比的 DataFrame
        """
        query = """
        SELECT
            energy_type,
            COUNT(*) AS model_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM models), 2) AS percentage
        FROM models
        GROUP BY energy_type
        ORDER BY model_count DESC
        """
        return pd.read_sql(query, self.conn)

    def get_energy_type_sales(self, year: int = 2024) -> pd.DataFrame:
        """
        各能源类型销量

        Returns:
            包含能源类型、销量、市场份额的 DataFrame
        """
        query = """
        SELECT
            m.energy_type,
            SUM(s.sales_volume) AS total_sales,
            COUNT(DISTINCT m.id) AS model_count
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year = ?
        GROUP BY m.energy_type
        ORDER BY total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算市场份额
        total_sales = df["total_sales"].sum()
        df["market_share"] = (df["total_sales"] / total_sales * 100).round(2)

        # 计算单车型平均销量
        df["avg_sales_per_model"] = (df["total_sales"] / df["model_count"]).round(0).astype(int)

        return df

    def get_new_energy_penetration(self, year: int = 2024) -> pd.DataFrame:
        """
        新能源渗透率（按月）

        Returns:
            包含月份、新能源销量、总销量、渗透率的 DataFrame
        """
        query = """
        SELECT
            s.month,
            SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) AS new_energy_sales,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year = ?
        GROUP BY s.month
        ORDER BY s.month
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算渗透率
        df["penetration_rate"] = (df["new_energy_sales"] / df["total_sales"] * 100).round(2)

        return df

    def get_ev_vs_phev_analysis(self, year: int = 2024) -> pd.DataFrame:
        """
        纯电动 vs 插电混动 vs 增程式分析

        Returns:
            包含各类型销量、占比的 DataFrame
        """
        query = """
        SELECT
            m.energy_type,
            SUM(s.sales_volume) AS total_sales,
            COUNT(DISTINCT m.id) AS model_count,
            ROUND(AVG(m.guide_price_min), 2) AS avg_price,
            ROUND(AVG(s2.range_km), 0) AS avg_range,
            ROUND(AVG(s2.horsepower), 0) AS avg_horsepower
        FROM sales s
        JOIN models m ON s.model_id = m.id
        LEFT JOIN specs s2 ON m.id = s2.model_id
        WHERE s.year = ? AND m.energy_type IN ('纯电动', '插电混动', '增程式')
        GROUP BY m.energy_type
        ORDER BY total_sales DESC
        """
        return pd.read_sql(query, self.conn, params=[year])

    def get_new_energy_brands(self, year: int = 2024) -> pd.DataFrame:
        """
        新能源品牌销量排名

        Returns:
            包含品牌、新能源销量、市场份额的 DataFrame
        """
        query = """
        SELECT
            b.name AS brand_name,
            b.category AS brand_category,
            SUM(s.sales_volume) AS total_sales,
            COUNT(DISTINCT m.id) AS model_count
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ? AND m.energy_type IN ('纯电动', '插电混动', '增程式')
        GROUP BY b.id
        ORDER BY total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算市场份额
        total_sales = df["total_sales"].sum()
        df["market_share"] = (df["total_sales"] / total_sales * 100).round(2)

        return df

    def get_new_energy_models(self, year: int = 2024, top_n: int = 20) -> pd.DataFrame:
        """
        新能源车型销量排名

        Returns:
            包含车型、品牌、销量、续航的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            m.energy_type,
            m.guide_price_min AS price,
            s2.range_km AS range_km,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        LEFT JOIN specs s2 ON m.id = s2.model_id
        WHERE s.year = ? AND m.energy_type IN ('纯电动', '插电混动', '增程式')
        GROUP BY m.id
        ORDER BY total_sales DESC
        LIMIT ?
        """
        return pd.read_sql(query, self.conn, params=[year, top_n])

    def get_range_analysis(self) -> pd.DataFrame:
        """
        续航里程分析（纯电动）

        Returns:
            包含续航区间、车型数量的 DataFrame
        """
        query = """
        SELECT
            CASE
                WHEN s.range_km < 300 THEN '300km以下'
                WHEN s.range_km < 400 THEN '300-400km'
                WHEN s.range_km < 500 THEN '400-500km'
                WHEN s.range_km < 600 THEN '500-600km'
                WHEN s.range_km < 700 THEN '600-700km'
                ELSE '700km以上'
            END AS range_group,
            COUNT(*) AS model_count,
            ROUND(AVG(m.guide_price_min), 2) AS avg_price
        FROM specs s
        JOIN models m ON s.model_id = m.id
        WHERE m.energy_type = '纯电动' AND s.range_km IS NOT NULL
        GROUP BY range_group
        ORDER BY MIN(s.range_km)
        """
        return pd.read_sql(query, self.conn)

    def analyze(self) -> dict:
        """运行新能源分析"""
        print("\n" + "=" * 60)
        print("新能源分析")
        print("=" * 60)

        results = {}

        # 1. 能源类型分布
        print("\n[1/6] 能源类型分布...")
        results["energy_type_distribution"] = self.get_energy_type_distribution()

        # 2. 各能源类型销量
        print("[2/6] 各能源类型销量...")
        results["energy_type_sales"] = self.get_energy_type_sales()

        # 3. 新能源渗透率
        print("[3/6] 新能源渗透率...")
        results["new_energy_penetration"] = self.get_new_energy_penetration()

        # 4. 纯电动 vs 插电混动
        print("[4/6] 纯电动 vs 插电混动分析...")
        results["ev_vs_phev"] = self.get_ev_vs_phev_analysis()

        # 5. 新能源品牌排名
        print("[5/6] 新能源品牌排名...")
        results["new_energy_brands"] = self.get_new_energy_brands()

        # 6. 续航分析
        print("[6/6] 续航分析...")
        results["range_analysis"] = self.get_range_analysis()

        # 打印摘要
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """打印分析摘要"""
        print("\n" + "-" * 60)
        print("新能源分析摘要")
        print("-" * 60)

        # 能源类型销量
        print("\n各能源类型销量占比:")
        for _, row in results["energy_type_sales"].iterrows():
            print(f"  - {row['energy_type']}: {row['total_sales']:,} 辆 ({row['market_share']}%)")

        # 新能源渗透率
        penetration = results["new_energy_penetration"]
        avg_penetration = penetration["penetration_rate"].mean()
        print(f"\n2024年新能源平均渗透率: {avg_penetration:.1f}%")

        # 新能源品牌 TOP 5
        print("\n新能源品牌 TOP 5:")
        top5 = results["new_energy_brands"].head(5)
        for i, row in top5.iterrows():
            print(f"  {i+1}. {row['brand_name']}: {row['total_sales']:,} 辆 ({row['market_share']}%)")

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    analyzer = EnergyAnalyzer()
    results = analyzer.analyze()
    analyzer.close()
