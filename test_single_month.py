"""测试单个月份的数据采集"""
import re
import subprocess
import csv
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
    script = f'''
new_tab("https://www.dongchedi.com/sales?year={year}&month={month}")
wait_for_load()
time.sleep(3)

# 滚动加载更多数据
for i in range(15):
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

        # 匹配排名
        if line.isdigit() and 1 <= int(line) <= 100:
            rank = int(line)
            model_info = ""
            price_min = 0
            price_max = 0
            sales = 0

            # 查找车型名称
            if i + 1 < len(lines):
                model_line = lines[i + 1].strip()
                if "/" in model_line and len(model_line) < 50:
                    model_info = model_line

            # 查找价格和销量
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

            # 解析车型名称
            if model_info and sales > 0:
                parts = model_info.split("/")
                if len(parts) >= 2:
                    name_brand = parts[0].strip()
                    body_type = parts[1].strip()

                    # 常见品牌列表
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
    print("=" * 60)
    print("测试单个月份数据采集")
    print("=" * 60)

    year = 2026
    month = 7

    print(f"\n[*] 获取 {year}年{month}月 销量数据...")
    content = fetch_sales_page(year, month)

    if content:
        print(f"  [OK] 获取到 {len(content)} 字符")

        # 保存原始内容用于调试
        with open("debug_raw.txt", "w", encoding="utf-8") as f:
            f.write(content)

        data = parse_sales_data(content, year, month)
        if data:
            print(f"\n  [OK] 解析到 {len(data)} 条数据")
            print("\n  前10条数据:")
            for item in data[:10]:
                print(f"    排名{item['rank']:2d}: {item['model']:<10s} ({item['brand']:<8s}) {item['body_type']:<8s} {item['sales']:>8,}辆")

            save_csv(data, f"sales_{year}_{month:02d}.csv")
        else:
            print("  [!] 未解析到数据，请检查 debug_raw.txt")
    else:
        print("  [!] 获取数据失败")


if __name__ == "__main__":
    main()
