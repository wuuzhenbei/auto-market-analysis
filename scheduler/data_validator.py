"""
数据校验模块
检查数据完整性和准确性
"""
import sqlite3
import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import DB_PATH

logger = logging.getLogger(__name__)


class DataValidator:
    """数据校验器"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.errors = []
        self.warnings = []

    def validate_all(self):
        """执行所有校验"""
        logger.info("开始数据校验...")

        self.validate_sales_data()
        self.validate_models_data()
        self.validate_brands_data()
        self.validate_data_consistency()
        self.validate_data_freshness()

        result = {
            'timestamp': datetime.now().isoformat(),
            'has_errors': len(self.errors) > 0,
            'has_warnings': len(self.warnings) > 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'summary': self.get_summary()
        }

        self.save_report(result)
        return result

    def validate_sales_data(self):
        """校验销量数据"""
        logger.info("校验销量数据...")

        # 检查是否有空值
        query = "SELECT COUNT(*) FROM sales WHERE sales_volume IS NULL OR sales_volume = 0"
        count = self.conn.execute(query).fetchone()[0]
        if count > 0:
            self.warnings.append(f"销量数据有 {count} 条空值或零值")

        # 检查销量是否合理（不应为负数）
        query = "SELECT COUNT(*) FROM sales WHERE sales_volume < 0"
        count = self.conn.execute(query).fetchone()[0]
        if count > 0:
            self.errors.append(f"销量数据有 {count} 条负值")

        # 检查销量是否异常高（超过100万）
        query = "SELECT COUNT(*) FROM sales WHERE sales_volume > 1000000"
        count = self.conn.execute(query).fetchone()[0]
        if count > 0:
            self.warnings.append(f"销量数据有 {count} 条超过100万，可能异常")

        # 检查月份数据完整性
        query = """
        SELECT year, month, COUNT(*) as cnt
        FROM sales
        GROUP BY year, month
        HAVING cnt < 5
        """
        df = pd.read_sql(query, self.conn)
        if len(df) > 0:
            for _, row in df.iterrows():
                self.warnings.append(f"{row['year']}年{row['month']}月只有 {row['cnt']} 条数据")

    def validate_models_data(self):
        """校验车型数据"""
        logger.info("校验车型数据...")

        # 检查价格数据
        query = "SELECT COUNT(*) FROM models WHERE guide_price_min <= 0"
        count = self.conn.execute(query).fetchone()[0]
        if count > 0:
            self.warnings.append(f"有 {count} 个车型最低价小于等于0")

        # 检查价格合理性
        query = "SELECT COUNT(*) FROM models WHERE guide_price_min > guide_price_max"
        count = self.conn.execute(query).fetchone()[0]
        if count > 0:
            self.errors.append(f"有 {count} 个车型最低价大于最高价")

        # 检查能源类型
        valid_types = ['纯电动', '插电混动', '增程式', '燃油', '油电混动']
        query = f"SELECT DISTINCT energy_type FROM models WHERE energy_type NOT IN ({','.join(['?' for _ in valid_types])})"
        invalid = pd.read_sql(query, self.conn, params=valid_types)
        if len(invalid) > 0:
            self.warnings.append(f"有无效能源类型: {invalid['energy_type'].tolist()}")

    def validate_brands_data(self):
        """校验品牌数据"""
        logger.info("校验品牌数据...")

        # 检查品牌是否有对应车型
        query = """
        SELECT b.name, COUNT(m.id) as model_count
        FROM brands b
        LEFT JOIN models m ON b.id = m.brand_id
        GROUP BY b.id
        HAVING model_count = 0
        """
        df = pd.read_sql(query, self.conn)
        if len(df) > 0:
            self.warnings.append(f"有 {len(df)} 个品牌没有对应车型: {df['name'].tolist()}")

    def validate_data_consistency(self):
        """校验数据一致性"""
        logger.info("校验数据一致性...")

        # 检查销量数据是否有对应车型
        query = """
        SELECT COUNT(*) FROM sales s
        LEFT JOIN models m ON s.model_id = m.id
        WHERE m.id IS NULL
        """
        count = self.conn.execute(query).fetchone()[0]
        if count > 0:
            self.errors.append(f"有 {count} 条销量数据没有对应车型")

        # 检查车型是否有对应品牌
        query = """
        SELECT COUNT(*) FROM models m
        LEFT JOIN brands b ON m.brand_id = b.id
        WHERE b.id IS NULL
        """
        count = self.conn.execute(query).fetchone()[0]
        if count > 0:
            self.errors.append(f"有 {count} 个车型没有对应品牌")

    def validate_data_freshness(self):
        """校验数据新鲜度"""
        logger.info("校验数据新鲜度...")

        # 检查最新数据时间
        query = "SELECT MAX(year * 100 + month) as latest FROM sales"
        latest = self.conn.execute(query).fetchone()[0]

        if latest:
            now = datetime.now()
            current_month = now.year * 100 + now.month
            if current_month - latest > 1:
                self.warnings.append(f"数据可能过期，最新数据是 {latest}")

    def get_summary(self):
        """获取数据摘要"""
        summary = {}

        # 销量数据
        query = "SELECT COUNT(*), SUM(sales_volume) FROM sales"
        result = self.conn.execute(query).fetchone()
        summary['sales_count'] = result[0]
        summary['total_sales'] = result[1]

        # 车型数据
        query = "SELECT COUNT(*) FROM models"
        summary['model_count'] = self.conn.execute(query).fetchone()[0]

        # 品牌数据
        query = "SELECT COUNT(*) FROM brands"
        summary['brand_count'] = self.conn.execute(query).fetchone()[0]

        # 评分数据
        query = "SELECT COUNT(*) FROM ratings"
        summary['rating_count'] = self.conn.execute(query).fetchone()[0]

        return summary

    def save_report(self, result):
        """保存校验报告"""
        report_dir = PROJECT_ROOT / "reports"
        report_dir.mkdir(exist_ok=True)

        filename = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = report_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info(f"校验报告已保存: {filepath}")

    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    validator = DataValidator()
    results = validator.validate_all()
    validator.close()

    print("\n" + "="*50)
    print("数据校验结果")
    print("="*50)
    print(f"错误: {len(results['errors'])}")
    print(f"警告: {len(results['warnings'])}")

    if results['errors']:
        print("\n错误:")
        for e in results['errors']:
            print(f"  ❌ {e}")

    if results['warnings']:
        print("\n警告:")
        for w in results['warnings']:
            print(f"  ⚠️ {w}")

    print(f"\n数据摘要: {json.dumps(results['summary'], indent=2)}")
