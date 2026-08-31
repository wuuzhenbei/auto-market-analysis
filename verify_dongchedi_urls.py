"""
懂车帝URL参数验证脚本
用于验证URL参数的含义，确保数据正确
"""
import subprocess
import time


def run_browser_harness(script):
    """运行 browser-harness 脚本"""
    try:
        result = subprocess.run(
            ["browser-harness", "-c", script],
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8"
        )
        return result.stdout
    except Exception as e:
        print(f"  [!] 错误: {e}")
        return None


def verify_url(url, description):
    """验证URL并显示结果"""
    print(f"\n{'='*60}")
    print(f"验证: {description}")
    print(f"URL: {url}")
    print('='*60)

    script = f'''
new_tab("{url}")
wait_for_load()
time.sleep(3)

// 获取页面标题
title = document.title
print("标题: " + title)

// 获取页面内容
content = document.body.innerText
print("内容预览:")
print(content.substring(0, 2000))
'''
    result = run_browser_harness(script)
    if result:
        print(result)
    else:
        print("[!] 获取失败")

    print("\n" + "-"*60)
    input("按回车键继续下一个URL...")


def main():
    print("="*60)
    print("懂车帝URL参数验证工具")
    print("="*60)
    print("\n请根据显示的内容验证URL参数的含义")
    print("每次验证后，记录参数的实际含义\n")

    # 用户提供的URL示例
    urls_to_verify = [
        ("https://www.dongchedi.com/sales/sale-x-202606-x-x-x-x", "2026年6月销量"),
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-x-x", "2026年7月销量"),
        ("https://www.dongchedi.com/sales/sale-x-500-x-x-x-x", "近半年销量"),
        ("https://www.dongchedi.com/sales/sale-x-1000-x-x-x-x", "近一年销量"),
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-x-483", "2026年7月问界销量"),
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-x-2", "2026年7月奥迪销量"),
    ]

    # 测试车型类型参数
    print("\n[测试1] 车型类型参数")
    print("测试参数1的不同值，观察页面变化")
    type_tests = [
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-x-x", "全部"),
        ("https://www.dongchedi.com/sales/sale-1-202607-x-x-x-x", "参数1=1"),
        ("https://www.dongchedi.com/sales/sale-2-202607-x-x-x-x", "参数1=2"),
        ("https://www.dongchedi.com/sales/sale-3-202607-x-x-x-x", "参数1=3"),
        ("https://www.dongchedi.com/sales/sale-4-202607-x-x-x-x", "参数1=4"),
    ]

    for url, desc in type_tests:
        verify_url(url, desc)

    # 测试数据类型参数
    print("\n[测试2] 数据类型参数")
    print("测试参数3的不同值，观察页面变化")
    data_type_tests = [
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-x-x", "默认"),
        ("https://www.dongchedi.com/sales/sale-x-202607-1-x-x-x", "参数3=1"),
        ("https://www.dongchedi.com/sales/sale-x-202607-2-x-x-x", "参数3=2"),
    ]

    for url, desc in data_type_tests:
        verify_url(url, desc)

    # 测试厂商属性参数
    print("\n[测试3] 厂商属性参数")
    print("测试参数5的不同值，观察页面变化")
    property_tests = [
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-x-x", "默认"),
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-1-x", "参数5=1"),
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-2-x", "参数5=2"),
        ("https://www.dongchedi.com/sales/sale-x-202607-x-x-3-x", "参数5=3"),
    ]

    for url, desc in property_tests:
        verify_url(url, desc)

    print("\n" + "="*60)
    print("验证完成！")
    print("="*60)
    print("\n请根据验证结果更新 DONGCHEDI_URL_GUIDE.md 文件")
    print("记录每个参数的实际含义")


if __name__ == "__main__":
    main()
