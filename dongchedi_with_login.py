"""
懂车帝数据采集器（需要登录）
先手动登录获取cookie，再采集数据
"""
import json
import csv
import time
import subprocess
from pathlib import Path


COOKIE_FILE = Path("data/dongchedi_cookie.txt")


def run_browser_harness(script):
    """运行 browser-harness 脚本"""
    try:
        result = subprocess.run(
            ["browser-harness", "-c", script],
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8"
        )
        return result.stdout
    except Exception as e:
        print(f"  [!] 错误: {e}")
        return None


def save_cookie(cookie_string):
    """保存cookie到文件"""
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookie_string)
    print(f"  [OK] Cookie已保存到: {COOKIE_FILE}")


def load_cookie():
    """加载已保存的cookie"""
    if COOKIE_FILE.exists():
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def login_and_get_cookie():
    """打开浏览器让用户登录，然后获取cookie"""
    print("=" * 60)
    print("懂车帝登录")
    print("=" * 60)
    print("\n将打开懂车帝网站，请手动登录")
    print("登录方式：手机号/微信/抖音等\n")

    # 打开懂车帝
    script = '''
new_tab("https://www.dongchedi.com")
wait_for_load()
time.sleep(2)
print("READY")
'''
    result = run_browser_harness(script)
    if not result or "READY" not in result:
        print("[!] 无法打开网站")
        return None

    print("请在浏览器中登录懂车帝账号...")
    input("\n登录完成后，按回车键继续...")

    # 获取cookie
    print("\n[*] 正在获取cookie...")
    script = '''
cookies = document.cookie
print(cookies)
'''
    result = run_browser_harness(script)
    if result:
        cookie = result.strip()
        if cookie:
            save_cookie(cookie)
            return cookie

    print("[!] 获取cookie失败")
    return None


def fetch_sales_page(url, cookie):
    """使用cookie获取销量页面"""
    script = f'''
// 设置cookie
document.cookie = "{cookie}"

// 访问页面
new_tab("{url}")
wait_for_load()
time.sleep(5)

// 滚动加载
for (var i = 0; i < 20; i++) {{
    window.scrollBy(0, 800)
    await new Promise(r => setTimeout(r, 300))
}}

content = document.body.innerText
print(content)
'''
    return run_browser_harness(script)


def parse_sales_data(text, year, month):
    """解析销量数据"""
    if not text:
        return []

    import re
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
    print("懂车帝数据采集器（登录版）")
    print("=" * 60)

    # 检查是否有保存的cookie
    cookie = load_cookie()
    if cookie:
        print(f"\n[*] 找到已保存的cookie")
        use_saved = input("是否使用已保存的cookie？(y/n): ").strip().lower()
        if use_saved != 'y':
            cookie = None

    # 如果没有cookie，进行登录
    if not cookie:
        cookie = login_and_get_cookie()
        if not cookie:
            print("\n[!] 登录失败，程序退出")
            return

    print("\n" + "=" * 60)
    print("开始采集数据")
    print("=" * 60)

    # 测试URL格式
    # 根据用户提供的信息：
    # https://www.dongchedi.com/sales/sale-x-202607-x-x-x-x
    # 第1个x: 车型类型（轿车/SUV/MPV/新能源/全部）
    # 第2个x: 时间（202607=2026年7月，500=近半年，1000=近一年）
    # 第3个x: 零售量/批发量
    # 第4个x: 价格
    # 第5个x: 合资/自主/进口
    # 最后的数字: 品牌ID（483=问界，2=奥迪）

    # 先测试一个URL
    test_url = "https://www.dongchedi.com/sales/sale-x-202607-x-x-x-x"
    print(f"\n[测试] {test_url}")
    content = fetch_sales_page(test_url, cookie)
    if content:
        print(f"  获取到 {len(content)} 字符")
        if "暂无车系" in content:
            print("  [!] 显示'暂无车系'，可能需要其他URL格式")
        elif "验证码" in content:
            print("  [!] 触发验证码，cookie可能已失效")
        else:
            data = parse_sales_data(content, 2026, 7)
            if data:
                print(f"  [OK] 解析到 {len(data)} 条数据")
                for item in data[:3]:
                    print(f"    排名{item['rank']}: {item['model']} - {item['sales']:,}辆")
            else:
                print("  [!] 未解析到数据")
    else:
        print("  [!] 获取失败")


if __name__ == "__main__":
    main()
