"""
图表生成模块
"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, CHART_OUTPUT_DIR, CHINESE_FONT

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = [CHINESE_FONT]
matplotlib.rcParams['axes.unicode_minus'] = False

# 设置 Seaborn 样式
sns.set_theme(style="whitegrid", palette="husl")
sns.set_context("notebook", font_scale=1.2)


class ChartGenerator:
    """图表生成器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.output_dir = CHART_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 颜色配置
        self.colors = {
            "primary": "#3B82F6",
            "secondary": "#10B981",
            "accent": "#F59E0B",
            "danger": "#EF4444",
            "purple": "#8B5CF6",
            "pink": "#EC4899",
        }

        self.energy_colors = {
            "纯电动": "#3B82F6",
            "插电混动": "#10B981",
            "增程式": "#F59E0B",
            "燃油": "#6B7280",
            "油电混动": "#8B5CF6",
        }

    def create_brand_sales_pie(self, year: int = 2024) -> str:
        """
        品牌市场份额饼图

        Returns:
            图表文件路径
        """
        query = """
        SELECT b.name, SUM(s.sales_volume) as total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ?
        GROUP BY b.id
        ORDER BY total_sales DESC
        LIMIT 10
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 创建饼图
        fig = px.pie(
            df,
            values="total_sales",
            names="name",
            title=f"{year}年品牌市场份额 TOP 10",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            width=800,
            height=600,
        )

        # 保存
        filepath = self.output_dir / "brand_sales_pie.html"
        fig.write_html(str(filepath))
        print(f"  - 品牌市场份额饼图: {filepath}")

        return str(filepath)

    def create_price_distribution_bar(self) -> str:
        """
        价格区间分布柱状图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            CASE
                WHEN guide_price_min < 5 THEN '5万以下'
                WHEN guide_price_min < 10 THEN '5-10万'
                WHEN guide_price_min < 15 THEN '10-15万'
                WHEN guide_price_min < 20 THEN '15-20万'
                WHEN guide_price_min < 30 THEN '20-30万'
                WHEN guide_price_min < 50 THEN '30-50万'
                WHEN guide_price_min < 100 THEN '50-100万'
                ELSE '100万以上'
            END AS price_range,
            COUNT(*) AS model_count
        FROM models
        GROUP BY price_range
        ORDER BY MIN(guide_price_min)
        """
        df = pd.read_sql(query, self.conn)

        # 创建柱状图
        fig = px.bar(
            df,
            x="price_range",
            y="model_count",
            title="车型价格区间分布",
            labels={"price_range": "价格区间", "model_count": "车型数量"},
            color="model_count",
            color_continuous_scale="Blues",
        )

        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            xaxis_tickangle=-45,
            width=900,
            height=600,
        )

        # 保存
        filepath = self.output_dir / "price_distribution_bar.html"
        fig.write_html(str(filepath))
        print(f"  - 价格区间分布柱状图: {filepath}")

        return str(filepath)

    def create_energy_type_sales_bar(self, year: int = 2024) -> str:
        """
        各能源类型销量柱状图

        Returns:
            图表文件路径
        """
        query = """
        SELECT m.energy_type, SUM(s.sales_volume) as total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year = ?
        GROUP BY m.energy_type
        ORDER BY total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 创建柱状图
        fig = px.bar(
            df,
            x="energy_type",
            y="total_sales",
            title=f"{year}年各能源类型销量",
            labels={"energy_type": "能源类型", "total_sales": "销量"},
            color="energy_type",
            color_discrete_map=self.energy_colors,
        )

        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            width=800,
            height=600,
            showlegend=False,
        )

        # 保存
        filepath = self.output_dir / "energy_type_sales_bar.html"
        fig.write_html(str(filepath))
        print(f"  - 能源类型销量柱状图: {filepath}")

        return str(filepath)

    def create_new_energy_penetration_line(self, year: int = 2024) -> str:
        """
        新能源渗透率趋势图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            s.month,
            SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) * 100.0 / SUM(s.sales_volume) AS penetration_rate
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year = ?
        GROUP BY s.month
        ORDER BY s.month
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 创建折线图
        fig = px.line(
            df,
            x="month",
            y="penetration_rate",
            title=f"{year}年新能源渗透率趋势",
            labels={"month": "月份", "penetration_rate": "渗透率 (%)"},
            markers=True,
        )

        fig.update_traces(line_color=self.colors["primary"], line_width=3)
        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            width=900,
            height=500,
            xaxis=dict(tickmode='linear', dtick=1),
        )

        # 保存
        filepath = self.output_dir / "new_energy_penetration_line.html"
        fig.write_html(str(filepath))
        print(f"  - 新能源渗透率趋势图: {filepath}")

        return str(filepath)

    def create_rating_radar(self, brand_name: str) -> str:
        """
        品牌评分雷达图

        Args:
            brand_name: 品牌名称

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            ROUND(AVG(r.appearance_score), 2) AS 外观,
            ROUND(AVG(r.interior_score), 2) AS 内饰,
            ROUND(AVG(r.power_score), 2) AS 动力,
            ROUND(AVG(r.space_score), 2) AS 空间,
            ROUND(AVG(r.fuel_score), 2) AS 油耗,
            ROUND(AVG(r.handling_score), 2) AS 操控,
            ROUND(AVG(r.comfort_score), 2) AS 舒适性,
            ROUND(AVG(r.value_score), 2) AS 性价比
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE b.name = ?
        """
        df = pd.read_sql(query, self.conn, params=[brand_name])

        if df.empty:
            return ""

        # 准备雷达图数据
        categories = df.columns.tolist()
        values = df.iloc[0].tolist()
        values.append(values[0])  # 闭合
        categories.append(categories[0])

        # 创建雷达图
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=brand_name,
            line_color=self.colors["primary"],
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=True,
            title=f"{brand_name}品牌评分雷达图",
            font=dict(family=CHINESE_FONT, size=14),
            width=700,
            height=600,
        )

        # 保存
        filepath = self.output_dir / f"rating_radar_{brand_name}.html"
        fig.write_html(str(filepath))
        print(f"  - {brand_name}评分雷达图: {filepath}")

        return str(filepath)

    def create_price_sales_scatter(self, year: int = 2024) -> str:
        """
        价格与销量散点图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            m.name AS model_name,
            b.name AS brand_name,
            m.guide_price_min AS price,
            SUM(s.sales_volume) AS total_sales,
            m.energy_type
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ? AND m.guide_price_min > 0
        GROUP BY m.id
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 创建散点图
        fig = px.scatter(
            df,
            x="price",
            y="total_sales",
            color="energy_type",
            size="total_sales",
            hover_name="model_name",
            hover_data=["brand_name", "price", "total_sales"],
            title=f"{year}年价格与销量关系",
            labels={"price": "价格 (万元)", "total_sales": "销量"},
            color_discrete_map=self.energy_colors,
        )

        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            width=1000,
            height=700,
        )

        # 保存
        filepath = self.output_dir / "price_sales_scatter.html"
        fig.write_html(str(filepath))
        print(f"  - 价格销量散点图: {filepath}")

        return str(filepath)

    def create_city_sales_bar(self, year: int = 2024, top_n: int = 15) -> str:
        """
        城市销量柱状图

        Returns:
            图表文件路径
        """
        query = """
        SELECT city, SUM(sales_volume) as total_sales
        FROM city_sales
        WHERE year = ?
        GROUP BY city
        ORDER BY total_sales DESC
        LIMIT ?
        """
        df = pd.read_sql(query, self.conn, params=[year, top_n])

        # 创建柱状图
        fig = px.bar(
            df,
            x="city",
            y="total_sales",
            title=f"{year}年城市销量 TOP {top_n}",
            labels={"city": "城市", "total_sales": "销量"},
            color="total_sales",
            color_continuous_scale="Viridis",
        )

        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            xaxis_tickangle=-45,
            width=1000,
            height=600,
        )

        # 保存
        filepath = self.output_dir / "city_sales_bar.html"
        fig.write_html(str(filepath))
        print(f"  - 城市销量柱状图: {filepath}")

        return str(filepath)

    def create_region_sales_pie(self, year: int = 2024) -> str:
        """
        区域销量饼图

        Returns:
            图表文件路径
        """
        query = """
        SELECT region, SUM(sales_volume) as total_sales
        FROM city_sales
        WHERE year = ?
        GROUP BY region
        ORDER BY total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 创建饼图
        fig = px.pie(
            df,
            values="total_sales",
            names="region",
            title=f"{year}年区域销量分布",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            width=800,
            height=600,
        )

        # 保存
        filepath = self.output_dir / "region_sales_pie.html"
        fig.write_html(str(filepath))
        print(f"  - 区域销量饼图: {filepath}")

        return str(filepath)

    def create_monthly_sales_trend(self, year: int = 2024) -> str:
        """
        月度销量趋势图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            s.month,
            m.energy_type,
            SUM(s.sales_volume) as total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        WHERE s.year = ?
        GROUP BY s.month, m.energy_type
        ORDER BY s.month, m.energy_type
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 创建折线图
        fig = px.line(
            df,
            x="month",
            y="total_sales",
            color="energy_type",
            title=f"{year}年月度销量趋势",
            labels={"month": "月份", "total_sales": "销量", "energy_type": "能源类型"},
            markers=True,
            color_discrete_map=self.energy_colors,
        )

        fig.update_layout(
            font=dict(family=CHINESE_FONT, size=14),
            width=1000,
            height=600,
            xaxis=dict(tickmode='linear', dtick=1),
        )

        # 保存
        filepath = self.output_dir / "monthly_sales_trend.html"
        fig.write_html(str(filepath))
        print(f"  - 月度销量趋势图: {filepath}")

        return str(filepath)

    def create_brand_category_comparison(self, year: int = 2024) -> str:
        """
        品牌类别对比图

        Returns:
            图表文件路径
        """
        query = """
        SELECT
            b.category,
            SUM(s.sales_volume) as total_sales,
            COUNT(DISTINCT m.id) as model_count
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE s.year = ?
        GROUP BY b.category
        ORDER BY total_sales DESC
        """
        df = pd.read_sql(query, self.conn, params=[year])

        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("销量占比", "车型数量"),
            specs=[[{"type": "pie"}, {"type": "pie"}]]
        )

        # 销量饼图
        fig.add_trace(
            go.Pie(
                labels=df["category"],
                values=df["total_sales"],
                name="销量",
                marker_colors=px.colors.qualitative.Set3,
            ),
            row=1, col=1
        )

        # 车型数量饼图
        fig.add_trace(
            go.Pie(
                labels=df["category"],
                values=df["model_count"],
                name="车型数",
                marker_colors=px.colors.qualitative.Set3,
            ),
            row=1, col=2
        )

        fig.update_layout(
            title=f"{year}年品牌类别对比",
            font=dict(family=CHINESE_FONT, size=14),
            width=1200,
            height=500,
        )

        # 保存
        filepath = self.output_dir / "brand_category_comparison.html"
        fig.write_html(str(filepath))
        print(f"  - 品牌类别对比图: {filepath}")

        return str(filepath)

    def generate_all_charts(self, year: int = 2024):
        """生成所有图表"""
        print("\n" + "=" * 60)
        print("生成可视化图表")
        print("=" * 60)

        charts = []

        # 1. 品牌市场份额饼图
        print("\n[1/9] 品牌市场份额饼图...")
        charts.append(self.create_brand_sales_pie(year))

        # 2. 价格区间分布柱状图
        print("[2/9] 价格区间分布柱状图...")
        charts.append(self.create_price_distribution_bar())

        # 3. 能源类型销量柱状图
        print("[3/9] 能源类型销量柱状图...")
        charts.append(self.create_energy_type_sales_bar(year))

        # 4. 新能源渗透率趋势图
        print("[4/9] 新能源渗透率趋势图...")
        charts.append(self.create_new_energy_penetration_line(year))

        # 5. 价格销量散点图
        print("[5/9] 价格销量散点图...")
        charts.append(self.create_price_sales_scatter(year))

        # 6. 城市销量柱状图
        print("[6/9] 城市销量柱状图...")
        charts.append(self.create_city_sales_bar(year))

        # 7. 区域销量饼图
        print("[7/9] 区域销量饼图...")
        charts.append(self.create_region_sales_pie(year))

        # 8. 月度销量趋势图
        print("[8/9] 月度销量趋势图...")
        charts.append(self.create_monthly_sales_trend(year))

        # 9. 品牌类别对比图
        print("[9/9] 品牌类别对比图...")
        charts.append(self.create_brand_category_comparison(year))

        # 生成品牌评分雷达图（TOP 5 品牌）
        print("\n[额外] 品牌评分雷达图...")
        top_brands = pd.read_sql(
            "SELECT b.name FROM brands b JOIN models m ON b.id = m.brand_id GROUP BY b.id ORDER BY COUNT(m.id) DESC LIMIT 5",
            self.conn
        )
        for _, row in top_brands.iterrows():
            charts.append(self.create_rating_radar(row["name"]))

        print(f"\n[[OK]] 共生成 {len(charts)} 个图表")
        print(f"[[OK]] 图表保存目录: {self.output_dir}")

        return charts

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    generator = ChartGenerator()
    generator.generate_all_charts()
    generator.close()
