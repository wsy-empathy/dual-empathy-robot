# 二重共情ロボットシステム v2.0

**Vercel Frontend + Local RTX 5070 Backend Architecture**

---

## 🎯 プロジェクト概要

AER（Affective Empathy Robot）とCER（Cognitive Empathy Robot）による二重共情対話システム。
大学生の悩み相談に対して、情感共感（AER）と認知共感（CER）を組み合わせた10段階の対話フローを提供します。

### システムアーキテクチャ

```
┌─────────────────────────────────────────────┐
│         Vercel Frontend (Next.js)           │
│   Topic Selection → Chat UI → Results      │
└───────────────┬─────────────────────────────┘
                │ REST API (HTTP)
                ↓
┌─────────────────────────────────────────────┐
│     FastAPI Backend (localhost:8000)        │
│  ┌────────────────────────────────────────┐ │
│  │ Session Manager (10-stage flow)       │ │
│  │ AER Agent (NURSE strategy)             │ │
│  │ CER Agent (PT/Mz/Advice strategy)      │ │
│  │ RAG V2 Retriever (stage-based)        │ │
│  │ Emotion Recognizer (ONNX CPU)          │ │
│  │ LLM Interface (Gemini API)             │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                 RTX 5070 (Future: local LLM)
```

### 核心機能

- **AER（情感共情ロボット）**: NURSE戦略（M+N/U/R/S/E）、3ラウンド情感鏡映
- **CER（認知共情ロボット）**: PT/Mz/Advice戦略、簡潔回答（≤2-3文）
- **10段階対話フロー**: Entry(3) → AER Round 1-3(4) → CER Round 1-3(3) → AER Closing(2)
- **純文本対話**: TTS/ASR削除、軽量CPU推論
- **Webデプロイ**: Vercel + FastAPI、オンラインアクセス可能

### トピック構造（4× 3 = 12組み合わせ）

1. **学業のこと** (academic)
   - 授業の内容についていくことが難しい
   - 勉強のペースやスケジュール管理に困っている
   - 試験やレポート前に不安が強くなる

2. **進路・将来のこと** (future)
   - 卒業後にやりたいことがまだはっきりしていない
   - 就職先や大学院、進学先の選択に迷っている
   - やりたいことはあるが、どう準備を進めればよいか分からない

3. **経済面のこと** (financial)
   - 学費や生活費の工面が負担になっている
   - アルバイトと勉強の両立がしんどい
   - 経済的な不安から精神的にしんどくなることがある

4. **学内の友人関係のこと** (relationship)
   - 学内で友達を作りにくいと感じている
   - クラスやサークル内の人間関係がうまくいかない
   - 何でも話せる友達がいなくて孤独を感じる


---

## 🚀 セットアップ

### 1. バックエンドセットアップ

```powershell
cd robotA_demo

# 仮想環境作成
python -m venv venv

# 仮想環境有効化（Windows）
.\venv\Scripts\Activate.ps1

# 依存関係インストール
pip install -r requirements.txt

# Gemini API Key設定
# core/config.pyで GEMINI_API_KEY を設定してください
```

**重要**: `core/config.py`でGemini APIキーを設定：
```python
GEMINI_API_KEY = "your-api-key-here"
```

### 2. バックエンド起動

```powershell
# 方法1: バッチファイル
.\start_backend.bat

# 方法2: PowerShellスクリプト
.\start_backend.ps1

# 方法3: 直接実行
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

バックエンドは http://localhost:8000 で起動します。

### 3. フロントエンドセットアップ

```powershell
cd ..\frontend

# 依存関係インストール
npm install

# 環境変数設定（.env.local）
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. フロントエンド起動（ローカル開発）

```powershell
npm run dev
```

http://localhost:3000 でアクセスできます。

### 5. Vercelデプロイ（本番環境）

```powershell
cd frontend

# Vercel CLIインストール
npm install -g vercel

# ログイン
vercel login

# デプロイ
vercel

# 環境変数設定（Vercelダッシュボード）
# NEXT_PUBLIC_API_URL = http://your-server-ip:8000
```

