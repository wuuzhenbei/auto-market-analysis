# 懂车帝数据采集器使用说明

## 问题背景

原有的 `fetch_dongchedi_data.py` 和 `fetch_real_data.py` 脚本存在解析问题，无法正确提取懂车帝销量数据。

## 解决方案

创建了新的采集脚本 `dongchedi_working.py`，修复了以下问题：

1. **解析逻辑修复**：正确处理懂车帝页面的HTML结构
2. **空行处理**：跳过数据之间的空行
3. **品牌分离**：从"车型名品牌/类型"格式中正确提取车型名和品牌
4. **数据验证**：只保存有效的销量数据（1000-999999辆）

## 使用方法

### 前置条件

1. 安装 browser-harness：
   ```bash
   pip install browser-harness
   ```

2. 确保 Chrome 浏览器正在运行

### 运行采集

```bash
python dongchedi_working.py
```

### 输出文件

数据保存在 `data/raw/dongchedi/` 目录下：

- `sales_2026_07.csv` - 2026年7月数据
- `sales_2026_05.csv` - 2026年5月数据
- ...
- `all_sales_data.csv` - 所有数据汇总

### CSV 字段说明

| 字段 | 说明 |
|------|------|
| year | 年份 |
| month | 月份 |
| rank | 排名 |
| model | 车型名称 |
| brand | 品牌 |
| body_type | 车身类型（轿车/SUV/MPV等）|
| price_min | 最低价格（万元）|
| price_max | 最高价格（万元）|
| sales | 销量（辆）|

## 自定义采集

修改 `dongchedi_working.py` 中的 `tasks` 列表来采集不同年份和月份：

```python
tasks = [
    (2024, [1, 3, 6, 9, 12]),  # 2024年关键月份
    (2025, [1, 3, 6, 9, 12]),  # 2025年关键月份
    (2026, [1, 3, 5, 7])       # 2026年
]
```

## 注意事项

1. 每次请求间隔2秒，避免被反爬
2. 每个月份最多获取前20名车型
3. 数据源于懂车帝公开页面，仅供参考

## 相关文件

- `dongchedi_working.py` - 主采集脚本
- `dongchedi_login_scraper.py` - 登录版本（备用）
- `dongchedi_cdp_scraper.py` - CDP版本（备用）
- `fetch_dongchedi_data.py` - 原始脚本（有问题）
- `fetch_real_data.py` - 原始脚本（有问题）
