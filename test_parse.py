"""测试解析逻辑"""
import re


def parse_sales_data(text, year, month):
    """解析销量数据"""
    results = []
    lines = text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 匹配排名（1-100的数字）
        if line.isdigit() and 1 <= int(line) <= 100:
            rank = int(line)
            model = ""
            body_type = ""
            price_min = 0
            price_max = 0
            sales = 0

            # 向后查找车型信息
            j = i + 1
            while j < min(i + 10, len(lines)):
                next_line = lines[j].strip()

                # 匹配车型名称（格式：品牌/类型）
                if "/" in next_line and len(next_line) < 40:
                    parts = next_line.split("/")
                    if len(parts) >= 2:
                        model = parts[0].strip()
                        body_type = parts[1].strip()

                # 匹配价格（格式：X.XX-XX.XX万）
                price_match = re.match(r'(\d+\.?\d*)-(\d+\.?\d*)万', next_line)
                if price_match:
                    price_min = float(price_match.group(1))
                    price_max = float(price_match.group(2))

                # 匹配销量（带逗号的数字，如32,306）
                sales_match = re.match(r'^([\d,]+)$', next_line)
                if sales_match:
                    sales_str = sales_match.group(1).replace(",", "")
                    if sales_str.isdigit() and 1000 <= int(sales_str) <= 999999:
                        sales = int(sales_str)
                        break

                j += 1

            # 只保存有效数据
            if model and sales > 0:
                results.append({
                    "year": year,
                    "month": month,
                    "rank": rank,
                    "model": model,
                    "body_type": body_type,
                    "price_min": price_min,
                    "price_max": price_max,
                    "sales": sales
                })

        i += 1

    return results


# 测试数据
test_text = """1
星愿吉利银河/小型车

5.98-9.18万

参数
图片
懂车分
车友圈

32,306

销量趋势
询底价二手车
1
零跑A10零跑汽车/小型suv

6.58-8.68万

参数
图片
懂车分
车友圈

26,424

销量趋势
询底价二手车
2
Model Y特斯拉中国/中型suv

26.35-31.35万

参数
图片
懂车分
车友圈

25,158"""

print("测试解析...")
result = parse_sales_data(test_text, 2026, 7)
print(f"解析到 {len(result)} 条数据")
for item in result:
    print(f"  排名{item['rank']}: {item['model']} - {item['sales']}辆")
