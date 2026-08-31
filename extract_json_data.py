"""
懂车帝数据采集 - 从HTML中提取JSON数据
"""
import requests
import re
import json
import csv
import time
from pathlib import Path


# Cookie配置
COOKIE = 'session_tlb_tag=sttt%7C13%7CicnhGtqsaE_ouavWV0_M2v_________rp7n_VsHvU84rJzu-ycCJEQ3deI1fiZjIfwKvbpMmgC8%3D; sessionid=89c9e11adaac684fe8b9abd6574fccda; sessionid_ss=89c9e11adaac684fe8b9abd6574fccda; sid_guard=89c9e11adaac684fe8b9abd6574fccda%7C1788149539%7C5184002%7CFri%2C+30-Oct-2026+04%3A12%3A21+GMT; sid_tt=89c9e11adaac684fe8b9abd6574fccda; sid_ucp_v1=1.0.0-KGE1NzJjNzg0ZTQ3ODA2OTRlMTY3ZmY3ZTliY2M1NWIyMWIyYmEzMWYKFwik1fTa-AIQo_7T1AYYrw4gDDgCQPEHGgJscSIgODljOWUxMWFkYWFjNjg0ZmU4YjlhYmQ2NTc0ZmNjZGE; ssid_ucp_v1=1.0.0-KGE1NzJjNzg0ZTQ3ODA2OTRlMTY3ZmY3ZTliY2M1NWIyMWIyYmEzMWYKFwik1fTa-AIQo_7T1AYYrw4gDDgCQPEHGgJscSIgODljOWUxMWFkYWFjNjg0ZmU4YjlhYmQ2NTc0ZmNjZGE; tt_web_version=new; tt_webid=7680043508783646233; ttwid=1%7ClRU4UZmLJA-TCXhiJba4_1Cr9xq34Qo-7PXL4U4zfpk%7C1788149510%7C9611342040e94077354043ceed764e4bac851f010dbecda53cb7cf87cc25ac0d; uid_tt=5bc91f40fb9407f0f57d97950b4c1547; uid_tt_ss=5bc91f40fb9407f0f57d97950b4c1547; user_data=%7B%22gender%22%3A1%2C%22name%22%3A%22%E5%A4%95%E5%8E%BB%E4%B9%9D%E5%B7%9E%22%2C%22screen_name%22%3A%22%E5%A4%95%E5%8E%BB%E4%B9%9D%E5%B7%9E%22%2C%22user_id%22%3A101122386596%2C%22avatar_url%22%3A%22https%3A%2F%2Fp3-passport.byteacctimg.com%2Fimg%2Fmosaic-legacy%2F2f79d00013e8967625a7f~120x256.image%22%2C%22mobile%22%3A%22182******96%22%7D; x-web-secsdk-uid=4a7c7165-2108-4f31-afe6-35e93a3145c8'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie': COOKIE,
    'Referer': 'https://www.dongchedi.com/',
}


