"""
绕过懂车帝反爬虫的采集脚本
使用从Edge获取的cookie
"""
import requests
import json
import csv
import re
import time
from pathlib import Path


def fetch_with_cookie(url, cookie_string):
    """使用cookie访问页面"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': cookie_string,
        'Referer': 'https://www.dongchedi.com/',
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        return resp.text
    except Exception as e:
        print(f"  [!] 请求失败: {e}")
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

        if line.isdigit() and 1 <= int(line) <= 100:
            rank = int(line)

            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            if j < len(lines):
                model_line = lines[j].strip()
                if "/" in model_line and len(model_line) < 50:
                    parts = model_line.split("/")
                    name_brand = parts[0].strip()
                    body_type = parts[1].strip() if len(parts) > 1 else ""

                    k = j + 1
                    price_min = 0
                    price_max = 0
                    sales = 0

                    while k < len(lines) and k < j + 10:
                        next_line = lines[k].strip()

                        price_match = re.match(r'(\d+\.?\d*)-(\d+\.?\d*)万', next_line)
                        if price_match:
                            price_min = float(price_match.group(1))
                            price_max = float(price_match.group(2))

                        sales_match = re.match(r'^([\d,]+)$', next_line)
                        if sales_match:
                            sales_str = sales_match.group(1).replace(",", "")
                            if sales_str.isdigit() and 1000 <= int(sales_str) <= 999999:
                                sales = int(sales_str)
                                break
                        k += 1

                    if sales > 0:
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
    print("="*60)
    print("懂车帝数据采集（绕过反爬版）")
    print("="*60)
    print("\n请从Edge浏览器获取cookie：")
    print("1. 在Edge中打开 https://www.dongchedi.com/sales")
    print("2. 按F12打开开发者工具")
    print("3. 切换到'Application'标签")
    print("4. 左侧点击'Cookies' -> 'https://www.dongchedi.com'")
    print("5. 复制所有cookie值\n")

    cookie = input("请粘贴cookie: ").strip()
    if not cookie:
        print("[!] 未提供cookie，程序退出")
        return

    print("\n" + "="*60)
    print("开始采集数据")
    print("="*60)

    all_data = []

    # 测试URL格式
    # 根据用户提供的信息
    urls_to_test = [
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-x-x", 2026, 7, "2026年7月全部"),
        ("https://www.dongchedi.com/sales/sale-x-202606-x-x-x-x", 2026, 6, "2026年6月全部"),
        ("https://www.dongchedi.com/sales/sale-x-500-x-x-x-x", None, None, "近半年"),
        ("https://www.dongchedi.com/sales/sale-x-1000-x-x-x-x", None, None, "近一年"),
    ]

    for url, year, month, desc in urls_to_test:
        print(f"\n[测试] {desc}: {url}")
        content = fetch_with_cookie(url, cookie)
        if content:
            print(f"  获取到 {len(content)} 字符")
            if "验证码" in content:
                print("  [!] 触发验证码，cookie可能已失效")
                break
            elif "暂无车系" in content:
                print("  [!] 显示'暂无车系'")
            else:
                if year and month:
                    data = parse_sales_data(content, year, month)
                    if data:
                        print(f"  [OK] 解析到 {len(data)} 条数据")
                        for item in data[:3]:
                            print(f"    排名{item['rank']}: {item['model']} - {item['sales']:,}辆")
                        all_data.extend(data)
                        save_csv(data, f"sales_{year}_{month:02d}.csv")
                else:
                    print("  [i] 需要手动确认年份和月份")
        time.sleep(2)

    if all_data:
        save_csv(all_data, "all_sales_data.csv")
        print(f"\n采集完成！共获取 {len(all_data)} 条数据")


if __name__ == "__main__":
    main()
