"""
综合报告生成模块
"""
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH, PROCESSED_DATA_DIR
from analysis.brand_analysis import BrandAnalyzer
from analysis.price_analysis import PriceAnalyzer
from analysis.energy_analysis import EnergyAnalyzer
from analysis.rating_analysis import RatingAnalyzer
from analysis.performance_analysis import PerformanceAnalyzer


class ComprehensiveReport:
    """综合报告生成器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.PROCESSED_DATA_DIR = PROCESSED_DATA_DIR
        self.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    def generate_market_overview(self, year: int = None) -> dict:
        """
        生成市场概览

        Returns:
            包含市场关键指标的字典
        """
        overview = {}

        # 总销量
        if year:
            query = "SELECT SUM(sales_volume) FROM sales WHERE year = ?"
            cursor = self.conn.execute(query, [year])
        else:
            query = "SELECT SUM(sales_volume) FROM sales"
            cursor = self.conn.execute(query)
        result = cursor.fetchone()[0]
        overview["total_sales"] = result if result else 0

        # 品牌数量
        query = "SELECT COUNT(*) FROM brands"
        cursor = self.conn.execute(query)
        overview["brand_count"] = cursor.fetchone()[0]

        # 车型数量
        query = "SELECT COUNT(*) FROM models"
        cursor = self.conn.execute(query)
        overview["model_count"] = cursor.fetchone()[0]

        # 新能源渗透率
        if year:
            query = """
            SELECT
                SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) * 100.0 / SUM(s.sales_volume)
            FROM sales s
            JOIN models m ON s.model_id = m.id
            WHERE s.year = ?
            """
            cursor = self.conn.execute(query, [year])
        else:
            query = """
            SELECT
                SUM(CASE WHEN m.energy_type IN ('纯电动', '插电混动', '增程式') THEN s.sales_volume ELSE 0 END) * 100.0 / SUM(s.sales_volume)
            FROM sales s
            JOIN models m ON s.model_id = m.id
            """
            cursor = self.conn.execute(query)
        result = cursor.fetchone()[0]
        overview["new_energy_penetration"] = round(result, 2) if result else 0

        # 平均售价
        query = "SELECT AVG((guide_price_min + guide_price_max) / 2) FROM models WHERE guide_price_min > 0"
        cursor = self.conn.execute(query)
        result = cursor.fetchone()[0]
        overview["avg_price"] = round(result, 2) if result else 0

        # 平均评分
        query = "SELECT AVG(overall_score) FROM ratings"
        cursor = self.conn.execute(query)
        result = cursor.fetchone()[0]
        overview["avg_rating"] = round(result, 2) if result else 0

        return overview

    def generate_insights(self) -> list:
        """
        生成分析洞察

        Returns:
            洞察列表
        """
        insights = []

        # 1. 市场集中度分析
        query = """
        SELECT b.name, SUM(s.sales_volume) as total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.id
        ORDER BY total_sales DESC
        LIMIT 5
        """
        df = pd.read_sql(query, self.conn)
        total_query = "SELECT SUM(sales_volume) FROM sales"
        total = pd.read_sql(total_query, self.conn).iloc[0, 0]
        top5_share = df["total_sales"].sum() / total * 100 if total else 0

        insights.append({
            "category": "市场集中度",
            "insight": f"TOP 5 品牌市场份额合计 {top5_share:.1f}%，市场集中度{'较高' if top5_share > 50 else '适中'}",
            "detail": f"前五名: {', '.join(df['name'].tolist())}"
        })

        # 2. 新能源趋势
        query = """
        SELECT
            m.energy_type,
            SUM(s.sales_volume) as total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        GROUP BY m.energy_type
        """
        energy_df = pd.read_sql(query, self.conn)
        ne_sales = energy_df[energy_df["energy_type"].isin(["纯电动", "插电混动", "增程式"])]["total_sales"].sum()
        total_sales = energy_df["total_sales"].sum()
        ne_ratio = ne_sales / total_sales * 100 if total_sales else 0

        insights.append({
            "category": "新能源趋势",
            "insight": f"新能源车型销量占比 {ne_ratio:.1f}%，{'已成为市场主流' if ne_ratio > 50 else '正在快速渗透'}",
            "detail": f"纯电动、插电混动、增程式三分天下"
        })

        # 3. 价格战分析
        query = """
        SELECT
            CASE
                WHEN m.guide_price_min < 10 THEN '10万以下'
                WHEN m.guide_price_min < 20 THEN '10-20万'
                WHEN m.guide_price_min < 30 THEN '20-30万'
                ELSE '30万以上'
            END AS price_range,
            SUM(s.sales_volume) as total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        GROUP BY price_range
        ORDER BY total_sales DESC
        """
        price_df = pd.read_sql(query, self.conn)
        if not price_df.empty:
            top_range = price_df.iloc[0]
            insights.append({
                "category": "价格分布",
                "insight": f"最热销价格区间为 {top_range['price_range']}，销量占比 {top_range['total_sales']/total_sales*100:.1f}%",
                "detail": "经济型车型仍是市场主力"
            })

        # 4. 品牌类别分析
        query = """
        SELECT b.category, SUM(s.sales_volume) as total_sales
        FROM sales s
        JOIN models m ON s.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.category
        ORDER BY total_sales DESC
        """
        category_df = pd.read_sql(query, self.conn)
        if not category_df.empty:
            top_category = category_df.iloc[0]
            insights.append({
                "category": "品牌格局",
                "insight": f"{top_category['category']}品牌销量最高，占比 {top_category['total_sales']/total_sales*100:.1f}%",
                "detail": f"各类别销量: {', '.join([f'{row['category']}({row['total_sales']/total_sales*100:.1f}%)' for _, row in category_df.iterrows()])}"
            })

        # 5. 评分分析
        query = """
        SELECT
            b.name,
            AVG(r.overall_score) as avg_score
        FROM ratings r
        JOIN models m ON r.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        GROUP BY b.id
        ORDER BY avg_score DESC
        LIMIT 3
        """
        rating_df = pd.read_sql(query, self.conn)

        insights.append({
            "category": "用户口碑",
            "insight": f"用户评分最高的品牌: {', '.join(rating_df['name'].tolist())}",
            "detail": f"平均评分: {', '.join([f'{row['name']}({row['avg_score']:.1f})' for _, row in rating_df.iterrows()])}"
        })

        return insights

    def generate_report(self) -> str:
        """
        生成综合报告

        Returns:
            报告文本
        """
        print("\n" + "=" * 60)
        print("生成综合报告")
        print("=" * 60)

        # 1. 市场概览
        print("\n[1/3] 生成市场概览...")
        overview = self.generate_market_overview()

        # 2. 分析洞察
        print("[2/3] 生成分析洞察...")
        insights = self.generate_insights()

        # 3. 生成报告文本
        print("[3/3] 生成报告文本...")

        report = f"""
