"""
数据库连接管理
"""
import sqlite3
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from config import DB_PATH


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def query_to_dict(query: str, params: list = None) -> list:
    """执行查询并返回字典列表"""
    conn = get_connection()
    try:
        cursor = conn.execute(query, params or [])
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def query_to_dataframe(query: str, params: list = None):
    """执行查询并返回 DataFrame"""
    import pandas as pd
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()
