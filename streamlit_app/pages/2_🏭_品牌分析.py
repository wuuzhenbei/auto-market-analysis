"""
品牌分析页面
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from streamlit_app.utils import (
    load_sales_with_models, load_ratings_with_models,
    get_year_options, get_brand_categories, get_brand_options,
)

st.set_page_config(page_title="品牌分析", page_icon="🏭", layout="wide")

# 侧边栏
st.sidebar.header("🏭 品牌筛选")
years = get_year_options()
selected_year = st.sidebar.selectbox("选择年份", years, index=len(years) - 1 if years else 0)
categories = get_brand_categories()
selected_categories = st.sidebar.multiselect("品牌类别", categories, default=categories)

st.title("🏭 品牌分析")

# 加载数据
sales_df = load_sales_with_models(selected_year)
ratings_df = load_ratings_with_models()

# 筛选品牌类别
sales_df = sales_df[sales_df["brand_category"].isin(selected_categories)]
ratings_df = ratings_df[ratings_df["brand_category"].isin(selected_categories)]

# ========== 品牌销量排名 ==========
st.subheader("📈 品牌销量排名")
brand_sales = sales_df.groupby(["brand_name", "brand_category"])["sales_volume"].sum().reset_index()
brand_sales = brand_sales.sort_values("sales_volume", ascending=False)

fig_ranking = px.bar(
    brand_sales.head(20), x="sales_volume", y="brand_name",
    orientation="h", color="brand_category",
    title=f"{selected_year}年 品牌销量 TOP 20",
    labels={"sales_volume": "销量(辆)", "brand_name": "品牌", "brand_category": "类别"},
    color_discrete_map={"自主": "#ff6b6b", "合资": "#4ecdc4", "豪华": "#45b7d1", "新势力": "#96ceb4"},
)
fig_ranking.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_ranking, use_container_width=True)

# ========== 品牌分类对比 ==========
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏷️ 品牌类别销量占比")
    cat_sales = sales_df.groupby("brand_category")["sales_volume"].sum().reset_index()
    fig_cat = px.pie(
        cat_sales, values="sales_volume", names="brand_category",
        title="品牌类别销量占比",
        color="brand_category",
        color_discrete_map={"自主": "#ff6b6b", "合资": "#4ecdc4", "豪华": "#45b7d1", "新势力": "#96ceb4"},
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    st.subheader("🌍 品牌国别分布")
    country_sales = sales_df.groupby("brand_country")["sales_volume"].sum().reset_index()
    country_sales = country_sales.sort_values("sales_volume", ascending=False)
    fig_country = px.bar(
        country_sales, x="brand_country", y="sales_volume",
        title="品牌国别销量分布",
        labels={"brand_country": "国别", "sales_volume": "销量(辆)"},
        color="sales_volume", color_continuous_scale="Blues",
    )
    st.plotly_chart(fig_country, use_container_width=True)

# ========== 品牌评分排名 ==========
st.subheader("⭐ 品牌平均评分排名")
brand_ratings = ratings_df.groupby(["brand_name", "brand_category"]).agg({
    "overall_score": "mean",
    "appearance_score": "mean",
    "interior_score": "mean",
    "power_score": "mean",
    "space_score": "mean",
    "fuel_score": "mean",
    "handling_score": "mean",
    "comfort_score": "mean",
    "value_score": "mean",
}).reset_index()
brand_ratings = brand_ratings.sort_values("overall_score", ascending=False)

fig_rating = px.bar(
    brand_ratings.head(15), x="overall_score", y="brand_name",
    orientation="h", color="brand_category",
    title="品牌平均评分 TOP 15",
    labels={"overall_score": "综合评分", "brand_name": "品牌", "brand_category": "类别"},
    color_discrete_map={"自主": "#ff6b6b", "合资": "#4ecdc4", "豪华": "#45b7d1", "新势力": "#96ceb4"},
)
fig_rating.update_layout(yaxis=dict(autorange="reversed"), xaxis_range=[3.5, 5])
st.plotly_chart(fig_rating, use_container_width=True)

# ========== 品牌详情 ==========
st.subheader("🔍 品牌详情")
brand_options = get_brand_options()
selected_brand = st.selectbox("选择品牌查看详情", brand_options)

if selected_brand:
    brand_sales_detail = sales_df[sales_df["brand_name"] == selected_brand]
    brand_models = brand_sales_detail.groupby("model_name").agg({
        "sales_volume": "sum",
        "energy_type": "first",
        "avg_price": "first",
    }).reset_index().sort_values("sales_volume", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{selected_brand}** 车型销量排名")
        st.dataframe(brand_models, use_container_width=True, hide_index=True)
    with col2:
        fig_brand = px.bar(
            brand_models, x="sales_volume", y="model_name",
            orientation="h", color="energy_type",
            title=f"{selected_brand} 车型销量",
            labels={"sales_volume": "销量(辆)", "model_name": "车型", "energy_type": "能源类型"},
        )
        fig_brand.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_brand, use_container_width=True)
