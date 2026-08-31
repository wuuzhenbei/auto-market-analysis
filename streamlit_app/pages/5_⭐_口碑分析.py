"""
口碑分析页面
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from streamlit_app.utils import (
    load_ratings_with_models, get_brand_options,
    get_price_ranges, RATING_DIMENSIONS,
)
from config import PRICE_RANGES

st.set_page_config(page_title="口碑分析", page_icon="⭐", layout="wide")

# 侧边栏
st.sidebar.header("⭐ 口碑筛选")
price_ranges = get_price_ranges()
selected_price = st.sidebar.multiselect("价格区间", price_ranges, default=price_ranges)

st.title("⭐ 口碑评分分析")

# 加载数据
ratings_df = load_ratings_with_models()

# 价格筛选
price_bins = [low for low, high, label in PRICE_RANGES] + [float('inf')]
price_labels = [label for low, high, label in PRICE_RANGES]
ratings_df["price_range"] = pd.cut(
    ratings_df["guide_price_min"], bins=price_bins, labels=price_labels, right=False
)
ratings_df = ratings_df[ratings_df["price_range"].isin(selected_price)]

# ========== 评分分布 ==========
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 综合评分分布")
    fig_hist = px.histogram(
        ratings_df, x="overall_score", nbins=20,
        title="车型综合评分分布",
        labels={"overall_score": "综合评分", "count": "车型数量"},
        color_discrete_sequence=["#1f77b4"],
    )
    fig_hist.update_layout(bargap=0.1)
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("📈 各维度平均评分")
    dim_scores = {}
    for dim in ["appearance_score", "interior_score", "power_score", "space_score",
                 "fuel_score", "handling_score", "comfort_score", "value_score"]:
        dim_scores[dim] = ratings_df[dim].mean()
    dim_df = pd.DataFrame({
        "dimension": ["外观", "内饰", "动力", "空间", "油耗", "操控", "舒适性", "性价比"],
        "avg_score": [dim_scores.get(f"{d}_score", 0) for d in
                      ["appearance", "interior", "power", "space", "fuel", "handling", "comfort", "value"]]
    })

    fig_dim = px.bar(
        dim_df, x="dimension", y="avg_score",
        title="各评分维度平均分",
        labels={"dimension": "维度", "avg_score": "平均分"},
        color="avg_score", color_continuous_scale="RdYlGn",
        range_y=[3.5, 5],
    )
    st.plotly_chart(fig_dim, use_container_width=True)

# ========== 品牌评分排名 ==========
st.subheader("🏭 品牌平均评分排名")
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

fig_br = px.bar(
    brand_ratings.head(15), x="overall_score", y="brand_name",
    orientation="h", color="brand_category",
    title="品牌平均评分 TOP 15",
    labels={"overall_score": "综合评分", "brand_name": "品牌", "brand_category": "类别"},
    range_x=[3.5, 5],
)
fig_br.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_br, use_container_width=True)

# ========== 雷达图 ==========
st.subheader("🎯 品牌雷达图对比")
brand_options = get_brand_options()
selected_brands = st.multiselect("选择品牌对比（最多 5 个）", brand_options, default=brand_options[:3])

if selected_brands and len(selected_brands) <= 5:
    dimensions = ["外观", "内饰", "动力", "空间", "油耗", "操控", "舒适性", "性价比"]
    score_cols = ["appearance_score", "interior_score", "power_score", "space_score",
                  "fuel_score", "handling_score", "comfort_score", "value_score"]

    fig_radar = go.Figure()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for i, brand in enumerate(selected_brands):
        brand_data = ratings_df[ratings_df["brand_name"] == brand]
        if not brand_data.empty:
            scores = [brand_data[col].mean() for col in score_cols]
            scores.append(scores[0])  # 闭合
            dims = dimensions + [dimensions[0]]

            fig_radar.add_trace(go.Scatterpolar(
                r=scores, theta=dims, fill='toself',
                name=brand, line_color=colors[i % len(colors)],
                opacity=0.6,
            ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[3.5, 5])),
        showlegend=True, title="品牌评分雷达图对比",
        height=600,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ========== 车型评分 TOP ==========
st.subheader("🏆 车型综合评分 TOP 20")
model_ratings = ratings_df.sort_values("overall_score", ascending=False).head(20)

fig_mr = px.bar(
    model_ratings, x="overall_score", y="model_name",
    orientation="h", color="brand_category",
    title="车型综合评分 TOP 20",
    labels={"overall_score": "综合评分", "model_name": "车型", "brand_category": "类别"},
    range_x=[3.5, 5],
)
fig_mr.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_mr, use_container_width=True)
