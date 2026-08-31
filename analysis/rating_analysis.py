"""
口碑评分分析模块
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, RATING_DIMENSIONS


class RatingAnalyzer:
    """口碑评分分析器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))

    def get_rating_distribution(self) -> pd.DataFrame:
        """
        评分分布

        Returns:
            包含评分区间、车型数量的 DataFrame
        """
        query = """
        SELECT
            CASE
                WHEN overall_score < 3.5 THEN '3.5以下'
                WHEN overall_score < 4.0 THEN '3.5-4.0'
                WHEN overall_score < 4.5 THEN '4.0-4.5'
                ELSE '4.5以上'
            END AS rating_range,
            COUNT(*) AS model_count
        FROM ratings
        GROUP BY rating_range
        ORDER BY MIN(overall_score)
        """
        df = pd.read_sql(query, self.conn)

        # 计算占比
        total = df["model_count"].sum()
        df["percentage"] = (df["model_count"] / total * 100).round(2)

        return df

    def get_brand_rating_ranking(self) -> pd.DataFrame:
        """
        品牌评分排名

        Returns:
            包含品牌、各维度评分的 DataFrame
        """
        query = """
        SELECT
            b.name AS brand_name,
            b.category AS brand_category,
            ROUND(AVG(r.overall_score), 2) AS avg_overall,
            ROUND(AVG(r.appearance_score), 2) AS avg_appearance,
            ROUND(AVG(r.interior_score), 2) AS avg_interior,
            ROUND(AVG(r.power_score), 2) AS avg_power,
            ROUND(AVG(r.space_score), 2) AS avg_space,
            ROUND(AVG(r.fuel_score), 2) AS avg_fuel,
            ROUND(AVG(r.handling_score), 2) AS avg_handling,
            ROUND(AVG(r.comfort_score), 2) AS avg_comfort,
            ROUND(AVG(r.value_score), 2) AS avg_value,
            COUNT(m.id) AS model_count
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.id
        HAVING model_count >= 2
        ORDER BY avg_overall DESC
        """
        return pd.read_sql(query, self.conn)

    def get_model_rating_ranking(self, top_n: int = 20) -> pd.DataFrame:
        """
        车型评分排名

        Returns:
            包含车型、品牌、各维度评分的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
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
        ORDER BY r.overall_score DESC
        LIMIT ?
        """
        return pd.read_sql(query, self.conn, params=[top_n])

    def get_rating_by_energy_type(self) -> pd.DataFrame:
        """
        各能源类型评分对比

        Returns:
            包含能源类型、各维度平均评分的 DataFrame
        """
        query = """
        SELECT
            m.energy_type,
            ROUND(AVG(r.overall_score), 2) AS avg_overall,
            ROUND(AVG(r.appearance_score), 2) AS avg_appearance,
            ROUND(AVG(r.interior_score), 2) AS avg_interior,
            ROUND(AVG(r.power_score), 2) AS avg_power,
            ROUND(AVG(r.space_score), 2) AS avg_space,
            ROUND(AVG(r.fuel_score), 2) AS avg_fuel,
            ROUND(AVG(r.handling_score), 2) AS avg_handling,
            ROUND(AVG(r.comfort_score), 2) AS avg_comfort,
            ROUND(AVG(r.value_score), 2) AS avg_value,
            COUNT(m.id) AS model_count
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        GROUP BY m.energy_type
        ORDER BY avg_overall DESC
        """
        return pd.read_sql(query, self.conn)

    def get_rating_by_price_range(self) -> pd.DataFrame:
        """
        各价格区间评分对比

        Returns:
            包含价格区间、各维度平均评分的 DataFrame
        """
        query = """
        SELECT
            CASE
                WHEN m.guide_price_min < 10 THEN '10万以下'
                WHEN m.guide_price_min < 20 THEN '10-20万'
                WHEN m.guide_price_min < 30 THEN '20-30万'
                WHEN m.guide_price_min < 50 THEN '30-50万'
                ELSE '50万以上'
            END AS price_range,
            ROUND(AVG(r.overall_score), 2) AS avg_overall,
            ROUND(AVG(r.appearance_score), 2) AS avg_appearance,
            ROUND(AVG(r.interior_score), 2) AS avg_interior,
            ROUND(AVG(r.power_score), 2) AS avg_power,
            ROUND(AVG(r.space_score), 2) AS avg_space,
            ROUND(AVG(r.fuel_score), 2) AS avg_fuel,
            ROUND(AVG(r.handling_score), 2) AS avg_handling,
            ROUND(AVG(r.comfort_score), 2) AS avg_comfort,
            ROUND(AVG(r.value_score), 2) AS avg_value,
            COUNT(m.id) AS model_count
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        GROUP BY price_range
        ORDER BY MIN(m.guide_price_min)
        """
        return pd.read_sql(query, self.conn)

    def get_rating_sales_correlation(self, year: int = 2024) -> pd.DataFrame:
        """
        评分与销量相关性分析

        Returns:
            包含车型、评分、销量的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            r.overall_score,
            r.value_score,
            SUM(s.sales_volume) AS total_sales
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        JOIN sales s ON m.id = s.model_id
        WHERE s.year = ?
        GROUP BY m.id
        ORDER BY r.overall_score DESC
        """
        return pd.read_sql(query, self.conn, params=[year])

    def get_dimension_analysis(self) -> pd.DataFrame:
        """
        各维度评分分析

        Returns:
            包含各维度平均分、最高分、最低分的 DataFrame
        """
        dimensions = [
            ("appearance_score", "外观"),
            ("interior_score", "内饰"),
            ("power_score", "动力"),
            ("space_score", "空间"),
            ("fuel_score", "油耗"),
            ("handling_score", "操控"),
            ("comfort_score", "舒适性"),
            ("value_score", "性价比"),
        ]

        results = []
        for col, name in dimensions:
            query = f"""
            SELECT
                ROUND(AVG({col}), 2) AS avg_score,
                ROUND(MIN({col}), 2) AS min_score,
                ROUND(MAX({col}), 2) AS max_score
            FROM ratings
            WHERE {col} IS NOT NULL
            """
            df = pd.read_sql(query, self.conn)
            # 使用 Pandas 计算标准差
            scores = pd.read_sql(f"SELECT {col} FROM ratings WHERE {col} IS NOT NULL", self.conn)
            df["std_score"] = round(scores[col].std(), 2)
            df["dimension"] = name
            results.append(df)

        return pd.concat(results, ignore_index=True)

    def analyze(self) -> dict:
        """运行口碑评分分析"""
        print("\n" + "=" * 60)
        print("口碑评分分析")
        print("=" * 60)

        results = {}

        # 1. 评分分布
        print("\n[1/6] 评分分布...")
        results["rating_distribution"] = self.get_rating_distribution()

        # 2. 品牌评分排名
        print("[2/6] 品牌评分排名...")
        results["brand_rating_ranking"] = self.get_brand_rating_ranking()

        # 3. 车型评分排名
        print("[3/6] 车型评分排名...")
        results["model_rating_ranking"] = self.get_model_rating_ranking()

        # 4. 各能源类型评分
        print("[4/6] 各能源类型评分...")
        results["rating_by_energy_type"] = self.get_rating_by_energy_type()

        # 5. 各价格区间评分
        print("[5/6] 各价格区间评分...")
        results["rating_by_price_range"] = self.get_rating_by_price_range()

        # 6. 各维度分析
        print("[6/6] 各维度分析...")
        results["dimension_analysis"] = self.get_dimension_analysis()

        # 打印摘要
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """打印分析摘要"""
        print("\n" + "-" * 60)
        print("口碑评分分析摘要")
        print("-" * 60)

        # 评分分布
        print("\n评分分布:")
        for _, row in results["rating_distribution"].iterrows():
            print(f"  - {row['rating_range']}: {row['model_count']} 个车型 ({row['percentage']}%)")

        # 品牌评分 TOP 5
        print("\n品牌评分 TOP 5:")
        top5 = results["brand_rating_ranking"].head(5)
        for i, row in top5.iterrows():
            print(f"  {i+1}. {row['brand_name']}: {row['avg_overall']} 分")

        # 车型评分 TOP 5
        print("\n车型评分 TOP 5:")
        top5 = results["model_rating_ranking"].head(5)
        for i, row in top5.iterrows():
            print(f"  {i+1}. {row['brand_name']} {row['model_name']}: {row['overall_score']} 分")

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    analyzer = RatingAnalyzer()
    results = analyzer.analyze()
    analyzer.close()
