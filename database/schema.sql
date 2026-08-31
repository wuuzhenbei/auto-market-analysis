-- 汽车市场数据分析 - 数据库表结构

-- 品牌表
CREATE TABLE IF NOT EXISTS brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- 品牌名称
    country TEXT,                         -- 国家/地区
    category TEXT,                        -- 品牌类别：自主/合资/豪华/新势力
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 车型表
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER NOT NULL,
    name TEXT NOT NULL,                   -- 车型名称
    series TEXT,                          -- 车系
    year INTEGER,                         -- 年款
    energy_type TEXT,                     -- 能源类型：纯电动/插电混动/增程式/燃油/油电混动
    body_type TEXT,                       -- 车身类型：轿车/SUV/MPV/跑车
    guide_price_min REAL,                 -- 指导价（最低）
    guide_price_max REAL,                 -- 指导价（最高）
    source TEXT,                          -- 数据来源：dongchedi/autohome
    source_url TEXT,                      -- 来源URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands(id)
);

-- 车型参数表
CREATE TABLE IF NOT EXISTS specs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    engine_type TEXT,                     -- 发动机类型
    displacement REAL,                    -- 排量(L)
    horsepower INTEGER,                   -- 马力(ps)
    torque INTEGER,                       -- 扭矩(N·m)
    transmission TEXT,                    -- 变速箱
    drive_type TEXT,                      -- 驱动方式：前驱/后驱/四驱
    length REAL,                          -- 长度(mm)
    width REAL,                           -- 宽度(mm)
    height REAL,                          -- 高度(mm)
    wheelbase REAL,                       -- 轴距(mm)
    curb_weight REAL,                     -- 整备质量(kg)
    fuel_consumption REAL,                -- 综合油耗(L/100km)
    battery_capacity REAL,                -- 电池容量(kWh) - 新能源
    range_km INTEGER,                     -- 纯电续航(km) - 新能源
    acceleration_100 REAL,                -- 0-100km/h加速(s)
    top_speed INTEGER,                    -- 最高时速(km/h)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id)
);

-- 销量表
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    sales_volume INTEGER,                 -- 月销量
    yoy_growth REAL,                      -- 同比增长率(%)
    mom_growth REAL,                      -- 环比增长率(%)
    ranking INTEGER,                      -- 排名
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id)
);

-- 用户评分表
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    overall_score REAL,                   -- 综合评分
    appearance_score REAL,                -- 外观评分
    interior_score REAL,                  -- 内饰评分
    power_score REAL,                     -- 动力评分
    space_score REAL,                     -- 空间评分
    fuel_score REAL,                      -- 油耗评分
    handling_score REAL,                  -- 操控评分
    comfort_score REAL,                   -- 舒适性评分
    value_score REAL,                     -- 性价比评分
    review_count INTEGER,                 -- 评价数量
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id)
);

-- 城市销量分布表
CREATE TABLE IF NOT EXISTS city_sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    city TEXT NOT NULL,                   -- 城市
    province TEXT,                        -- 省份
    region TEXT,                          -- 区域：华东/华南/华北/华中/西南/西北/东北
    sales_volume INTEGER,                 -- 销量
    year INTEGER,
    month INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_models_brand ON models(brand_id);
CREATE INDEX IF NOT EXISTS idx_models_energy ON models(energy_type);
CREATE INDEX IF NOT EXISTS idx_specs_model ON specs(model_id);
CREATE INDEX IF NOT EXISTS idx_sales_model ON sales(model_id);
CREATE INDEX IF NOT EXISTS idx_sales_year_month ON sales(year, month);
CREATE INDEX IF NOT EXISTS idx_ratings_model ON ratings(model_id);
CREATE INDEX IF NOT EXISTS idx_city_sales_model ON city_sales(model_id);
CREATE INDEX IF NOT EXISTS idx_city_sales_city ON city_sales(city);
