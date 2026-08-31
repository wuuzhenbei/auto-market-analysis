"""
懂车帝销量数据采集器（可用版）
"""
import re
import subprocess
import csv
import time
from pathlib import Path


def fetch_sales_page(year, month):
    """获取销量页面"""
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
        return result.stdout
    except Exception as e:
        print(f"  [!] 获取失败: {e}")
        return None


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

            # 向后查找非空行（车型名）
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            if j < len(lines):
                model_line = lines[j].strip()
                if "/" in model_line and len(model_line) < 50:
                    # 解析车型名和类型
                    parts = model_line.split("/")
                    name_brand = parts[0].strip()
                    body_type = parts[1].strip() if len(parts) > 1 else ""

                    # 查找价格和销量
                    k = j + 1
                    price_min = 0
                    price_max = 0
                    sales = 0

                    while k < len(lines) and k < j + 10:
                        next_line = lines[k].strip()

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
                        k += 1

                    if sales > 0:
                        # 分离车型名和品牌
                        brands = [
                            "吉利银河", "吉利汽车", "零跑汽车", "特斯拉中国", "小米汽车",
                            "比亚迪", "长安启源", "理想汽车", "一汽丰田", "上汽大众",
                            "广汽丰田", "一汽-大众", "广汽埃安新能源", "方程豹", "上汽集团",
                            "上汽通用五菱", "问界汽车", "蔚来汽车", "小鹏汽车", "极氪汽车",
                            "哪吒汽车", "长城汽车", "长安汽车", "奇瑞汽车", "北京现代",
                            "东风日产", "华晨宝马", "北京奔驰", "一汽奥迪", "沃尔沃亚太",
                            "东风本田", "广汽本田", "一汽大众", "上汽乘用车", "吉利沃尔沃"
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
    print("懂车帝销量数据采集器")
    print("=" * 60)

    all_data = []

    # 定义采集任务
    tasks = [
        # (2024, [1, 3, 6, 9, 12]),
        # (2025, [1, 3, 6, 9, 12]),
        (2026, [1, 3, 5, 7])  # 先测试2026年
    ]

    for year, months in tasks:
        print(f"\n[采集] {year}年数据")
        for month in months:
            print(f"\n  {year}年{month}月:")
            content = fetch_sales_page(year, month)
            if content:
                data = parse_sales_data(content, year, month)
                if data:
                    print(f"    解析到 {len(data)} 条数据")
                    for item in data[:3]:
                        print(f"      排名{item['rank']}: {item['model']} - {item['sales']:,}辆")
                    all_data.extend(data)
                    save_csv(data, f"sales_{year}_{month:02d}.csv")
                else:
                    print("    未解析到数据")
            time.sleep(2)

    # 保存汇总
    if all_data:
        save_csv(all_data, "all_sales_data.csv")

    print("\n" + "=" * 60)
    print(f"采集完成！共获取 {len(all_data)} 条数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
