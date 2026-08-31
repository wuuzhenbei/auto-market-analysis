"""
城市分析页面
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from streamlit_app.utils import (
    load_city_sales, load_sales_with_models,
    get_year_options, get_regions,
)

st.set_page_config(page_title="城市分析", page_icon="🗺️", layout="wide")

# 侧边栏
st.sidebar.header("🗺️ 城市筛选")
years = get_year_options()
selected_year = st.sidebar.selectbox("选择年份", years, index=len(years) - 1 if years else 0)
regions = get_regions()
selected_regions = st.sidebar.multiselect("区域", regions, default=regions)

st.title("🗺️ 城市与区域分析")

# 加载数据
city_df = load_city_sales(selected_year)
city_df = city_df[city_df["region"].isin(selected_regions)]

# ========== 城市销量 TOP ==========
st.subheader("🏙️ 城市销量 TOP 20")
city_sales = city_df.groupby(["city", "province", "region"])["sales_volume"].sum().reset_index()
city_sales = city_sales.sort_values("sales_volume", ascending=False)

fig_city = px.bar(
    city_sales.head(20), x="sales_volume", y="city",
    orientation="h", color="region",
    title=f"{selected_year}年 城市销量 TOP 20",
    labels={"sales_volume": "销量(辆)", "city": "城市", "region": "区域"},
)
fig_city.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_city, use_container_width=True)

# ========== 区域分布 ==========
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌍 区域销量分布")
    region_sales = city_df.groupby("region")["sales_volume"].sum().reset_index()
    region_sales = region_sales.sort_values("sales_volume", ascending=False)

    fig_region = px.pie(
        region_sales, values="sales_volume", names="region",
        title="区域销量占比", hole=0.4,
    )
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    st.subheader("📊 区域销量对比")
    fig_rb = px.bar(
        region_sales, x="region", y="sales_volume",
        title="区域销量对比",
        labels={"region": "区域", "sales_volume": "销量(辆)"},
        color="sales_volume", color_continuous_scale="Blues",
    )
    st.plotly_chart(fig_rb, use_container_width=True)

# ========== 省份分析 ==========
st.subheader("🗺️ 省份销量排名")
province_sales = city_df.groupby(["province", "region"])["sales_volume"].sum().reset_index()
province_sales = province_sales.sort_values("sales_volume", ascending=False)

fig_prov = px.bar(
    province_sales.head(20), x="sales_volume", y="province",
    orientation="h", color="region",
    title="省份销量 TOP 20",
    labels={"sales_volume": "销量(辆)", "province": "省份", "region": "区域"},
)
fig_prov.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_prov, use_container_width=True)

# ========== 区域详情 ==========
st.subheader("🔍 区域详情")
selected_region = st.selectbox("选择区域查看详情", regions)

if selected_region:
    region_detail = city_df[city_df["region"] == selected_region]
    region_cities = region_detail.groupby(["city", "province"])["sales_volume"].sum().reset_index()
    region_cities = region_cities.sort_values("sales_volume", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{selected_region}** 各城市销量")
        st.dataframe(region_cities, use_container_width=True, hide_index=True)

    with col2:
        fig_rd = px.pie(
            region_cities, values="sales_volume", names="city",
            title=f"{selected_region} 城市销量分布",
        )
        st.plotly_chart(fig_rd, use_container_width=True)
