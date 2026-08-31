"""
懂车帝 CDP 采集器
使用 Chrome DevTools Protocol 获取登录cookie
参考Mineradio项目的实现方式
"""
import json
import csv
import time
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


class DongchediCDPScraper:
    """使用CDP协议的懂车帝采集器"""

    BASE_URL = "https://www.dongchedi.com"
    COOKIE_FILE = Path("data/dongchedi_cookie.json")

    def __init__(self):
        self.cookies = {}
        self.cookie_string = ""
        self.load_cookie()

    def load_cookie(self):
        """加载已保存的cookie"""
        if self.COOKIE_FILE.exists():
            with open(self.COOKIE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.cookies = data.get("cookies", {})
                self.cookie_string = data.get("cookie_string", "")
                return True
        return False

    def save_cookie(self):
        """保存cookie到文件"""
        self.COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cookie_data = {
            "timestamp": datetime.now().isoformat(),
            "cookies": self.cookies,
            "cookie_string": self.cookie_string
        }
        with open(self.COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookie_data, f, ensure_ascii=False, indent=2)
        print(f"  [OK] Cookie已保存到: {self.COOKIE_FILE}")

    def run_browser_harness(self, script):
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

    def login(self):
        """交互式登录懂车帝"""
        print("=" * 60)
        print("懂车帝登录")
        print("=" * 60)
        print("\n将打开浏览器，请手动登录懂车帝")
        print("支持：手机号、微信、抖音等方式\n")

        # 打开登录页面
        script = '''
new_tab("https://www.dongchedi.com")
wait_for_load()
time.sleep(2)
print("READY")
'''
        result = self.run_browser_harness(script)
        if not result or "READY" not in result:
            print("[!] 无法打开网站")
            return False

        print("请在浏览器中完成登录...")
        input("\n登录完成后，按回车键继续...")

        # 获取cookie
        return self.get_cookies_from_browser()

    def get_cookies_from_browser(self):
        """从浏览器获取cookie"""
        print("\n[*] 正在获取cookie...")

        script = '''
import json

# 使用CDP获取cookie
try:
    cookies = cdp("Network.getCookies", {"urls": ["https://www.dongchedi.com"]})
    print("RESULT:" + json.dumps(cookies))
except Exception as e:
    print("ERROR:" + str(e))
'''

        result = self.run_browser_harness(script)
        if not result:
            print("[!] 获取cookie失败")
            return False

        # 解析结果
        for line in result.split("\n"):
            line = line.strip()
            if line.startswith("RESULT:"):
                try:
                    data = json.loads(line[7:])
                    for cookie in data.get("cookies", []):
                        self.cookies[cookie["name"]] = cookie["value"]
                except Exception as e:
                    print(f"[!] 解析cookie失败: {e}")
                    return False
            elif line.startswith("ERROR:"):
                print(f"[!] CDP错误: {line[6:]}")
                return False

        if not self.cookies:
            print("[!] 未获取到cookie")
            return False

        # 构建cookie字符串
        self.cookie_string = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        self.save_cookie()

        print(f"  [OK] 获取到 {len(self.cookies)} 个cookie")
        return True

    def fetch_page(self, url, use_api=False):
        """使用cookie获取页面内容"""
        if not self.cookie_string:
            print("[!] 无可用cookie，请先登录")
            return None

        # 构建请求脚本
        if use_api:
            script = f'''
import json
import urllib.request

url = "{url}"
cookies = "{self.cookie_string}"

req = urllib.request.Request(url)
req.add_header("Cookie", cookies)
req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
req.add_header("Referer", "https://www.dongchedi.com/")

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("DATA:" + json.dumps(data))
except Exception as e:
    print("ERROR:" + str(e))
'''
        else:
            script = f'''
new_tab("{url}")
wait_for_load()
time.sleep(3)

# 滚动加载
for i in range(10):
    js("window.scrollBy(0, 600)")
    time.sleep(0.3)

content = js("document.body.innerText")
print(content[:20000])
'''

        result = self.run_browser_harness(script)
        if not result:
            return None

        # 解析API响应
        if use_api:
            for line in result.split("\n"):
                line = line.strip()
                if line.startswith("DATA:"):
                    try:
                        return json.loads(line[5:])
                    except:
                        pass
                elif line.startswith("ERROR:"):
                    print(f"  [!] 请求错误: {line[6:]}")
            return None

        return result

    def fetch_sales_data(self, year, month):
        """获取指定月份的销量数据"""
        print(f"\n[*] 获取 {year}年{month}月 销量数据...")

        # 尝试API方式
        url = f"{self.BASE_URL}/motor/pc/car/rank?aid=1839&app_name=auto_web_pc&count=10&month={month}&new_energy_type=&rank_data_type=11&brand_id=&price=&outter_detail_type=&nation=0&year={year}"
        data = self.fetch_page(url, use_api=True)

        if data and "data" in data:
            return self.parse_api_sales(data, year, month)

        # 备用：页面抓取方式
        url = f"{self.BASE_URL}/sales?year={year}&month={month}"
        content = self.fetch_page(url)
        if content:
            return self.parse_sales_text(content, year, month)

        return []

    def parse_api_sales(self, data, year, month):
        """解析API返回的销量数据"""
        results = []
        rank_list = data.get("data", {}).get("rank_list", [])

        for i, item in enumerate(rank_list, 1):
            series_info = item.get("series_info", {})
            results.append({
                "year": year,
                "month": month,
                "rank": i,
                "model": series_info.get("series_name", ""),
                "brand": series_info.get("brand_name", ""),
                "body_type": series_info.get("vehicle_type", ""),
                "price_min": series_info.get("min_price", 0) / 10000,
                "price_max": series_info.get("max_price", 0) / 10000,
                "sales": item.get("count", 0)
            })

        return results

    def parse_sales_text(self, text, year, month):
        """解析页面文本中的销量数据"""
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

            # 匹配车型
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

            # 匹配销量
            if "," in line:
                sales_str = line.replace(",", "").strip()
                if sales_str.isdigit() and 1000 <= int(sales_str) <= 999999:
                    current["sales"] = int(sales_str)

        # 添加最后一条
        if current.get("rank") and current.get("model") and current.get("sales"):
            results.append(current)

        return results

    def save_csv(self, data, filename):
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

    def run(self):
        """运行采集流程"""
        print("=" * 60)
        print("懂车帝数据采集器 (CDP模式)")
        print("=" * 60)

        # 检查登录状态
        if not self.cookie_string:
            print("\n[*] 需要登录懂车帝账号")
            if not self.login():
                print("\n[!] 登录失败，程序退出")
                return
        else:
            print("\n[*] 使用已保存的cookie")

        print("\n" + "=" * 60)
        print("开始采集数据")
        print("=" * 60)

        all_data = []

        # 采集2024年数据
        print("\n[采集] 2024年数据")
        for month in [1, 3, 6, 9, 12]:
            data = self.fetch_sales_data(2024, month)
            if data:
                all_data.extend(data)
                self.save_csv(data, f"sales_2024_{month:02d}.csv")
            time.sleep(3)

        # 采集2025年数据
        print("\n[采集] 2025年数据")
        for month in [1, 3, 6, 9, 12]:
            data = self.fetch_sales_data(2025, month)
            if data:
                all_data.extend(data)
                self.save_csv(data, f"sales_2025_{month:02d}.csv")
            time.sleep(3)

        # 采集2026年数据
        print("\n[采集] 2026年数据")
        for month in [1, 3, 5, 7]:
            data = self.fetch_sales_data(2026, month)
            if data:
                all_data.extend(data)
                self.save_csv(data, f"sales_2026_{month:02d}.csv")
            time.sleep(3)

        # 保存汇总
        if all_data:
            self.save_csv(all_data, "all_sales_data.csv")

        print("\n" + "=" * 60)
        print(f"采集完成！共获取 {len(all_data)} 条数据")
        print("=" * 60)


if __name__ == "__main__":
    scraper = DongchediCDPScraper()
    scraper.run()