---

## 📊 対話フロー（10段階）

### Stage 1-3: Entry（システム主導）
1. **topic**: トピック選択（4選択肢）
2. **subtopic**: サブトピック選択（3選択肢）
3. **initial**: 初回状況入力（ユーザー記述）

### Stage 4-7: AER Round 1-3 + Transition
4. **aer_1**: M+N/U+E（明確化＋理解＋感情探索）
5. **aer_2**: M+R+E（共感応答＋感情深掘り）
6. **aer_3**: M+S+E（支持＋感情まとめ）
7. **cer_transition**: CER紹介・切り替え（固定メッセージ）

### Stage 8-10: CER Round 1-3
8. **cer_1**: PT（視点取得、≤2文）
9. **cer_2**: Mz（メンタライジング、可証伪仮説）
10. **cer_3**: Advice（単一具体策：做什么+怎么做+完成判据）

### Stage 11-12: AER Closing
11. **aer_closing_1**: M+R（共感応答で締め）
12. **aer_closing_2**: M+S（支持で完結）→ 対話終了

---

## 🎨 AER/CER戦略詳細

### AER（Affective Empathy Robot）- NURSE戦略

- **M (Mirroring)**: 全応答で感情を鏡映
- **N (Name)**: 感情を明確に言語化
- **U (Understand)**: 理解を示す
- **R (Respect)**: 共感的応答
- **S (Support)**: 支持的メッセージ
- **E (Explore)**: 感情の深掘り質問

**禁止事項**：
- ❌ 分析的言語（「〜ということですね」）
- ❌ アドバイス提供
- ❌ 「なぜ」質問

### CER（Cognitive Empathy Robot）- PT/Mz/Advice戦略

- **PT (Perspective-Taking)**: 視点取得（≤2文）
- **Mz (Mentalizing)**: 可証伪仮説（「もしかして〜かもしれない」）
- **Advice**: 単一具体策（做什么+怎么做+完成判据）

**禁止事項**：
- ❌ 複数の選択肢提示
- ❌ 繰り返し発言
- ❌ 感情労働

---

## 📁 プロジェクト構造

```
robotA_demo/
├── api_server.py              # FastAPI Backend ⭐
├── requirements.txt           # Python依存関係
├── start_backend.bat          # Backend起動（Windows）
├── start_backend.ps1          # Backend起動（PowerShell）
├── core/
│   ├── config.py             # 設定ファイル（API Key等）
│   ├── topics.py             # トピック/サブトピック定義
│   ├── session_manager.py    # セッション管理（10段階フロー）
│   ├── llm_gemini.py         # Gemini LLM統合
│   ├── rag_v2_retriever.py   # RAG V2リトリーバー
│   ├── emo_wrime_luke_onnx.py # 感情認識（ONNX CPU）
│   └── agents/
│       ├── aer_agent.py      # AERエージェント
│       └── cer_agent.py      # CERエージェント
├── prompts/
│   ├── aer_system.txt        # AERシステムプロンプト
│   └── cer_system.txt        # CERシステムプロンプト
├── data/
│   └── rag_v2/              # RAGコンテンツファイル（12ファイル）
│       ├── academic_follow_content.txt
│       ├── academic_study_pace.txt
│       ├── academic_exam_anxiety.txt
│       ├── future_unclear_goals.txt
│       ├── future_career_choice.txt
│       ├── future_preparation.txt
│       ├── financial_cost_burden.txt
│       ├── financial_work_study_balance.txt
│       ├── financial_financial_anxiety.txt
│       ├── relationship_making_friends.txt
│       ├── relationship_interaction_issues.txt
│       └── relationship_no_confidant.txt
└── logs/
    └── experiments/          # 実験データ自動保存

frontend/
├── package.json（Node.js依存関係）
├── next.config.js          # Next.js設定
├── vercel.json             # Vercel設定
├── app/
│   ├── layout.tsx          # レイアウト
│   ├── page.tsx            # メインページ ⭐
│   └── globals.css         # スタイル（AER/CER色分け）
└── README.md               # フロントエンド文書
```

