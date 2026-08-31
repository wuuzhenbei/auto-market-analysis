@echo off
echo ========================================
echo   设置Windows定时任务
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 创建数据采集定时任务（每月1号凌晨2点）...
schtasks /create /tn "AutoMarket_CollectData" /tr "python \"%~dp0collect_limited_data.py\"" /sc monthly /d 1 /st 02:00 /f
if %errorlevel% equ 0 (
    echo     ✅ 创建成功
) else (
    echo     ❌ 创建失败
)

echo.
echo [2/3] 创建数据校验定时任务（每天凌晨3点）...
schtasks /create /tn "AutoMarket_ValidateData" /tr "python \"%~dp0scheduler\data_validator.py\"" /sc daily /st 03:00 /f
if %errorlevel% equ 0 (
    echo     ✅ 创建成功
) else (
    echo     ❌ 创建失败
)

echo.
echo [3/3] 创建数据导出定时任务（每月2号凌晨4点）...
schtasks /create /tn "AutoMarket_ExportData" /tr "python \"%~dp0export\excel_exporter.py\"" /sc monthly /d 2 /st 04:00 /f
if %errorlevel% equ 0 (
    echo     ✅ 创建成功
) else (
    echo     ❌ 创建失败
)

echo.
echo ========================================
echo   定时任务设置完成！
echo ========================================
echo.
echo 查看任务：schtasks /query /tn "AutoMarket_*"
echo 删除任务：schtasks /delete /tn "AutoMarket_*" /f
echo.
pause