# 汽车市场数据分析报告

**报告日期**: {datetime.now().strftime('%Y年%m月%d日')}
**数据来源**: 懂车帝 (dongchedi.com)

---

## 一、市场概览

| 指标 | 数值 |
|------|------|
| 总销量 | {overview['total_sales']:,} 辆 |
| 品牌数量 | {overview['brand_count']} 个 |
| 车型数量 | {overview['model_count']} 个 |
| 新能源渗透率 | {overview['new_energy_penetration']}% |
| 平均售价 | {overview['avg_price']:.1f} 万元 |
| 平均评分 | {overview['avg_rating']:.1f} 分 |

---

## 二、核心洞察

"""

        for i, insight in enumerate(insights, 1):
            report += f"""### {i}. {insight['category']}

**洞察**: {insight['insight']}

**详情**: {insight['detail']}

"""

        report += """
---

## 三、分析维度

本报告涵盖以下分析维度：

1. **品牌分析** - 品牌销量排名、市场份额、品牌类别对比
2. **价格分析** - 价格区间分布、各价格段销量、性价比分析
3. **新能源分析** - 新能源渗透率、纯电动/插混/增程对比、续航分析
4. **口碑评分分析** - 评分分布、品牌/车型评分排名、各维度对比
5. **性能参数分析** - 动力对比、油耗分析、车身尺寸分析

---

## 四、数据来源

- 懂车帝 (dongchedi.com)
- 汽车之家 (autohome.com.cn)

---

## 五、技术栈

- **数据采集**: Python + Requests + BeautifulSoup
- **数据处理**: Pandas + NumPy
- **数据存储**: SQLite
- **数据可视化**: Matplotlib + Seaborn + Plotly
- **数据导出**: Excel + Tableau + Power BI

---

*报告由自动化分析系统生成*
"""

        # 保存报告
        report_path = self.PROCESSED_DATA_DIR / "analysis_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n[[OK]] 报告已保存: {report_path}")

        return report

    def run_all_analyses(self) -> dict:
        """运行所有分析"""
        print("=" * 60)
        print("汽车市场综合分析")
        print("=" * 60)

        results = {}

        # 1. 品牌分析
        brand_analyzer = BrandAnalyzer()
        results["brand"] = brand_analyzer.analyze()
        brand_analyzer.close()

        # 2. 价格分析
        price_analyzer = PriceAnalyzer()
        results["price"] = price_analyzer.analyze()
        price_analyzer.close()

        # 3. 新能源分析
        energy_analyzer = EnergyAnalyzer()
        results["energy"] = energy_analyzer.analyze()
        energy_analyzer.close()

        # 4. 口碑评分分析
        rating_analyzer = RatingAnalyzer()
        results["rating"] = rating_analyzer.analyze()
        rating_analyzer.close()

        # 5. 性能参数分析
        performance_analyzer = PerformanceAnalyzer()
        results["performance"] = performance_analyzer.analyze()
        performance_analyzer.close()

        # 6. 生成综合报告
        report = self.generate_report()

        return results

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    report_generator = ComprehensiveReport()
    results = report_generator.run_all_analyses()
    report_generator.close()
