"""
懂车帝数据采集器（最终版）
使用Edge的cookie绕过反爬虫
"""
import requests
import re
import csv
import time
from pathlib import Path
from urllib.parse import unquote


# Edge的cookie（需要定期更新）
COOKIE = 'session_tlb_tag=sttt%7C13%7CicnhGtqsaE_ouavWV0_M2v_________rp7n_VsHvU84rJzu-ycCJEQ3deI1fiZjIfwKvbpMmgC8%3D; sessionid=89c9e11adaac684fe8b9abd6574fccda; sessionid_ss=89c9e11adaac684fe8b9abd6574fccda; sid_guard=89c9e11adaac684fe8b9abd6574fccda%7C1788149539%7C5184002%7CFri%2C+30-Oct-2026+04%3A12%3A21+GMT; sid_tt=89c9e11adaac684fe8b9abd6574fccda; sid_ucp_v1=1.0.0-KGE1NzJjNzg0ZTQ3ODA2OTRlMTY3ZmY3ZTliY2M1NWIyMWIyYmEzMWYKFwik1fTa-AIQo_7T1AYYrw4gDDgCQPEHGgJscSIgODljOWUxMWFkYWFjNjg0ZmU4YjlhYmQ2NTc0ZmNjZGE; ssid_ucp_v1=1.0.0-KGE1NzJjNzg0ZTQ3ODA2OTRlMTY3ZmY3ZTliY2M1NWIyMWIyYmEzMWYKFwik1fTa-AIQo_7T1AYYrw4gDDgCQPEHGgJscSIgODljOWUxMWFkYWFjNjg0ZmU4YjlhYmQ2NTc0ZmNjZGE; tt_web_version=new; tt_webid=7680043508783646233; ttwid=1%7ClRU4UZmLJA-TCXhiJba4_1Cr9xq34Qo-7PXL4U4zfpk%7C1788149510%7C9611342040e94077354043ceed764e4bac851f010dbecda53cb7cf87cc25ac0d; uid_tt=5bc91f40fb9407f0f57d97950b4c1547; uid_tt_ss=5bc91f40fb9407f0f57d97950b4c1547; user_data=%7B%22gender%22%3A1%2C%22name%22%3A%22%E5%A4%95%E5%8E%BB%E4%B9%9D%E5%B7%9E%22%2C%22screen_name%22%3A%22%E5%A4%95%E5%8E%BB%E4%B9%9D%E5%B7%9E%22%2C%22user_id%22%3A101122386596%2C%22avatar_url%22%3A%22https%3A%2F%2Fp3-passport.byteacctimg.com%2Fimg%2Fmosaic-legacy%2F2f79d00013e8967625a7f~120x256.image%22%2C%22mobile%22%3A%22182******96%22%7D; x-web-secsdk-uid=4a7c7165-2108-4f31-afe6-35e93a3145c8'


def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': COOKIE,
        'Referer': 'https://www.dongchedi.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }


def fetch_page(url):
    """获取页面内容"""
    try:
        resp = requests.get(url, headers=get_headers(), timeout=15)
        resp.encoding = 'utf-8'
        return resp.text
    except Exception as e:
        print(f"  [!] 请求失败: {e}")
        return None


def extract_text_from_html(html):
    """从HTML中提取纯文本"""
    # 移除script和style标签
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '\n', html)
    # 解码HTML实体
    text = unquote(text)
    # 清理空白
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def parse_sales_data(text, year, month):
    """解析销量数据"""
    results = []
    lines = text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 匹配排名
        if line.isdigit() and 1 <= int(line) <= 100:
            rank = int(line)

            # 向后查找车型信息
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


def fetch_sales_data(year, month):
    """获取指定月份的销量数据"""
    print(f"\n[*] 获取 {year}年{month}月 销量数据...")

    # 使用URL格式: /sales/sale-x-YYYYMM-x-x-x-x
    url = f"https://www.dongchedi.com/sales/sale-x-{year}{month:02d}-x-x-x-x"
    print(f"  URL: {url}")

    html = fetch_page(url)
    if not html:
        return []

    # 检查是否需要登录
    if 'login-required' in html:
        print("  [!] 需要登录，cookie可能已失效")
        return []

    # 检查是否有验证码
    if '验证码' in html:
        print("  [!] 触发验证码")
        return []

    # 提取文本
    text = extract_text_from_html(html)

    # 检查是否有数据
    if '暂无车系' in text:
        print("  [!] 暂无车系")
        return []

    # 解析数据
    data = parse_sales_data(text, year, month)
    if data:
        print(f"  [OK] 解析到 {len(data)} 条数据")
        for item in data[:3]:
            print(f"    排名{item['rank']}: {item['model']} - {item['sales']:,}辆")
    else:
        print("  [!] 未解析到数据")

    return data


def main():
    print("="*60)
    print("懂车帝数据采集器（最终版）")
    print("="*60)

    all_data = []

    # 采集2026年数据
    print("\n" + "="*60)
    print("采集2026年数据")
    print("="*60)
    for month in [1, 2, 3, 4, 5, 6, 7]:
        data = fetch_sales_data(2026, month)
        all_data.extend(data)
        if data:
            save_csv(data, f"sales_2026_{month:02d}.csv")
        time.sleep(2)

    # 采集2025年数据
    print("\n" + "="*60)
    print("采集2025年数据")
    print("="*60)
    for month in [1, 3, 6, 9, 12]:
        data = fetch_sales_data(2025, month)
        all_data.extend(data)
        if data:
            save_csv(data, f"sales_2025_{month:02d}.csv")
        time.sleep(2)

    # 采集2024年数据
    print("\n" + "="*60)
    print("采集2024年数据")
    print("="*60)
    for month in [1, 3, 6, 9, 12]:
        data = fetch_sales_data(2024, month)
        all_data.extend(data)
        if data:
            save_csv(data, f"sales_2024_{month:02d}.csv")
        time.sleep(2)

    # 保存汇总
    if all_data:
        save_csv(all_data, "all_sales_data.csv")

    print("\n" + "="*60)
    print(f"采集完成！共获取 {len(all_data)} 条数据")
    print("="*60)


if __name__ == "__main__":
    main()
