# 定时任务和数据校验

## 功能说明

### 定时任务

| 任务 | 执行时间 | 说明 |
|------|----------|------|
| 数据采集 | 每月1号 02:00 | 从懂车帝采集上月销量数据 |
| 数据校验 | 每天 03:00 | 检查数据完整性和准确性 |
| 数据导出 | 每月2号 04:00 | 导出Excel报告 |

### 数据校验

校验项目包括：
- ✅ 销量数据空值检查
- ✅ 销量负值检查
- ✅ 销量异常高值检查
- ✅ 月份数据完整性
- ✅ 价格数据合理性
- ✅ 能源类型有效性
- ✅ 品牌车型关联
- ✅ 数据新鲜度

## 使用方法

### 方法一：Windows任务计划程序（推荐）

```bash
# 一键设置定时任务
setup_task_scheduler.bat
```

### 方法二：Python调度器

```bash
# 启动调度器（持续运行）
start_scheduler.bat
```

### 方法三：手动执行

```bash
# 数据采集
python collect_limited_data.py

# 数据校验
python scheduler/data_validator.py

# 数据导出
python export/excel_exporter.py
```

## 配置说明

编辑 `config/scheduler_config.json`：

```json
{
  "collect_time": "02:00",    // 采集时间
  "validate_time": "03:00",   // 校验时间
  "export_time": "04:00",     // 导出时间
  "collect_day": 1,           // 每月几号采集
  "email_alert": true,        // 是否发送邮件告警
  "email_config": {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender": "your_email@qq.com",
    "password": "your_password",
    "receivers": ["receiver@example.com"]
  }
}
```

## 查看日志

```bash
# 查看调度器日志
type logs\scheduler.log

# 查看校验报告
dir reports\
```

## 管理定时任务

```bash
# 查看任务
schtasks /query /tn "AutoMarket_*"

# 手动运行任务
schtasks /run /tn "AutoMarket_CollectData"

# 删除任务
schtasks /delete /tn "AutoMarket_*" /f
```

## 校验报告示例

```json
{
  "timestamp": "2026-08-31T03:00:00",
  "has_errors": false,
  "has_warnings": false,
  "errors": [],
  "warnings": [],
  "summary": {
    "sales_count": 110,
    "total_sales": 1931056,
    "model_count": 55,
    "brand_count": 26,
    "rating_count": 50
  }
}
```
