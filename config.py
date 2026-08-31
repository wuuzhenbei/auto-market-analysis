"""
汽车市场数据分析项目 - 配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXCEL_DIR = DATA_DIR / "excel"
TABLEAU_DIR = DATA_DIR / "tableau"

# 数据库
DB_PATH = PROJECT_ROOT / "database" / "auto_market.db"

# 可视化输出
CHART_OUTPUT_DIR = PROJECT_ROOT / "visualization" / "output"

# 采集配置
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # 请求间隔（秒）
MAX_RETRIES = 3

# User-Agent 轮换
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# 分析配置
PRICE_RANGES = [
    (0, 5, "5万以下"),
    (5, 10, "5-10万"),
    (10, 15, "10-15万"),
    (15, 20, "15-20万"),
    (20, 30, "20-30万"),
    (30, 50, "30-50万"),
    (50, 100, "50-100万"),
    (100, float('inf'), "100万以上"),
]

# 新能源类型
ENERGY_TYPES = ["纯电动", "插电混动", "增程式", "燃油", "油电混动"]

# 评分维度
RATING_DIMENSIONS = ["外观", "内饰", "动力", "空间", "油耗", "操控", "舒适性", "性价比"]

# 图表样式
CHART_STYLE = {
    "figure.figsize": (12, 8),
    "figure.dpi": 150,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 12,
}

# 中文字体配置
CHINESE_FONT = "Microsoft YaHei"  # Windows
# CHINESE_FONT = "PingFang SC"  # macOS
# CHINESE_FONT = "WenQuanYi Micro Hei"  # Linux
