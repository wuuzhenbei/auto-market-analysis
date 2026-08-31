"""
从懂车帝获取真实数据
使用 browser-harness 采集销量和参数数据
"""
import json
import csv
import time
import subprocess
from pathlib import Path


def run_browser_harness(script):
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


def fetch_sales_data(year, month):
    """获取指定月份的销量数据"""
    print(f"\n[*] 获取 {year}年{month}月 销量数据...")

    script = f'''
new_tab("https://www.dongchedi.com/sales?year={year}&month={month}")
wait_for_load()
time.sleep(3)

# 滚动加载更多数据
for i in range(15):
    js("window.scrollBy(0, 600)")
    time.sleep(0.3)

content = js("document.body.innerText")
print(content[:15000])
'''

    return run_browser_harness(script)


def parse_sales_text(text, year, month):
    """解析销量数据文本"""
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
    """保存为 CSV"""
    if not data:
        return

    filepath = Path("data/raw/dongchedi") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["year", "month", "rank", "model", "body_type", "price_min", "price_max", "sales"]
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

    print(f"  [OK] 保存: {filepath} ({len(data)} 条)")
    return filepath


def fetch_car_specs():
    """获取车型参数数据"""
    print("\n" + "=" * 60)
    print("获取车型参数数据")
    print("=" * 60)

    # 热门车型列表
    popular_models = [
        "秦PLUS DM-i", "宋PLUS DM-i", "汉EV", "海豚", "元PLUS",
        "Model Y", "Model 3", "小米SU7", "理想L7", "理想L8",
        "问界M7", "问界M9", "蔚来ES6", "小鹏P7", "朗逸",
        "帕萨特", "凯美瑞", "RAV4荣放", "CR-V", "宝马3系",
    ]

    specs_data = []

    for model_name in popular_models[:5]:  # 先获取5个车型的参数
        print(f"\n[*] 获取 {model_name} 参数...")

        script = f'''
new_tab("https://www.dongchedi.com/auto/params-carIds-x-{model_name}")
wait_for_load()
time.sleep(3)
content = js("document.body.innerText")
print(content[:5000])
'''

        content = run_browser_harness(script)
        if content:
            # 解析参数数据
            spec = parse_spec_text(content, model_name)
            if spec:
                specs_data.append(spec)

        time.sleep(2)

    return specs_data


def parse_spec_text(text, model_name):
    """解析参数数据"""
    spec = {"model": model_name}

    lines = text.split("\n")
    for i, line in enumerate(lines):
        line = line.strip()

        # 提取各种参数
        if "发动机" in line or "电机" in line:
            spec["engine"] = line
        elif "马力" in line:
            spec["horsepower"] = line
        elif "扭矩" in line:
            spec["torque"] = line
        elif "油耗" in line or "电耗" in line:
            spec["consumption"] = line
        elif "续航" in line:
            spec["range"] = line
        elif "长×宽×高" in line or "车身尺寸" in line:
            spec["dimensions"] = line
        elif "轴距" in line:
            spec["wheelbase"] = line
        elif "整备质量" in line:
            spec["weight"] = line

    return spec if len(spec) > 1 else None


def main():
    """主函数"""
    print("=" * 60)
    print("懂车帝真实数据采集")
    print("=" * 60)

    all_data = []

    # 采集 2024 年关键月份数据
    print("\n" + "=" * 60)
    print("采集 2024 年数据")
    print("=" * 60)

    for month in [1, 3, 6, 9, 12]:  # 采集关键月份
        content = fetch_sales_data(2024, month)
        if content:
            data = parse_sales_text(content, 2024, month)
            all_data.extend(data)
            save_csv(data, f"sales_2024_{month:02d}.csv")
        time.sleep(3)

    # 采集 2025 年关键月份数据
    print("\n" + "=" * 60)
    print("采集 2025 年数据")
    print("=" * 60)

    for month in [1, 3, 6, 9, 12]:
        content = fetch_sales_data(2025, month)
        if content:
            data = parse_sales_text(content, 2025, month)
            all_data.extend(data)
            save_csv(data, f"sales_2025_{month:02d}.csv")
        time.sleep(3)

    # 采集 2026 年数据
    print("\n" + "=" * 60)
    print("采集 2026 年数据")
    print("=" * 60)

    for month in [1, 3, 5, 7]:
        content = fetch_sales_data(2026, month)
        if content:
            data = parse_sales_text(content, 2026, month)
            all_data.extend(data)
            save_csv(data, f"sales_2026_{month:02d}.csv")
        time.sleep(3)

    # 保存汇总数据
    save_csv(all_data, "all_sales_data.csv")

    # 获取车型参数
    specs = fetch_car_specs()
    if specs:
        save_csv(specs, "car_specs.csv")

    print("\n" + "=" * 60)
    print(f"采集完成！共获取 {len(all_data)} 条销量数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
