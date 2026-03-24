# 清理旧文件脚本 - 二重共情ロボットシステム v2.0
# 删除旧Gradio系统的残余文件

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  清理旧文件 - Dual Empathy Robot v2.0" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = "c:\Users\wangs\Desktop\robotA_demo_2\robotA_demo"
Set-Location $rootDir

Write-Host "[1/5] 删除旧Gradio UI文件..." -ForegroundColor Yellow

# 旧Gradio应用
$filesToDelete = @(
    "app_gradio_parallel_v2.py",
    ".gradio"
)

foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ 删除: $file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[2/5] 删除旧的测试和检查脚本..." -ForegroundColor Yellow

$oldScripts = @(
    "test_cpu_full.py",
    "test_system_integrity.py",
    "test_rag_topics.py",
    "test_quick.py",
    "test_text_only.py",
    "check_cpu_status.py",
    "check_defender.ps1",
    "check_defender_status.ps1",
    "check_returns.py",
    "check_system.py",
    "fix_guide.py",
    "fix_security.bat",
    "fix_windows_security.ps1"
)

foreach ($script in $oldScripts) {
    if (Test-Path $script) {
        Remove-Item -Path $script -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ 删除: $script" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[3/5] 删除旧的启动脚本..." -ForegroundColor Yellow

$oldStartScripts = @(
    "run_windows.bat",
    "run_windows.ps1",
    "quick_start.bat",
    "start.ps1",
    "start_app.bat",
    "start_app.ps1",
    "start_cpu.bat",
    "install_gpu.bat",
    "install_gpu.ps1",
    "setup_https.md",
    "QUICKSTART.md"
)

foreach ($script in $oldStartScripts) {
    if (Test-Path $script) {
        Remove-Item -Path $script -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ 删除: $script" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[4/5] 删除旧的core文件..." -ForegroundColor Yellow

$oldCoreFiles = @(
    "core\asr.py",
    "core\tts_edge.py",
    "core\rag_onnx.py",
    "core\agents\robot_a.py",
    "core\agents\robot_b.py",
    "core\agents\intent_detector.py"
)

foreach ($file in $oldCoreFiles) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ 删除: $file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[5/5] 删除旧的RAG数据..." -ForegroundColor Yellow

if (Test-Path "data\rag_corpus") {
    Remove-Item -Path "data\rag_corpus" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ 删除: data\rag_corpus" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  清理完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "保留的新系统文件:" -ForegroundColor White
Write-Host "  ✓ api_server.py (FastAPI后端)" -ForegroundColor Green
Write-Host "  ✓ core/agents/aer_agent.py" -ForegroundColor Green
Write-Host "  ✓ core/agents/cer_agent.py" -ForegroundColor Green
Write-Host "  ✓ core/rag_v2_retriever.py" -ForegroundColor Green
Write-Host "  ✓ data/rag_v2/ (12个RAG文件)" -ForegroundColor Green
Write-Host "  ✓ start_backend.bat/ps1" -ForegroundColor Green
Write-Host ""
Write-Host "下一步: 运行 check_project.ps1 检查完整性" -ForegroundColor Yellow
Write-Host ""
