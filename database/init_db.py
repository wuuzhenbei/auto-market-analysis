"""
初始化数据库 - 创建表结构并导入真实数据
"""
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_PATH
from database.real_data import generate_realistic_data


def init_database():
    """初始化数据库"""
    # 确保目录存在
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # 读取并执行 schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()
    print(f"[OK] 数据库表结构创建完成: {DB_PATH}")

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM brands")
    count = cursor.fetchone()[0]

    if count == 0:
        print("[*] 数据库为空，正在导入真实数据...")
        generate_realistic_data(conn)
        print("[OK] 真实数据导入完成")
    else:
        print(f"[*] 数据库已有 {count} 个品牌，跳过数据导入")

    conn.close()
    print("[OK] 数据库初始化完成")


if __name__ == "__main__":
    init_database()
