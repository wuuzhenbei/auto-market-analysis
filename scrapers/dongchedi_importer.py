"""
懂车帝数据导入器 - Playwright 浏览器自动化
用户登录后自动抓取销量数据并写入数据库
"""
import sqlite3
import time
import re
import random
from pathlib import Path
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import DB_PATH


class DongchediImporter:
    """懂车帝数据导入器"""

    SALES_URL = "https://www.dongchedi.com/sales"

    def __init__(self):
        self.progress_callback = None
        self.status = "idle"  # idle, logging_in, scraping, saving, done, error
        self.progress = 0
        self.total = 0
        self.message = ""
        self.results = []

    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback

    def _update_progress(self, status, progress, message):
        """更新进度"""
        self.status = status
        self.progress = progress
        self.message = message
        if self.progress_callback:
            self.progress_callback(status, progress, message)

    def run_import(self) -> dict:
        """
        执行完整导入流程
        Returns: {"status": "ok/error", "message": str, "stats": dict}
        """
        from playwright.sync_api import sync_playwright

        self._update_progress("starting", 0, "正在启动浏览器...")

        try:
            with sync_playwright() as p:
                # 启动有头浏览器（用户可以看到并操作）
                browser = p.chromium.launch(
                    headless=False,
                    args=["--start-maximized"]
                )
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    locale="zh-CN",
                )
                page = context.new_page()

                # 1. 打开懂车帝销量页
                self._update_progress("logging_in", 10, "正在打开懂车帝...")
                page.goto(self.SALES_URL, wait_until="networkidle", timeout=30000)
                time.sleep(2)

                # 2. 等待用户登录
                self._update_progress("logging_in", 20, "请在浏览器中登录懂车帝（扫码或账号登录），登录后会自动继续...")
                login_success = self._wait_for_login(page, timeout=300)

                if not login_success:
                    browser.close()
                    self._update_progress("error", 0, "登录超时，请重试")
                    return {"status": "error", "message": "登录超时"}

                self._update_progress("scraping", 40, "登录成功，正在抓取数据...")

                # 3. 抓取销量数据
                sales_data = self._scrape_sales_data(page)

                if not sales_data:
                    browser.close()
                    self._update_progress("error", 0, "未抓取到数据")
                    return {"status": "error", "message": "未抓取到数据"}

                self._update_progress("scraping", 70, f"抓取到 {len(sales_data)} 条数据，正在保存...")

                # 4. 写入数据库
                stats = self._save_to_database(sales_data)

                browser.close()

                self._update_progress("done", 100, f"导入完成！新增 {stats['new_brands']} 个品牌，{stats['new_models']} 个车型，{stats['new_sales']} 条销量数据")
                return {
                    "status": "ok",
                    "message": "导入完成",
                    "stats": stats,
                    "data_count": len(sales_data),
                }

        except Exception as e:
            self._update_progress("error", 0, f"导入失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _wait_for_login(self, page, timeout=300) -> bool:
        """
        等待用户登录
        检测方式：页面上是否出现用户头像/昵称，或登录按钮消失
        """
        start_time = time.time()
        check_interval = 2  # 每 2 秒检查一次

        while time.time() - start_time < timeout:
            try:
                # 检查是否已登录：查找用户头像或"我的"元素
                logged_in = page.evaluate("""
                    () => {
                        // 检查多种登录标志
                        const avatar = document.querySelector('.header-login-avatar');
                        const userInfo = document.querySelector('.user-info');
                        const loginBtn = document.querySelector('.login-btn');
                        const headerUser = document.querySelector('[class*="avatar"]');

                        // 如果有头像或用户信息，说明已登录
                        if (avatar || userInfo || headerUser) return true;

                        // 如果登录按钮消失，也可能已登录
                        if (!loginBtn) {
                            // 额外检查：页面是否有销量数据
                            const salesTable = document.querySelector('[class*="sales"]');
                            if (salesTable) return true;
                        }

                        return false;
                    }
                """)

                if logged_in:
                    time.sleep(2)  # 等待页面完全加载
                    return True

                # 也检查 URL 变化（登录后可能跳转）
                current_url = page.url
                if "login" not in current_url and "sales" in current_url:
                    # 检查页面是否有实际内容
                    content = page.content()
                    if "销量" in content and ("排名" in content or "排行" in content):
                        time.sleep(2)
                        return True

            except Exception:
                pass

            time.sleep(check_interval)

        return False

    def _scrape_sales_data(self, page) -> list:
        """
        抓取销量排名数据
        从懂车帝销量排行榜页面提取数据
        """
        all_data = []

        try:
            # 等待页面加载完成
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # 抓取当前页面数据
            page_data = page.evaluate("""
                () => {
                    const results = [];

                    // 方法1: 查找销量表格行
                    const rows = document.querySelectorAll('table tbody tr, [class*="table"] [class*="row"], [class*="list"] [class*="item"]');
                    rows.forEach(row => {
                        const cells = row.querySelectorAll('td, [class*="cell"], [class*="col"]');
                        if (cells.length >= 3) {
                            const texts = Array.from(cells).map(c => c.textContent.trim());
                            results.push(texts);
                        }
                    });

                    // 方法2: 查找销量排行卡片
                    if (results.length === 0) {
                        const cards = document.querySelectorAll('[class*="rank"], [class*="sales-item"], [class*="car-item"]');
                        cards.forEach(card => {
                            const text = card.textContent;
                            results.push([text]);
                        });
                    }

                    // 方法3: 直接获取页面文本用于解析
                    if (results.length === 0) {
                        const main = document.querySelector('main, [class*="content"], [class*="container"]');
                        if (main) {
                            results.push([main.textContent.substring(0, 5000)]);
                        }
                    }

                    return results;
                }
            """)

            # 解析抓取到的数据
            for row in page_data:
                parsed = self._parse_row(row)
                if parsed:
                    all_data.append(parsed)

            # 尝试翻页抓取更多
            for page_num in range(2, 6):  # 最多抓 5 页
                try:
                    next_btn = page.query_selector('[class*="next"], [class*="下一页"], button:has-text("下一页")')
                    if next_btn and next_btn.is_visible():
                        next_btn.click()
                        time.sleep(2)
                        page.wait_for_load_state("networkidle")

                        more_data = page.evaluate("""
                            () => {
                                const results = [];
                                const rows = document.querySelectorAll('table tbody tr, [class*="table"] [class*="row"], [class*="list"] [class*="item"]');
                                rows.forEach(row => {
                                    const cells = row.querySelectorAll('td, [class*="cell"], [class*="col"]');
                                    if (cells.length >= 3) {
                                        results.push(Array.from(cells).map(c => c.textContent.trim()));
                                    }
                                });
                                return results;
                            }
                        """)

                        for row in more_data:
                            parsed = self._parse_row(row)
                            if parsed:
                                all_data.append(parsed)
                    else:
                        break
                except Exception:
                    break

            # 如果表格方式没抓到数据，尝试 API 拦截方式
            if not all_data:
                all_data = self._scrape_via_api(page)

        except Exception as e:
            print(f"抓取数据出错: {e}")

        return all_data

    def _scrape_via_api(self, page) -> list:
        """
        通过拦截 API 请求获取数据
        懂车帝销量页会调用 API 获取数据
        """
        api_data = []

        try:
            # 监听网络请求
            api_responses = []

            def handle_response(response):
                url = response.url
                if "sales" in url or "ranking" in url or "chart" in url:
                    try:
                        data = response.json()
                        api_responses.append(data)
                    except Exception:
                        pass

            page.on("response", handle_response)

            # 刷新页面触发 API 请求
            page.reload(wait_until="networkidle")
            time.sleep(3)

            # 解析 API 响应
            for resp in api_responses:
                if isinstance(resp, dict) and "data" in resp:
                    data = resp["data"]
                    if isinstance(data, list):
                        for item in data:
                            parsed = self._parse_api_item(item)
                            if parsed:
                                api_data.append(parsed)
                    elif isinstance(data, dict):
                        for key in ["list", "rank_list", "series_list", "items"]:
                            if key in data and isinstance(data[key], list):
                                for item in data[key]:
                                    parsed = self._parse_api_item(item)
                                    if parsed:
                                        api_data.append(parsed)

        except Exception as e:
            print(f"API 拦截出错: {e}")

        return api_data

    def _parse_row(self, row_texts: list) -> dict | None:
        """解析表格行为车型数据"""
        try:
            if len(row_texts) < 3:
                # 尝试从长文本中解析
                if len(row_texts) == 1:
                    return self._parse_text_block(row_texts[0])
                return None

            text = " ".join(row_texts)

            # 提取销量数字
            sales_match = re.search(r'(\d[\d,]+)\s*(?:辆|台|销量)', text)
            sales = int(sales_match.group(1).replace(",", "")) if sales_match else 0

            # 提取价格
            price_match = re.search(r'(\d+\.?\d*)\s*[-~]\s*(\d+\.?\d*)\s*万', text)
            price_min = float(price_match.group(1)) if price_match else 0
            price_max = float(price_match.group(2)) if price_match else 0

            # 提取排名
            rank_match = re.search(r'^(\d+)', row_texts[0].strip())
            rank = int(rank_match.group(1)) if rank_match else 0

            if sales > 0:
                # 尝试从文本中提取品牌和车型名
                model_name = row_texts[1] if len(row_texts) > 1 else ""
                brand_name = row_texts[2] if len(row_texts) > 2 else ""

                return {
                    "rank": rank,
                    "model": model_name,
                    "brand": brand_name,
                    "price_min": price_min,
                    "price_max": price_max,
                    "sales": sales,
                }

        except Exception:
            pass

        return None

    def _parse_text_block(self, text: str) -> dict | None:
        """从文本块中解析数据"""
        try:
            sales_match = re.search(r'(\d[\d,]+)\s*(?:辆|台)', text)
            if not sales_match:
                return None

            sales = int(sales_match.group(1).replace(",", ""))
            if sales < 100:
                return None

            return {"rank": 0, "model": "", "brand": "", "price_min": 0, "price_max": 0, "sales": sales}
        except Exception:
            return None

    def _parse_api_item(self, item: dict) -> dict | None:
        """解析 API 返回的数据项"""
        try:
            # 懂车帝 API 常见字段名
            sales = item.get("sales_volume") or item.get("sale") or item.get("count") or 0
            sales = int(sales) if sales else 0

            if sales <= 0:
                return None

            return {
                "rank": item.get("rank", 0),
                "model": item.get("series_name") or item.get("name") or item.get("model_name", ""),
                "brand": item.get("brand_name") or item.get("brand", ""),
                "price_min": float(item.get("min_price", 0) or 0),
                "price_max": float(item.get("max_price", 0) or 0),
                "sales": sales,
                "type": item.get("type") or item.get("vehicle_type", ""),
            }
        except Exception:
            return None

    def _save_to_database(self, data: list) -> dict:
        """将抓取的数据写入数据库（增量更新）"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("PRAGMA journal_mode=WAL")

        now = datetime.now()
        year = now.year
        month = now.month

        stats = {"new_brands": 0, "new_models": 0, "new_sales": 0, "updated_sales": 0}

        # 获取现有品牌和车型映射
        brand_map = {}
        for row in conn.execute("SELECT id, name FROM brands"):
            brand_map[row[1]] = row[0]

        model_map = {}
        for row in conn.execute("SELECT id, name FROM models"):
            model_map[row[1]] = row[0]

        for item in data:
            brand_name = item.get("brand", "").strip()
            model_name = item.get("model", "").strip()
            sales = item.get("sales", 0)

            if not model_name or sales <= 0:
                continue

            # 1. 确保品牌存在
            if brand_name and brand_name not in brand_map:
                category = self._classify_brand(brand_name)
                cursor = conn.execute(
                    "INSERT INTO brands (name, country, category) VALUES (?, ?, ?)",
                    (brand_name, "中国", category)
                )
                brand_map[brand_name] = cursor.lastrowid
                stats["new_brands"] += 1

            brand_id = brand_map.get(brand_name, 1)

            # 2. 确保车型存在
            if model_name not in model_map:
                energy_type = self._guess_energy_type(model_name, item.get("type", ""))
                body_type = self._guess_body_type(item.get("type", ""))
                price_min = item.get("price_min", 0)
                price_max = item.get("price_max", 0) if item.get("price_max", 0) > 0 else price_min * 1.3

                cursor = conn.execute(
                    """INSERT INTO models (brand_id, name, series, year, energy_type, body_type,
                       guide_price_min, guide_price_max, source)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (brand_id, model_name, model_name, year, energy_type, body_type,
                     price_min, price_max, "dongchedi_import")
                )
                model_map[model_name] = cursor.lastrowid
                stats["new_models"] += 1

            model_id = model_map[model_name]

            # 3. 更新或插入销量数据
            existing = conn.execute(
                "SELECT id FROM sales WHERE model_id = ? AND year = ? AND month = ?",
                (model_id, year, month)
            ).fetchone()

            if existing:
                conn.execute(
                    "UPDATE sales SET sales_volume = ?, ranking = ? WHERE id = ?",
                    (sales, item.get("rank", 0), existing[0])
                )
                stats["updated_sales"] += 1
            else:
                conn.execute(
                    """INSERT INTO sales (model_id, year, month, sales_volume, yoy_growth, mom_growth, ranking)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (model_id, year, month, sales, 0, 0, item.get("rank", 0))
                )
                stats["new_sales"] += 1

        conn.commit()
        conn.close()

        return stats

    def _classify_brand(self, brand_name: str) -> str:
        """品牌分类"""
        new_forces = ["蔚来", "小鹏", "理想", "哪吒", "零跑", "极氪", "问界", "小米", "阿维塔", "智己", "岚图", "方程豹"]
        luxury = ["奔驰", "宝马", "奥迪", "沃尔沃", "凯迪拉克", "雷克萨斯", "保时捷", "特斯拉"]
        joint = ["大众", "丰田", "本田", "日产", "别克", "现代", "起亚", "福特", "马自达", "雪佛兰"]

        for b in new_forces:
            if b in brand_name:
                return "新势力"
        for b in luxury:
            if b in brand_name:
                return "豪华"
        for b in joint:
            if b in brand_name:
                return "合资"
        return "自主"

    def _guess_energy_type(self, model_name: str, type_str: str) -> str:
        """推测能源类型"""
        combined = model_name + type_str
        if any(k in combined for k in ["EV", "电动", "纯电", "e-tron", "EQ"]):
            return "纯电动"
        if any(k in combined for k in ["DM", "PHEV", "插混", "混动", "e+"]):
            return "插电混动"
        if any(k in combined for k in ["增程", "EREV"]):
            return "增程式"
        return "燃油"

    def _guess_body_type(self, type_str: str) -> str:
        """推测车身类型"""
        if "SUV" in type_str.upper():
            return "SUV"
        if "MPV" in type_str.upper():
            return "MPV"
        return "轿车"


# 便捷函数
def run_import(progress_callback=None) -> dict:
    """运行导入"""
    importer = DongchediImporter()
    if progress_callback:
        importer.set_progress_callback(progress_callback)
    return importer.run_import()


if __name__ == "__main__":
    result = run_import(lambda s, p, m: print(f"[{s}] {p}% - {m}"))
    print(result)
