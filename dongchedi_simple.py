"""
懂车帝销量数据采集器（简化版）
"""
import re
import subprocess
import csv
import time
from pathlib import Path


def fetch_and_parse(year, month):
    """获取并解析数据"""
    print(f"\n[*] 获取 {year}年{month}月 销量数据...")

    script = f'''
new_tab("https://www.dongchedi.com/sales?year={year}&month={month}")
wait_for_load()
time.sleep(3)

for i in range(15):
    js("window.scrollBy(0, 800)")
    time.sleep(0.3)

content = js("document.body.innerText")
print(content)
'''

    try:
        result = subprocess.run(
            ["browser-harness", "-c", script],
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8"
        )
        content = result.stdout
    except Exception as e:
        print(f"  [!] 获取失败: {e}")
        return []

    if not content:
        return []

    # 解析数据
    results = []
    lines = content.split("\n")

    for i in range(len(lines)):
        line = lines[i].strip()

        # 匹配排名
        if line.isdigit() and 1 <= int(line) <= 100:
            rank = int(line)

            # 检查下一行是否是车型
            if i + 1 < len(lines):
                model_line = lines[i + 1].strip()
                if "/" not in model_line or len(model_line) >= 50:
                    continue

                # 解析车型名和类型
                parts = model_line.split("/")
                if len(parts) < 2:
                    continue

                name_brand = parts[0].strip()
                body_type = parts[1].strip()

                # 查找价格和销量
                price_min = 0
                price_max = 0
                sales = 0

                for j in range(i + 2, min(i + 8, len(lines))):
                    next_line = lines[j].strip()

                    # 匹配价格
                    price_match = re.match(r'(\d+\.?\d*)-(\d+\.?\d*)万', next_line)
                    if price_match:
                        price_min = float(price_match.group(1))
                        price_max = float(price_match.group(2))

                    # 匹配销量
                    sales_match = re.match(r'^([\d,]+)$', next_line)
                    if sales_match:
                        sales_str = sales_match.group(1).replace(",", "")
                        if sales_str.isdigit() and 1000 <= int(sales_str) <= 999999:
                            sales = int(sales_str)
                            break

                if sales > 0:
                    # 分离车型名和品牌
                    brands = [
                        "吉利银河", "吉利汽车", "零跑汽车", "特斯拉中国", "小米汽车",
                        "比亚迪", "长安启源", "理想汽车", "一汽丰田", "上汽大众",
                        "广汽丰田", "一汽-大众", "广汽埃安新能源", "方程豹", "上汽集团",
                        "上汽通用五菱"
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

    return results


def save_csv(data, filename):
    """保存为CSV"""
    if not data:
        return

    filepath = Path("data/raw/dongchedi") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["year", "month", "rank", "model", "brand", "body_type",
                 "price_min", "price_max", "sales"]
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

    print(f"  [OK] 保存: {filepath} ({len(data)} 条)")


def main():
    print("=" * 60)
    print("懂车帝销量数据采集器")
    print("=" * 60)

    # 测试单个月份
    print("\n[测试] 2026年7月")
    data = fetch_and_parse(2026, 7)
    if data:
        print(f"  [OK] 解析到 {len(data)} 条数据")
        print("\n  前5条:")
        for item in data[:5]:
            print(f"    排名{item['rank']:2d}: {item['model']:<10s} ({item['brand']}) - {item['sales']:>8,}辆")
        save_csv(data, "sales_2026_07.csv")
    else:
        print("  [!] 未解析到数据")


if __name__ == "__main__":
    main()
