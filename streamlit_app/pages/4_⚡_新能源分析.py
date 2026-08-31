"""
新能源分析页面
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from streamlit_app.utils import (
    load_sales_with_models, load_specs_with_models,
    get_year_options, get_energy_types,
)

st.set_page_config(page_title="新能源分析", page_icon="⚡", layout="wide")

# 侧边栏
st.sidebar.header("⚡ 新能源筛选")
years = get_year_options()
selected_year = st.sidebar.selectbox("选择年份", years, index=len(years) - 1 if years else 0)

st.title("⚡ 新能源分析")

# 加载数据
sales_df = load_sales_with_models(selected_year)
specs_df = load_specs_with_models()

# ========== 新能源渗透率 ==========
st.subheader("📈 新能源渗透率")
all_sales = load_sales_with_models(selected_year)
all_sales["is_new_energy"] = all_sales["energy_type"].isin(["纯电动", "插电混动", "增程式"])
ne_summary = all_sales.groupby("is_new_energy")["sales_volume"].sum().reset_index()
ne_summary["type"] = ne_summary["is_new_energy"].map({True: "新能源", False: "传统燃油"})
total_sales = ne_summary["sales_volume"].sum()
ne_ratio = ne_summary[ne_summary["is_new_energy"] == True]["sales_volume"].sum() / total_sales * 100 if total_sales > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("新能源销量", f"{ne_summary[ne_summary['is_new_energy'] == True]['sales_volume'].sum():,} 辆")
with col2:
    st.metric("传统燃油销量", f"{ne_summary[ne_summary['is_new_energy'] == False]['sales_volume'].sum():,} 辆")
with col3:
    st.metric("新能源渗透率", f"{ne_ratio:.1f}%")

# ========== EV vs PHEV vs 增程 ==========
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🔋 新能源类型销量")
    ne_sales = all_sales[all_sales["is_new_energy"]]
    ne_type_sales = ne_sales.groupby("energy_type")["sales_volume"].sum().reset_index()

    fig_ne = px.pie(
        ne_type_sales, values="sales_volume", names="energy_type",
        title="新能源类型销量占比",
        color="energy_type",
        color_discrete_map={"纯电动": "#00d4aa", "插电混动": "#ffd93d", "增程式": "#6c5ce7"},
    )
    st.plotly_chart(fig_ne, use_container_width=True)

with col_right:
    st.subheader("🏭 新能源品牌排名")
    ne_brand = ne_sales.groupby("brand_name")["sales_volume"].sum().reset_index()
    ne_brand = ne_brand.sort_values("sales_volume", ascending=False).head(15)

    fig_neb = px.bar(
        ne_brand, x="sales_volume", y="brand_name",
        orientation="h", title="新能源品牌销量 TOP 15",
        labels={"sales_volume": "销量(辆)", "brand_name": "品牌"},
        color="sales_volume", color_continuous_scale="Tealgrn",
    )
    fig_neb.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_neb, use_container_width=True)

# ========== 续航分析 ==========
st.subheader("🔋 续航里程分析")
ev_specs = specs_df[specs_df["energy_type"] == "纯电动"].copy()
ev_specs = ev_specs[ev_specs["range_km"] > 0]

if not ev_specs.empty:
    # 续航分组
    range_bins = [0, 300, 400, 500, 600, 700, float('inf')]
    range_labels = ["300km以下", "300-400km", "400-500km", "500-600km", "600-700km", "700km以上"]
    ev_specs["range_group"] = pd.cut(ev_specs["range_km"], bins=range_bins, labels=range_labels, right=False)

    col1, col2 = st.columns(2)
    with col1:
        range_dist = ev_specs.groupby("range_group", observed=False).size().reset_index(name="count")
        fig_range = px.bar(
            range_dist, x="range_group", y="count",
            title="纯电动车型续航分布",
            labels={"range_group": "续航区间", "count": "车型数量"},
            color="count", color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig_range, use_container_width=True)

    with col2:
        # 续航 vs 价格
        ev_price_range = ev_specs.groupby("range_group", observed=False)["guide_price_min"].mean().reset_index()
        fig_rp = px.bar(
            ev_price_range, x="range_group", y="guide_price_min",
            title="各续航区间平均价格",
            labels={"range_group": "续航区间", "guide_price_min": "平均价格(万元)"},
            color="guide_price_min", color_continuous_scale="RdYlGn_r",
        )
        st.plotly_chart(fig_rp, use_container_width=True)

# ========== 新能源车型 TOP ==========
st.subheader("🏆 新能源车型销量 TOP 20")
ne_models = ne_sales.groupby(["model_name", "brand_name", "energy_type", "avg_price"]).agg({
    "sales_volume": "sum"
}).reset_index().sort_values("sales_volume", ascending=False).head(20)

fig_nem = px.bar(
    ne_models, x="sales_volume", y="model_name",
    orientation="h", color="energy_type",
    title="新能源车型销量 TOP 20",
    labels={"sales_volume": "销量(辆)", "model_name": "车型", "energy_type": "类型"},
    color_discrete_map={"纯电动": "#00d4aa", "插电混动": "#ffd93d", "增程式": "#6c5ce7"},
)
fig_nem.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_nem, use_container_width=True)
