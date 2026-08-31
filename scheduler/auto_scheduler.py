"""
定时自动化调度器
支持定时采集数据和数据校验
"""
import schedule
import time
import logging
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 配置日志
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "scheduler.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataScheduler:
    """数据调度器"""

    def __init__(self):
        self.config_file = PROJECT_ROOT / "config" / "scheduler_config.json"
        self.config = self.load_config()

    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "collect_time": "02:00",  # 每天凌晨2点采集
            "validate_time": "03:00",  # 每天凌晨3点校验
            "export_time": "04:00",  # 每天凌晨4点导出
            "collect_day": 1,  # 每月1号采集上月数据
            "email_alert": False,
            "email_config": {
                "smtp_server": "smtp.qq.com",
                "smtp_port": 465,
                "sender": "",
                "password": "",
                "receivers": []
            }
        }

    def save_config(self):
        """保存配置"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def collect_data(self):
        """采集数据任务"""
        logger.info("="*50)
        logger.info("开始采集数据...")

        try:
            from collect_limited_data import main as collect_main
            collect_main()
            logger.info("数据采集完成!")
            self.send_alert("数据采集成功", "懂车帝数据采集完成")
        except Exception as e:
            logger.error(f"数据采集失败: {e}")
            self.send_alert("数据采集失败", str(e))

    def validate_data(self):
        """数据校验任务"""
        logger.info("="*50)
        logger.info("开始数据校验...")

        try:
            from scheduler.data_validator import DataValidator
            validator = DataValidator()
            results = validator.validate_all()

            if results['has_errors']:
                logger.warning(f"发现数据问题: {results['errors']}")
                self.send_alert("数据校验发现问题", json.dumps(results['errors'], ensure_ascii=False))
            else:
                logger.info("数据校验通过!")
        except Exception as e:
            logger.error(f"数据校验失败: {e}")
            self.send_alert("数据校验失败", str(e))

    def export_data(self):
        """导出数据任务"""
        logger.info("="*50)
        logger.info("开始导出数据...")

        try:
            from export.excel_exporter import ExcelExporter
            exporter = ExcelExporter()
            exporter.export_all(2026)
            exporter.close()
            logger.info("数据导出完成!")
        except Exception as e:
            logger.error(f"数据导出失败: {e}")

    def send_alert(self, subject, content):
        """发送告警邮件"""
        if not self.config.get('email_alert'):
            return

        try:
            email_config = self.config['email_config']
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['Subject'] = f"[汽车数据分析] {subject}"
            msg['From'] = email_config['sender']
            msg['To'] = ', '.join(email_config['receivers'])

            with smtplib.SMTP_SSL(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.login(email_config['sender'], email_config['password'])
                server.send_message(msg)
            logger.info(f"告警邮件已发送: {subject}")
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")

    def setup_schedule(self):
        """设置定时任务"""
        # 每月1号采集数据
        schedule.every().month.at(self.config['collect_time']).do(self.collect_data)

        # 每天校验数据
        schedule.every().day.at(self.config['validate_time']).do(self.validate_data)

        # 每月2号导出数据
        schedule.every().month.at(self.config['export_time']).do(self.export_data)

        logger.info("定时任务已设置:")
        logger.info(f"  - 数据采集: 每月1号 {self.config['collect_time']}")
        logger.info(f"  - 数据校验: 每天 {self.config['validate_time']}")
        logger.info(f"  - 数据导出: 每月2号 {self.config['export_time']}")

    def run(self):
        """运行调度器"""
        logger.info("="*50)
        logger.info("启动定时调度器")
        logger.info("="*50)

        self.setup_schedule()

        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    scheduler = DataScheduler()
    scheduler.run()
