"""
采集器基类
"""
import time
import random
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import USER_AGENTS, REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES


class BaseScraper(ABC):
    """采集器基类"""

    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })

    def get_random_ua(self) -> str:
        """获取随机 User-Agent"""
        return random.choice(USER_AGENTS)

    def fetch_page(self, url: str, params: Optional[Dict] = None, use_api: bool = False) -> Optional[str]:
        """
        获取页面内容

        Args:
            url: 请求URL
            params: 请求参数
            use_api: 是否为 API 请求（返回 JSON）

        Returns:
            页面内容或 None
        """
        for attempt in range(MAX_RETRIES):
            try:
                self.session.headers["User-Agent"] = self.get_random_ua()
                response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                if use_api:
                    return response.json()
                return response.text

            except requests.RequestException as e:
                print(f"  [!] 请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(REQUEST_DELAY * (attempt + 1))

        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """解析 HTML"""
        return BeautifulSoup(html, "lxml")

    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机延时"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    @abstractmethod
    def scrape_brand_list(self) -> List[Dict]:
        """采集品牌列表"""
        pass

    @abstractmethod
    def scrape_model_list(self, brand_id: str) -> List[Dict]:
        """采集车型列表"""
        pass

    @abstractmethod
    def scrape_model_detail(self, model_id: str) -> Dict:
        """采集车型详情"""
        pass

    def run(self):
        """运行采集流程"""
        print(f"\n[*] 开始采集: {self.name}")
        print("=" * 50)

        try:
            # 1. 采集品牌列表
            print("[1/3] 采集品牌列表...")
            brands = self.scrape_brand_list()
            print(f"  - 获取到 {len(brands)} 个品牌")

            # 2. 采集车型列表
            print("[2/3] 采集车型列表...")
            all_models = []
            for brand in brands:
                models = self.scrape_model_list(brand["id"])
                all_models.extend(models)
                self.random_delay()
            print(f"  - 获取到 {len(all_models)} 个车型")

            # 3. 采集车型详情
            print("[3/3] 采集车型详情...")
            details = []
            for model in all_models[:10]:  # 限制数量，避免被封
                detail = self.scrape_model_detail(model["id"])
                if detail:
                    details.append(detail)
                self.random_delay()

            print(f"\n[[OK]] 采集完成: {len(details)} 条详情数据")
            return details

        except Exception as e:
            print(f"\n[[FAIL]] 采集失败: {e}")
            return []
