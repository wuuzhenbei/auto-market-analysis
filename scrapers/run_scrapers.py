"""
运行所有采集器
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.dongchedi_scraper import DongchediScraper
from scrapers.autohome_scraper import AutohomeScraper


def run_all_scrapers():
    """运行所有采集器"""
    print("=" * 60)
    print("汽车市场数据采集")
    print("=" * 60)

    scrapers = [
        DongchediScraper(),
        AutohomeScraper(),
    ]

    all_results = {}

    for scraper in scrapers:
        try:
            results = scraper.run()
            all_results[scraper.name] = results
        except Exception as e:
            print(f"\n[[FAIL]] {scraper.name} 采集失败: {e}")
            all_results[scraper.name] = []

    # 汇总结果
    print("\n" + "=" * 60)
    print("采集结果汇总")
    print("=" * 60)

    total_count = 0
    for source, results in all_results.items():
        count = len(results)
        total_count += count
        print(f"  {source}: {count} 条数据")

    print(f"\n  总计: {total_count} 条数据")

    return all_results


if __name__ == "__main__":
    run_all_scrapers()
