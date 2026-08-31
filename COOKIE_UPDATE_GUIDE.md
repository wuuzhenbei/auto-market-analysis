# Cookie更新指南

## 为什么需要更新Cookie？

懂车帝的Cookie有时效性，过期后需要重新获取。当脚本显示"需要登录"或"验证码"时，说明Cookie已失效。

## 更新步骤

### 步骤1：在Edge中登录懂车帝

1. 打开Edge浏览器
2. 访问 `https://www.dongchedi.com`
3. 登录你的账号

### 步骤2：获取Cookie

1. 按 `F12` 打开开发者工具
2. 点击 **应用程序** 标签
3. 在左侧找到 **存储** -> **Cookie** -> `https://www.dongchedi.com`
4. 复制所有Cookie

### 步骤3：更新脚本

打开 `dongchedi_final_scraper.py`，找到以下行：

```python
COOKIE = 'session_tlb_tag=...你的旧cookie...'
```

替换为新的Cookie值。

### 步骤4：测试

运行脚本测试：
```bash
python dongchedi_final_scraper.py
```

## Cookie有效期

- 通常有效期：1-3个月
- 如果频繁使用，可能需要更频繁更新

## 常见问题

### Q: 显示"需要登录"怎么办？
A: Cookie已失效，需要重新获取。

### Q: 显示"验证码"怎么办？
A: 可能是访问太频繁，等待一段时间后重试，或更新Cookie。

### Q: 显示"暂无车系"怎么办？
A: 可能是Cookie不完整，确保复制了所有Cookie。

## 快速获取Cookie方法

在Edge控制台（F12 -> 控制台）输入：
```javascript
document.cookie
```
复制输出的内容。

注意：如果输出为空，说明Cookie设置了HttpOnly，需要通过"应用程序"标签获取。