def fetch_page(url):
    """获取页面"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        return resp.text if resp.status_code == 200 else None
    except Exception as e:
        print(f"  [!] 请求失败: {e}")
        return None


def extract_json_from_html(html):
    """从HTML中提取JSON数据"""
    # 查找__NEXT_DATA__中的JSON
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if match:
        try:
            json_str = match.group(1)
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # 查找其他JSON数据
    match = re.search(r'"rank_list":\s*(\[.*?\])', html, re.DOTALL)
    if match:
        try:
            return json.loads('{"rank_list":' + match.group(1) + '}')
        except json.JSONDecodeError:
            pass

    return None


def parse_sales_from_json(data, year, month):
    """从JSON中解析销量数据"""
    results = []

    # 尝试不同的JSON结构
    rank_list = None

    if isinstance(data, dict):
        # 查找rank_list
        if 'rank_list' in data:
            rank_list = data['rank_list']
        elif 'props' in data and 'pageProps' in data['props']:
            page_props = data['props']['pageProps']
            if 'rankList' in page_props:
                rank_list = page_props['rankList']
            elif 'rank_list' in page_props:
                rank_list = page_props['rank_list']

    if not rank_list:
        return results

    for i, item in enumerate(rank_list, 1):
        if isinstance(item, dict):
            series_info = item.get('series_info', item)
            series_name = series_info.get('series_name', '')
            brand_name = series_info.get('brand_name', '')
            vehicle_type = series_info.get('vehicle_type', '')
            count = item.get('count', 0)
            min_price = series_info.get('min_price', 0)
            max_price = series_info.get('max_price', 0)

            # 价格转换（分 -> 万）
            if min_price > 1000:
                min_price = min_price / 10000
            if max_price > 1000:
                max_price = max_price / 10000

            if series_name and count > 0:
                results.append({
                    'year': year,
                    'month': month,
                    'rank': i,
                    'model': series_name,
                    'brand': brand_name,
                    'body_type': vehicle_type,
                    'price_min': min_price,
                    'price_max': max_price,
                    'sales': count
                })

    return results


def save_csv(data, filename):
    """保存CSV"""
    if not data:
        return

    filepath = Path('data/raw/dongchedi') / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['year', 'month', 'rank', 'model', 'brand',
                                               'body_type', 'price_min', 'price_max', 'sales'])
        writer.writeheader()
        writer.writerows(data)

    print(f'  [OK] 保存: {filepath} ({len(data)} 条)')


def main():
    print('='*60)
    print('懂车帝数据采集（JSON提取版）')
    print('='*60)

    all_data = []

    # 测试2026年7月
    print('\n[测试] 2026年7月')
    url = 'https://www.dongchedi.com/sales/sale-x-202607-x-x-x-x'
    html = fetch_page(url)

    if html:
        print(f'  获取到 {len(html)} 字符')

        # 保存HTML用于调试
        with open('debug_html.html', 'w', encoding='utf-8') as f:
            f.write(html)

        # 提取JSON
        json_data = extract_json_from_html(html)
        if json_data:
            print('  [OK] 提取到JSON数据')

            # 解析数据
            data = parse_sales_from_json(json_data, 2026, 7)
            if data:
                print(f'  [OK] 解析到 {len(data)} 条数据')
                for item in data[:5]:
                    print(f'    排名{item["rank"]}: {item["model"]} ({item["brand"]}) - {item["sales"]:,}辆')
                all_data.extend(data)
                save_csv(data, 'sales_2026_07.csv')
            else:
                print('  [!] 未解析到数据')
        else:
            print('  [!] 未提取到JSON')

    # 采集更多月份
    print('\n' + '='*60)
    print('采集完整数据')
    print('='*60)

    months_to_collect = [
        (2026, [1, 2, 3, 4, 5, 6, 7]),
    ]

    for year, months in months_to_collect:
        print(f'\n[采集] {year}年')
        for month in months:
            if year == 2026 and month == 7:
                continue  # 已经测试过

            url = f'https://www.dongchedi.com/sales/sale-x-{year}{month:02d}-x-x-x-x'
            print(f'\n  {year}年{month}月: {url}')

            html = fetch_page(url)
            if html:
                json_data = extract_json_from_html(html)
                if json_data:
                    data = parse_sales_from_json(json_data, year, month)
                    if data:
                        print(f'    解析到 {len(data)} 条')
                        all_data.extend(data)
                        save_csv(data, f'sales_{year}_{month:02d}.csv')
                    else:
                        print('    未解析到数据')
                else:
                    print('    未提取到JSON')
            time.sleep(2)

    # 保存汇总
    if all_data:
        save_csv(all_data, 'all_sales_data.csv')

    print('\n' + '='*60)
    print(f'完成！共获取 {len(all_data)} 条数据')
    print('='*60)


if __name__ == '__main__':
    main()
