# Start Backend Server
Write-Host "Starting Dual Empathy Robot Backend Server..." -ForegroundColor Green
Write-Host ""

# 切换到脚本目录
Set-Location -Path $PSScriptRoot

# 激活虚拟环境（如果存在）
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# 启动FastAPI服务器
Write-Host "Starting FastAPI server on http://0.0.0.0:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
