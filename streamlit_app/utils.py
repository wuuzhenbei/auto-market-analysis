"""
Streamlit 公共工具模块
数据加载、缓存、通用函数
"""
import sqlite3
import pandas as pd
import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import DB_PATH, PRICE_RANGES, ENERGY_TYPES, RATING_DIMENSIONS


# ========== 数据库连接 ==========

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(str(DB_PATH))


# ========== 缓存数据加载 ==========

@st.cache_data(ttl=300)
def load_brands():
    """加载品牌数据"""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM brands", conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_models():
    """加载车型数据"""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM models", conn)
    conn.close()
    # 计算均价
    df["avg_price"] = (df["guide_price_min"] + df["guide_price_max"]) / 2
    return df


@st.cache_data(ttl=300)
def load_sales(year: int = None):
    """加载销量数据"""
    conn = get_connection()
    if year:
        df = pd.read_sql(f"SELECT * FROM sales WHERE year = {year}", conn)
    else:
        df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_ratings():
    """加载评分数据"""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM ratings", conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_specs():
    """加载规格数据"""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM specs", conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_city_sales(year: int = None):
    """加载城市销量数据"""
    conn = get_connection()
    if year:
        df = pd.read_sql(f"SELECT * FROM city_sales WHERE year = {year}", conn)
    else:
        df = pd.read_sql("SELECT * FROM city_sales", conn)
    conn.close()
    return df


# ========== 复合查询 ==========

@st.cache_data(ttl=300)
def load_sales_with_models(year: int = None):
    """加载销量+车型+品牌关联数据"""
    conn = get_connection()
    query = """
    SELECT s.*, m.name as model_name, m.energy_type, m.body_type,
           m.guide_price_min, m.guide_price_max,
           b.name as brand_name, b.category as brand_category, b.country as brand_country
    FROM sales s
    JOIN models m ON s.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    """
    if year:
        query += f" WHERE s.year = {year}"
    df = pd.read_sql(query, conn)
    conn.close()
    df["avg_price"] = (df["guide_price_min"] + df["guide_price_max"]) / 2
    return df


@st.cache_data(ttl=300)
def load_ratings_with_models():
    """加载评分+车型+品牌关联数据"""
    conn = get_connection()
    query = """
    SELECT r.*, m.name as model_name, m.energy_type, m.body_type,
           m.guide_price_min, m.guide_price_max,
           b.name as brand_name, b.category as brand_category
    FROM ratings r
    JOIN models m ON r.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df["avg_price"] = (df["guide_price_min"] + df["guide_price_max"]) / 2
    return df


@st.cache_data(ttl=300)
def load_specs_with_models():
    """加载规格+车型+品牌关联数据"""
    conn = get_connection()
    query = """
    SELECT sp.*, m.name as model_name, m.energy_type, m.body_type,
           m.guide_price_min, m.guide_price_max,
           b.name as brand_name, b.category as brand_category
    FROM specs sp
    JOIN models m ON sp.model_id = m.id
    JOIN brands b ON m.brand_id = b.id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ========== 市场概览 ==========

@st.cache_data(ttl=300)
def get_market_overview(year: int = None):
    """获取市场概览数据"""
    conn = get_connection()
    overview = {}

    # 总销量
    if year:
        query = "SELECT SUM(sales_volume) FROM sales WHERE year = ?"
        cursor = conn.execute(query, [year])
    else:
        query = "SELECT SUM(sales_volume) FROM sales"
        cursor = conn.execute(query)
    result = cursor.fetchone()[0]
    overview["total_sales"] = result if result else 0

    # 品牌数量
    overview["brand_count"] = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]

    # 车型数量
    overview["model_count"] = conn.execute("SELECT COUNT(*) FROM models").fetchone()[0]

    # 新能源渗透率
    if year:
        query = """
        SELECT SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) * 100.0 / SUM(s.sales_volume)
        FROM sales s JOIN models m ON s.model_id = m.id WHERE s.year = ?
        """
        cursor = conn.execute(query, [year])
    else:
        query = """
        SELECT SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) * 100.0 / SUM(s.sales_volume)
        FROM sales s JOIN models m ON s.model_id = m.id
        """
        cursor = conn.execute(query)
    result = cursor.fetchone()[0]
    overview["new_energy_penetration"] = round(result, 2) if result else 0

    # 平均售价
    query = "SELECT AVG((guide_price_min + guide_price_max) / 2) FROM models WHERE guide_price_min > 0"
    result = conn.execute(query).fetchone()[0]
    overview["avg_price"] = round(result, 2) if result else 0

    # 平均评分
    result = conn.execute("SELECT AVG(overall_score) FROM ratings").fetchone()[0]
    overview["avg_rating"] = round(result, 2) if result else 0

    conn.close()
    return overview


# ========== 通用筛选 ==========

def get_year_options():
    """获取可用年份列表"""
    conn = get_connection()
    years = pd.read_sql("SELECT DISTINCT year FROM sales ORDER BY year", conn)["year"].tolist()
    conn.close()
    return years


def get_brand_options():
    """获取品牌列表"""
    conn = get_connection()
    brands = pd.read_sql("SELECT name FROM brands ORDER BY name", conn)["name"].tolist()
    conn.close()
    return brands


def get_brand_categories():
    """获取品牌分类列表"""
    return ["自主", "合资", "豪华", "新势力"]


def get_energy_types():
    """获取能源类型列表"""
    return ENERGY_TYPES


def get_body_types():
    """获取车身类型列表"""
    return ["轿车", "SUV", "MPV", "跑车"]


def get_price_ranges():
    """获取价格区间列表"""
    return [label for _, _, label in PRICE_RANGES]


def get_regions():
    """获取区域列表"""
    return ["华东", "华南", "华北", "华中", "西南", "西北", "东北"]
