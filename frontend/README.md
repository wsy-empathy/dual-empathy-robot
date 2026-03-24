# 二重共情ロボットシステム - フロントエンド

## セットアップ

### ローカル開発

1. 依存関係をインストール:
```bash
npm install
```

2. 環境変数を設定:
`.env.local`ファイルを編集し、バックエンドAPIのURLを設定してください:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. 開発サーバーを起動:
```bash
npm run dev
```

4. ブラウザで開く: http://localhost:3000

### 本番環境（Vercel）デプロイ

1. Vercelにログイン:
```bash
npm install -g vercel
vercel login
```

2. デプロイ:
```bash
vercel
```

3. 環境変数を設定:
Vercelダッシュボードで`NEXT_PUBLIC_API_URL`を設定してください。
例: `http://your-server-ip:8000`

## 使用方法

1. **対話を開始**: 「対話を開始」ボタンをクリック
2. **トピック選択**: 4つの主要トピックから選択
   - 学業のこと
   - 進路・将来のこと
   - 経済面のこと
   - 学内の友人関係のこと
3. **サブトピック選択**: 3つのサブトピックから選択
4. **対話開始**: メッセージを入力してAER/CERと対話

## 機能

- ✅ トピック/サブトピック選択UI
- ✅ AER/CERメッセージの視覚的区別（色分け、バッジ表示）
- ✅ 感情検出結果の表示
- ✅ リアルタイムチャット
- ✅ レスポンシブデザイン
- ✅ 日本語UI

## 技術スタック

- **Next.js 14**: Reactフレームワーク
- **TypeScript**: 型安全性
- **Tailwind CSS**: スタイリング
- **Axios**: HTTP通信
- **Vercel**: デプロイプラットフォーム

## API連携

フロントエンドは以下のバックエンドAPIエンドポイントと通信します:

- `POST /api/session/create` - セッション作成
- `GET /api/topics` - トピック一覧取得
- `POST /api/session/select-topic` - トピック選択
- `POST /api/session/select-subtopic` - サブトピック選択
- `POST /api/chat` - メッセージ送信

## カスタマイズ

### AER/CERの色変更

`tailwind.config.js`で色を変更できます:
```javascript
colors: {
  'aer': '#FF6B9D',  // AER粉色
  'cer': '#4A90E2',  // CER蓝色
}
```

### スタイル調整

`app/globals.css`でメッセージボックスのスタイルをカスタマイズできます。
