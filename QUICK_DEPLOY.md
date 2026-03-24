# 🚀 Vercel 部署快速命令

## 📦 准备提交到 GitHub

```powershell
# Windows PowerShell
cd c:\Users\wangs\Desktop\robotA_demo_2
.\prepare_github.ps1
```

## 🔄 GitHub 操作

### 初次推送
```bash
# 1. 初始化（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit: Dual Empathy Robot System"

# 4. 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/dual-empathy-robot.git

# 5. 推送
git branch -M main
git push -u origin main
```

### 后续更新
```bash
# 查看修改
git status

# 添加修改
git add .

# 提交
git commit -m "Update: 描述你的修改"

# 推送（触发 Vercel 自动部署）
git push
```

## 🌐 Vercel 部署

### 通过 Web 界面
1. 访问 https://vercel.com
2. 登录/注册
3. 点击 "Add New Project"
4. 选择 GitHub 仓库
5. 配置：
   - Framework: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
6. 添加环境变量：
   ```
   GEMINI_API_KEY=你的密钥
   ```
7. 点击 Deploy

### 通过 CLI（可选）
```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel

# 部署到生产环境
vercel --prod
```

## 🔧 环境变量设置

### Vercel Dashboard
```
Settings → Environment Variables → Add New

必需变量：
- GEMINI_API_KEY: 你的 Gemini API 密钥
- PYTHON_VERSION: 3.11

可选变量：
- BACKEND_API: 独立后端地址（如果使用）
- NEXT_PUBLIC_API_URL: 前端访问的API地址
```

## 📝 常用 Git 命令

```bash
# 查看状态
git status

# 查看修改
git diff

# 查看历史
git log --oneline

# 创建分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 撤销修改
git checkout -- filename

# 查看远程仓库
git remote -v

# 拉取最新代码
git pull

# 克隆自己的仓库
git clone https://github.com/YOUR_USERNAME/dual-empathy-robot.git
```

## 🐛 问题排查

```bash
# 查看 Vercel 日志
vercel logs

# 实时日志
vercel logs --follow

# 查看部署列表
vercel ls

# 查看项目信息
vercel inspect

# 删除部署
vercel rm deployment-url
```

## 📊 部署状态检查

### 前端
```bash
# 访问健康检查
curl https://your-project.vercel.app/

# 应该返回 Next.js 页面
```

### API
```bash
# 测试 API 健康检查
curl https://your-project.vercel.app/api/health

# 预期响应
{
  "status": "ok",
  "service": "Dual Empathy Robot API",
  "version": "2.0.0"
}
```

## 🔄 自动部署流程

```
本地修改 
  ↓
git commit 
  ↓
git push 
  ↓
GitHub 更新 
  ↓
Vercel Webhook 触发 
  ↓
自动构建 
  ↓
自动部署 
  ↓
部署完成通知
```

## 📱 分支部署策略

| 分支 | 部署环境 | URL 格式 |
|------|---------|----------|
| `main` | Production | `your-project.vercel.app` |
| `dev` | Preview | `your-project-git-dev.vercel.app` |
| `feature/*` | Preview | `your-project-git-feature-*.vercel.app` |

## 🎯 One-Line 部署命令

```bash
# 一键提交并推送（触发自动部署）
git add . && git commit -m "Update" && git push

# 带描述的提交
git add . && git commit -m "feat: add new feature" && git push
```

## 📋 提交信息规范

```bash
# 功能
git commit -m "feat: 添加新功能"

# 修复
git commit -m "fix: 修复bug"

# 文档
git commit -m "docs: 更新文档"

# 样式
git commit -m "style: 改进UI"

# 重构
git commit -m "refactor: 代码重构"

# 测试
git commit -m "test: 添加测试"

# 构建
git commit -m "build: 更新依赖"
```

## 🔐 安全检查清单

- [ ] ✅ `.gitignore` 包含敏感文件
- [ ] ✅ 环境变量设置在 Vercel（不在代码中）
- [ ] ✅ API 密钥已删除（不提交到 Git）
- [ ] ✅ `.env` 文件被忽略
- [ ] ✅ 虚拟环境 `.venv` 被忽略
- [ ] ✅ `node_modules` 被忽略
- [ ] ✅ 日志和输出文件被忽略

## 🚨 紧急回滚

```bash
# 查看最近的部署
vercel ls

# 回滚到上一个版本
vercel rollback

# 或在 Vercel Dashboard
# Deployments → 选择旧版本 → Promote to Production
```

## 📖 更多资源

- 📘 [详细部署指南](DEPLOYMENT_VERCEL.md)
- 🌐 [Vercel 文档](https://vercel.com/docs)
- 🐙 [GitHub 文档](https://docs.github.com/)
- ⚡ [Next.js 部署](https://nextjs.org/docs/deployment)