---

## 🔧 API エンドポイント

### セッション管理
- `POST /api/session/create` - 新規セッション作成
  - Response: `{session_id, message}`
- `DELETE /api/session/{session_id}` - セッション削除

### トピック選択
- `GET /api/topics` - トピック一覧取得
  - Response: `{topics: [{key, ja, zh}, ...]}`
- `GET /api/topics/{topic_key}/subtopics` - サブトピック一覧取得
  - Response: `{subtopics: [[key, ja, zh], ...]}`
- `POST /api/session/select-topic` - トピック選択
  - Body: `{session_id, topic_key}`
  - Response: `{message, subtopics}`
- `POST /api/session/select-subtopic` - サブトピック選択
  - Body: `{session_id, subtopic_key}`
  - Response: `{message}` （stage → aer_1へ自動進行）

### 対話
- `POST /api/chat` - メッセージ送信
  - Body: `{session_id, message}`
  - Response: `{message, agent, emotion, is_completed}`
- `GET /api/session/{session_id}/status` - セッション状態取得
  - Response: `{topic, subtopic, current_stage, ...}`

---

## 🧪 実験データログ

対話終了時、実験データは自動的に `logs/experiments/` に保存されます：

```json
{
  "session_id": "uuid",
  "topic": "academic",
  "subtopic": "follow_content",
  "start_time": "2025-02-01T10:00:00",
  "end_time": "2025-02-01T10:15:30",
  "emotion_detected": {"label": "sadness", "score": 0.85},
  "dialogue_history": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "AER", "content": "...", "timestamp": "..."}
  ],
  "stages_completed": ["topic", "subtopic", "initial", ...]
}
```

---

## 🎨 RAGコンテンツファイル形式

各トピック/サブトピックに対応するRAGファイル：

```
=== AER Content ===

AER_R1_M+N/U+E:
もしかして、授業の内容が難しくて...（M+N/U+E戦略内容）

AER_R2_M+R+E:
それは本当にしんどいですよね...（M+R+E戦略内容）

AER_R3_M+S+E:
あなたは一人じゃないです...（M+S+E戦略内容）

AER_Transition:
（CER紹介メッセージ）

AER_Closing1_M+R:
（締めの共感応答）

AER_Closing2_M+S:
（最終支持メッセージ）

=== CER Content ===

CER_PT:
もしかして、周りのペースに合わせるのが難しいと感じているかもしれませんね。（≤2文）

CER_Mz:
予習する時間があまり取れていない可能性があるかもしれません。（可証伪仮説）

CER_Advice:
授業の後に30分復習する時間を作ってみる。具体的には、帰宅後すぐにノートを見返す。1週間続けられたら成功。

=== Keywords ===
授業内容, 難しい, ついていけない, 予習復習, 理解度
```

---

## 🐛 よくある質問

### Q: バックエンドが起動しない
1. 仮想環境が有効化されているか確認
2. `pip install -r requirements.txt` を再実行
3. `core/config.py` でGemini APIキーを設定

### Q: フロントエンドがバックエンドに接続できない
1. バックエンドが http://localhost:8000 で起動しているか確認
2. `.env.local` のAPI URLが正しいか確認
3. CORS設定を確認（`api_server.py`で設定済み）

### Q: Vercelデプロイ後、バックエンドに接続できない
1. Vercelダッシュボードで環境変数 `NEXT_PUBLIC_API_URL` を設定
2. バックエンドサーバーのIPアドレスとポート8000が公開されているか確認
3. ファイアウォール設定を確認

### Q: 感情認識が動作しない
1. ONNXモデルファイルが `models/onnx/` にあるか確認
2. `onnxruntime` がインストールされているか確認

### Q: RAGコンテンツが見つからない
1. `data/rag_v2/` ディレクトリに12個のファイルがあるか確認
2. ファイル名が `{topic}_{subtopic}.txt` の形式か確認

