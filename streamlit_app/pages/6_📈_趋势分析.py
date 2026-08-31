"""
趋势分析页面
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from streamlit_app.utils import (
    load_sales_with_models, get_year_options, get_brand_options,
)

st.set_page_config(page_title="趋势分析", page_icon="📈", layout="wide")

# 侧边栏
st.sidebar.header("📈 趋势筛选")
years = get_year_options()
if len(years) >= 2:
    start_year = st.sidebar.selectbox("起始年份", years, index=0)
    end_year = st.sidebar.selectbox("结束年份", years, index=len(years) - 1)
else:
    start_year = end_year = years[0] if years else 2024

st.title("📈 趋势分析")

# 导出按钮
col_export1, col_export2, col_export3 = st.columns([1, 1, 1])
with col_export1:
    if st.button("📥 导出Excel", use_container_width=True):
        with st.spinner("导出中..."):
            from export.excel_exporter import ExcelExporter
            exporter = ExcelExporter()
            exporter.export_comprehensive_data(2026)
            exporter.close()
            st.success("✅ 已导出到 data/excel/")
with col_export2:
    all_sales_export = load_sales_with_models()
    csv_data = all_sales_export.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下载CSV", csv_data, "trend_analysis.csv", "text/csv", use_container_width=True)

st.markdown("---")

# 加载多月数据
all_sales = load_sales_with_models()

# 筛选时间范围
all_sales = all_sales[(all_sales["year"] >= start_year) & (all_sales["year"] <= end_year)]
all_sales["year_month"] = all_sales["year"].astype(str) + "-" + all_sales["month"].astype(str).str.zfill(2)

# ========== 月度销量趋势 ==========
st.subheader("📊 月度销量趋势")
monthly_total = all_sales.groupby("year_month")["sales_volume"].sum().reset_index()
monthly_total = monthly_total.sort_values("year_month")

fig_monthly = px.line(
    monthly_total, x="year_month", y="sales_volume",
    title="月度总销量趋势",
    labels={"year_month": "月份", "sales_volume": "销量(辆)"},
    markers=True,
)
fig_monthly.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig_monthly, use_container_width=True)

# ========== 按能源类型月度趋势 ==========
st.subheader("⚡ 按能源类型月度趋势")
monthly_energy = all_sales.groupby(["year_month", "energy_type"])["sales_volume"].sum().reset_index()
monthly_energy = monthly_energy.sort_values("year_month")

fig_me = px.line(
    monthly_energy, x="year_month", y="sales_volume", color="energy_type",
    title="各能源类型月度销量趋势",
    labels={"year_month": "月份", "sales_volume": "销量(辆)", "energy_type": "能源类型"},
    markers=True,
    color_discrete_map={
        "纯电动": "#00d4aa", "插电混动": "#ffd93d", "增程式": "#6c5ce7",
        "燃油": "#ff6b6b", "油电混动": "#a8e6cf"
    },
)
fig_me.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig_me, use_container_width=True)

# ========== 新能源渗透率趋势 ==========
st.subheader("🔋 新能源渗透率趋势")
all_sales["is_new_energy"] = all_sales["energy_type"].isin(["纯电动", "插电混动", "增程式"])
ne_monthly = all_sales.groupby(["year_month", "is_new_energy"])["sales_volume"].sum().reset_index()
ne_pivot = ne_monthly.pivot(index="year_month", columns="is_new_energy", values="sales_volume").fillna(0)
ne_pivot.columns = ["传统燃油", "新能源"]
ne_pivot["渗透率"] = ne_pivot["新能源"] / (ne_pivot["新能源"] + ne_pivot["传统燃油"]) * 100
ne_pivot = ne_pivot.reset_index().sort_values("year_month")

fig_ne = px.line(
    ne_pivot, x="year_month", y="渗透率",
    title="新能源月度渗透率趋势",
    labels={"year_month": "月份", "渗透率": "渗透率(%)"},
    markers=True,
)
fig_ne.update_layout(xaxis_tickangle=45, yaxis_range=[0, 100])
st.plotly_chart(fig_ne, use_container_width=True)

# ========== 同比增长分析 ==========
if len(years) >= 2:
    st.subheader("📊 同比增长分析")
    target_year = st.selectbox("选择分析年份", years, index=len(years) - 1)
    prev_year = target_year - 1

    current = all_sales[all_sales["year"] == target_year].groupby("brand_name")["sales_volume"].sum().reset_index()
    current.columns = ["brand_name", "current_sales"]
    previous = all_sales[all_sales["year"] == prev_year].groupby("brand_name")["sales_volume"].sum().reset_index()
    previous.columns = ["brand_name", "last_sales"]

    yoy = current.merge(previous, on="brand_name", how="left")
    yoy["last_sales"] = yoy["last_sales"].fillna(0)
    yoy["yoy_growth"] = ((yoy["current_sales"] - yoy["last_sales"]) / yoy["last_sales"] * 100).round(1)
    yoy = yoy[yoy["last_sales"] > 0].sort_values("yoy_growth", ascending=False)

    fig_yoy = px.bar(
        yoy.head(20), x="yoy_growth", y="brand_name",
        orientation="h", title=f"{target_year}年 vs {prev_year}年 同比增长 TOP 20",
        labels={"yoy_growth": "同比增长(%)", "brand_name": "品牌"},
        color="yoy_growth",
        color_continuous_scale=["#ff4444", "#ffffff", "#00aa00"],
        color_continuous_midpoint=0,
    )
    fig_yoy.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_yoy, use_container_width=True)

# ========== 品牌份额趋势 ==========
st.subheader("🏭 品牌月度份额趋势")
brand_options = get_brand_options()
selected_brand = st.sidebar.selectbox("选择品牌", brand_options)

if selected_brand:
    brand_monthly = all_sales[all_sales["brand_name"] == selected_brand].groupby("year_month")["sales_volume"].sum().reset_index()
    total_monthly = all_sales.groupby("year_month")["sales_volume"].sum().reset_index()
    total_monthly.columns = ["year_month", "total_sales"]

    share = brand_monthly.merge(total_monthly, on="year_month")
    share["market_share"] = (share["sales_volume"] / share["total_sales"] * 100).round(1)
    share = share.sort_values("year_month")

    fig_share = px.line(
        share, x="year_month", y="market_share",
        title=f"{selected_brand} 月度市场份额趋势",
        labels={"year_month": "月份", "market_share": "市场份额(%)"},
        markers=True,
    )
    fig_share.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_share, use_container_width=True)
