@echo off
echo ========================================
echo   启动定时调度器
echo   按 Ctrl+C 停止
echo ========================================
echo.

cd /d "%~dp0"
python scheduler\auto_scheduler.py

pause
