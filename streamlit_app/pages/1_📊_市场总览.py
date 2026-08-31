"""
市场总览页面
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from streamlit_app.utils import (
    get_market_overview, get_year_options, load_sales_with_models,
    load_ratings_with_models, get_brand_categories,
)

st.set_page_config(page_title="市场总览", page_icon="📊", layout="wide")

# 侧边栏
st.sidebar.header("📊 筛选条件")
years = get_year_options()
selected_year = st.sidebar.selectbox("选择年份", years, index=len(years) - 1 if years else 0)

st.title("📊 市场总览")

# 导出按钮
col_export1, col_export2, col_export3 = st.columns([1, 1, 1])
with col_export1:
    if st.button("📥 导出Excel", use_container_width=True):
        with st.spinner("导出中..."):
            from export.excel_exporter import ExcelExporter
            exporter = ExcelExporter()
            exporter.export_brand_sales(selected_year)
            exporter.export_model_sales(selected_year)
            exporter.close()
            st.success("✅ 已导出到 data/excel/")
with col_export2:
    csv_data = sales_df.to_csv(index=False).encode('utf-8-sig') if 'sales_df' in locals() else b''
    st.download_button("📥 下载CSV", csv_data, f"market_overview_{selected_year}.csv", "text/csv", use_container_width=True)

st.markdown("---")

# KPI 卡片
overview = get_market_overview(selected_year)
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("总销量", f"{overview['total_sales']:,} 辆")
with col2:
    st.metric("品牌数量", f"{overview['brand_count']} 个")
with col3:
    st.metric("车型数量", f"{overview['model_count']} 个")
with col4:
    st.metric("新能源渗透率", f"{overview['new_energy_penetration']}%")
with col5:
    st.metric("平均售价", f"{overview['avg_price']:.1f} 万")
with col6:
    st.metric("平均评分", f"{overview['avg_rating']:.1f} 分")

st.markdown("---")

# 图表区域
sales_df = load_sales_with_models(selected_year)

col_left, col_right = st.columns(2)

with col_left:
    # 品牌销量份额饼图
    brand_sales = sales_df.groupby("brand_name")["sales_volume"].sum().reset_index()
    brand_sales = brand_sales.sort_values("sales_volume", ascending=False)
    top10 = brand_sales.head(10)
    others = pd.DataFrame({
        "brand_name": ["其他"],
        "sales_volume": [brand_sales.iloc[10:]["sales_volume"].sum()] if len(brand_sales) > 10 else [0]
    })
    pie_data = pd.concat([top10, others], ignore_index=True)

    fig_pie = px.pie(
        pie_data, values="sales_volume", names="brand_name",
        title=f"{selected_year}年 品牌销量份额",
        hole=0.4,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    # 品牌类别对比
    import pandas as pd
    category_sales = sales_df.groupby("brand_category")["sales_volume"].sum().reset_index()
    category_sales = category_sales.sort_values("sales_volume", ascending=False)

    fig_cat = px.bar(
        category_sales, x="brand_category", y="sales_volume",
        title=f"{selected_year}年 品牌类别销量对比",
        labels={"brand_category": "品牌类别", "sales_volume": "销量(辆)"},
        color="brand_category",
        color_discrete_map={"自主": "#ff6b6b", "合资": "#4ecdc4", "豪华": "#45b7d1", "新势力": "#96ceb4"},
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# 下方图表
col_left2, col_right2 = st.columns(2)

with col_left2:
    # 价格区间分布
    from config import PRICE_RANGES
    price_bins = [low for low, high, label in PRICE_RANGES] + [float('inf')]
    price_labels = [label for low, high, label in PRICE_RANGES]
    sales_df["price_range"] = pd.cut(
        sales_df["guide_price_min"], bins=price_bins, labels=price_labels, right=False
    )
    price_dist = sales_df.groupby("price_range", observed=False)["sales_volume"].sum().reset_index()

    fig_price = px.bar(
        price_dist, x="price_range", y="sales_volume",
        title=f"{selected_year}年 价格区间销量分布",
        labels={"price_range": "价格区间", "sales_volume": "销量(辆)"},
        color="sales_volume", color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_price, use_container_width=True)

with col_right2:
    # 能源类型销量
    energy_sales = sales_df.groupby("energy_type")["sales_volume"].sum().reset_index()
    energy_sales = energy_sales.sort_values("sales_volume", ascending=False)

    fig_energy = px.bar(
        energy_sales, x="energy_type", y="sales_volume",
        title=f"{selected_year}年 能源类型销量",
        labels={"energy_type": "能源类型", "sales_volume": "销量(辆)"},
        color="energy_type",
        color_discrete_map={
            "纯电动": "#00d4aa", "插电混动": "#ffd93d", "增程式": "#6c5ce7",
            "燃油": "#ff6b6b", "油电混动": "#a8e6cf"
        },
    )
    st.plotly_chart(fig_energy, use_container_width=True)
