"""
数据清洗模块
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, PROCESSED_DATA_DIR


class DataCleaner:
    """数据清洗器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.PROCESSED_DATA_DIR = PROCESSED_DATA_DIR
        self.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> dict:
        """从数据库加载数据"""
        print("[*] 加载数据...")

        data = {}

        # 品牌数据
        data["brands"] = pd.read_sql("SELECT * FROM brands", self.conn)
        print(f"  - 品牌: {len(data['brands'])} 条")

        # 车型数据
        data["models"] = pd.read_sql("SELECT * FROM models", self.conn)
        print(f"  - 车型: {len(data['models'])} 条")

        # 参数数据
        data["specs"] = pd.read_sql("SELECT * FROM specs", self.conn)
        print(f"  - 参数: {len(data['specs'])} 条")

        # 销量数据
        data["sales"] = pd.read_sql("SELECT * FROM sales", self.conn)
        print(f"  - 销量: {len(data['sales'])} 条")

        # 评分数据
        data["ratings"] = pd.read_sql("SELECT * FROM ratings", self.conn)
        print(f"  - 评分: {len(data['ratings'])} 条")

        # 城市销量数据
        data["city_sales"] = pd.read_sql("SELECT * FROM city_sales", self.conn)
        print(f"  - 城市销量: {len(data['city_sales'])} 条")

        return data

    def clean_data(self, data: dict) -> dict:
        """清洗数据"""
        print("\n[*] 清洗数据...")

        # 1. 处理缺失值
        print("  [1/5] 处理缺失值...")
        data = self._handle_missing_values(data)

        # 2. 处理异常值
        print("  [2/5] 处理异常值...")
        data = self._handle_outliers(data)

        # 3. 数据类型转换
        print("  [3/5] 数据类型转换...")
        data = self._convert_types(data)

        # 4. 数据标准化
        print("  [4/5] 数据标准化...")
        data = self._standardize_data(data)

        # 5. 生成衍生字段
        print("  [5/5] 生成衍生字段...")
        data = self._create_derived_fields(data)

        print("[[OK]] 数据清洗完成")
        return data

    def _handle_missing_values(self, data: dict) -> dict:
        """处理缺失值"""
        # 车型数据
        models_df = data["models"]
        models_df["energy_type"] = models_df["energy_type"].fillna("未知")
        models_df["body_type"] = models_df["body_type"].fillna("未知")
        models_df["guide_price_min"] = models_df["guide_price_min"].fillna(0)
        models_df["guide_price_max"] = models_df["guide_price_max"].fillna(0)

        # 参数数据
        specs_df = data["specs"]
        numeric_cols = ["displacement", "horsepower", "torque", "length", "width", "height",
                       "wheelbase", "curb_weight", "fuel_consumption", "battery_capacity",
                       "range_km", "acceleration_100", "top_speed"]
        for col in numeric_cols:
            if col in specs_df.columns:
                specs_df[col] = specs_df[col].fillna(specs_df[col].median())

        # 评分数据
        ratings_df = data["ratings"]
        score_cols = ["overall_score", "appearance_score", "interior_score", "power_score",
                     "space_score", "fuel_score", "handling_score", "comfort_score", "value_score"]
        for col in score_cols:
            if col in ratings_df.columns:
                ratings_df[col] = ratings_df[col].fillna(ratings_df[col].median())

        return data

    def _handle_outliers(self, data: dict) -> dict:
        """处理异常值"""
        # 销量数据 - 移除负数
        sales_df = data["sales"]
        sales_df = sales_df[sales_df["sales_volume"] >= 0]

        # 价格数据 - 移除异常值
        models_df = data["models"]
        models_df = models_df[models_df["guide_price_min"] >= 0]
        models_df = models_df[models_df["guide_price_max"] >= models_df["guide_price_min"]]

        # 评分数据 - 限制在 1-5 范围
        ratings_df = data["ratings"]
        score_cols = ["overall_score", "appearance_score", "interior_score", "power_score",
                     "space_score", "fuel_score", "handling_score", "comfort_score", "value_score"]
        for col in score_cols:
            if col in ratings_df.columns:
                ratings_df[col] = ratings_df[col].clip(1, 5)

        return data

    def _convert_types(self, data: dict) -> dict:
        """数据类型转换"""
        # 车型数据
        models_df = data["models"]
        models_df["year"] = models_df["year"].astype(int)
        models_df["guide_price_min"] = models_df["guide_price_min"].astype(float)
        models_df["guide_price_max"] = models_df["guide_price_max"].astype(float)

        # 销量数据
        sales_df = data["sales"]
        sales_df["year"] = sales_df["year"].astype(int)
        sales_df["month"] = sales_df["month"].astype(int)
        sales_df["sales_volume"] = sales_df["sales_volume"].astype(int)

        return data

    def _standardize_data(self, data: dict) -> dict:
        """数据标准化"""
        # 品牌名称标准化
        brands_df = data["brands"]
        brands_df["name"] = brands_df["name"].str.strip()

        # 车型名称标准化
        models_df = data["models"]
        models_df["name"] = models_df["name"].str.strip()

        # 能源类型标准化
        energy_type_map = {
            "纯电": "纯电动",
            "插混": "插电混动",
            "增程": "增程式",
            "汽油": "燃油",
            "柴油": "燃油",
            "油电混合": "油电混动",
        }
        models_df["energy_type"] = models_df["energy_type"].replace(energy_type_map)

        return data

    def _create_derived_fields(self, data: dict) -> dict:
        """生成衍生字段"""
        models_df = data["models"]

        # 平均价格
        models_df["avg_price"] = (models_df["guide_price_min"] + models_df["guide_price_max"]) / 2

        # 价格区间
        def price_range(price):
            if price < 5:
                return "5万以下"
            elif price < 10:
                return "5-10万"
            elif price < 15:
                return "10-15万"
            elif price < 20:
                return "15-20万"
            elif price < 30:
                return "20-30万"
            elif price < 50:
                return "30-50万"
            elif price < 100:
                return "50-100万"
            else:
                return "100万以上"

        models_df["price_range"] = models_df["guide_price_min"].apply(price_range)

        # 是否新能源
        models_df["is_new_energy"] = models_df["energy_type"].isin(["纯电动", "插电混动", "增程式"])

        # 销量数据 - 计算累计销量
        sales_df = data["sales"]
        cumulative_sales = sales_df.groupby("model_id")["sales_volume"].sum().reset_index()
        cumulative_sales.columns = ["id", "total_sales"]
        models_df = models_df.merge(cumulative_sales, on="id", how="left")
        models_df["total_sales"] = models_df["total_sales"].fillna(0).astype(int)

        data["models"] = models_df

        return data

    def save_processed_data(self, data: dict):
        """保存清洗后的数据"""
        print("\n[*] 保存清洗后的数据...")

        for name, df in data.items():
            filepath = self.PROCESSED_DATA_DIR / f"{name}.csv"
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
            print(f"  - {name}: {filepath}")

        print("[[OK]] 数据保存完成")

    def run(self):
        """运行数据清洗流程"""
        print("=" * 60)
        print("数据清洗")
        print("=" * 60)

        # 加载数据
        data = self.load_data()

        # 清洗数据
        data = self.clean_data(data)

        # 保存数据
        self.save_processed_data(data)

        # 关闭连接
        self.conn.close()

        return data


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.run()
