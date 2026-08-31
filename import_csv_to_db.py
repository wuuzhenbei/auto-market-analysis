"""
将懂车帝CSV数据导入数据库
"""
import csv
import sqlite3
from pathlib import Path


DB_PATH = Path("database/auto_market.db")
CSV_DIR = Path("data/raw/dongchedi")


def import_sales_data():
    """导入销量数据"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # 读取所有CSV文件
    all_data = []
    for csv_file in CSV_DIR.glob("sales_2026_*.csv"):
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_data.append(row)

    print(f"读取到 {len(all_data)} 条数据")

    # 获取品牌和车型ID映射
    brand_ids = {}
    model_ids = {}

    for row in all_data:
        brand_name = row.get("brand", "")
        model_name = row.get("model", "")

        # 确保品牌存在
        if brand_name and brand_name not in brand_ids:
            cursor.execute("SELECT id FROM brands WHERE name = ?", (brand_name,))
            result = cursor.fetchone()
            if result:
                brand_ids[brand_name] = result[0]
            else:
                cursor.execute(
                    "INSERT INTO brands (name, country, category) VALUES (?, ?, ?)",
                    (brand_name, "中国", "自主")
                )
                brand_ids[brand_name] = cursor.lastrowid

        # 确保车型存在
        if model_name:
            cursor.execute("SELECT id FROM models WHERE name = ?", (model_name,))
            result = cursor.fetchone()
            if result:
                model_ids[model_name] = result[0]
            else:
                brand_id = brand_ids.get(brand_name, 1)
                price_min = float(row.get("price_min", 0))
                price_max = float(row.get("price_max", 0))
                body_type = row.get("body_type", "轿车")

                cursor.execute(
                    """INSERT INTO models (name, brand_id, body_type, energy_type,
                       guide_price_min, guide_price_max) VALUES (?, ?, ?, ?, ?, ?)""",
                    (model_name, brand_id, body_type, "燃油", price_min, price_max)
                )
                model_ids[model_name] = cursor.lastrowid

    # 导入销量数据
    imported = 0
    for row in all_data:
        model_name = row.get("model", "")
        if model_name in model_ids:
            model_id = model_ids[model_name]
            year = int(row.get("year", 2026))
            month = int(row.get("month", 1))
            sales_volume = int(row.get("sales", 0))

            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM sales WHERE model_id = ? AND year = ? AND month = ?",
                (model_id, year, month)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO sales (model_id, year, month, sales_volume) VALUES (?, ?, ?, ?)",
                    (model_id, year, month, sales_volume)
                )
                imported += 1

    conn.commit()
    conn.close()

    print(f"成功导入 {imported} 条销量数据")


if __name__ == "__main__":
    import_sales_data()
