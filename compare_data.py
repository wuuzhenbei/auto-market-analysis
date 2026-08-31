"""
数据对比分析脚本
对比项目示例数据与真实市场数据
"""

# 2024年中国汽车市场真实数据（来源：中汽协、乘联会公开数据）
REAL_DATA_2024 = {
    "brand_sales": {
        "比亚迪": 4270000,
        "奇瑞": 1800000,
        "吉利": 1600000,
        "长安": 1500000,
        "大众": 2000000,
        "丰田": 1700000,
        "本田": 1000000,
        "日产": 700000,
        "特斯拉": 650000,
        "宝马": 820000,
        "奔驰": 750000,
        "奥迪": 700000,
        "蔚来": 220000,
        "小鹏": 190000,
        "理想": 380000,
        "问界": 370000,
        "小米": 130000,
    },
    "new_energy_penetration": 40.9,  # 2024年新能源渗透率约40.9%
    "total_sales": 31000000,  # 2024年全年销量约3100万辆
}

# 项目示例数据
SAMPLE_DATA = {
    "brand_sales": {
        "比亚迪": 745993,
        "奥迪": 635170,
        "吉利": 585505,
        "理想": 520432,
        "大众": 519005,
        "奔驰": 446025,
        "宝马": 435161,
        "蔚来": 418105,
        "小鹏": 393719,
        "丰田": 346450,
    },
    "new_energy_penetration": 58.5,
    "total_sales": 6323758,
}


def compare_data():
    """对比数据"""
    print("=" * 70)
    print("项目示例数据 vs 真实市场数据 对比分析")
    print("=" * 70)

    print("\n【说明】")
    print("项目使用的是模拟示例数据，用于演示数据分析流程。")
    print("以下对比展示示例数据与真实数据的差异，帮助理解数据规模。")

    # 1. 总销量对比
    print("\n" + "-" * 70)
    print("1. 总销量对比")
    print("-" * 70)
    print(f"  真实数据: {REAL_DATA_2024['total_sales']:,} 辆 (2024年全年)")
    print(f"  示例数据: {SAMPLE_DATA['total_sales']:,} 辆")
    print(f"  比例: 示例数据是真实数据的 {SAMPLE_DATA['total_sales']/REAL_DATA_2024['total_sales']*100:.1f}%")
    print("\n  差异原因: 示例数据仅包含56个车型，真实市场有数百款车型")

    # 2. 新能源渗透率对比
    print("\n" + "-" * 70)
    print("2. 新能源渗透率对比")
    print("-" * 70)
    print(f"  真实数据: {REAL_DATA_2024['new_energy_penetration']}%")
    print(f"  示例数据: {SAMPLE_DATA['new_energy_penetration']}%")
    diff = SAMPLE_DATA['new_energy_penetration'] - REAL_DATA_2024['new_energy_penetration']
    print(f"  差异: {'+' if diff > 0 else ''}{diff:.1f}%")
    print("\n  差异原因: 示例数据中新能源车型占比较高（56款中约30款为新能源）")

    # 3. 品牌销量对比
    print("\n" + "-" * 70)
    print("3. 品牌销量对比（TOP 10）")
    print("-" * 70)
    print(f"{'品牌':<8} {'真实销量':<15} {'示例销量':<15} {'比例':<10}")
    print("-" * 50)

    # 获取示例数据中的TOP 10品牌
    sample_top10 = list(SAMPLE_DATA["brand_sales"].keys())[:10]

    for brand in sample_top10:
        real_sales = REAL_DATA_2024["brand_sales"].get(brand, 0)
        sample_sales = SAMPLE_DATA["brand_sales"].get(brand, 0)

        if real_sales > 0:
            ratio = f"{sample_sales/real_sales*100:.1f}%"
        else:
            ratio = "N/A"

        print(f"{brand:<8} {real_sales:<15,} {sample_sales:<15,} {ratio:<10}")

    # 4. 排名对比
    print("\n" + "-" * 70)
    print("4. 品牌排名对比")
    print("-" * 70)

    # 真实数据排名
    real_ranking = sorted(REAL_DATA_2024["brand_sales"].items(), key=lambda x: x[1], reverse=True)
    # 示例数据排名
    sample_ranking = sorted(SAMPLE_DATA["brand_sales"].items(), key=lambda x: x[1], reverse=True)

    print(f"{'品牌':<8} {'真实排名':<10} {'示例排名':<10} {'排名变化':<10}")
    print("-" * 40)

    real_rank_map = {brand: i+1 for i, (brand, _) in enumerate(real_ranking)}
    sample_rank_map = {brand: i+1 for i, (brand, _) in enumerate(sample_ranking)}

    for brand in sample_top10[:8]:  # 显示前8个
        real_rank = real_rank_map.get(brand, "-")
        sample_rank = sample_rank_map.get(brand, "-")

        if isinstance(real_rank, int) and isinstance(sample_rank, int):
            change = real_rank - sample_rank
            change_str = f"{'↑' if change > 0 else '↓' if change < 0 else '→'}{abs(change)}"
        else:
            change_str = "N/A"

        print(f"{brand:<8} {real_rank:<10} {sample_rank:<10} {change_str:<10}")

    # 5. 数据特点分析
    print("\n" + "-" * 70)
    print("5. 示例数据特点分析")
    print("-" * 70)
    print("""
  【示例数据的优势】
  [OK] 数据结构完整：包含品牌、车型、参数、销量、评分、城市分布
  [OK] 字段丰富：涵盖价格、动力、油耗、续航、评分等多维度
  [OK] 关联清晰：品牌-车型-参数-销量-评分形成完整数据链
  [OK] 可直接用于分析：无需清洗即可进行多维度分析

  【示例数据的局限】
  [FAIL] 数据量较小：仅56个车型，真实市场有数百款
  [FAIL] 销量规模偏小：示例总销量约632万，真实约3100万
  [FAIL] 新能源占比偏高：示例58.5%，真实约40.9%
  [FAIL] 部分品牌数据缺失：如特斯拉、丰田等在示例中销量偏低

  【改进建议】
  1. 接入真实API：使用懂车帝/汽车之家API获取真实数据
  2. 扩大样本量：增加到200+车型
  3. 调整比例：使新能源/燃油车比例更接近真实市场
  4. 定期更新：建立数据更新机制
""")


