"""
懂车帝销量数据采集器（最终版）
直接通过browser-harness抓取页面数据
"""
import json
import csv
import time
import subprocess
import re
from pathlib import Path


def run_browser_harness(script):
    """运行 browser-harness 脚本"""
    try:
        result = subprocess.run(
            ["browser-harness", "-c", script],
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8"
        )
        return result.stdout
    except Exception as e:
        print(f"  [!] 错误: {e}")
        return None


def fetch_sales_page(year, month):
    """获取销量页面内容"""
    print(f"\n[*] 获取 {year}年{month}月 销量数据...")

    script = f'''
new_tab("https://www.dongchedi.com/sales?year={year}&month={month}")
wait_for_load()
time.sleep(3)

# 滚动加载更多数据
for i in range(20):
    js("window.scrollBy(0, 800)")
    time.sleep(0.3)

content = js("document.body.innerText")
print(content)
'''

    return run_browser_harness(script)


def parse_sales_data(text, year, month):
    """
    解析销量数据
    格式示例:
    1
    星愿吉利银河/小型车
    5.98-9.18万
    32,306
    """
    if not text:
        return []

    results = []
    lines = text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 匹配排名（1-100的数字）
        if line.isdigit() and 1 <= int(line) <= 100:
            rank = int(line)

            # 向后查找5行内的信息
            model_info = ""
            price_min = 0
            price_max = 0
            sales = 0

            # 查找车型名称（下一行应该是车型）
            if i + 1 < len(lines):
                model_line = lines[i + 1].strip()
                if "/" in model_line and len(model_line) < 50:
                    model_info = model_line

            # 查找价格和销量
            for j in range(i + 2, min(i + 8, len(lines))):
                next_line = lines[j].strip()

                # 匹配价格（格式：X.XX-XX.XX万）
                price_match = re.match(r'(\d+\.?\d*)-(\d+\.?\d*)万', next_line)
                if price_match:
                    price_min = float(price_match.group(1))
                    price_max = float(price_match.group(2))

                # 匹配销量（带逗号的数字，如32,306）
                sales_match = re.match(r'^([\d,]+)$', next_line)
                if sales_match:
                    sales_str = sales_match.group(1).replace(",", "")
                    if sales_str.isdigit() and 1000 <= int(sales_str) <= 999999:
                        sales = int(sales_str)
                        break

            # 解析车型名称
            if model_info and sales > 0:
                # 格式：车型名品牌/类型，如"星愿吉利银河/小型车"
                parts = model_info.split("/")
                if len(parts) >= 2:
                    # 提取车型名和品牌
                    name_brand = parts[0].strip()
                    body_type = parts[1].strip()

                    # 尝试分离车型名和品牌
                    # 常见品牌列表
                    brands = [
                        "吉利银河", "吉利汽车", "零跑汽车", "特斯拉中国", "小米汽车",
                        "比亚迪", "长安启源", "理想汽车", "一汽丰田", "上汽大众",
                        "广汽丰田", "一汽-大众", "广汽埃安新能源", "方程豹", "上汽集团",
                        "上汽通用五菱", "问界", "蔚来", "小鹏", "极氪", "哪吒",
                        "长城汽车", "长安汽车", "奇瑞汽车", "北京现代", "东风日产",
                        "华晨宝马", "北京奔驰", "一汽奥迪", "沃尔沃亚太", "东风本田"
                    ]

                    model_name = name_brand
                    brand = ""

                    for b in brands:
                        if name_brand.endswith(b):
                            model_name = name_brand[:-len(b)]
                            brand = b
                            break

                    results.append({
                        "year": year,
                        "month": month,
                        "rank": rank,
                        "model": model_name,
                        "brand": brand,
                        "body_type": body_type,
                        "price_min": price_min,
                        "price_max": price_max,
                        "sales": sales
                    })

        i += 1

    return results


def save_csv(data, filename):
    """保存为CSV"""
    if not data:
        return None

    filepath = Path("data/raw/dongchedi") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["year", "month", "rank", "model", "brand", "body_type",
                 "price_min", "price_max", "sales"]
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

    print(f"  [OK] 保存: {filepath} ({len(data)} 条)")
    return filepath


def main():
    """主函数"""
    print("=" * 60)
    print("懂车帝销量数据采集器")
    print("=" * 60)

    all_data = []

    # 采集2026年7月数据（测试）
    print("\n[测试] 采集2026年7月数据...")
    content = fetch_sales_page(2026, 7)
    if content:
        data = parse_sales_data(content, 2026, 7)
        if data:
            print(f"  [OK] 解析到 {len(data)} 条数据")
            print("\n  前5条数据:")
            for item in data[:5]:
                print(f"    排名{item['rank']}: {item['model']} ({item['brand']}) - {item['sales']}辆")
            all_data.extend(data)
            save_csv(data, "sales_2026_07.csv")
        else:
            print("  [!] 未解析到数据")

    # 采集更多月份
    print("\n" + "=" * 60)
    print("采集完整数据")
    print("=" * 60)

    # 定义要采集的月份
    months_to_fetch = [
        (2024, [1, 3, 6, 9, 12]),
        (2025, [1, 3, 6, 9, 12]),
        (2026, [1, 3, 5, 7])
    ]

    for year, months in months_to_fetch:
        print(f"\n[采集] {year}年数据")
        for month in months:
            content = fetch_sales_page(year, month)
            if content:
                data = parse_sales_data(content, year, month)
                all_data.extend(data)
                save_csv(data, f"sales_{year}_{month:02d}.csv")
            time.sleep(2)

    # 保存汇总
    if all_data:
        save_csv(all_data, "all_sales_data.csv")

    print("\n" + "=" * 60)
    print(f"采集完成！共获取 {len(all_data)} 条数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
