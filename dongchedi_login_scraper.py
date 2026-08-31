"""
懂车帝登录采集器
参考Mineradio项目，使用浏览器登录获取cookie来采集数据
"""
import json
import csv
import time
import os
import sys
from pathlib import Path
from datetime import datetime


def run_browser_harness(script):
    """运行 browser-harness 脚本"""
    import subprocess
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


def login_dongchedi():
    """
    登录懂车帝并获取cookie
    返回保存的cookie文件路径
    """
    print("=" * 60)
    print("懂车帝登录采集器")
    print("=" * 60)
    print("\n提示：将打开浏览器，请手动登录懂车帝账号")
    print("登录成功后，程序会自动获取cookie并保存\n")

    cookie_file = Path("data/dongchedi_cookie.json")
    cookie_file.parent.mkdir(parents=True, exist_ok=True)

    # 打开懂车帝登录页面
    script = '''
new_tab("https://www.dongchedi.com")
wait_for_load()
time.sleep(2)

# 获取页面信息
info = page_info()
print(info)
'''

    print("[1/3] 打开懂车帝网站...")
    result = run_browser_harness(script)
    if not result:
        print("[!] 无法打开网站，请检查browser-harness是否正常")
        return None

    print("\n" + "=" * 60)
    print("请在浏览器中手动登录懂车帝账号")
    print("登录方式：手机号/微信/抖音等")
    print("=" * 60)
    input("\n登录完成后，按回车键继续...")

    # 获取cookie
    print("\n[2/3] 获取登录cookie...")
    script = '''
# 获取所有cookie
cookies = js("document.cookie")
print(cookies)

# 同时尝试通过CDP获取更完整的cookie
try:
    import json
    cdp_result = cdp("Network.getCookies", {"urls": ["https://www.dongchedi.com"]})
    print("CDP_COOKIES:" + json.dumps(cdp_result))
except Exception as e:
    print("CDP_ERROR:" + str(e))
'''

    result = run_browser_harness(script)
    if not result:
        print("[!] 无法获取cookie")
        return None

    # 解析cookie
    cookies = {}
    for line in result.split("\n"):
        line = line.strip()
        if line.startswith("CDP_COOKIES:"):
            try:
                cdp_data = json.loads(line[12:])
                for cookie in cdp_data.get("cookies", []):
                    cookies[cookie["name"]] = cookie["value"]
            except:
                pass
        elif "=" in line and not line.startswith("CDP_ERROR"):
            # 解析document.cookie格式
            for pair in line.split(";"):
                pair = pair.strip()
                if "=" in pair:
                    key, val = pair.split("=", 1)
                    cookies[key.strip()] = val.strip()

    if not cookies:
        print("[!] 未获取到cookie，可能登录未成功")
        return None

    # 保存cookie
    cookie_data = {
        "timestamp": datetime.now().isoformat(),
        "cookies": cookies,
        "cookie_string": "; ".join([f"{k}={v}" for k, v in cookies.items()])
    }

    with open(cookie_file, "w", encoding="utf-8") as f:
        json.dump(cookie_data, f, ensure_ascii=False, indent=2)

    print(f"\n[3/3] Cookie已保存到: {cookie_file}")
    print(f"  获取到 {len(cookies)} 个cookie")

    return cookie_file


