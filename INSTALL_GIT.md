# Git 安装指南

## 检查 Git 是否已安装

打开 PowerShell 或命令提示符，运行：
```bash
git --version
```

如果看到版本号（如 `git version 2.40.0`），说明已安装。
如果看到 "git 不是内部或外部命令"，需要安装。

---

## 安装 Git for Windows

### 方法 1：下载安装（推荐）

1. **下载 Git**
   - 访问：https://git-scm.com/download/win
   - 会自动下载适合你系统的版本
   - 文件名类似：`Git-2.44.0-64-bit.exe`

2. **安装步骤**
   - 双击下载的安装程序
   - 一路点击 "Next"（使用默认设置即可）
   - 重要选项说明：
     - ✅ "Git Bash Here" - 勾选
     - ✅ "Git GUI Here" - 勾选
     - ✅ "Associate .git* configuration files" - 勾选
     - 其他保持默认
   - 点击 "Install"
   - 完成后点击 "Finish"

3. **验证安装**
   - 关闭并重新打开 PowerShell
   - 运行：`git --version`
   - 应该能看到版本号

### 方法 2：使用 Winget（Windows 11）

```powershell
# 如果你有 Windows 11 或 Windows 10（较新版本）
winget install --id Git.Git -e --source winget
```

### 方法 3：使用 Chocolatey

```powershell
# 如果已安装 Chocolatey 包管理器
choco install git
```

---

## 配置 Git（首次使用）

安装完成后，配置你的用户信息：

```powershell
# 设置用户名（将来会显示在提交记录中）
git config --global user.name "你的名字"

# 设置邮箱（用于GitHub关联）
git config --global user.email "your.email@example.com"

# 查看配置
git config --list
```

---

## ✅ 安装完成检查清单

- [ ] 运行 `git --version` 能看到版本号
- [ ] 配置了 user.name
- [ ] 配置了 user.email

完成后，返回继续部署流程！

---

## 🆘 如果安装遇到问题

### 问题1：下载速度太慢
- 使用国内镜像：https://registry.npmmirror.com/binary.html?path=git-for-windows/

### 问题2：安装后仍然找不到git命令
- 重启电脑
- 或手动添加到PATH：
  - 右键 "此电脑" → 属性 → 高级系统设置
  - 环境变量 → 系统变量 → Path → 编辑
  - 添加：`C:\Program Files\Git\cmd`

### 问题3：权限问题
- 右键安装程序，选择 "以管理员身份运行"