def generate_comparison_report():
    """生成对比报告"""
    report = """
# 数据对比分析报告

## 一、数据来源说明

### 真实数据来源
- 中汽协（中国汽车工业协会）官方发布的2024年度数据
- 乘联会（乘用车市场信息联席会）月度销量数据
- 懂车帝、汽车之家等平台公开的排行榜数据

### 示例数据说明
- 项目内置的模拟数据，用于演示数据分析流程
- 包含30个品牌、56个车型的完整数据
- 数据结构与真实数据一致，但规模较小

## 二、核心指标对比

| 指标 | 真实数据 | 示例数据 | 差异 |
|------|----------|----------|------|
| 年度总销量 | 3100万辆 | 632万辆 | 示例约为真实的20% |
| 新能源渗透率 | 40.9% | 58.5% | 示例偏高17.6% |
| 品牌数量 | 100+ | 30 | 示例覆盖主要品牌 |
| 车型数量 | 500+ | 56 | 示例覆盖热销车型 |

## 三、品牌销量对比（TOP 5）

| 品牌 | 真实销量 | 示例销量 | 比例 |
|------|----------|----------|------|
| 比亚迪 | 427万辆 | 74.6万辆 | 17.5% |
| 大众 | 200万辆 | 51.9万辆 | 26.0% |
| 丰田 | 170万辆 | 34.6万辆 | 20.4% |
| 吉利 | 160万辆 | 58.6万辆 | 36.6% |
| 奇瑞 | 180万辆 | - | 示例未包含 |

## 四、数据质量评估

### 结构完整性：*****
- 品牌-车型-参数-销量-评分-城市 完整数据链
- 支持多维度交叉分析
- 数据关系清晰，可直接用于BI工具

### 数据准确性：***☆☆
- 示例数据为模拟生成，非真实采集
- 销量数据规模偏小，但分布趋势合理
- 价格、参数等数据参考真实车型设定

### 分析可用性：*****
- 可完整演示数据分析流程
- 支持品牌、价格、能源、评分、城市等多维度分析
- 可导出Excel、Tableau、Power BI格式

## 五、结论

项目示例数据虽然规模较小，但**数据结构完整、分析流程清晰**，完全可以用于：

1. **简历项目展示** - 体现数据分析能力
2. **技术栈演示** - Python + Pandas + SQL + 可视化
3. **分析方法验证** - 多维度分析方法可直接应用于真实数据

如需用于实际业务分析，建议接入真实数据源（懂车帝API、中汽协数据等）。
"""

    with open("data/processed/data_comparison_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n[OK] 对比报告已保存: data/processed/data_comparison_report.md")


if __name__ == "__main__":
    compare_data()
    generate_comparison_report()
