# 🎓 Vercel 部署教程 - 手把手教学版

## 📚 目录
1. [准备工作](#准备工作)
2. [第一步：提交代码到GitHub](#第一步提交代码到github)
3. [第二步：部署到Vercel](#第二步部署到vercel)
4. [第三步：配置环境变量](#第三步配置环境变量)
5. [第四步：测试访问](#第四步测试访问)

---

## 准备工作

### ✅ 需要准备的账号
1. **GitHub账号** - 代码托管平台
   - 如果没有：访问 https://github.com/signup 注册
   - 记住你的用户名（后面会用到）

2. **Vercel账号** - 部署平台
   - 如果没有：访问 https://vercel.com 
   - 点击 "Sign Up"，用GitHub账号登录（推荐）
   - 这样Vercel可以直接访问你的GitHub仓库

3. **Gemini API密钥**
   - 你应该已经有了（项目正在使用的那个）
   - 如果忘了在哪，检查 `.env` 文件

### ✅ 需要安装的工具
- ✅ Git（通常Windows已安装）
- ✅ PowerShell（Windows自带）

---

## 第一步：提交代码到GitHub

### 1.1 打开PowerShell
```powershell
# 按 Win + X，选择 "Windows PowerShell"
# 或者在VS Code里用终端
```

### 1.2 进入项目目录
```powershell
cd c:\Users\wangs\Desktop\robotA_demo_2
```

### 1.3 初始化Git仓库
```powershell
# 运行这个命令
git init

# 你应该看到：
# Initialized empty Git repository in C:/Users/wangs/Desktop/robotA_demo_2/.git/
```

### 1.4 添加所有文件
```powershell
# 运行这个命令
git add .

# 这会添加所有文件，.gitignore会自动排除不需要的
```

### 1.5 提交到本地
```powershell
# 运行这个命令
git commit -m "Initial commit: Dual Empathy Robot System"

# 你应该看到很多文件被提交的信息
```

### 1.6 在GitHub创建仓库

**📱 打开浏览器操作：**

1. 访问：https://github.com/new
2. 填写信息：
   - Repository name: `dual-empathy-robot`（或你喜欢的名字）
   - Description: `双共情机器人系统 - AER + CER`
   - 选择 **Public**（公开）或 **Private**（私有）
   - ⚠️ **不要**勾选任何初始化选项（README、.gitignore等）
3. 点击 **Create repository**

**📋 创建成功后，GitHub会显示一些命令，保持页面打开**

### 1.7 连接GitHub仓库
```powershell
# 复制GitHub页面上的命令，类似这样：
# 把 YOUR_USERNAME 替换成你的GitHub用户名

git remote add origin https://github.com/YOUR_USERNAME/dual-empathy-robot.git

# 例如，如果你的用户名是 wangs123：
# git remote add origin https://github.com/wangs123/dual-empathy-robot.git
```

### 1.8 推送到GitHub
```powershell
# 设置主分支名称
git branch -M main

# 推送代码
git push -u origin main

# 第一次推送可能需要登录GitHub
# 按提示登录即可
```

**✅ 完成标志：**
- 刷新GitHub页面，你应该能看到所有代码已经上传
- 可以看到文件列表、README.md等

---

## 第二步：部署到Vercel

### 2.1 登录Vercel
1. 访问：https://vercel.com
2. 点击右上角 **Log In** 或 **Sign Up**
3. 选择 **Continue with GitHub**
4. 授权Vercel访问你的GitHub账号

### 2.2 导入项目

**📱 在Vercel Dashboard操作：**

1. 点击 **Add New...** → **Project**
2. 在 "Import Git Repository" 列表中找到你的仓库：
   - 仓库名：`dual-empathy-robot`
   - 如果看不到，点击 "Adjust GitHub App Permissions"
3. 点击仓库右边的 **Import** 按钮

### 2.3 配置项目设置

**在 "Configure Project" 页面：**

#### Framework Preset（框架预设）
- 选择：**Next.js**
- Vercel应该会自动识别

#### Root Directory（根目录）
- ⚠️ 重要：点击 **Edit**
- 输入：`frontend`
- 点击 **Continue**

#### Build and Output Settings（构建设置）
通常保持默认即可：
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

**🚫 暂时不要点击 Deploy！先配置环境变量**

---

## 第三步：配置环境变量

### 3.1 添加环境变量

**还在 "Configure Project" 页面：**

1. 向下滚动找到 **Environment Variables**（环境变量）
2. 点击展开

#### 添加第一个变量：
- **Name**: `GEMINI_API_KEY`
- **Value**: `你的Gemini API密钥`
  ```
  从你的 .env 文件复制，或者：
  AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX （你的完整密钥）
  ```
- **Environment**: 全部勾选（Production, Preview, Development）
- 点击 **Add**

#### 添加第二个变量（可选）：
- **Name**: `PYTHON_VERSION`
- **Value**: `3.11`
- **Environment**: 全部勾选
- 点击 **Add**

### 3.2 开始部署

**✅ 确认检查清单：**
- [ ] Framework: Next.js
- [ ] Root Directory: frontend
- [ ] 环境变量：GEMINI_API_KEY 已添加

**🚀 点击 Deploy 按钮！**

### 3.3 等待部署

**部署过程（约2-3分钟）：**

你会看到实时日志：
```
▲ Vercel CLI 28.4.8
○ Installing dependencies...
○ Building...
○ Uploading...
✓ Deployment complete!
```

**📊 部署状态：**
- 🟡 Building... （构建中）
- 🟢 Ready （完成）
- 🔴 Error （出错了，查看日志）

---

## 第四步：测试访问

### 4.1 获取部署URL

**部署成功后：**

1. Vercel会显示：**Congratulations! 🎉**
2. 你会看到三个按钮：
   - **Visit** - 访问网站
   - **Dashboard** - 查看仪表板
3. 你的网站URL类似：
   ```
   https://dual-empathy-robot.vercel.app
   或
   https://dual-empathy-robot-你的用户名.vercel.app
   ```

### 4.2 测试网站

**点击 Visit 或直接访问URL：**

✅ **成功标志：**
- 看到Next.js应用页面
- 没有404错误
- 页面能正常加载

### 4.3 测试API

**在浏览器地址栏测试：**

```
你的URL/api/health

例如：
https://dual-empathy-robot.vercel.app/api/health
```

**✅ 应该看到：**
```json
{
  "status": "ok",
  "service": "Dual Empathy Robot API",
  "version": "2.0.0",
  "deployment": "vercel"
}
```

---

## 🎉 完成！自动部署设置

### 现在你已经完成部署！

**🔄 自动更新流程：**

以后每次修改代码，只需要：

```powershell
# 1. 修改代码后
cd c:\Users\wangs\Desktop\robotA_demo_2

# 2. 提交更改
git add .
git commit -m "Update: 描述你的修改"

# 3. 推送到GitHub
git push

# 4. Vercel 自动检测到更新并重新部署！
# 无需任何额外操作
```

**📧 部署通知：**
- Vercel会发邮件通知部署状态
- 可以在Dashboard查看部署历史

---

## 🐛 常见问题解决

### 问题1：git命令不存在
```powershell
# 安装Git
# 下载：https://git-scm.com/download/win
# 安装后重启PowerShell
```

### 问题2：GitHub推送需要登录
```powershell
# 第一次推送会弹出登录窗口
# 输入GitHub用户名和密码
# 或使用Personal Access Token

# 如果需要Token：
# GitHub → Settings → Developer settings → Personal access tokens
# Generate new token → 勾选 repo → 复制token
# 用token作为密码
```

### 问题3：Vercel构建失败
**查看日志：**
- Vercel Dashboard → 你的项目 → Deployments
- 点击失败的部署查看详细日志

**常见原因：**
- Root Directory设置错误（应该是 `frontend`）
- 环境变量未设置
- 依赖安装失败

### 问题4：看不到GitHub仓库
- Vercel → Account Settings → Git
- 点击 "Adjust GitHub App Permissions"
- 重新授权

### 问题5：API返回错误
- 检查环境变量是否正确设置
- 重新部署：Dashboard → Deployments → 最新部署 → ... → Redeploy

---

## 📚 下一步学习

### 1. 自定义域名
- Vercel Dashboard → Settings → Domains
- 添加你自己的域名

### 2. 查看分析数据
- Dashboard → Analytics
- 查看访问量、性能等

### 3. 查看日志
- Dashboard → Logs
- 实时查看运行日志

### 4. 团队协作
- Dashboard → Settings → Team
- 邀请团队成员

---

## ✅ 检查清单

部署完成后，确认：

- [ ] GitHub仓库已创建，代码已上传
- [ ] Vercel项目已创建
- [ ] Root Directory 设置为 `frontend`
- [ ] 环境变量 GEMINI_API_KEY 已添加
- [ ] 部署状态显示 "Ready"（绿色）
- [ ] 访问URL能看到网站
- [ ] /api/health 返回正确JSON

**全部打勾 = 部署成功！🎉**

---

## 🆘 需要帮助？

1. **查看详细文档**：[DEPLOYMENT_VERCEL.md](DEPLOYMENT_VERCEL.md)
2. **Vercel官方文档**：https://vercel.com/docs
3. **GitHub帮助**：https://docs.github.com/

---

## 📞 重要链接

- **你的GitHub仓库**：https://github.com/YOUR_USERNAME/dual-empathy-robot
- **Vercel Dashboard**：https://vercel.com/dashboard
- **你的网站**：https://dual-empathy-robot.vercel.app（替换成你的实际URL）

---

**恭喜你完成部署！现在你的双共情机器人系统已经在线运行了！🚀**

---

**最后提醒：**
- 📝 记住你的GitHub仓库URL
- 🌐 记住你的Vercel部署URL
- 🔑 保管好你的API密钥（不要分享给别人）
- 💾 定期提交代码到GitHub备份
