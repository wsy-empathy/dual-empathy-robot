# 🚀 Vercel 部署指南

## 📋 部署架构说明

本项目采用 **混合部署架构**：

### 方案 A：前端 + Serverless API（推荐用于演示）
- ✅ **前端**: Next.js 部署到 Vercel
- ✅ **API**: Python Serverless Functions（简化版）
- ⚠️ **限制**: 
  - 无GPU支持（情绪识别使用CPU）
  - 函数执行时间限制10秒
  - 模型文件大小限制50MB

### 方案 B：前端 + 独立后端（推荐用于生产）
- ✅ **前端**: Next.js 部署到 Vercel
- ✅ **后端**: Python FastAPI 部署到其他服务
  - Railway.app（支持GPU）
  - Render.com
  - Google Cloud Run
  - AWS Lambda + API Gateway

---

## 🎯 方案 A：Vercel 完整部署

### 步骤 1: 准备 GitHub 仓库

```bash
# 初始化 Git 仓库
cd c:\Users\wangs\Desktop\robotA_demo_2
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Dual Empathy Robot System"

# 创建 GitHub 仓库（在 GitHub 网站上）
# 然后关联远程仓库
git remote add origin https://github.com/YOUR_USERNAME/dual-empathy-robot.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤 2: 连接 Vercel

1. **访问 Vercel**: https://vercel.com
2. **登录/注册**: 使用 GitHub 账号
3. **导入项目**:
   - 点击 "Add New Project"
   - 选择 "Import Git Repository"
   - 选择你的 `dual-empathy-robot` 仓库

### 步骤 3: 配置 Vercel 项目

#### 3.1 项目设置
```
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

#### 3.2 环境变量设置
在 Vercel Dashboard → Settings → Environment Variables 添加：

```env
# 必需
GEMINI_API_KEY=你的Gemini_API密钥

# 可选（如果使用独立后端）
BACKEND_API=https://your-backend-api.com
NEXT_PUBLIC_API_URL=https://your-backend-api.com

# Python版本
PYTHON_VERSION=3.11
```

### 步骤 4: 部署

点击 **Deploy** 按钮，Vercel 会自动：
1. ✅ 安装依赖
2. ✅ 构建 Next.js 前端
3. ✅ 构建 Python Serverless Functions
4. ✅ 部署到全球 CDN

部署完成后，你会得到一个 URL：
```
https://dual-empathy-robot.vercel.app
```

---

## 🎯 方案 B：前端 Vercel + 后端 Railway

### Railway 后端部署

#### 步骤 1: 准备后端部署文件

在 `robotA_demo/` 目录创建 `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api_server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### 步骤 2: 部署到 Railway

1. 访问 https://railway.app
2. 登录并创建新项目
3. 连接 GitHub 仓库
4. 选择 `robotA_demo` 目录
5. 添加环境变量：
   ```env
   GEMINI_API_KEY=你的密钥
   PORT=8000
   ```
6. 部署

#### 步骤 3: 配置 Vercel 连接后端

在 Vercel 环境变量中添加：
```env
BACKEND_API=https://your-app.railway.app
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

---

## 🔄 自动部署工作流

### GitHub → Vercel 自动部署

配置完成后，每次 push 代码：

```bash
# 修改代码后
git add .
git commit -m "Update: 描述你的修改"
git push

# Vercel 自动触发部署
# - 主分支 (main) → 生产环境
# - 其他分支 → 预览环境
```

**自动化流程**:
1. 🔍 GitHub 检测到 push
2. 🔔 触发 Vercel Webhook
3. 🏗️ Vercel 自动构建
4. ✅ 部署到生产环境
5. 📧 发送部署通知

---

## 📝 重要配置文件说明

### 1. `vercel.json` (根目录)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    }
  ]
}
```

### 2. `requirements.txt`
列出 Python 依赖（Serverless Functions 需要）

### 3. `.gitignore`
排除不需要提交的文件

---

## ⚙️ 环境变量管理

### Vercel Dashboard 设置

1. 进入项目 Settings → Environment Variables
2. 添加以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `GEMINI_API_KEY` | Gemini API密钥 | `AIza...` |
| `BACKEND_API` | 后端API地址（可选） | `https://api.example.com` |
| `PYTHON_VERSION` | Python版本 | `3.11` |

### 环境切换

- **Production**: 主分支 (main)
- **Preview**: 其他分支
- **Development**: 本地开发

---

## 🔍 部署后验证

### 1. 前端访问测试
```bash
# 访问你的 Vercel URL
https://your-project.vercel.app

# 检查页面是否正常显示
```

### 2. API 健康检查
```bash
# 测试 Serverless API
curl https://your-project.vercel.app/api/health

# 预期响应
{
  "status": "ok",
  "service": "Dual Empathy Robot API",
  "version": "2.0.0"
}
```

### 3. 功能测试
1. ✅ 话题选择
2. ✅ 对话流程
3. ✅ AER/CER 切换
4. ✅ 情绪识别

---

## 🐛 常见问题

### 1. 部署失败：依赖安装错误
**解决方案**: 检查 `requirements.txt` 和 `package.json`

### 2. API 响应超时
**原因**: Vercel Serverless 函数有10秒限制
**解决方案**: 使用独立后端 (Railway/Render)

### 3. 模型文件过大
**原因**: Vercel 函数大小限制50MB
**解决方案**: 
- 使用外部存储（S3/CDN）
- 使用更小的模型
- 部署到支持大文件的平台

### 4. GPU 不可用
**原因**: Vercel Serverless 不支持GPU
**解决方案**: 
- 使用CPU版ONNX Runtime
- 部署后端到支持GPU的平台

---

## 📊 性能优化

### 1. 前端优化
```javascript
// next.config.js
module.exports = {
  // 启用图片优化
  images: {
    domains: ['your-cdn.com'],
  },
  // 压缩
  compress: true,
  // 缓存
  headers: async () => [
    {
      source: '/api/:path*',
      headers: [
        { key: 'Cache-Control', value: 'public, max-age=60' }
      ],
    },
  ],
}
```

### 2. API 优化
- 使用边缘函数（Edge Functions）
- 启用响应缓存
- 使用 CDN 缓存静态资源

---

## 🔐 安全最佳实践

### 1. 环境变量
✅ 所有 API 密钥存储在 Vercel 环境变量
❌ 不要硬编码在代码中
❌ 不要提交到 Git

### 2. CORS 配置
```python
# api_server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-project.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 速率限制
考虑添加 API 速率限制防止滥用

---

## 📈 监控和日志

### Vercel Analytics
1. 进入 Dashboard → Analytics
2. 查看：
   - 访问量
   - 响应时间
   - 错误率

### 日志查看
```bash
# Vercel CLI
vercel logs <deployment-url>

# 实时日志
vercel logs --follow
```

---

## 🎓 推荐学习资源

- [Vercel 官方文档](https://vercel.com/docs)
- [Next.js 部署指南](https://nextjs.org/docs/deployment)
- [Serverless Functions](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Railway 部署教程](https://docs.railway.app/)

---

## 📞联系和支持

遇到问题？
1. 查看 Vercel 部署日志
2. 检查环境变量配置
3. 确认 API 端点可访问
4. 查看浏览器控制台错误

---

## 🎉 完成！

部署成功后，你的系统将：
- ✅ 自动化部署（每次 push 更新）
- ✅ 全球 CDN 加速
- ✅ HTTPS 安全连接
- ✅ 自动扩展
- ✅ 零停机部署

**项目 URL**: `https://your-project.vercel.app`

享受你的双共情机器人系统吧！🤖💖🧠
