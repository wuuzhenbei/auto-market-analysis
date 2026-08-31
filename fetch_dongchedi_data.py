"""
从懂车帝获取真实销量数据
支持获取多个月份的数据
"""
import json
import csv
import time
from pathlib import Path


def parse_dongchedi_text(text):
    """解析懂车帝页面文本，提取销量数据"""
    lines = text.split("\n")
    results = []
    current = {}

    for i, line in enumerate(lines):
        line = line.strip()

        # 匹配排名数字（1-100）
        if line.isdigit() and 1 <= int(line) <= 100:
            if current.get("rank"):
                results.append(current)
            current = {"rank": int(line)}

        # 匹配车型名称（包含品牌和类型）
        if "/" in line and ("车" in line or "suv" in line.lower() or "SUV" in line):
            parts = line.split("/")
            if len(parts) >= 2:
                current["model"] = parts[0].strip()
                current["type"] = parts[1].strip()

        # 匹配价格
        if "万" in line and "-" in line and line.count("万") == 1:
            price_str = line.replace("万", "").strip()
            if "-" in price_str:
                try:
                    parts = price_str.split("-")
                    current["price_min"] = float(parts[0])
                    current["price_max"] = float(parts[1])
                except:
                    pass

        # 匹配销量数字（4-6位数，带逗号）
        if "," in line and line.replace(",", "").isdigit():
            sales_str = line.replace(",", "")
            if 1000 <= int(sales_str) <= 999999:
                current["sales"] = int(sales_str)

    # 添加最后一条
    if current.get("rank"):
        results.append(current)

    return results


def fetch_monthly_data(year, month):
    """获取指定月份的销量数据"""
    print(f"\n[*] 获取 {year}年{month}月 数据...")

    # 使用 browser-harness 获取数据
    import subprocess

    script = f'''
new_tab("https://www.dongchedi.com/sales?year={year}&month={month}")
wait_for_load()
time.sleep(2)

# 滚动加载更多数据
for i in range(10):
    js("window.scrollBy(0, 800)")
    time.sleep(0.5)

content = js("document.body.innerText")
print(content[:10000])
'''

    try:
        result = subprocess.run(
            ["browser-harness", "-c", script],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    except Exception as e:
        print(f"  [!] 获取失败: {e}")
        return None


def save_to_csv(data, filename):
    """保存数据到 CSV 文件"""
    if not data:
        return

    filepath = Path("data/raw") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "model", "type", "price_min", "price_max", "sales"])
        writer.writeheader()
        writer.writerows(data)

    print(f"  [OK] 保存到: {filepath} ({len(data)} 条)")


def main():
    """主函数"""
    print("=" * 60)
    print("懂车帝数据采集")
    print("=" * 60)

    # 采集 2024 年数据
    print("\n" + "=" * 60)
    print("采集 2024 年数据")
    print("=" * 60)

    all_data_2024 = []
    for month in range(1, 13):
        text = fetch_monthly_data(2024, month)
        if text:
            data = parse_dongchedi_text(text)
            for item in data:
                item["year"] = 2024
                item["month"] = month
            all_data_2024.extend(data)
            save_to_csv(data, f"dongchedi_2024_{month:02d}.csv")
        time.sleep(2)

    # 采集 2025 年数据
    print("\n" + "=" * 60)
    print("采集 2025 年数据")
    print("=" * 60)

    all_data_2025 = []
    for month in range(1, 13):
        text = fetch_monthly_data(2025, month)
        if text:
            data = parse_dongchedi_text(text)
            for item in data:
                item["year"] = 2025
                item["month"] = month
            all_data_2025.extend(data)
            save_to_csv(data, f"dongchedi_2025_{month:02d}.csv")
        time.sleep(2)

    # 采集 2026 年数据（到7月）
    print("\n" + "=" * 60)
    print("采集 2026 年数据")
    print("=" * 60)

    all_data_2026 = []
    for month in range(1, 8):
        text = fetch_monthly_data(2026, month)
        if text:
            data = parse_dongchedi_text(text)
            for item in data:
                item["year"] = 2026
                item["month"] = month
            all_data_2026.extend(data)
            save_to_csv(data, f"dongchedi_2026_{month:02d}.csv")
        time.sleep(2)

    # 保存汇总数据
    all_data = all_data_2024 + all_data_2025 + all_data_2026
    save_to_csv(all_data, "dongchedi_all.csv")

    print("\n" + "=" * 60)
    print(f"采集完成！共获取 {len(all_data)} 条数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
