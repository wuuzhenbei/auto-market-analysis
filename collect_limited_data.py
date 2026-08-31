"""
懂车帝数据采集 - 有限数据版
每次获取前10条数据
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


def extract_sales_data(html, year, month):
    """从HTML中提取销量数据"""
    results = []

    # 提取__NEXT_DATA__
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not match:
        return results

    try:
        data = json.loads(match.group(1))
        rank_data = data['props']['pageProps']['rankData']
        sales_list = rank_data.get('list', [])

        for item in sales_list:
            series_name = item.get('series_name', '')
            count = item.get('count', 0)
            min_price = item.get('min_price', 0)
            max_price = item.get('max_price', 0)
            rank = item.get('rank', 0)

            # 从series_name中提取品牌
            brands = [
                '吉利银河', '吉利汽车', '零跑汽车', '特斯拉中国', '小米汽车',
                '比亚迪', '长安启源', '理想汽车', '一汽丰田', '上汽大众',
                '广汽丰田', '一汽-大众', '广汽埃安新能源', '方程豹', '上汽集团',
                '上汽通用五菱', '问界汽车', '蔚来汽车', '小鹏汽车', '极氪汽车',
                '哪吒汽车', '长城汽车', '长安汽车', '奇瑞汽车', '北京现代',
                '东风日产', '华晨宝马', '北京奔驰', '一汽奥迪', '沃尔沃亚太',
                '东风本田', '广汽本田', '一汽大众', '上汽乘用车', '吉利沃尔沃'
            ]

            model_name = series_name
            brand = ''
            for b in brands:
                if series_name.endswith(b):
                    model_name = series_name[:-len(b)]
                    brand = b
                    break

            if series_name and count > 0:
                results.append({
                    'year': year,
                    'month': month,
                    'rank': rank,
                    'model': model_name,
                    'brand': brand,
                    'body_type': '',
                    'price_min': min_price,
                    'price_max': max_price,
                    'sales': count
                })
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [!] 解析失败: {e}")

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
    print('懂车帝数据采集（有限数据版）')
    print('='*60)
    print('\n注意：每次只获取前10条数据（懂车帝限制）')

    all_data = []

    # 采集2026年数据
    print('\n' + '='*60)
    print('采集2026年数据')
    print('='*60)

    for month in [1, 2, 3, 4, 5, 6, 7]:
        url = f'https://www.dongchedi.com/sales/sale-x-2026{month:02d}-x-x-x-x'
        print(f'\n  2026年{month}月: {url}')

        html = fetch_page(url)
        if html:
            data = extract_sales_data(html, 2026, month)
            if data:
                print(f'    获取到 {len(data)} 条数据')
                for item in data[:3]:
                    print(f'      排名{item["rank"]}: {item["model"]} - {item["sales"]:,}辆')
                all_data.extend(data)
                save_csv(data, f'sales_2026_{month:02d}.csv')
            else:
                print('    未获取到数据')
        time.sleep(2)

    # 保存汇总
    if all_data:
        save_csv(all_data, 'all_sales_data.csv')

    print('\n' + '='*60)
    print(f'完成！共获取 {len(all_data)} 条数据')
    print('='*60)
    print('\n提示：如需获取更多数据，请在Edge浏览器中手动复制')


if __name__ == '__main__':
    main()
