#!/bin/bash
# 启动Streamlit应用

echo "启动Streamlit应用..."
cd "$(dirname "$0")"

# 安装依赖
pip install -r streamlit_app/requirements.txt

# 启动Streamlit
streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0