def load_cookie():
    """加载已保存的cookie"""
    cookie_file = Path("data/dongchedi_cookie.json")
    if not cookie_file.exists():
        return None

    with open(cookie_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("cookie_string", "")


def fetch_with_cookie(url, cookie_string=None):
    """使用cookie请求页面"""
    if not cookie_string:
        cookie_string = load_cookie()

    if not cookie_string:
        print("[!] 无可用cookie，请先登录")
        return None

    # 使用browser-harness发送带cookie的请求
    script = f'''
# 设置cookie
js("document.cookie = '{cookie_string}'")

# 访问页面
new_tab("{url}")
wait_for_load()
time.sleep(3)

# 滚动加载
for i in range(10):
    js("window.scrollBy(0, 600)")
    time.sleep(0.3)

# 获取内容
content = js("document.body.innerText")
print(content[:20000])
'''

    return run_browser_harness(script)


def fetch_sales_data_with_login(year, month):
    """使用登录状态获取销量数据"""
    print(f"\n[*] 获取 {year}年{month}月 销量数据...")

    url = f"https://www.dongchedi.com/sales?year={year}&month={month}"
    return fetch_with_cookie(url)


def parse_sales_text(text, year, month):
    """解析销量数据文本"""
    if not text:
        return []

    lines = text.split("\n")
    results = []
    current = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 匹配排名
        if line.isdigit() and 1 <= int(line) <= 100:
            if current.get("rank") and current.get("model") and current.get("sales"):
                results.append(current)
            current = {"rank": int(line), "year": year, "month": month}

        # 匹配车型（包含/分隔的品牌和类型）
        if "/" in line and len(line) < 30:
            parts = line.split("/")
            if len(parts) == 2 and len(parts[0]) > 1:
                current["model"] = parts[0].strip()
                current["body_type"] = parts[1].strip()

        # 匹配价格
        if "万" in line and "-" in line:
            try:
                price_str = line.replace("万", "").strip()
                parts = price_str.split("-")
                if len(parts) == 2:
                    current["price_min"] = float(parts[0])
                    current["price_max"] = float(parts[1])
            except:
                pass

        # 匹配销量（带逗号的数字）
        if "," in line:
            sales_str = line.replace(",", "").strip()
            if sales_str.isdigit() and 1000 <= int(sales_str) <= 999999:
                current["sales"] = int(sales_str)

    # 添加最后一条
    if current.get("rank") and current.get("model") and current.get("sales"):
        results.append(current)

    return results


def save_csv(data, filename):
    """保存为CSV"""
    if not data:
        return None

    filepath = Path("data/raw/dongchedi") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["year", "month", "rank", "model", "body_type", "price_min", "price_max", "sales"]
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

    print(f"  [OK] 保存: {filepath} ({len(data)} 条)")
    return filepath


def main():
    """主函数"""
    print("=" * 60)
    print("懂车帝登录采集器")
    print("=" * 60)

    # 检查是否已有cookie
    cookie = load_cookie()
    if cookie:
        print("\n[*] 检测到已保存的cookie")
        choice = input("是否使用已有cookie？(y/n): ").strip().lower()
        if choice != 'y':
            cookie = None

    # 如果没有cookie，进行登录
    if not cookie:
        cookie_file = login_dongchedi()
        if not cookie_file:
            print("\n[!] 登录失败，程序退出")
            return
        cookie = load_cookie()

    print("\n" + "=" * 60)
    print("开始采集数据")
    print("=" * 60)

    all_data = []

    # 采集2024年数据
    print("\n[采集] 2024年数据")
    for month in [1, 3, 6, 9, 12]:
        content = fetch_sales_data_with_login(2024, month)
        if content:
            data = parse_sales_text(content, 2024, month)
            all_data.extend(data)
            save_csv(data, f"sales_2024_{month:02d}.csv")
        time.sleep(3)

    # 采集2025年数据
    print("\n[采集] 2025年数据")
    for month in [1, 3, 6, 9, 12]:
        content = fetch_sales_data_with_login(2025, month)
        if content:
            data = parse_sales_text(content, 2025, month)
            all_data.extend(data)
            save_csv(data, f"sales_2025_{month:02d}.csv")
        time.sleep(3)

    # 采集2026年数据
    print("\n[采集] 2026年数据")
    for month in [1, 3, 5, 7]:
        content = fetch_sales_data_with_login(2026, month)
        if content:
            data = parse_sales_text(content, 2026, month)
            all_data.extend(data)
            save_csv(data, f"sales_2026_{month:02d}.csv")
        time.sleep(3)

    # 保存汇总
    if all_data:
        save_csv(all_data, "all_sales_data.csv")

    print("\n" + "=" * 60)
    print(f"采集完成！共获取 {len(all_data)} 条数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
