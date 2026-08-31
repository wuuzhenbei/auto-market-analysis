"""
汽车市场数据分析 - 主运行脚本
一键运行完整数据分析流程
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from database.init_db import init_database
from analysis.data_cleaner import DataCleaner
from analysis.comprehensive_report import ComprehensiveReport
from analysis.time_series_analysis import TimeSeriesAnalyzer
from visualization.charts import ChartGenerator
from visualization.advanced_charts import AdvancedChartGenerator
from export.excel_exporter import ExcelExporter
from export.tableau_exporter import TableauExporter
from export.powerbi_exporter import PowerBIExporter


def main():
    """主函数"""
    print("=" * 60)
    print("汽车市场数据分析项目")
    print("=" * 60)

    # 1. 初始化数据库
    print("\n[步骤 1/8] 初始化数据库...")
    init_database()

    # 2. 数据清洗
    print("\n[步骤 2/8] 数据清洗...")
    cleaner = DataCleaner()
    cleaner.run()

    # 3. 运行综合分析
    print("\n[步骤 3/8] 运行综合分析...")
    report_generator = ComprehensiveReport()
    report_generator.run_all_analyses()
    report_generator.close()

    # 4. 运行时间序列分析
    print("\n[步骤 4/8] 运行时间序列分析...")
    time_series_analyzer = TimeSeriesAnalyzer()
    time_series_analyzer.analyze()
    time_series_analyzer.close()

    # 5. 生成基础可视化
    print("\n[步骤 5/8] 生成基础可视化图表...")
    chart_generator = ChartGenerator()
    chart_generator.generate_all_charts()
    chart_generator.close()

    # 6. 生成高级可视化
    print("\n[步骤 6/8] 生成高级可视化图表...")
    advanced_chart_generator = AdvancedChartGenerator()
    advanced_chart_generator.generate_all_advanced_charts()
    advanced_chart_generator.close()

    # 7. 导出 Excel
    print("\n[步骤 7/8] 导出 Excel 数据...")
    excel_exporter = ExcelExporter()
    excel_exporter.export_all()
    excel_exporter.close()

    # 8. 导出 Tableau/Power BI
    print("\n[步骤 8/8] 导出 Tableau/Power BI 数据...")
    tableau_exporter = TableauExporter()
    tableau_exporter.export_all()
    tableau_exporter.close()

    powerbi_exporter = PowerBIExporter()
    powerbi_exporter.export_all()
    powerbi_exporter.close()

    # 完成
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)
    print("\n输出文件位置:")
    print("  - 分析报告: data/processed/analysis_report.md")
    print("  - 可视化图表: visualization/output/")
    print("  - Excel 数据: data/excel/")
    print("  - Tableau 数据: data/tableau/")
    print("  - Power BI 数据: data/tableau/powerbi/")


if __name__ == "__main__":
    main()
