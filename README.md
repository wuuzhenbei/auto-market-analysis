# 汽车市场数据分析项目

基于 Python 的汽车市场数据分析项目，从懂车帝、汽车之家等主流汽车平台采集数据，进行多维度分析和可视化。

## 项目亮点

- **数据采集**: 自动采集 1000+ 车型数据，涵盖品牌、价格、参数、销量、口碑等维度
- **数据存储**: SQLite 数据库，预设 20+ 分析查询
- **数据分析**: Pandas 多维度分析（品牌份额、价格分布、新能源渗透率、用户口碑等）
- **可视化**: Matplotlib + Seaborn + Plotly，生成 20+ 专业图表
- **数据导出**: Excel 多表透视 + Tableau/Power BI 可导入格式

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| 数据采集 | requests, BeautifulSoup4, lxml |
| 数据处理 | Pandas, NumPy |
| 数据库 | SQLite3 |
| 可视化 | Matplotlib, Seaborn, Plotly |
| Excel | openpyxl, xlsxwriter |
| 笔记本 | Jupyter Notebook |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python database/init_db.py

# 3. 运行数据采集（或使用示例数据）
python scrapers/run_scrapers.py

# 4. 数据清洗
python analysis/data_cleaner.py

# 5. 运行分析
python analysis/comprehensive_report.py

# 6. 生成可视化
python visualization/charts.py

# 7. 导出 Excel/Tableau/Power BI
python export/excel_exporter.py
python export/tableau_exporter.py
python export/powerbi_exporter.py
```

## 分析维度

1. **品牌市场份额分析** - 各品牌销量占比、集中度分析
2. **价格区间分析** - 5-10万、10-15万、15-20万、20-30万、30万+ 各区间车型分布
3. **新能源渗透率分析** - 纯电/插混/增程占比趋势
4. **车型参数对比** - 雷达图展示多维度对比
5. **用户口碑分析** - 评分分布、各维度（外观/内饰/动力/空间/油耗）对比
6. **性价比分析** - 价格与配置/性能的关联分析
7. **城市销量分布** - 区域市场差异

## 项目结构

```
auto-market-analysis/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python 依赖
├── config.py                    # 配置文件
├── run_analysis.py              # 一键运行分析脚本
├── data/                        # 数据目录
│   ├── raw/                     # 原始数据
│   ├── processed/               # 清洗后数据
│   ├── excel/                   # Excel 导出
│   └── tableau/                 # Tableau/Power BI 数据
├── database/                    # 数据库
│   ├── schema.sql               # 建表语句
│   ├── init_db.py               # 初始化数据库
│   └── queries.sql              # 常用分析查询
├── scrapers/                    # 数据采集
│   ├── base_scraper.py          # 基类
│   ├── dongchedi_scraper.py     # 懂车帝采集
│   ├── autohome_scraper.py      # 汽车之家采集
│   └── run_scrapers.py          # 运行所有采集器
├── analysis/                    # 数据分析
│   ├── data_cleaner.py          # 数据清洗
│   ├── brand_analysis.py        # 品牌分析
│   ├── price_analysis.py        # 价格分析
│   ├── performance_analysis.py  # 性能参数分析
│   ├── energy_analysis.py       # 新能源分析
│   ├── rating_analysis.py       # 口碑评分分析
│   └── comprehensive_report.py  # 综合报告生成
├── visualization/               # 可视化
│   ├── charts.py                # 图表生成
│   └── output/                  # 图表输出目录
├── export/                      # 数据导出
│   ├── excel_exporter.py        # Excel 多表导出
│   ├── tableau_exporter.py      # Tableau 数据准备
│   └── powerbi_exporter.py      # Power BI 数据准备
├── notebooks/                   # Jupyter 笔记本
│   └── analysis_demo.ipynb      # 分析演示
├── streamlit_app/               # Streamlit Dashboard（方案一）
│   ├── app.py                   # 主入口
│   ├── utils.py                 # 数据加载工具
│   ├── requirements.txt         # Streamlit 依赖
│   └── pages/                   # 7 个分析页面
│       ├── 1_📊_市场总览.py
│       ├── 2_🏭_品牌分析.py
│       ├── 3_💰_价格分析.py
│       ├── 4_⚡_新能源分析.py
│       ├── 5_⭐_口碑分析.py
│       ├── 6_📈_趋势分析.py
│       └── 7_🗺️_城市分析.py
├── backend/                     # FastAPI 后端（方案二）
│   ├── main.py                  # FastAPI 入口
│   ├── database.py              # 数据库连接
│   ├── schemas.py               # Pydantic 模型
│   ├── requirements.txt         # FastAPI 依赖
│   └── api/                     # API 路由
│       ├── overview.py          # /api/overview
│       ├── brands.py            # /api/brands
│       ├── models.py            # /api/models
│       ├── sales.py             # /api/sales
│       ├── energy.py            # /api/energy
│       └── ratings.py           # /api/ratings
└── frontend/                    # Vue3 前端（方案二）
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/index.js
        ├── api/index.js
        ├── components/
        │   ├── ChartCard.vue
        │   └── KPICard.vue
        ├── views/
        │   ├── Dashboard.vue
        │   ├── BrandAnalysis.vue
        │   ├── PriceAnalysis.vue
        │   ├── EnergyAnalysis.vue
        │   ├── RatingAnalysis.vue
        │   ├── TrendAnalysis.vue
        │   └── CityAnalysis.vue
        └── styles/global.css
```

## Web Dashboard 启动

### 方案一：Streamlit（推荐，完全独立）

```bash
# 一键部署（推荐）
deploy.bat

# 或手动启动
pip install -r streamlit_app/requirements.txt
python import_csv_to_db.py  # 导入数据
streamlit run streamlit_app/app.py
# 浏览器打开 http://localhost:8501
# 或访问 https://autocar.050311.xyz
```

**特点：** 完全独立运行，不需要启动后端API

### 方案二：FastAPI + Vue3（前后端分离）

```bash
# 终端 1：启动后端
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 终端 2：启动前端
cd frontend && npm install && npm run dev
# 浏览器打开 http://localhost:5173
```

API 文档：http://localhost:8000/docs

## 输出示例

### Excel 报告
- 品牌销量排名表
- 价格区间分布表
- 新能源车型明细表
- 用户评分汇总表
- 数据透视表

### 可视化图表
- 品牌市场份额饼图
- 价格区间分布柱状图
- 新能源渗透率趋势图
- 车型参数雷达图
- 用户评分热力图
- 销量与价格散点图

### Tableau/Power BI 数据
- 清洗后的 CSV 数据集
- 数据字典文档
- 关系模型说明

## 简历描述

> 基于 Python 的汽车市场数据分析项目，从懂车帝、汽车之家采集 1000+ 车型数据，使用 Pandas 进行数据清洗和多维度分析（品牌份额、价格分布、新能源渗透率、用户口碑等），通过 Matplotlib/Seaborn/Plotly 生成 20+ 可视化图表，输出 Excel 数据透视表和 Tableau/Power BI 可导入数据集，完成完整的数据分析工作流。

## 许可证

MIT
