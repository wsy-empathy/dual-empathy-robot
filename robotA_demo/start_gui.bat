@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 双共情机器人 GUI 启动
echo Dual Empathy Robot GUI Launcher
echo ========================================
echo.
echo 选择语言 / Select Language:
echo 1. 日本語 (Japanese)
echo 2. 中文 (Chinese)
echo.
set /p choice="请输入选项 / Enter choice (1-2): "

if "%choice%"=="1" (
    echo.
    echo 启动日语界面...
    python gui_chat.py --lang ja
) else if "%choice%"=="2" (
    echo.
    echo 启动中文界面...
    python gui_chat.py --lang zh
) else (
    echo.
    echo 无效选择，默认使用日语
    python gui_chat.py --lang ja
)

pause
