"""
测试数据分析功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.init_db import init_database
from analysis.brand_analysis import BrandAnalyzer
from analysis.price_analysis import PriceAnalyzer
from analysis.energy_analysis import EnergyAnalyzer


def test_brand_analysis():
    """测试品牌分析"""
    print("测试品牌分析...")
    analyzer = BrandAnalyzer()
    results = analyzer.analyze()
    analyzer.close()

    assert "brand_sales_ranking" in results
    assert len(results["brand_sales_ranking"]) > 0
    print("[[OK]] 品牌分析测试通过")


def test_price_analysis():
    """测试价格分析"""
    print("\n测试价格分析...")
    analyzer = PriceAnalyzer()
    results = analyzer.analyze()
    analyzer.close()

    assert "price_distribution" in results
    assert len(results["price_distribution"]) > 0
    print("[[OK]] 价格分析测试通过")


def test_energy_analysis():
    """测试新能源分析"""
    print("\n测试新能源分析...")
    analyzer = EnergyAnalyzer()
    results = analyzer.analyze()
    analyzer.close()

    assert "energy_type_sales" in results
    assert len(results["energy_type_sales"]) > 0
    print("[[OK]] 新能源分析测试通过")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("运行测试")
    print("=" * 60)

    # 初始化数据库
    print("\n初始化数据库...")
    init_database()

    # 运行测试
    test_brand_analysis()
    test_price_analysis()
    test_energy_analysis()

    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    main()
