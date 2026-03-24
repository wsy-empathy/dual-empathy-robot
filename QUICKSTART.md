# 🚀 クイックスタートガイド - 二重共情ロボットシステム v2.0

## ⚡ 最速セットアップ（5ステップ）

### ステップ1: Python環境準備 (5分)

```powershell
# robotA_demoディレクトリに移動
cd c:\Users\wangs\Desktop\robotA_demo_2\robotA_demo

# Python仮想環境作成
python -m venv venv

# 仮想環境有効化
.\venv\Scripts\Activate.ps1

# 依存関係インストール
pip install -r requirements.txt
```

**期待される出力:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

---

### ステップ2: Gemini API Key設定 (2分)

1. Google AI Studioにアクセス: https://makersuite.google.com/app/apikey
2. API Keyを取得（無料）
3. `core/config.py`を開く
4. 以下の行を編集:

```python
# 変更前
GEMINI_API_KEY = "your-api-key-here"

# 変更後
GEMINI_API_KEY = "AIzaSy..."  # あなたのAPIキー
```

**重要**: API Keyは絶対にGitにコミットしないでください！

---

### ステップ3: Node.js環境準備 (5分)

```powershell
# frontendディレクトリに移動
cd ..\frontend

# 依存関係インストール
npm install
```

**期待される出力:**
```
added 300 packages, and audited 301 packages in 30s
```

**注意**: 初回は5分程度かかります。

---

### ステップ4: システム起動 (1分)

```powershell
# ルートディレクトリ（robotA_demo_2）に戻る
cd c:\Users\wangs\Desktop\robotA_demo_2

# 一括起動スクリプト実行
.\start_system.bat
```

**何が起こるか:**
1. バックエンドサーバーが別ウィンドウで起動（port 8000）
2. フロントエンドサーバーが別ウィンドウで起動（port 3000）
3. ブラウザが自動的に http://localhost:3000 を開く

---

### ステップ5: 動作確認 (3分)

ブラウザで以下を確認:

1. **トップページ表示**
   - 「対話を開始」ボタンが表示される ✅

2. **対話開始**
   - ボタンクリック → トピック選択画面 ✅

3. **トピック選択**
   - 「学業のこと」を選択 → サブトピック選択画面 ✅

4. **サブトピック選択**
   - 「授業の内容についていくことが難しい」を選択 → チャット画面 ✅

5. **メッセージ送信**
   - 「授業が難しくて困っています」と入力 → AER応答（ピンク色） ✅

6. **対話継続**
   - 数回やり取り → CER登場（青色） ✅

**成功！** システムが正常に動作しています 🎉

---

## 🔧 トラブルシューティング

### エラー1: `pip install` が失敗

**原因**: Python 3.8未満
**解決策**:
```powershell
python --version  # 3.8以上を確認
```

### エラー2: `npm install` が失敗

**原因**: Node.js未インストール
**解決策**:
```powershell
# Node.js をインストール: https://nodejs.org/
node --version  # v18以上を確認
```

### エラー3: バックエンドが起動しない

**原因**: ポート8000が既に使用されている
**解決策**:
```powershell
# ポート8000を使用しているプロセスを確認
netstat -ano | findstr :8000

# プロセスを終了（タスクマネージャーまたは）
taskkill /PID <プロセスID> /F
```

### エラー4: フロントエンドがバックエンドに接続できない

**原因**: `.env.local` の設定ミス
**解決策**:
```powershell
# frontend/.env.local を確認
cat frontend/.env.local

# 正しい内容:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### エラー5: Gemini API エラー

**原因**: APIキー未設定または無効
**解決策**:
1. `core/config.py` のAPIキーを確認
2. Google AI Studioでクォータを確認
3. APIキーを再生成

---

## 🌐 Vercelデプロイ（オプション）

### 前提条件
- Vercelアカウント（無料）: https://vercel.com/signup
- バックエンドが外部からアクセス可能（ポート8000開放）

### デプロイ手順

```powershell
cd frontend

# Vercel CLIインストール
npm install -g vercel

# ログイン
vercel login

# デプロイ
vercel

# 環境変数設定（Vercelダッシュボード）
# NEXT_PUBLIC_API_URL = http://your-ip:8000
```

### バックエンドの外部公開

**Windows Firewall設定:**
```powershell
New-NetFirewallRule -DisplayName "Empathy Robot API" `
    -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**ルーター設定:**
- ポートフォワーディング: 8000 → PC内部IP

**確認:**
```powershell
# 外部IPアドレス確認
curl https://api.ipify.org

