# 项目完整性检查脚本 - 二重共情ロボットシステム v2.0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  项目完整性检查" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = "c:\Users\wangs\Desktop\robotA_demo_2"
$backendDir = "$rootDir\robotA_demo"
$frontendDir = "$rootDir\frontend"

$allPassed = $true

# 检查函数
function Check-File {
    param($path, $description)
    if (Test-Path $path) {
        Write-Host "  ✓ $description" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  ✗ $description (缺失!)" -ForegroundColor Red
        $script:allPassed = $false
        return $false
    }
}

Write-Host "[1/6] 检查后端核心文件..." -ForegroundColor Yellow
Check-File "$backendDir\api_server.py" "FastAPI后端"
Check-File "$backendDir\requirements.txt" "Python依赖"
Check-File "$backendDir\core\config.py" "配置文件"
Check-File "$backendDir\core\topics.py" "Topic定义"
Check-File "$backendDir\core\session_manager.py" "Session管理"
Check-File "$backendDir\core\llm_gemini.py" "Gemini LLM"
Check-File "$backendDir\core\emo_wrime_luke_onnx.py" "情绪识别"
Check-File "$backendDir\core\rag_v2_retriever.py" "RAG V2检索器"

Write-Host ""
Write-Host "[2/6] 检查Agent文件..." -ForegroundColor Yellow
Check-File "$backendDir\core\agents\aer_agent.py" "AER Agent"
Check-File "$backendDir\core\agents\cer_agent.py" "CER Agent"

Write-Host ""
Write-Host "[3/6] 检查Prompt文件..." -ForegroundColor Yellow
Check-File "$backendDir\prompts\aer_system.txt" "AER系统提示词"
Check-File "$backendDir\prompts\cer_system.txt" "CER系统提示词"

Write-Host ""
Write-Host "[4/6] 检查RAG V2内容文件 (12个)..." -ForegroundColor Yellow
$ragFiles = @(
    "academic_follow_content.txt",
    "academic_study_pace.txt",
    "academic_exam_anxiety.txt",
    "future_unclear_goals.txt",
    "future_career_choice.txt",
    "future_preparation.txt",
    "financial_cost_burden.txt",
    "financial_work_study_balance.txt",
    "financial_financial_anxiety.txt",
    "relationship_making_friends.txt",
    "relationship_interaction_issues.txt",
    "relationship_no_confidant.txt"
)

$ragCount = 0
foreach ($file in $ragFiles) {
    if (Check-File "$backendDir\data\rag_v2\$file" $file) {
        $ragCount++
    }
}
Write-Host "  RAG文件: $ragCount/12" -ForegroundColor $(if ($ragCount -eq 12) { "Green" } else { "Red" })

Write-Host ""
Write-Host "[5/6] 检查前端文件..." -ForegroundColor Yellow
Check-File "$frontendDir\package.json" "package.json"
Check-File "$frontendDir\next.config.js" "Next.js配置"
Check-File "$frontendDir\app\page.tsx" "主页面"
Check-File "$frontendDir\app\layout.tsx" "布局"
Check-File "$frontendDir\app\globals.css" "全局样式"
Check-File "$frontendDir\vercel.json" "Vercel配置"
Check-File "$frontendDir\.env.local" "环境变量"

Write-Host ""
Write-Host "[6/6] 检查文档和启动脚本..." -ForegroundColor Yellow
Check-File "$rootDir\README.md" "主README"
Check-File "$rootDir\QUICKSTART.md" "快速启动指南"
Check-File "$rootDir\SYSTEM_COMPLETE.md" "系统完成报告"
Check-File "$rootDir\start_system.bat" "系统启动脚本"
Check-File "$backendDir\start_backend.bat" "后端启动脚本"
Check-File "$backendDir\DEPLOYMENT.md" "部署文档"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "  ✓ 所有检查通过! 项目完整!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "下一步:" -ForegroundColor Yellow
    Write-Host "  1. cd robotA_demo" -ForegroundColor White
    Write-Host "  2. python -m venv venv" -ForegroundColor White
    Write-Host "  3. .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  4. pip install -r requirements.txt" -ForegroundColor White
    Write-Host "  5. 编辑 core\config.py 设置Gemini API Key" -ForegroundColor White
    Write-Host "  6. cd ..\frontend" -ForegroundColor White
    Write-Host "  7. npm install" -ForegroundColor White
    Write-Host "  8. cd .." -ForegroundColor White
    Write-Host "  9. .\start_system.bat" -ForegroundColor White
} else {
    Write-Host "  ✗ 有文件缺失! 请检查!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
}
Write-Host ""
