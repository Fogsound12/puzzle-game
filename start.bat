@echo off
cd /d "%~dp0"
echo 正在启动拼图游戏服务器...
start /b pythonw server.py
timeout /t 3 >nul
start http://127.0.0.1:8080/index.html
exit
