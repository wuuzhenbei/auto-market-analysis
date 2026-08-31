"""
从Edge浏览器获取懂车帝cookie
"""
import subprocess
import json
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


def main():
    print("="*60)
    print("从Edge获取懂车帝Cookie")
    print("="*60)
    print("\n请先在Edge浏览器中：")
    print("1. 打开 https://www.dongchedi.com/sales")
    print("2. 确认能看到销量数据")
    print("3. 如果需要，先登录懂车帝账号\n")

    input("准备好了吗？按回车键继续...")

    print("\n[*] 正在获取cookie...")

    # 尝试通过CDP获取cookie
    script = '''
// 获取当前页面的cookie
cookies = document.cookie
print("COOKIES:" + cookies)
'''
    result = run_browser_harness(script)
    if result:
        print(result)

    # 尝试获取更详细的cookie信息
    script2 = '''
// 尝试通过CDP获取cookie
try {
    // 这可能需要不同的方法
    var allCookies = document.cookie
    print("ALL_COOKIES:" + allCookies)
} catch(e) {
    print("ERROR:" + e.message)
}
'''
    result2 = run_browser_harness(script2)
    if result2:
        print(result2)

    print("\n" + "="*60)
    print("请将上面显示的cookie复制下来")
    print("然后我们可以用它来访问懂车帝数据")
    print("="*60)


if __name__ == "__main__":
    main()
