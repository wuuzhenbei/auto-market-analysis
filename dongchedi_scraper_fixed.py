"""
懂车帝销量数据采集器（修复版）
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
    """解析销量数据"""
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
            model = ""
            brand = ""
            body_type = ""
            price_min = 0
            price_max = 0
            sales = 0

            # 向后查找车型信息
            j = i + 1
            while j < min(i + 10, len(lines)):
                next_line = lines[j].strip()

                # 匹配车型名称（格式：品牌/类型）
                if "/" in next_line and len(next_line) < 40:
                    parts = next_line.split("/")
                    if len(parts) >= 2:
                        model = parts[0].strip()
                        type_part = parts[1].strip()
                        # 提取品牌（如果有厂商信息）
                        if "厂商" not in type_part and "汽车" not in type_part:
                            body_type = type_part

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

                j += 1

            # 只保存有效数据
            if model and sales > 0:
                results.append({
                    "year": year,
                    "month": month,
                    "rank": rank,
                    "model": model,
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

    fieldnames = ["year", "month", "rank", "model", "body_type",
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
            print(f"  前3条: {[d['model'] for d in data[:3]]}")
            all_data.extend(data)
            save_csv(data, "sales_2026_07.csv")
        else:
            print("  [!] 未解析到数据")
            # 保存原始内容用于调试
            with open("debug_sales_page.txt", "w", encoding="utf-8") as f:
                f.write(content)
            print("  [i] 原始内容已保存到 debug_sales_page.txt")

    # 采集更多月份
    print("\n" + "=" * 60)
    print("采集完整数据")
    print("=" * 60)

    # 2024年
    print("\n[采集] 2024年数据")
    for month in [1, 3, 6, 9, 12]:
        content = fetch_sales_page(2024, month)
        if content:
            data = parse_sales_data(content, 2024, month)
            all_data.extend(data)
            save_csv(data, f"sales_2024_{month:02d}.csv")
        time.sleep(2)

    # 2025年
    print("\n[采集] 2025年数据")
    for month in [1, 3, 6, 9, 12]:
        content = fetch_sales_page(2025, month)
        if content:
            data = parse_sales_data(content, 2025, month)
            all_data.extend(data)
            save_csv(data, f"sales_2025_{month:02d}.csv")
        time.sleep(2)

    # 2026年
    print("\n[采集] 2026年数据")
    for month in [1, 3, 5, 7]:
        content = fetch_sales_page(2026, month)
        if content:
            data = parse_sales_data(content, 2026, month)
            all_data.extend(data)
            save_csv(data, f"sales_2026_{month:02d}.csv")
        time.sleep(2)

    # 保存汇总
    if all_data:
        save_csv(all_data, "all_sales_data.csv")

    print("\n" + "=" * 60)
    print(f"采集完成！共获取 {len(all_data)} 条数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
