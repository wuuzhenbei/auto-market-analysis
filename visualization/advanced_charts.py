"""
高级可视化图表模块
生成时间序列、趋势分析等高级图表
"""
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, CHART_OUTPUT_DIR, CHINESE_FONT


class AdvancedChartGenerator:
    """高级图表生成器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.output_dir = CHART_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.energy_colors = {
            "纯电动": "#3B82F6",
            "插电混动": "#10B981",
            "增程式": "#F59E0B",
            "燃油": "#6B7280",
            "油电混动": "#8B5CF6",
        }

    def create_monthly_sales_trend(self, start_year=2024, end_year=2026) -> str:
        """
        月度销量趋势图（多线图）

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            s.year,
            s.month,
            m.energy_type,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year >= ? AND s.year <= ?
        GROUP BY s.year, s.month, m.energy_type
        ORDER BY s.year, s.month, m.energy_type
        """
        df = pd.read_sql(query, self.conn, params=[start_year, end_year])
        df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)

        fig = px.line(
            df,
            x="year_month",
            y="total_sales",
            color="energy_type",
            title=f"{start_year}-{end_year}年各能源类型月度销量趋势",
            labels={"year_month": "年月", "total_sales": "销量", "energy_type": "能源类型"},
            color_discrete_map=self.energy_colors,
        )

        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            width=1200,
            height=600,
            xaxis_tickangle=-45,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        filepath = self.output_dir / "monthly_sales_trend_multi.html"
        fig.write_html(str(filepath))
        print(f"  - 月度销量趋势图: {filepath}")
        return str(filepath)

    def create_ne_penetration_trend(self, start_year=2024, end_year=2026) -> str:
        """
        新能源渗透率趋势图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            s.year,
            s.month,
            SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) * 100.0 / SUM(s.sales_volume) AS penetration_rate
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year >= ? AND s.year <= ?
        GROUP BY s.year, s.month
        ORDER BY s.year, s.month
        """
        df = pd.read_sql(query, self.conn, params=[start_year, end_year])
        df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["year_month"],
            y=df["penetration_rate"],
            mode="lines+markers",
            name="新能源渗透率",
            line=dict(color="#3B82F6", width=3),
            marker=dict(size=8),
        ))

        # 添加趋势线（需要至少2个数据点）
        if len(df) >= 2:
            try:
                z = np.polyfit(range(len(df)), df["penetration_rate"], 1)
                p = np.poly1d(z)
                fig.add_trace(go.Scatter(
                    x=df["year_month"],
                    y=p(range(len(df))),
                    mode="lines",
                    name="趋势线",
                    line=dict(color="#EF4444", width=2, dash="dash"),
                ))
            except:
                pass  # 跳过趋势线计算

        fig.update_layout(
            title=f"{start_year}-{end_year}年新能源渗透率趋势",
            xaxis_title="年月",
            yaxis_title="渗透率 (%)",
            font=dict(family=CHINESE_FONT, size=14),
            width=1200,
            height=600,
            xaxis_tickangle=-45,
        )

        filepath = self.output_dir / "ne_penetration_trend.html"
        fig.write_html(str(filepath))
        print(f"  - 新能源渗透率趋势图: {filepath}")
        return str(filepath)

    def create_brand_market_share_heatmap(self, start_year=2024, end_year=2026, top_n=10) -> str:
        """
        品牌市场份额热力图

        Returns:
            图表文件路径
        """
        # 获取TOP N品牌
        query = """
        SELECT b.name
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.id
        ORDER BY SUM(s.sales_volume) DESC
        LIMIT ?
        """
        top_brands = pd.read_sql(query, self.conn, params=[top_n])["name"].tolist()

        # 获取各品牌季度市场份额
        data = []
        for year in range(start_year, end_year + 1):
            max_q = 3 if year == end_year else 4
            for q in range(1, max_q + 1):
                months = [(q-1)*3+1, (q-1)*3+2, (q-1)*3+3]
                query = """
                SELECT
                    b.name AS brand_name,
                    SUM(s.sales_volume) AS brand_sales
                FROM sales s
                JOIN models m ON s.model_id = m.id
                JOIN brands b ON m.brand_id = b.id
                WHERE s.year = ? AND s.month IN (?, ?, ?)
                GROUP BY b.id
                """
                brand_df = pd.read_sql(query, self.conn, params=[year] + months)

                total_query = """
                SELECT SUM(sales_volume) AS total_sales
                FROM sales
                WHERE year = ? AND month IN (?, ?, ?)
                """
                total = pd.read_sql(total_query, self.conn, params=[year] + months).iloc[0, 0]

                for _, row in brand_df.iterrows():
                    if row["brand_name"] in top_brands:
                        share = round(row["brand_sales"] / total * 100, 2)
                        data.append({
                            "brand": row["brand_name"],
                            "quarter": f"{year}Q{q}",
                            "share": share
                        })

        df = pd.DataFrame(data)
        pivot = df.pivot(index="brand", columns="quarter", values="share").fillna(0)

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale="YlOrRd",
            text=pivot.values.round(1),
            texttemplate="%{text}%",
            textfont={"size": 12},
        ))

        fig.update_layout(
            title=f"{start_year}-{end_year}年品牌市场份额变化热力图",
            xaxis_title="季度",
            yaxis_title="品牌",
            font=dict(family=CHINESE_FONT, size=14),
            width=1200,
            height=600,
        )

        filepath = self.output_dir / "brand_share_heatmap.html"
        fig.write_html(str(filepath))
        print(f"  - 品牌份额热力图: {filepath}")
        return str(filepath)

    def create_yoy_growth_bar(self, year=2025) -> str:
        """
        同比增长率柱状图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            b.name AS brand_name,
            SUM(CASE WHEN s.year = ? THEN s.sales_volume ELSE 0 END) AS current_sales,
            SUM(CASE WHEN s.year = ? - 1 THEN s.sales_volume ELSE 0 END) AS last_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year IN (?, ? - 1)
        GROUP BY b.id
        HAVING last_sales > 10000
        ORDER BY current_sales DESC
        LIMIT 20
        """
        df = pd.read_sql(query, self.conn, params=[year, year, year, year])
        df["yoy_growth"] = ((df["current_sales"] - df["last_sales"]) / df["last_sales"] * 100).round(2)
        df = df.sort_values("yoy_growth", ascending=True)

        colors = ["#EF4444" if x < 0 else "#10B981" for x in df["yoy_growth"]]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=df["brand_name"],
            x=df["yoy_growth"],
            orientation="h",
            marker_color=colors,
            text=df["yoy_growth"].apply(lambda x: f"{x:+.1f}%"),
            textposition="outside",
        ))

        fig.update_layout(
            title=f"{year}年品牌同比增长率 TOP 20",
            xaxis_title="同比增长率 (%)",
            yaxis_title="品牌",
            font=dict(family=CHINESE_FONT, size=14),
            width=1000,
            height=800,
            xaxis=dict(zeroline=True, zerolinecolor="black", zerolinewidth=1),
        )

        filepath = self.output_dir / f"yoy_growth_{year}.html"
        fig.write_html(str(filepath))
        print(f"  - 同比增长率图: {filepath}")
        return str(filepath)

    def create_seasonal_analysis_chart(self) -> str:
        """
        季节性分析图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            month,
            ROUND(AVG(monthly_sales), 0) AS avg_sales
        FROM (
            SELECT
                year,
                month,
                SUM(sales_volume) AS monthly_sales
            FROM sales
            GROUP BY year, month
        )
        GROUP BY month
        ORDER BY month
        """
        df = pd.read_sql(query, self.conn)

        # 添加月份名称
        month_names = ["1月", "2月", "3月", "4月", "5月", "6月",
                      "7月", "8月", "9月", "10月", "11月", "12月"]
        df["month_name"] = df["month"].apply(lambda x: month_names[x-1])

        # 计算平均值
        avg = df["avg_sales"].mean()

        fig = go.Figure()

        # 柱状图
        colors = ["#EF4444" if x < avg else "#10B981" for x in df["avg_sales"]]
        fig.add_trace(go.Bar(
            x=df["month_name"],
            y=df["avg_sales"],
            marker_color=colors,
            name="月均销量",
        ))

        # 平均线
        fig.add_trace(go.Scatter(
            x=df["month_name"],
            y=[avg] * len(df),
            mode="lines",
            name="年均值",
            line=dict(color="#6B7280", width=2, dash="dash"),
        ))

        fig.update_layout(
            title="汽车销量季节性分析（月均销量）",
            xaxis_title="月份",
            yaxis_title="平均销量",
            font=dict(family=CHINESE_FONT, size=14),
            width=1000,
            height=600,
        )

        filepath = self.output_dir / "seasonal_analysis.html"
        fig.write_html(str(filepath))
        print(f"  - 季节性分析图: {filepath}")
        return str(filepath)

    def create_price_segment_analysis(self) -> str:
        """
        价格段销量分析图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            CASE
                WHEN m.guide_price_min < 10 THEN '10万以下'
                WHEN m.guide_price_min < 20 THEN '10-20万'
                WHEN m.guide_price_min < 30 THEN '20-30万'
                WHEN m.guide_price_min < 50 THEN '30-50万'
                ELSE '50万以上'
            END AS price_segment,
            s.year,
            SUM(s.sales_volume) AS total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year IN (2024, 2025, 2026)
        GROUP BY price_segment, s.year
        ORDER BY MIN(m.guide_price_min), s.year
        """
        df = pd.read_sql(query, self.conn)

        fig = px.bar(
            df,
            x="price_segment",
            y="total_sales",
            color="year",
            title="各价格段年度销量对比",
            labels={"price_segment": "价格段", "total_sales": "销量", "year": "年份"},
            barmode="group",
            color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
        )

        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            width=1000,
            height=600,
        )

        filepath = self.output_dir / "price_segment_analysis.html"
        fig.write_html(str(filepath))
        print(f"  - 价格段分析图: {filepath}")
        return str(filepath)

    def generate_all_advanced_charts(self):
        """生成所有高级图表"""
        print("\n" + "=" * 60)
        print("生成高级可视化图表")
        print("=" * 60)

        charts = []

        print("\n[1/6] 月度销量趋势图...")
        charts.append(self.create_monthly_sales_trend())

        print("[2/6] 新能源渗透率趋势图...")
        charts.append(self.create_ne_penetration_trend())

        print("[3/6] 品牌份额热力图...")
        charts.append(self.create_brand_market_share_heatmap())

        print("[4/6] 同比增长率图...")
        charts.append(self.create_yoy_growth_bar(2025))

        print("[5/6] 季节性分析图...")
        charts.append(self.create_seasonal_analysis_chart())

        print("[6/6] 价格段分析图...")
        charts.append(self.create_price_segment_analysis())

        print(f"\n[OK] 共生成 {len(charts)} 个高级图表")
        return charts

    def close(self):
        """关闭连接"""
        self.conn.close()


# 需要导入 numpy
import numpy as np


if __name__ == "__main__":
    generator = AdvancedChartGenerator()
    generator.generate_all_advanced_charts()
    generator.close()
