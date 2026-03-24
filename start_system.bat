@echo off
echo ==========================================
echo  二重共情ロボットシステム v2.0
echo  Dual Empathy Robot System
echo ==========================================
echo.

echo [1/3] バックエンドを起動中...
start "Backend Server" cmd /k "cd /d %~dp0robotA_demo && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (echo WARNING: Virtual environment not found!)) && python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/3] フロントエンドを起動中...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"

echo [3/3] システムを起動しています...
timeout /t 5 /nobreak >nul

echo.
echo ==========================================
echo  システムが起動しました！
echo ==========================================
echo.
echo  バックエンド: http://localhost:8000
echo  フロントエンド: http://localhost:3000
echo  API Docs: http://localhost:8000/docs
echo.
echo  ブラウザでフロントエンドを開いています...
echo.
echo  終了するには各ウィンドウでCtrl+Cを押してください
echo ==========================================

timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo システム起動完了！対話を楽しんでください！
pause
