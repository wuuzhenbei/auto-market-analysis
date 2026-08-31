# 获取懂车帝Cookie的其他方法

## 方法1：通过Application标签获取（推荐）

1. 在Edge中打开 `https://www.dongchedi.com/sales`
2. 按 `F12` 打开开发者工具
3. 点击顶部的 **Application**（应用程序）标签
4. 在左侧栏展开 **Storage** -> **Cookies**
5. 点击 `https://www.dongchedi.com`
6. 你会看到一个表格，包含所有cookie

**复制方法：**
- 点击表格中的任意一行
- 按 `Ctrl+A` 全选
- 按 `Ctrl+C` 复制
- 粘贴到记事本中

## 方法2：通过Network标签获取

1. 在Edge中打开 `https://www.dongchedi.com/sales`
2. 按 `F12` 打开开发者工具
3. 点击顶部的 **Network**（网络）标签
4. 刷新页面（按F5）
5. 点击列表中的第一个请求（通常是 `sales` 或 `sale-x-...`）
6. 在右侧找到 **Request Headers** -> **Cookie**
7. 复制Cookie的值

## 方法3：直接在地址栏输入

在Edge地址栏输入以下内容并回车：
```
javascript:alert(document.cookie)
```
注意：可能需要手动输入，不能直接复制粘贴

## 方法4：使用浏览器扩展

安装Cookie编辑器扩展，如：
- EditThisCookie
- Cookie Editor

## 我需要的Cookie格式

Cookie应该是一长串类似这样的文本：
```
ttwid=xxx; sessionid=xxx; passport_csrf_token=xxx; ...
```

请复制整行内容给我。
