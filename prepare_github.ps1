# 准备 GitHub 提交的脚本

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "GitHub 提交准备脚本" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已初始化 Git
if (-not (Test-Path ".git")) {
    Write-Host "[1/6] 初始化 Git 仓库..." -ForegroundColor Yellow
    git init
    Write-Host "成功：Git 仓库初始化完成" -ForegroundColor Green
}
else {
    Write-Host "[1/6] Git 仓库已存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/6] 检查 .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    Write-Host "成功：.gitignore 已存在" -ForegroundColor Green
}
else {
    Write-Host "警告：请先创建 .gitignore 文件" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/6] 显示将要提交的文件..." -ForegroundColor Yellow
git add -n .
Write-Host ""

$confirm = Read-Host "是否继续添加这些文件? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "已取消" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "[4/6] 添加文件到 Git..." -ForegroundColor Yellow
git add .
Write-Host "成功：文件已添加" -ForegroundColor Green

Write-Host ""
Write-Host "[5/6] 提交到本地仓库..." -ForegroundColor Yellow
$commitMessage = Read-Host "输入提交消息 (默认: Initial commit)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Initial commit: Dual Empathy Robot System"
}

git commit -m "$commitMessage"
Write-Host "成功：提交完成" -ForegroundColor Green

Write-Host ""
Write-Host "[6/6] 下一步操作提示" -ForegroundColor Yellow
Write-Host ""
Write-Host "接下来需要手动操作：" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 在 GitHub 上创建新仓库" -ForegroundColor White
Write-Host "   访问: https://github.com/new" -ForegroundColor Gray
Write-Host "   仓库名建议: dual-empathy-robot" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 关联远程仓库" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/dual-empathy-robot.git" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 推送到 GitHub" -ForegroundColor White
Write-Host "   git branch -M main" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 部署到 Vercel" -ForegroundColor White
Write-Host "   访问: https://vercel.com" -ForegroundColor Gray
Write-Host "   点击 'Add New Project' 然后导入你的 GitHub 仓库" -ForegroundColor Gray
Write-Host ""
Write-Host "详细步骤请查看: DEPLOYMENT_VERCEL.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "准备完成!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
