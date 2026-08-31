"""
汽车市场数据分析 - Streamlit 主入口
"""
import streamlit as st
import requests
import time
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_app.utils import get_market_overview, get_year_options

API_BASE = "http://localhost:8000"

# ========== 页面配置 ==========
st.set_page_config(
    page_title="汽车市场数据分析平台",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== 自定义样式 ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .insight-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ========== 主页 ==========
def main():
    st.markdown('<div class="main-header">🚗 汽车市场数据分析平台</div>', unsafe_allow_html=True)
    st.markdown("---")

    # 侧边栏筛选
    st.sidebar.header("📊 筛选条件")
    years = get_year_options()
    selected_year = st.sidebar.selectbox("选择年份", years, index=len(years) - 1 if years else 0)

    # ========== 数据导入 ==========
    st.sidebar.markdown("---")
    st.sidebar.header("📥 数据导入")

    if st.sidebar.button("🚗 从懂车帝导入数据", use_container_width=True):
        st.session_state.show_import = True

    if st.session_state.get("show_import"):
        with st.sidebar:
            st.info("点击下方按钮启动导入，浏览器会自动打开懂车帝，请手动登录后系统会自动抓取数据。")
            if st.button("▶ 启动导入", use_container_width=True):
                try:
                    resp = requests.post(f"{API_BASE}/api/import/dongchedi", timeout=5)
                    if resp.status_code == 200:
                        task_id = resp.json()["task_id"]
                        st.session_state.import_task_id = task_id
                        st.success(f"任务已启动: {task_id}")
                    else:
                        st.error("启动失败")
                except Exception as e:
                    st.error(f"连接后端失败: {e}")
                    st.info("请确保 FastAPI 后端已启动: cd backend && uvicorn main:app --reload")

            # 显示导入进度
            if st.session_state.get("import_task_id"):
                task_id = st.session_state.import_task_id
                try:
                    resp = requests.get(f"{API_BASE}/api/import/status/{task_id}", timeout=5)
                    if resp.status_code == 200:
                        task = resp.json()
                        status = task.get("status", "unknown")
                        progress = task.get("progress", 0)
                        message = task.get("message", "")

                        if status == "done":
                            st.success(f"✅ {message}")
                            if st.button("刷新数据", use_container_width=True):
                                st.cache_data.clear()
                                st.rerun()
                        elif status == "error":
                            st.error(f"❌ {message}")
                        else:
                            st.progress(progress / 100)
                            st.info(message)
                except Exception:
                    pass

    # 加载概览数据
    overview = get_market_overview(selected_year)

    # ========== KPI 卡片 ==========
    st.subheader("📈 市场概览")
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

    # ========== 快速图表 ==========
    st.subheader("📊 快速分析")
    col_left, col_right = st.columns(2)

    with col_left:
        # 品牌销量 TOP 10
        from streamlit_app.utils import load_sales_with_models
        import plotly.express as px

        sales_df = load_sales_with_models(selected_year)
        brand_sales = sales_df.groupby("brand_name")["sales_volume"].sum().reset_index()
        brand_sales = brand_sales.sort_values("sales_volume", ascending=False).head(10)

        fig_brand = px.bar(
            brand_sales, x="sales_volume", y="brand_name",
            orientation="h", title=f"{selected_year}年 品牌销量 TOP 10",
            labels={"sales_volume": "销量(辆)", "brand_name": "品牌"},
            color="sales_volume", color_continuous_scale="Blues",
        )
        fig_brand.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        st.plotly_chart(fig_brand, use_container_width=True)

    with col_right:
        # 新能源渗透率
        from streamlit_app.utils import load_sales_with_models as load_sw
        import pandas as pd

        all_sales = load_sw(selected_year)
        energy_sales = all_sales.groupby("energy_type")["sales_volume"].sum().reset_index()
        energy_sales["is_ne"] = energy_sales["energy_type"].isin(["纯电动", "插电混动", "增程式"])
        ne_summary = energy_sales.groupby("is_ne")["sales_volume"].sum().reset_index()
        ne_summary["type"] = ne_summary["is_ne"].map({True: "新能源", False: "传统燃油"})

        fig_energy = px.pie(
            ne_summary, values="sales_volume", names="type",
            title=f"{selected_year}年 新能源 vs 传统燃油",
            color_discrete_map={"新能源": "#00d4aa", "传统燃油": "#ff6b6b"},
        )
        st.plotly_chart(fig_energy, use_container_width=True)

    # ========== 导航提示 ==========
    st.markdown("---")
    st.info("👈 使用左侧导航栏访问各分析模块：品牌分析、价格分析、新能源分析、口碑分析、趋势分析、城市分析")


if __name__ == "__main__":
    main()
