# 如何从Edge获取懂车帝Cookie

## 步骤1：在Edge中打开懂车帝

1. 打开Edge浏览器
2. 访问 `https://www.dongchedi.com/sales`
3. 确认能看到销量数据

## 步骤2：打开开发者工具

1. 按 `F12` 键
2. 或者右键点击页面 -> 选择"检查"

## 步骤3：找到Cookie

1. 在开发者工具顶部，点击 `Application`（应用程序）标签
2. 在左侧栏找到 `Storage` -> `Cookies`
3. 点击 `https://www.dongchedi.com`

## 步骤4：复制Cookie

你会看到一个cookie列表，包含：
- `Name`：cookie名称
- `Value`：cookie值

**方法A：复制单个重要cookie**
找到以下关键cookie并复制其值：
- `sessionid`
- `ttwid`
- `passport_csrf_token`
- `sid_guard`

**方法B：复制所有cookie**
1. 点击表格上方的任意位置
2. 按 `Ctrl+A` 全选
3. 按 `Ctrl+C` 复制
4. 粘贴到文本编辑器中整理

**方法C：使用控制台获取**
1. 点击 `Console`（控制台）标签
2. 输入 `document.cookie` 并回车
3. 复制输出的内容

## 步骤5：使用Cookie

运行采集脚本：
```bash
python bypass_anti_crawler.py
```

然后粘贴你复制的cookie。

## 注意事项

1. Cookie有时效性，过期后需要重新获取
2. 不要分享你的cookie，包含登录信息
3. 如果cookie失效，重复上述步骤

## 快速获取方法

在Edge中打开懂车帝后，按F12打开控制台，输入：
```javascript
document.cookie
```
复制输出的字符串即可。
