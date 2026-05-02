@echo off
chcp 65001 >nul
title Office Agent GitHub推送工具
cd /d "%~dp0"
echo.
echo ============================================
echo    Office Agent - GitHub推送工具
echo ============================================
echo.
echo 正在检查Python环境...
"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请确保已安装Python 3.12
    pause
    exit /b 1
)

echo [OK] Python环境正常
echo.
echo 开始推送代码到GitHub...
echo.
"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" push_to_github.py
echo.
pause