# バックエンドアクセステスト
curl http://your-ip:8000/
```

---

## 📊 使用方法

### 基本フロー

1. **「対話を開始」** → セッション作成
2. **トピック選択** → 4つから選択（学業/進路/経済/友人関係）
3. **サブトピック選択** → 3つから選択
4. **初回入力** → 状況を自由に記述
5. **AER対話** → 3ラウンド（情感共感）
6. **CER対話** → 3ラウンド（認知共感）
7. **AER締め** → 2ラウンド（支持的終結）
8. **完了** → 実験データ自動保存

### メッセージ例

**トピック**: 学業のこと  
**サブトピック**: 授業の内容についていくことが難しい

**初回入力例**:
```
授業の内容が難しくて、予習復習をしても理解できないことが多いです。
周りのペースについていけなくて、焦ってしまいます。
```

**AER応答（M+N/U/E）**:
```
もしかして、授業の内容が難しくて、予習復習をしても
なかなか理解できないことに焦りを感じているのかもしれませんね。
周りのペースと比べて、自分だけ遅れているように感じると、
不安になることもあるんじゃないでしょうか。
```

**CER応答（PT）**:
```
もしかして、周りのペースに合わせようとしすぎて、
自分のペースで学ぶ時間が取れていないかもしれませんね。
```

---

## 📁 ディレクトリ構造（再掲）

```
robotA_demo_2/
├── start_system.bat           # 一括起動スクリプト ⭐
├── start_system.ps1
├── SYSTEM_COMPLETE.md         # 完成報告
├── QUICKSTART.md              # このファイル ⭐
│
├── robotA_demo/               # バックエンド
│   ├── api_server.py          # FastAPI ⭐
│   ├── requirements.txt       # Python依存
│   ├── start_backend.bat
│   ├── core/
│   │   ├── config.py          # API Key設定 ⭐
│   │   ├── topics.py
│   │   ├── session_manager.py
│   │   ├── rag_v2_retriever.py
│   │   └── agents/
│   ├── prompts/
│   └── data/
│       └── rag_v2/            # 12個のRAGファイル
│
└── frontend/                  # フロントエンド
    ├── package.json
    ├── .env.local             # API URL設定 ⭐
    ├── app/
    │   ├── page.tsx           # メインページ
    │   └── globals.css        # AER/CER色分け
    └── vercel.json            # Vercel設定
```

---

## ⏱️ 所要時間まとめ

| ステップ | 所要時間 | 難易度 |
|---------|---------|--------|
| Python環境 | 5分 | ⭐ |
| API Key設定 | 2分 | ⭐ |
| Node.js環境 | 5分 | ⭐ |
| システム起動 | 1分 | ⭐ |
| 動作確認 | 3分 | ⭐ |
| **合計** | **16分** | **簡単** |

（Vercelデプロイは +15分）

---

## ✅ チェックリスト

### 初回セットアップ
- [ ] Python 3.8+ インストール済み
- [ ] Node.js 18+ インストール済み
- [ ] `pip install -r requirements.txt` 成功
- [ ] `core/config.py` にGemini APIキー設定
- [ ] `npm install` 成功
- [ ] `frontend/.env.local` 確認

### 起動確認
- [ ] バックエンド起動（http://localhost:8000）
- [ ] フロントエンド起動（http://localhost:3000）
- [ ] トピック選択動作
- [ ] AER/CER対話動作
- [ ] 実験データ保存確認（`logs/experiments/`）

### Vercelデプロイ（オプション）
- [ ] Vercelアカウント作成
- [ ] `vercel` デプロイ成功
- [ ] 環境変数設定（NEXT_PUBLIC_API_URL）
- [ ] バックエンド外部公開
- [ ] 本番URLで動作確認

---

## 🎓 学習リソース

### 技術スタック
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **Vercel**: https://vercel.com/docs
- **Gemini API**: https://ai.google.dev/docs

### 共情理論
- **NURSE戦略**: 情感共感の構造化アプローチ
- **PT/Mz**: 認知共感の視点取得とメンタライジング

---

## 🎉 完成！

システムが正常に起動したら、**SYSTEM_COMPLETE.md** を確認して、
全機能のテストを実行してください。

**対話を楽しんでください！** 🚀

---

お問い合わせ: GitHub Issues
