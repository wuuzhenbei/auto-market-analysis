"""
设置Cookie并获取懂车帝数据
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


def main():
    print("="*60)
    print("设置Cookie并获取懂车帝数据")
    print("="*60)

    # 用户提供的cookie
    cookie_string = "sessionid=89c9e11adaac684fe8b9abd6574fccda; ttwid=1%7ClRU4UZmLJA-TCXhiJba4_1Cr9xq34Qo-7PXL4U4zfpk%7C1788149510%7C9611342040e94077354043ceed764e4bac851f010dbecda53cb7cf87cc25ac0d; sid_guard=89c9e11adaac684fe8b9abd6574fccda%7C1788149539%7C5184002%7CFri%2C+30-Oct-2026+04%3A12%3A21+GMT; sid_tt=89c9e11adaac684fe8b9abd6574fccda; tt_webid=7680043508783646233"

    # 构建设置cookie的JavaScript代码
    js_code = f'''
var cookieStr = "{cookie_string}";
var cookies = cookieStr.split("; ");
for (var i = 0; i < cookies.length; i++) {{
    document.cookie = cookies[i] + "; path=/; domain=.dongchedi.com";
}}
print("Cookie已设置");

new_tab("https://www.dongchedi.com/sales");
wait_for_load();
await new Promise(r => setTimeout(r, 5000));

var content = document.body.innerText;
print(content.substring(0, 3000));
'''

    print("\n[*] 正在设置cookie并访问懂车帝...")
    result = run_browser_harness(js_code)
    if result:
        print(result)
    else:
        print("[!] 获取失败")


if __name__ == "__main__":
    main()
