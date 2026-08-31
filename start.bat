@echo off
echo 启动Streamlit应用...
cd /d "%~dp0"
pip install -r streamlit_app\requirements.txt
streamlit run streamlit_app\app.py --server.port 8501 --server.address 0.0.0.0
pause
