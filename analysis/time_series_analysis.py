"""
时间序列分析模块
分析月度销量趋势、同比增长、环比变化等
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH


class TimeSeriesAnalyzer:
    """时间序列分析器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))

    def get_monthly_sales_trend(self, start_year=2024, end_year=2026) -> pd.DataFrame:
        """
        月度销量趋势

        Returns:
            包含年月、总销量的 DataFrame
        """
        query = """
        SELECT
            year,
            month,
            SUM(sales_volume) AS total_sales
        FROM sales
        WHERE year >= ? AND year <= ?
        GROUP BY year, month
        ORDER BY year, month
        """
        df = pd.read_sql(query, self.conn, params=[start_year, end_year])
        df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
        return df

    def get_energy_type_monthly_trend(self, start_year=2024, end_year=2026) -> pd.DataFrame:
        """
        各能源类型月度销量趋势

        Returns:
            包含年月、能源类型、销量的 DataFrame
        """
        query = """
        SELECT
            s.year,
            s.month,
            m.energy_type,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year >= ? AND s.year <= ?
        GROUP BY s.year, s.month, m.energy_type
        ORDER BY s.year, s.month, m.energy_type
        """
        df = pd.read_sql(query, self.conn, params=[start_year, end_year])
        df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
        return df

    def get_new_energy_penetration_trend(self, start_year=2024, end_year=2026) -> pd.DataFrame:
        """
        新能源渗透率月度趋势

        Returns:
            包含年月、渗透率的 DataFrame
        """
        query = """
        SELECT
            s.year,
            s.month,
            SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) AS ne_sales,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year >= ? AND s.year <= ?
        GROUP BY s.year, s.month
        ORDER BY s.year, s.month
        """
        df = pd.read_sql(query, self.conn, params=[start_year, end_year])
        df["penetration_rate"] = (df["ne_sales"] / df["total_sales"] * 100).round(2)
        df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
        return df

    def get_brand_monthly_sales(self, brand_name, start_year=2024, end_year=2026) -> pd.DataFrame:
        """
        指定品牌月度销量

        Args:
            brand_name: 品牌名称

        Returns:
            包含年月、销量的 DataFrame
        """
        query = """
        SELECT
            s.year,
            s.month,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE b.name = ? AND s.year >= ? AND s.year <= ?
        GROUP BY s.year, s.month
        ORDER BY s.year, s.month
        """
        df = pd.read_sql(query, self.conn, params=[brand_name, start_year, end_year])
        df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
        return df

    def get_yoy_growth_analysis(self, year=2025) -> pd.DataFrame:
        """
        同比增长率分析

        Args:
            year: 要分析的年份

        Returns:
            包含品牌、同比增长率的 DataFrame
        """
        query = """
        SELECT
            b.name AS brand_name,
            SUM(CASE WHEN s.year = ? THEN s.sales_volume ELSE 0 END) AS current_sales,
            SUM(CASE WHEN s.year = ? - 1 THEN s.sales_volume ELSE 0 END) AS last_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year IN (?, ? - 1)
        GROUP BY b.id
        HAVING last_sales > 0
        ORDER BY current_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year, year, year, year])
        df["yoy_growth"] = ((df["current_sales"] - df["last_sales"]) / df["last_sales"] * 100).round(2)
        return df

    def get_market_share_trend(self, start_year=2024, end_year=2026, top_n=10) -> dict:
        """
        市场份额变化趋势

        Returns:
            包含各品牌市场份额变化的字典
        """
        # 获取TOP N品牌
        query = """
        SELECT b.name
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.id
        ORDER BY SUM(s.sales_volume) DESC
        LIMIT ?
        """
        top_brands = pd.read_sql(query, self.conn, params=[top_n])["name"].tolist()

        # 获取各品牌月度销量
        result = {}
        for brand in top_brands:
            query = """
            SELECT
                s.year,
                s.month,
                SUM(s.sales_volume) AS brand_sales
            FROM sales s
            JOIN models m ON s.model_id = m.id
            JOIN brands b ON m.brand_id = b.id
            WHERE b.name = ? AND s.year >= ? AND s.year <= ?
            GROUP BY s.year, s.month
            ORDER BY s.year, s.month
            """
            brand_df = pd.read_sql(query, self.conn, params=[brand, start_year, end_year])

            # 获取总销量
            total_query = """
            SELECT
                year,
                month,
                SUM(sales_volume) AS total_sales
            FROM sales
            WHERE year >= ? AND year <= ?
            GROUP BY year, month
            ORDER BY year, month
            """
            total_df = pd.read_sql(total_query, self.conn, params=[start_year, end_year])

            # 合并计算市场份额
            merged = pd.merge(brand_df, total_df, on=["year", "month"])
            merged["market_share"] = (merged["brand_sales"] / merged["total_sales"] * 100).round(2)
            merged["year_month"] = merged["year"].astype(str) + "-" + merged["month"].astype(str).str.zfill(2)

            result[brand] = merged

        return result

    def get_seasonal_analysis(self) -> pd.DataFrame:
        """
        季节性分析

        Returns:
            包含月份、平均销量的 DataFrame
        """
        query = """
        SELECT
            month,
            ROUND(AVG(monthly_sales), 0) AS avg_sales
        FROM (
            SELECT
                year,
                month,
                SUM(sales_volume) AS monthly_sales
            FROM sales
            GROUP BY year, month
        )
        GROUP BY month
        ORDER BY month
        """
        return pd.read_sql(query, self.conn)

    def analyze(self) -> dict:
        """运行时间序列分析"""
        print("\n" + "=" * 60)
        print("时间序列分析")
        print("=" * 60)

        results = {}

        # 1. 月度销量趋势
        print("\n[1/5] 月度销量趋势...")
        results["monthly_trend"] = self.get_monthly_sales_trend()
        print(f"  - 获取 {len(results['monthly_trend'])} 个月的数据")

        # 2. 能源类型月度趋势
        print("[2/5] 能源类型月度趋势...")
        results["energy_monthly_trend"] = self.get_energy_type_monthly_trend()

        # 3. 新能源渗透率趋势
        print("[3/5] 新能源渗透率趋势...")
        results["ne_penetration_trend"] = self.get_new_energy_penetration_trend()

        # 4. 同比增长分析
        print("[4/5] 同比增长分析...")
        results["yoy_growth"] = self.get_yoy_growth_analysis(2025)

        # 5. 季节性分析
        print("[5/5] 季节性分析...")
        results["seasonal"] = self.get_seasonal_analysis()

        # 打印摘要
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """打印分析摘要"""
        print("\n" + "-" * 60)
        print("时间序列分析摘要")
        print("-" * 60)

        # 月度趋势
        trend = results["monthly_trend"]
        if len(trend) > 0:
            print(f"\n数据覆盖: {trend['year_month'].iloc[0]} 至 {trend['year_month'].iloc[-1]}")
            print(f"总月数: {len(trend)} 个月")

            # 最高销量月份
            max_idx = trend["total_sales"].idxmax()
            print(f"最高销量月份: {trend.loc[max_idx, 'year_month']} ({trend.loc[max_idx, 'total_sales']:,} 辆)")

            # 最低销量月份
            min_idx = trend["total_sales"].idxmin()
            print(f"最低销量月份: {trend.loc[min_idx, 'year_month']} ({trend.loc[min_idx, 'total_sales']:,} 辆)")

        # 新能源渗透率趋势
        ne_trend = results["ne_penetration_trend"]
        if len(ne_trend) > 0:
            first_rate = ne_trend["penetration_rate"].iloc[0]
            last_rate = ne_trend["penetration_rate"].iloc[-1]
            print(f"\n新能源渗透率: {first_rate}% → {last_rate}% (变化: {last_rate - first_rate:+.1f}%)")

        # 同比增长 TOP 5
        yoy = results["yoy_growth"]
        if len(yoy) > 0 and "yoy_growth" in yoy.columns:
            try:
                yoy["yoy_growth"] = pd.to_numeric(yoy["yoy_growth"], errors="coerce")
                top5 = yoy.nlargest(5, "yoy_growth")
                print(f"\n同比增长 TOP 5:")
                for _, row in top5.iterrows():
                    print(f"  - {row['brand_name']}: {row['yoy_growth']:+.1f}%")
            except:
                print("\n同比增长分析: 数据不足")

        # 季节性分析
        seasonal = results["seasonal"]
        if len(seasonal) > 0:
            peak_month = seasonal.loc[seasonal["avg_sales"].idxmax(), "month"]
            low_month = seasonal.loc[seasonal["avg_sales"].idxmin(), "month"]
            print(f"\n季节性特征:")
            print(f"  - 销量高峰月份: {peak_month}月")
            print(f"  - 销量低谷月份: {low_month}月")

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    analyzer = TimeSeriesAnalyzer()
    results = analyzer.analyze()
    analyzer.close()