---

## 📖 開発者向けドキュメント

### 新しいトピック追加

1. `core/topics.py` の `TOPICS` 辞書に追加：
```python
TOPICS = {
    "new_topic": ["新トピック名（日本語）", "新话题名（中文）", {
        "sub1": ["サブトピック1", "子话题1"],
        "sub2": ["サブトピック2", "子话题2"],
    }]
}
```

2. `data/rag_v2/` に新しいRAGファイルを作成：
   - `new_topic_sub1.txt`
   - `new_topic_sub2.txt`

3. フロントエンドは自動的に新トピックを表示します

### エージェントカスタマイズ

- **AERプロンプト編集**: `prompts/aer_system.txt`
- **CERプロンプト編集**: `prompts/cer_system.txt`
- **エージェントロジック**: `core/agents/aer_agent.py`, `core/agents/cer_agent.py`

### 新しいステージ追加

1. `core/topics.py` の `DIALOGUE_STAGES` リストに追加
2. `core/session_manager.py` の `advance_stage()` ロジックを更新
3. 各エージェントの `format_prompt()` メソッドで新ステージを処理
4. RAGファイルに新ステージ用コンテンツを追加

### ログ解析

実験データは `logs/experiments/` に JSON形式で保存されます：
```python
import json
from pathlib import Path

# すべての実験データを読み込む
experiments = []
for file in Path("logs/experiments").glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        experiments.append(json.load(f))

# 統計分析
topics = [exp["topic"] for exp in experiments]
emotions = [exp["emotion_detected"]["label"] for exp in experiments]
```

---

## 🎯 システムの特徴

### ✅ AER/CERの明確な区別
- **視覚的区別**: フロントエンドで色分け（AER=ピンク、CER=青）
- **バッジ表示**: 各メッセージに「AER」「CER」バッジ
- **戦略の明示**: システムプロンプトで役割を明確化

### ✅ 段階的対話フロー
- **10段階の構造化フロー**: Entry → AER R1-3 → CER R1-3 → AER Closing
- **自動進行**: SessionManagerが状態を管理、自動的に次ステージへ
- **完了検知**: `aer_closing_2` で自動終了

### ✅ RAG V2システム
- **階層的コンテンツ**: トピック/サブトピック/ステージ別
- **セクション分離**: AER Content、CER Content、Keywords
- **ステージ適応**: 各ステージに合ったコンテンツを自動取得

### ✅ 実験データ自動記録
- **自動保存**: 対話終了時に自動的にJSON保存
- **詳細ログ**: トピック、感情、対話履歴、タイムスタンプ
- **分析ready**: JSON形式で後続分析が容易

---

## 📝 バージョン履歴

### v2.0.0 (2025-02)
- ✅ アーキテクチャ刷新: Vercel + FastAPI
- ✅ TTS/ASR削除: 純文本対話システム
- ✅ AER/CER分離: 明確な役割定義と戦略
- ✅ 10段階フロー: Entry → AER → CER → AER Closing
- ✅ RAG V2: ステージ別コンテンツ取得
- ✅ 新トピック構造: 4×3=12組み合わせ
- ✅ 実験データログ: 自動JSON保存
- ✅ Next.js Frontend: Vercelデプロイ対応

### v1.0.0 (2024)
- Robot A + Robot B システム
- Gradio UI
- 多模態情感識別
- TTS/ASR音声対話

---

## 📄 ライセンス

MIT License

---

## 🙏 謝辞

- **WRIME-LUKE**: 日本語感情認識
- **Google Gemini**: 対話生成AI
- **Next.js**: フロントエンドフレームワーク
- **FastAPI**: バックエンドフレームワーク
- **Vercel**: デプロイプラットフォーム

---

**システムは完全に稼働ready！** 🚀

バックエンド: `python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload`  
フロント エンド: `npm run dev` (http://localhost:3000)

---

お問い合わせ: GitHub Issues

