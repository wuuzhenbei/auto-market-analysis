"""
价格分析页面
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from streamlit_app.utils import (
    load_sales_with_models, load_ratings_with_models,
    get_year_options, get_energy_types, get_body_types, get_price_ranges,
)
from config import PRICE_RANGES

st.set_page_config(page_title="价格分析", page_icon="💰", layout="wide")

# 侧边栏
st.sidebar.header("💰 价格筛选")
years = get_year_options()
selected_year = st.sidebar.selectbox("选择年份", years, index=len(years) - 1 if years else 0)
energy_types = get_energy_types()
selected_energy = st.sidebar.multiselect("能源类型", energy_types, default=energy_types)

st.title("💰 价格分析")

# 加载数据
sales_df = load_sales_with_models(selected_year)
sales_df = sales_df[sales_df["energy_type"].isin(selected_energy)]

# 计算价格区间
price_bins = [low for low, high, label in PRICE_RANGES] + [float('inf')]
price_labels = [label for low, high, label in PRICE_RANGES]
sales_df["price_range"] = pd.cut(
    sales_df["guide_price_min"], bins=price_bins, labels=price_labels, right=False
)

# ========== 价格分布 ==========
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 车型数量价格分布")
    model_price = sales_df.drop_duplicates(subset=["model_name"])
    price_dist = model_price.groupby("price_range", observed=False).size().reset_index(name="model_count")

    fig_dist = px.bar(
        price_dist, x="price_range", y="model_count",
        title="车型数量价格分布",
        labels={"price_range": "价格区间", "model_count": "车型数量"},
        color="model_count", color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with col2:
    st.subheader("📈 价格区间销量占比")
    price_sales = sales_df.groupby("price_range", observed=False)["sales_volume"].sum().reset_index()

    fig_ps = px.pie(
        price_sales, values="sales_volume", names="price_range",
        title="价格区间销量占比", hole=0.4,
    )
    st.plotly_chart(fig_ps, use_container_width=True)

# ========== 价格-销量散点图 ==========
st.subheader("💹 价格与销量关系")
scatter_data = sales_df.groupby(["model_name", "brand_name", "energy_type", "avg_price"]).agg({
    "sales_volume": "sum"
}).reset_index()

fig_scatter = px.scatter(
    scatter_data, x="avg_price", y="sales_volume",
    color="energy_type", size="sales_volume",
    hover_data=["model_name", "brand_name"],
    title="价格 vs 销量",
    labels={"avg_price": "均价(万元)", "sales_volume": "销量(辆)", "energy_type": "能源类型"},
    color_discrete_map={
        "纯电动": "#00d4aa", "插电混动": "#ffd93d", "增程式": "#6c5ce7",
        "燃油": "#ff6b6b", "油电混动": "#a8e6cf"
    },
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ========== 按能源类型价格对比 ==========
col3, col4 = st.columns(2)

with col3:
    st.subheader("⚡ 能源类型价格对比")
    energy_price = sales_df.drop_duplicates(subset=["model_name"]).groupby("energy_type").agg({
        "avg_price": "mean",
        "guide_price_min": "min",
        "guide_price_max": "max",
    }).reset_index()

    fig_ep = px.bar(
        energy_price, x="energy_type", y="avg_price",
        title="各能源类型平均价格",
        labels={"energy_type": "能源类型", "avg_price": "均价(万元)"},
        color="energy_type",
        color_discrete_map={
            "纯电动": "#00d4aa", "插电混动": "#ffd93d", "增程式": "#6c5ce7",
            "燃油": "#ff6b6b", "油电混动": "#a8e6cf"
        },
    )
    st.plotly_chart(fig_ep, use_container_width=True)

with col4:
    st.subheader("🚙 车身类型价格对比")
    body_price = sales_df.drop_duplicates(subset=["model_name"]).groupby("body_type").agg({
        "avg_price": "mean",
    }).reset_index().sort_values("avg_price", ascending=False)

    fig_bp = px.bar(
        body_price, x="body_type", y="avg_price",
        title="各车身类型平均价格",
        labels={"body_type": "车身类型", "avg_price": "均价(万元)"},
        color="avg_price", color_continuous_scale="RdYlGn_r",
    )
    st.plotly_chart(fig_bp, use_container_width=True)

# ========== 性价比分析 ==========
st.subheader("💎 性价比 TOP 榜")
ratings_df = load_ratings_with_models()
ratings_df = ratings_df[ratings_df["energy_type"].isin(selected_energy)]

value_data = ratings_df.copy()
value_data["value_index"] = value_data["overall_score"] / value_data["avg_price"] * 100
value_data = value_data.sort_values("value_index", ascending=False).head(20)

fig_value = px.bar(
    value_data, x="value_index", y="model_name",
    orientation="h", color="brand_category",
    title="性价比指数 TOP 20（评分/价格×100）",
    labels={"value_index": "性价比指数", "model_name": "车型", "brand_category": "类别"},
)
fig_value.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_value, use_container_width=True)
