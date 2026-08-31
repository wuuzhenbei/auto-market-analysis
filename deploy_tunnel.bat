@echo off
echo ========================================
echo 部署到Cloudflare Tunnel
echo 域名: autocar.050311.xyz
echo ========================================

echo.
echo 步骤1: 启动Streamlit应用（请在另一个窗口运行 start.bat）
echo.
echo 步骤2: 启动Cloudflare Tunnel
echo.

cloudflared tunnel --url http://localhost:8501

pause
