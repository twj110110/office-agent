@echo off
chcp 65001 >nul
echo ============================================
echo Office Agent - GitHub 自动推送工具
echo ============================================
cd /d "%~dp0"
"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" auto_push.py
pause
