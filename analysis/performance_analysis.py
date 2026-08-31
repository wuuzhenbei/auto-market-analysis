"""
性能参数分析模块
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH


class PerformanceAnalyzer:
    """性能参数分析器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))

    def get_power_analysis(self) -> pd.DataFrame:
        """
        动力参数分析

        Returns:
            包含车型、马力、扭矩、加速的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            m.energy_type,
            m.guide_price_min AS price,
            s.horsepower,
            s.torque,
            s.acceleration_100,
            s.displacement,
            s.engine_type
        FROM specs s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.horsepower IS NOT NULL
        ORDER BY s.horsepower DESC
        """
        return pd.read_sql(query, self.conn)

    def get_power_by_energy_type(self) -> pd.DataFrame:
        """
        各能源类型动力对比

        Returns:
            包含能源类型、平均马力、平均扭矩的 DataFrame
        """
        query = """
        SELECT
            m.energy_type,
            ROUND(AVG(s.horsepower), 0) AS avg_horsepower,
            ROUND(AVG(s.torque), 0) AS avg_torque,
            ROUND(AVG(s.acceleration_100), 1) AS avg_acceleration,
            COUNT(*) AS model_count
        FROM specs s
        JOIN models m ON s.model_id = m.id
        WHERE s.horsepower IS NOT NULL
        GROUP BY m.energy_type
        ORDER BY avg_horsepower DESC
        """
        return pd.read_sql(query, self.conn)

    def get_power_by_price_range(self) -> pd.DataFrame:
        """
        各价格区间动力对比

        Returns:
            包含价格区间、平均马力、平均扭矩的 DataFrame
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
            ROUND(AVG(s.horsepower), 0) AS avg_horsepower,
            ROUND(AVG(s.torque), 0) AS avg_torque,
            ROUND(AVG(s.acceleration_100), 1) AS avg_acceleration,
            COUNT(*) AS model_count
        FROM specs s
        JOIN models m ON s.model_id = m.id
        WHERE s.horsepower IS NOT NULL
        GROUP BY price_range
        ORDER BY MIN(m.guide_price_min)
        """
        return pd.read_sql(query, self.conn)

    def get_fuel_consumption_analysis(self) -> pd.DataFrame:
        """
        油耗分析（燃油车）

        Returns:
            包含车型、油耗、排量的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            m.body_type,
            m.guide_price_min AS price,
            s.fuel_consumption,
            s.displacement,
            s.horsepower,
            s.curb_weight
        FROM specs s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE m.energy_type = '燃油' AND s.fuel_consumption IS NOT NULL
        ORDER BY s.fuel_consumption
        """
        return pd.read_sql(query, self.conn)

    def get_fuel_by_body_type(self) -> pd.DataFrame:
        """
        各车身类型油耗对比

        Returns:
            包含车身类型、平均油耗的 DataFrame
        """
        query = """
        SELECT
            m.body_type,
            ROUND(AVG(s.fuel_consumption), 1) AS avg_fuel_consumption,
            ROUND(MIN(s.fuel_consumption), 1) AS min_fuel_consumption,
            ROUND(MAX(s.fuel_consumption), 1) AS max_fuel_consumption,
            COUNT(*) AS model_count
        FROM specs s
        JOIN models m ON s.model_id = m.id
        WHERE m.energy_type = '燃油' AND s.fuel_consumption IS NOT NULL
        GROUP BY m.body_type
        ORDER BY avg_fuel_consumption
        """
        return pd.read_sql(query, self.conn)

    def get_dimension_analysis(self) -> pd.DataFrame:
        """
        车身尺寸分析

        Returns:
            包含车型、长宽高、轴距的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            m.body_type,
            m.guide_price_min AS price,
            s.length,
            s.width,
            s.height,
            s.wheelbase
        FROM specs s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.length IS NOT NULL
        ORDER BY s.wheelbase DESC
        """
        return pd.read_sql(query, self.conn)

    def get_dimension_by_body_type(self) -> pd.DataFrame:
        """
        各车身类型尺寸对比

        Returns:
            包含车身类型、平均尺寸的 DataFrame
        """
        query = """
        SELECT
            m.body_type,
            ROUND(AVG(s.length), 0) AS avg_length,
            ROUND(AVG(s.width), 0) AS avg_width,
            ROUND(AVG(s.height), 0) AS avg_height,
            ROUND(AVG(s.wheelbase), 0) AS avg_wheelbase,
            COUNT(*) AS model_count
        FROM specs s
        JOIN models m ON s.model_id = m.id
        WHERE s.length IS NOT NULL
        GROUP BY m.body_type
        ORDER BY avg_wheelbase DESC
        """
        return pd.read_sql(query, self.conn)

    def get_performance_value_analysis(self, year: int = 2024) -> pd.DataFrame:
        """
        性能性价比分析（马力/价格）

        Returns:
            包含车型、价格、马力、性价比指数的 DataFrame
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            m.energy_type,
            m.guide_price_min AS price,
            s.horsepower,
            s.torque,
            s.acceleration_100,
            SUM(sl.sales_volume) AS total_sales
        FROM specs s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        JOIN sales sl ON m.id = sl.model_id
        WHERE s.horsepower IS NOT NULL AND m.guide_price_min > 0 AND sl.year = ?
        GROUP BY m.id
        ORDER BY m.guide_price_min
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 计算性能性价比指数（马力/价格）
        df["power_value_index"] = (df["horsepower"] / df["price"]).round(2)

        return df

    def analyze(self) -> dict:
        """运行性能参数分析"""
        print("\n" + "=" * 60)
        print("性能参数分析")
        print("=" * 60)

        results = {}

        # 1. 动力参数分析
        print("\n[1/6] 动力参数分析...")
        results["power_analysis"] = self.get_power_analysis()

        # 2. 各能源类型动力对比
        print("[2/6] 各能源类型动力对比...")
        results["power_by_energy_type"] = self.get_power_by_energy_type()

        # 3. 各价格区间动力对比
        print("[3/6] 各价格区间动力对比...")
        results["power_by_price_range"] = self.get_power_by_price_range()

        # 4. 油耗分析
        print("[4/6] 油耗分析...")
        results["fuel_consumption"] = self.get_fuel_consumption_analysis()

        # 5. 车身尺寸分析
        print("[5/6] 车身尺寸分析...")
        results["dimension_analysis"] = self.get_dimension_analysis()

        # 6. 性能性价比分析
        print("[6/6] 性能性价比分析...")
        results["performance_value"] = self.get_performance_value_analysis()

        # 打印摘要
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """打印分析摘要"""
        print("\n" + "-" * 60)
        print("性能参数分析摘要")
        print("-" * 60)

        # 各能源类型动力
        print("\n各能源类型平均动力:")
        for _, row in results["power_by_energy_type"].iterrows():
            print(f"  - {row['energy_type']}: {row['avg_horsepower']} 马力, {row['avg_torque']} N·m")

        # 各价格区间动力
        print("\n各价格区间平均动力:")
        for _, row in results["power_by_price_range"].iterrows():
            print(f"  - {row['price_range']}: {row['avg_horsepower']} 马力, 0-100km/h {row['avg_acceleration']}s")

        # 油耗 TOP 5
        print("\n油耗最低 TOP 5 (燃油车):")
        top5 = results["fuel_consumption"].head(5)
        for i, row in top5.iterrows():
            print(f"  {i+1}. {row['brand_name']} {row['model_name']}: {row['fuel_consumption']} L/100km")

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    results = analyzer.analyze()
    analyzer.close()
