"""
示例数据生成模块 - 生成真实的汽车市场数据用于演示
"""
import random
from datetime import datetime


def generate_sample_data(conn):
    """生成示例数据"""
    cursor = conn.cursor()

    # ============ 品牌数据 ============
    brands = [
        # 自主品牌
        ("比亚迪", "中国", "自主"),
        ("吉利", "中国", "自主"),
        ("长安", "中国", "自主"),
        ("长城", "中国", "自主"),
        ("奇瑞", "中国", "自主"),
        ("广汽", "中国", "自主"),
        ("上汽", "中国", "自主"),
        ("红旗", "中国", "自主"),
        # 新势力
        ("蔚来", "中国", "新势力"),
        ("小鹏", "中国", "新势力"),
        ("理想", "中国", "新势力"),
        ("哪吒", "中国", "新势力"),
        ("零跑", "中国", "新势力"),
        ("极氪", "中国", "新势力"),
        ("问界", "中国", "新势力"),
        ("小米", "中国", "新势力"),
        # 合资品牌
        ("大众", "德国", "合资"),
        ("丰田", "日本", "合资"),
        ("本田", "日本", "合资"),
        ("日产", "日本", "合资"),
        ("别克", "美国", "合资"),
        ("现代", "韩国", "合资"),
        ("起亚", "韩国", "合资"),
        ("福特", "美国", "合资"),
        # 豪华品牌
        ("奔驰", "德国", "豪华"),
        ("宝马", "德国", "豪华"),
        ("奥迪", "德国", "豪华"),
        ("沃尔沃", "瑞典", "豪华"),
        ("凯迪拉克", "美国", "豪华"),
        ("雷克萨斯", "日本", "豪华"),
    ]

    cursor.executemany(
        "INSERT INTO brands (name, country, category) VALUES (?, ?, ?)",
        brands
    )

    # 获取品牌ID映射
    cursor.execute("SELECT id, name FROM brands")
    brand_map = {name: id for id, name in cursor.fetchall()}

    # ============ 车型数据 ============
    models_data = [
        # 比亚迪
        (brand_map["比亚迪"], "秦PLUS DM-i", "秦", 2024, "插电混动", "轿车", 9.98, 14.58),
        (brand_map["比亚迪"], "汉EV", "汉", 2024, "纯电动", "轿车", 20.98, 32.98),
        (brand_map["比亚迪"], "宋PLUS DM-i", "宋", 2024, "插电混动", "SUV", 13.58, 17.58),
        (brand_map["比亚迪"], "海豚", "海洋", 2024, "纯电动", "轿车", 9.68, 12.68),
        (brand_map["比亚迪"], "元PLUS", "元", 2024, "纯电动", "SUV", 12.98, 15.98),
        (brand_map["比亚迪"], "唐DM-i", "唐", 2024, "插电混动", "SUV", 20.58, 24.58),
        (brand_map["比亚迪"], "海豹", "海洋", 2024, "纯电动", "轿车", 16.68, 26.68),

        # 吉利
        (brand_map["吉利"], "星越L", "星", 2024, "燃油", "SUV", 13.72, 18.52),
        (brand_map["吉利"], "帝豪", "帝豪", 2024, "燃油", "轿车", 6.98, 9.88),
        (brand_map["吉利"], "银河L7", "银河", 2024, "插电混动", "SUV", 13.87, 17.37),
        (brand_map["吉利"], "极氪001", "极氪", 2024, "纯电动", "轿车", 26.90, 36.90),

        # 长安
        (brand_map["长安"], "CS75 PLUS", "CS", 2024, "燃油", "SUV", 10.19, 15.49),
        (brand_map["长安"], "逸动PLUS", "逸动", 2024, "燃油", "轿车", 7.19, 10.39),
        (brand_map["长安"], "深蓝SL03", "深蓝", 2024, "纯电动", "轿车", 14.59, 22.19),
        (brand_map["长安"], "阿维塔11", "阿维塔", 2024, "纯电动", "SUV", 31.99, 60.00),

        # 长城
        (brand_map["长城"], "哈弗H6", "哈弗", 2024, "燃油", "SUV", 9.89, 15.70),
        (brand_map["长城"], "坦克300", "坦克", 2024, "燃油", "SUV", 19.58, 24.38),
        (brand_map["长城"], "魏牌蓝山", "魏牌", 2024, "插电混动", "SUV", 27.38, 30.88),

        # 蔚来
        (brand_map["蔚来"], "ET5", "ET", 2024, "纯电动", "轿车", 29.80, 35.60),
        (brand_map["蔚来"], "ES6", "ES", 2024, "纯电动", "SUV", 33.80, 41.60),
        (brand_map["蔚来"], "ET7", "ET", 2024, "纯电动", "轿车", 42.80, 53.60),

        # 小鹏
        (brand_map["小鹏"], "P7", "P", 2024, "纯电动", "轿车", 20.99, 28.99),
        (brand_map["小鹏"], "G6", "G", 2024, "纯电动", "SUV", 18.99, 22.69),
        (brand_map["小鹏"], "X9", "X", 2024, "纯电动", "MPV", 35.98, 41.98),

        # 理想
        (brand_map["理想"], "L7", "L", 2024, "增程式", "SUV", 31.98, 37.98),
        (brand_map["理想"], "L8", "L", 2024, "增程式", "SUV", 33.98, 39.98),
        (brand_map["理想"], "L9", "L", 2024, "增程式", "SUV", 42.98, 45.98),
        (brand_map["理想"], "MEGA", "MEGA", 2024, "纯电动", "MPV", 55.98, 55.98),

        # 问界
        (brand_map["问界"], "M5", "M", 2024, "增程式", "SUV", 24.98, 33.18),
        (brand_map["问界"], "M7", "M", 2024, "增程式", "SUV", 24.98, 37.98),
        (brand_map["问界"], "M9", "M", 2024, "增程式", "SUV", 46.98, 56.98),

        # 小米
        (brand_map["小米"], "SU7", "SU", 2024, "纯电动", "轿车", 21.59, 29.99),
        (brand_map["小米"], "SU7 Ultra", "SU", 2024, "纯电动", "轿车", 52.99, 52.99),

        # 大众
        (brand_map["大众"], "朗逸", "朗逸", 2024, "燃油", "轿车", 9.99, 15.89),
        (brand_map["大众"], "帕萨特", "帕萨特", 2024, "燃油", "轿车", 18.19, 25.29),
        (brand_map["大众"], "途观L", "途观", 2024, "燃油", "SUV", 19.90, 28.50),
        (brand_map["大众"], "ID.4 CROZZ", "ID", 2024, "纯电动", "SUV", 19.39, 29.39),

        # 丰田
        (brand_map["丰田"], "卡罗拉", "卡罗拉", 2024, "燃油", "轿车", 10.98, 15.98),
        (brand_map["丰田"], "凯美瑞", "凯美瑞", 2024, "燃油", "轿车", 17.18, 26.98),
        (brand_map["丰田"], "RAV4荣放", "RAV4", 2024, "燃油", "SUV", 17.58, 25.98),
        (brand_map["丰田"], "汉兰达", "汉兰达", 2024, "燃油", "SUV", 26.88, 34.88),

        # 本田
        (brand_map["本田"], "思域", "思域", 2024, "燃油", "轿车", 12.99, 18.79),
        (brand_map["本田"], "雅阁", "雅阁", 2024, "燃油", "轿车", 17.98, 25.98),
        (brand_map["本田"], "CR-V", "CR-V", 2024, "燃油", "SUV", 18.59, 24.99),

        # 奔驰
        (brand_map["奔驰"], "C级", "C", 2024, "燃油", "轿车", 32.52, 41.42),
        (brand_map["奔驰"], "E级", "E", 2024, "燃油", "轿车", 43.80, 55.80),
        (brand_map["奔驰"], "GLC", "GLC", 2024, "燃油", "SUV", 42.72, 53.13),
        (brand_map["奔驰"], "EQC", "EQ", 2024, "纯电动", "SUV", 49.98, 57.98),

        # 宝马
        (brand_map["宝马"], "3系", "3", 2024, "燃油", "轿车", 29.99, 39.99),
        (brand_map["宝马"], "5系", "5", 2024, "燃油", "轿车", 43.99, 56.99),
        (brand_map["宝马"], "X3", "X", 2024, "燃油", "SUV", 38.98, 47.98),
        (brand_map["宝马"], "i3", "i", 2024, "纯电动", "轿车", 34.99, 41.99),

        # 奥迪
        (brand_map["奥迪"], "A4L", "A", 2024, "燃油", "轿车", 30.98, 39.98),
        (brand_map["奥迪"], "A6L", "A", 2024, "燃油", "轿车", 41.98, 65.38),
        (brand_map["奥迪"], "Q5L", "Q", 2024, "燃油", "SUV", 38.78, 48.78),
        (brand_map["奥迪"], "e-tron", "e", 2024, "纯电动", "SUV", 54.68, 64.88),
    ]

    for m in models_data:
        cursor.execute("""
            INSERT INTO models (brand_id, name, series, year, energy_type, body_type, guide_price_min, guide_price_max)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, m)

    # 获取车型ID映射
    cursor.execute("SELECT id, name FROM models")
    model_map = {name: id for id, name in cursor.fetchall()}

    # ============ 参数数据 ============
    specs_data = []
    for model_name, model_id in model_map.items():
        # 根据车型生成合理的参数
        energy_type = next(m[4] for m in models_data if m[1] == model_name)

        if energy_type == "纯电动":
            specs_data.append((
                model_id,
                "纯电动",  # engine_type
                None,  # displacement
                random.randint(200, 400),  # horsepower
                random.randint(300, 500),  # torque
                "单速固定齿比变速箱",  # transmission
                random.choice(["后驱", "四驱"]),  # drive_type
                round(random.uniform(4700, 5100), 0),  # length
                round(random.uniform(1850, 1980), 0),  # width
                round(random.uniform(1450, 1650), 0),  # height
                round(random.uniform(2800, 3100), 0),  # wheelbase
                round(random.uniform(1800, 2300), 0),  # curb_weight
                None,  # fuel_consumption
                round(random.uniform(60, 100), 1),  # battery_capacity
                random.randint(500, 800),  # range_km
                round(random.uniform(3.5, 7.0), 1),  # acceleration_100
                random.randint(180, 250),  # top_speed
            ))
        elif energy_type == "插电混动":
            specs_data.append((
                model_id,
                "插电混动",
                round(random.choice([1.5, 1.5, 1.5, 2.0]), 1),
                random.randint(150, 300),
                random.randint(250, 450),
                random.choice(["E-CVT", "DHT", "7DCT"]),
                random.choice(["前驱", "四驱"]),
                round(random.uniform(4600, 5000), 0),
                round(random.uniform(1850, 1950), 0),
                round(random.uniform(1450, 1700), 0),
                round(random.uniform(2700, 2900), 0),
                round(random.uniform(1600, 2100), 0),
                round(random.uniform(3.8, 5.5), 1),
                round(random.uniform(18, 35), 1),
                random.randint(100, 200),
                round(random.uniform(5.0, 8.0), 1),
                random.randint(180, 220),
            ))
        elif energy_type == "增程式":
            specs_data.append((
                model_id,
                "增程式",
                round(random.choice([1.5, 1.5, 1.5]), 1),
                random.randint(200, 350),
                random.randint(300, 500),
                "单速固定齿比变速箱",
                random.choice(["后驱", "四驱"]),
                round(random.uniform(4800, 5200), 0),
                round(random.uniform(1900, 2000), 0),
                round(random.uniform(1600, 1800), 0),
                round(random.uniform(2900, 3100), 0),
                round(random.uniform(2000, 2500), 0),
                round(random.uniform(6.0, 8.0), 1),
                round(random.uniform(30, 50), 1),
                random.randint(150, 250),
                round(random.uniform(4.5, 6.5), 1),
                random.randint(180, 220),
            ))
        else:  # 燃油
            displacement = random.choice([1.5, 1.5, 1.5, 1.5, 2.0, 2.0, 2.0, 2.5, 3.0])
            specs_data.append((
                model_id,
                "涡轮增压" if random.random() > 0.3 else "自然吸气",
                displacement,
                random.randint(120, 250),
                random.randint(150, 400),
                random.choice(["CVT", "7DCT", "8AT", "9AT", "6MT"]),
                random.choice(["前驱", "前驱", "前驱", "后驱", "四驱"]),
                round(random.uniform(4500, 5000), 0),
                round(random.uniform(1800, 1950), 0),
                round(random.uniform(1450, 1700), 0),
                round(random.uniform(2650, 2950), 0),
                round(random.uniform(1400, 1900), 0),
                round(random.uniform(6.0, 9.5), 1),
                None,
                None,
                round(random.uniform(7.0, 10.0), 1),
                random.randint(190, 240),
            ))

    cursor.executemany("""
        INSERT INTO specs (model_id, engine_type, displacement, horsepower, torque, transmission,
        drive_type, length, width, height, wheelbase, curb_weight, fuel_consumption,
        battery_capacity, range_km, acceleration_100, top_speed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, specs_data)

    # ============ 销量数据 ============
    # 生成 2024 年 1-12 月销量数据
    sales_data = []
    for model_name, model_id in model_map.items():
        # 基础销量（根据品牌和车型类型）
        brand_name = next(m[0] for m in models_data if m[1] == model_name)
        if brand_name in ["比亚迪", "大众", "丰田", "本田"]:
            base_sales = random.randint(5000, 30000)
        elif brand_name in ["奔驰", "宝马", "奥迪"]:
            base_sales = random.randint(8000, 20000)
        elif brand_name in ["蔚来", "小鹏", "理想", "问界", "小米"]:
            base_sales = random.randint(3000, 15000)
        else:
            base_sales = random.randint(2000, 15000)

        for month in range(1, 13):
            # 添加季节性波动
            season_factor = 1.0
            if month in [1, 2]:  # 春节淡季
                season_factor = 0.7
            elif month in [9, 10, 12]:  # 金九银十+年底冲量
                season_factor = 1.3

            sales_volume = int(base_sales * season_factor * random.uniform(0.8, 1.2))
            yoy_growth = round(random.uniform(-15, 30), 1)
            mom_growth = round(random.uniform(-20, 20), 1)

            sales_data.append((
                model_id, 2024, month, sales_volume, yoy_growth, mom_growth,
                random.randint(1, 100)
            ))

    cursor.executemany("""
        INSERT INTO sales (model_id, year, month, sales_volume, yoy_growth, mom_growth, ranking)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sales_data)

    # ============ 评分数据 ============
    ratings_data = []
    for model_name, model_id in model_map.items():
        overall = round(random.uniform(3.5, 4.9), 1)
        ratings_data.append((
            model_id,
            overall,
            round(overall + random.uniform(-0.3, 0.3), 1),  # 外观
            round(overall + random.uniform(-0.4, 0.2), 1),  # 内饰
            round(overall + random.uniform(-0.3, 0.3), 1),  # 动力
            round(overall + random.uniform(-0.3, 0.3), 1),  # 空间
            round(overall + random.uniform(-0.5, 0.3), 1),  # 油耗
            round(overall + random.uniform(-0.3, 0.3), 1),  # 操控
            round(overall + random.uniform(-0.3, 0.3), 1),  # 舒适性
            round(overall + random.uniform(-0.3, 0.4), 1),  # 性价比
            random.randint(100, 5000),  # 评价数量
        ))

    cursor.executemany("""
        INSERT INTO ratings (model_id, overall_score, appearance_score, interior_score,
        power_score, space_score, fuel_score, handling_score, comfort_score, value_score, review_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ratings_data)

    # ============ 城市销量数据 ============
    cities = [
        ("北京", "北京", "华北"), ("上海", "上海", "华东"), ("广州", "广东", "华南"),
        ("深圳", "广东", "华南"), ("成都", "四川", "西南"), ("杭州", "浙江", "华东"),
        ("武汉", "湖北", "华中"), ("南京", "江苏", "华东"), ("重庆", "重庆", "西南"),
        ("西安", "陕西", "西北"), ("苏州", "江苏", "华东"), ("天津", "天津", "华北"),
        ("郑州", "河南", "华中"), ("长沙", "湖南", "华中"), ("东莞", "广东", "华南"),
        ("青岛", "山东", "华东"), ("沈阳", "辽宁", "东北"), ("宁波", "浙江", "华东"),
        ("昆明", "云南", "西南"), ("大连", "辽宁", "东北"),
    ]

    city_sales_data = []
    for model_name, model_id in model_map.items():
        # 每个车型在 10-15 个城市有销量
        selected_cities = random.sample(cities, random.randint(10, 15))
        for city, province, region in selected_cities:
            sales_volume = random.randint(100, 3000)
            city_sales_data.append((
                model_id, city, province, region, sales_volume, 2024, random.randint(1, 12)
            ))

    cursor.executemany("""
        INSERT INTO city_sales (model_id, city, province, region, sales_volume, year, month)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, city_sales_data)

    conn.commit()
    print(f"  - 品牌: {len(brands)} 个")
    print(f"  - 车型: {len(models_data)} 个")
    print(f"  - 参数: {len(specs_data)} 条")
    print(f"  - 销量: {len(sales_data)} 条")
    print(f"  - 评分: {len(ratings_data)} 条")
    print(f"  - 城市销量: {len(city_sales_data)} 条")
