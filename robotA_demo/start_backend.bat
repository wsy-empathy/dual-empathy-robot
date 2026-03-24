@echo off
echo Starting Dual Empathy Robot Backend Server...
echo.

cd /d %~dp0

REM 激活虚拟环境（如果存在）
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM 启动FastAPI服务器
echo Starting FastAPI server on http://0.0.0.0:8000
echo Press Ctrl+C to stop
echo.

python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

pause
