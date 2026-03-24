Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " 二重共情ロボットシステム v2.0" -ForegroundColor Green
Write-Host " Dual Empathy Robot System" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = $PSScriptRoot

Write-Host "[1/3] バックエンドを起動中..." -ForegroundColor Yellow
$backendPath = Join-Path $rootDir "robotA_demo"
$backendCmd = "Set-Location '$backendPath'; if (Test-Path 'venv\Scripts\Activate.ps1') { & '.\venv\Scripts\Activate.ps1' } else { Write-Host 'WARNING: Virtual environment not found!' -ForegroundColor Red }; python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 3

Write-Host "[2/3] フロントエンドを起動中..." -ForegroundColor Yellow
$frontendPath = Join-Path $rootDir "frontend"
$frontendCmd = "Set-Location '$frontendPath'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "[3/3] システムを起動しています..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " システムが起動しました！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " バックエンド: http://localhost:8000" -ForegroundColor White
Write-Host " フロントエンド: http://localhost:3000" -ForegroundColor White
Write-Host " API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host " ブラウザでフロントエンドを開いています..." -ForegroundColor Yellow
Write-Host ""
Write-Host " 終了するには各PowerShellウィンドウでCtrl+Cを押してください" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Cyan

Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "システム起動完了！対話を楽しんでください！" -ForegroundColor Green
Write-Host ""
Read-Host "Enterキーで終了..."
