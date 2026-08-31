@echo off
echo ========================================
echo   汽车市场数据分析 - 部署脚本
echo   域名: autocar.050311.xyz
echo ========================================
echo.

echo [1/4] 安装依赖...
cd /d "%~dp0"
pip install -r streamlit_app\requirements.txt

echo.
echo [2/4] 导入数据到数据库...
python import_csv_to_db.py

echo.
echo [3/4] 启动Streamlit应用...
start "Streamlit" cmd /c "streamlit run streamlit_app\app.py --server.port 8501 --server.address 0.0.0.0"

echo.
echo [4/4] 启动Cloudflare Tunnel...
echo 访问地址: https://autocar.050311.xyz
echo.
cloudflared tunnel --config "C:\Users\DELL\.cloudflared\config-autocar.yml" run lingxun

pause
