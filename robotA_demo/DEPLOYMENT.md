# 二重共情ロボットシステム v2.0 - デプロイガイド

## ローカル開発環境セットアップ

### 1. バックエンドセッ トアップ

```powershell
# robotA_demoディレクトリに移動
cd robotA_demo

# Python仮想環境作成
python -m venv venv

# 仮想環境有効化（Windows PowerShell）
.\venv\Scripts\Activate.ps1

# 依存関係インストール
pip install -r requirements.txt

# Gemini API Key設定
# core/config.py を開いて以下を設定:
# GEMINI_API_KEY = "your-api-key-here"
```

### 2. フロントエンドセットアップ

```powershell
# frontendディレクトリに移動
cd ..\frontend

# Node.js依存関係インストール
npm install

# 環境変数ファイル確認
# .env.local が作成されていることを確認
# 内容: NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

##  ローカル起動手順

### 方法1: 自動起動スクリプト（推奨）

```powershell
# ルートディレクトリから
.\start_system.bat
```

このスクリプトは以下を実行します：
1. バックエンド起動（別ウィンドウ）
2. フロントエンド起動（別ウィンドウ）
3. 自動的にブラウザでフロントエンドを開く

### 方法2: 手動起動

**ターミナル1（バックエンド）：**
```powershell
cd robotA_demo
.\venv\Scripts\Activate.ps1
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

**ターミナル2（フロントエンド）：**
```powershell
cd frontend
npm run dev
```

**ブラウザで開く：**
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000/docs (FastAPI Swagger UI)

---

## Vercel本番環境デプロイ

### 1. バックエンドサーバー準備

バックエンドは **ローカルPC** または **クラウドサーバー** で起動します：

```powerhell
# ローカルPCの場合
cd robotA_demo
.\venv\Scripts\Activate.ps1
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000

# クラウドサーバーの場合（LinuxでPostgreSQL等）
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

**ポート8000を外部からアクセス可能にする：**
- Windowsファイアウォールで許可
- ルーターでポートフォワーディング設定
- または、クラウドサーバー（AWS/GCP/Azure）を使用

**バックエンドURLを確認：**
```
http://your-ip-address:8000
```

### 2. フロントエンドVercelデプロイ

```powershell
cd frontend

# Vercel CLIインストール（初回のみ）
npm install -g vercel

# Vercelにログイン
vercel login

# デプロイ
vercel

# プロンプト に従って設定：
# ? Set up and deploy "~/frontend"? Yes
# ? Which scope? [Your Account]
# ? Link to existing project? No
# ? What's your project's name? empathy-robot-frontend
# ? In which directory is your code located? ./
```

### 3. Vercel環境変数設定

Vercelダッシュボード (https://vercel.com/dashboard) で：

1. プロジェクトを選択
2. Settings → Environment Variables
3. 以下を追加：
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `http://your-ip-address:8000`
   - **Environments**: Production, Preview, Development すべてチェック
4. Save

### 4. 再デプロイ

環境変数設定後、再デプロイが必要：

```powershell
vercel --prod
```

### 5. 確認

Vercelが表示するURLにアクセス：
```
https://empathy-robot-frontend.vercel.app
```

---

## トラブルシューティング

### バックエンド接続エラー

**症状**: フロントエンドから「メッセージ送信に失敗しました」

**解決策**:
1. バックエンドが起動しているか確認
   ```powershell
   # ブラウザで開く
   http://localhost:8000/docs
   ```
   
2. CORS設定を確認（`api_server.py`）:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000", "https://*.vercel.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. ファイアウォール設定（Vercelから接続する場合）:
   ```powershell
   # Windows Firewall でポート8000を許可
   New-NetFirewallRule -DisplayName "Empathy Robot API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

### Gemini API エラー

**症状**: 「LLM生成に失敗しました」

**解決策**:
1. APIキーを確認（`core/config.py`）
2. APIキーが有効か確認（Google AI Studio）
3. レート制限に達していないか確認

### フロントエンド起動エラー

**症状**: `npm run dev` が失敗

**解決策**:
```powershell
# node_modules削除して再インストール
rm -r node_modules
rm package-lock.json
npm install

# または
npm清 install
```

### RAGファイルが見つからない

**症状**: 「RAGコンテンツ取得失敗」

**解決策**:
1. `data/rag_v2/` に12個のファイルがあるか確認
2. ファイル名が正しいか確認：
   - academic_follow_content.txt
   - academic_study_pace.txt
   - etc.

---

## セキュリティ考慮事項

### API Key保護

- **絶対にGitにコミットしない**: `.gitignore` に `config.py` を追加
- **環境変数を使用**: 本番環境では環境変数からAPI Keyを読み込む

```python
# config.py（本番環境推奨）
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "default-key-for-dev")
```

### CORS設定

- **本番環境**: Vercelの実際のURLのみ許可
  ```python
  allow_origins=["https://your-actual-domain.vercel.app"]
  ```

### HTTPS使用

- **Vercel**: 自動的にHTTPSを提供
- **バックエンド**: できればHTTPSで公開（Let's Encrypt等）

---

## パフォーマンス最適化

### バックエンド

1. **Uvicorn Workers追加**（本番環境）:
   ```powershell
   uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **RAGキャッシュ**: 既に実装済み（`rag_v2_retriever.py`）

3. **セッション永続化**: 必要に応じてRedis等を使用

### フロントエンド

1. **画像最適化**: Next.js Image Component使用
2. **コード分割**: 自動的に実行される
3. **CDN**: Vercelが自動的に提供

---

## モニタリング

### ログ確認

**バックエンドログ**:
```powershell
# Uvicornコンソール出力を確認
```

**実験データログ**:
```powershell
# logs/experiments/ を確認
ls logs/experiments/
```

**エラーログ**:
```python
# api_server.py に追加
import logging
logging.basicConfig(level=logging.INFO)
```

### Vercelダッシュボード

- デプロイ履歴
- エラーログ
- パフォーマンスメトリクス

---

## バックアップ

### 実験データバックアップ

```powershell
# 定期的にlogs/experiments/をバックアップ
Copy-Item -Path "logs/experiments" -Destination "backup/experiments_$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

### データベース（将来の拡張）

現在はファイルベースですが、将来的にはPostgreSQL等を検討。

---

## まとめ

✅ **ローカル開発**: バックエンド（port 8000）+ フロントエンド（port 3000）  
✅ **本番環境**: Vercel（フロントエンド）+ ローカル/クラウド（バックエンド）  
✅ **セキュリティ**: API Key保護、CORS設定、HTTPS  
✅ **モニタリング**: ログ確認、Vercelダッシュボード  

システムは完全にデプロイ可能です！🚀
