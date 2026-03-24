# 🤖 双共情机器人系统 | Dual Empathy Robot System

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**情感共情 (AER) + 认知共情 (CER) = 完整的心智对话系统**

[📱 Live Demo](https://your-project.vercel.app) | [📖 文档](./DEPLOYMENT_VERCEL.md) | [🚀 快速开始](#-快速开始)

</div>

---

## ✨ 特性

### 🎭 双共情架构
- **💖 AER (Affective Empathy Robot)** - 情感共情机器人
  - 温暖倾听，情感共鸣
  - 识别用户情绪状态
  - 提供情感支持和陪伴
  
- **🧠 CER (Cognitive Empathy Robot)** - 认知共情机器人
  - 理性分析问题
  - 提供具体建议方案
  - 引导行动计划

### 🌏 多语言支持
- 🇯🇵 日本語 (Japanese)
- 🇨🇳 中文 (Chinese)
- 完整的文化适配和语言优化

### 🎨 精美界面
- 💬 微信风格对话界面
- 🎨 AER粉色 vs CER蓝色视觉区分
- 📱 响应式设计，支持多设备
- 🖱️ 右键复制对话内容

### 🔬 先进技术
- 🤖 Gemini 2.5 Pro 大语言模型
- 😊 ONNX WRIME-LUKE 情绪识别 (GPU加速)
- 📚 RAG 知识检索系统
- 🎯 9阶段完整对话流程

---

## 🏗️ 项目结构

```
dual-empathy-robot/
├── frontend/              # Next.js 前端
│   ├── app/              # Next.js 14 App Router
│   ├── components/       # React 组件
│   └── package.json      # 前端依赖
│
├── robotA_demo/          # Python 后端
│   ├── core/             # 核心模块
│   │   ├── agents/       # AER/CER 代理
│   │   ├── llm_gemini.py # LLM 接口
│   │   ├── emo_wrime_luke_onnx.py  # 情绪识别
│   │   └── rag_v2_retriever.py     # RAG 检索
│   ├── data/             # 知识库数据
│   ├── api_server.py     # FastAPI 服务器
│   └── gui_chat.py       # GUI 桌面应用
│
├── api/                  # Vercel Serverless Functions
├── vercel.json          # Vercel 配置
├── requirements.txt     # Python 依赖
└── .gitignore          # Git 忽略文件
```

---

## 🚀 快速开始

### 方式 1: 本地运行

#### 前提条件
- Python 3.11+
- Node.js 18+
- Gemini API 密钥

#### 后端启动
```bash
cd robotA_demo

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 创建 .env 文件，添加:
# GEMINI_API_KEY=你的密钥

# 启动API服务器
python -m uvicorn api_server:app --reload --port 8000

# 或启动GUI（Windows）
python gui_chat.py --lang zh
```

#### 前端启动
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

### 方式 2: 运行测试
```bash
cd robotA_demo

# 自主对话测试
python test_autonomous_dialogue.py --lang ja  # 日语
python test_autonomous_dialogue.py --lang zh  # 中文

# GUI 显示测试
python test_gui_display.py
```

---

## 🌐 部署到 Vercel

### 一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/dual-empathy-robot)

### 手动部署

```bash
# 1. 准备 Git 仓库
.\prepare_github.ps1

# 2. 创建 GitHub 仓库并推送
git remote add origin https://github.com/YOUR_USERNAME/dual-empathy-robot.git
git branch -M main
git push -u origin main

# 3. 在 Vercel 导入项目
# 访问: https://vercel.com/new
# 选择你的 GitHub 仓库

# 4. 配置环境变量
# GEMINI_API_KEY=你的密钥

# 5. 部署！
```

详细步骤: [DEPLOYMENT_VERCEL.md](./DEPLOYMENT_VERCEL.md)  
快速命令: [QUICK_DEPLOY.md](./QUICK_DEPLOY.md)

---

## 📊 测试结果

### 日语测试 (Japanese)
```
✅ 自然性得分: 100.0/100 ⭐⭐⭐⭐⭐
✅ 质量问题数: 0
✅ 9阶段完整流转
✅ RAG检索正常
```

### 中文测试 (Chinese)
```
✅ 自然性得分: 52.5/100
✅ 文化优化完成
✅ 实用建议风格
```

---

## 🎯 使用场景

### 学业咨询 (Academic)
- 考试焦虑
- 学习方法
- 时间管理

### 经济问题 (Financial)
- 学费负担
- 打工平衡
- 财务规划

### 人际关系 (Relationship)
- 交友困难
- 人际冲突
- 社交焦虑

### 未来规划 (Future)
- 职业选择
- 目标迷茫
- 就业准备

---

## 🔧 配置说明

### 环境变量

#### 开发环境 (`.env`)
```env
# Gemini API
GEMINI_API_KEY=你的Gemini_API密钥
GEMINI_MODEL=gemini-2.5-pro-no
GEMINI_BASE_URL=https://hiapi.online/v1

# 后端配置
PORT=8000
HOST=0.0.0.0

# 前端配置 (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 生产环境 (Vercel)
在 Vercel Dashboard → Settings → Environment Variables 添加:
- `GEMINI_API_KEY`
- `PYTHON_VERSION=3.11`
- `BACKEND_API` (可选，独立后端地址)

---

## 📖 文档

- [部署指南](./DEPLOYMENT_VERCEL.md) - Vercel 完整部署流程
- [快速命令](./QUICK_DEPLOY.md) - 常用部署命令
- [项目优化报告](./PROJECT_OPTIMIZATION_REPORT.md) - 最新改进说明
- [GUI 设计说明](./robotA_demo/show_gui_design.py) - 界面设计详解
- [快速开始](./QUICKSTART.md) - 本地开发指南
- [系统完整文档](./SYSTEM_COMPLETE.md) - 系统架构说明

---

## 🛠️ 技术栈

### 前端
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **状态管理**: React Hooks
- **HTTP 客户端**: Axios

### 后端
- **框架**: FastAPI
- **语言**: Python 3.11+
- **LLM**: Gemini 2.5 Pro (OpenAI兼容)
- **情绪识别**: ONNX Runtime + WRIME-LUKE
- **RAG**: 自定义文件检索系统

### 部署
- **前端托管**: Vercel
- **后端选项**: 
  - Vercel Serverless Functions
  - Railway.app (GPU 支持)
  - Google Cloud Run
- **CI/CD**: GitHub → Vercel 自动部署

---

## 🔄 自动部署

每次 push 到 GitHub，Vercel 自动：
1. ✅ 拉取最新代码
2. ✅ 安装依赖
3. ✅ 构建项目
4. ✅ 部署到生产环境
5. ✅ 发送通知

```bash
# 触发自动部署
git add .
git commit -m "Update: 你的修改说明"
git push
```

---

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Gemini API](https://ai.google.dev/) - 大语言模型
- [WRIME Dataset](https://github.com/ids-cv/wrime) - 日语情绪数据集
- [Vercel](https://vercel.com/) - 部署平台
- [Next.js](https://nextjs.org/) - React 框架
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web 框架

---

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/dual-empathy-robot/issues)
- **讨论**: [GitHub Discussions](https://github.com/YOUR_USERNAME/dual-empathy-robot/discussions)

---

## 🌟 Star History

如果这个项目对你有帮助，请给个 ⭐ Star！

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/dual-empathy-robot&type=Date)](https://star-history.com/#YOUR_USERNAME/dual-empathy-robot&Date)

---

<div align="center">

**用❤️和🧠构建**

Made with 💖 Affective Empathy and 🧠 Cognitive Empathy

</div>
