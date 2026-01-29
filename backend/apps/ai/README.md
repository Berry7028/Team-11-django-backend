# AI アプリ

ユーザーのメンタルヘルスをサポートするAI機能を提供します。

## エンドポイント

### POST /api/ai/recommendations/

ユーザーの `users_condition` を元に、AIがクエスト（5件）とマスコット状態を生成し、Supabaseに保存します。

#### リクエスト

**ヘッダー:**
```
X-User-UUID: <ユーザーのUUID> (必須)
```

**ボディ:** 不要

#### レスポンス

**成功時 (200):**
```json
{
  "quests": [
    {
      "title": "5分間の深呼吸",
      "description": "朝の気分が少し重そうなので、リラックスのための深呼吸をおすすめします。"
    },
    ...
  ],
  "mascot": {
    "status": "Okay",
    "message": "今日は少しゆっくりいこう！無理しないでね。"
  }
}
```

**エラー時 (400):**
```json
{
  "error": "X-User-UUID ヘッダーが必要です"
}
```
または
```json
{
  "error": "users_condition が見つかりません"
}
```

#### 保存先

- **quests テーブル**: 当日分のクエストを5件保存（既存の当日分は削除してから挿入）
- **mascots テーブル**: マスコット状態を保存（既存があれば更新）

---

### POST /api/ai/hints/

プロンプトに対するヒントを返す（ダミー実装）。

#### リクエスト

**ボディ:**
```json
{
  "prompt": "質問やプロンプト"
}
```

#### レスポンス

```json
{
  "hint": "Hint for: 質問やプロンプト..."
}
```

---

## 環境変数

| 変数名 | 説明 |
|--------|------|
| `OPENAI_API_KEY` | OpenAI APIキー |
| `SUPABASE_URL` | Supabase プロジェクトURL |
| `SUPABASE_KEY` | Supabase APIキー |

## 依存関係

```
openai
supabase
```

## データベーススキーマ

### users_condition (入力)
- `uuid`: ユーザーUUID
- `morning_mood`: 朝の気分
- `morning_condition`: 朝の体調
- `morning_note`: 朝のメモ
- `night_mood`: 夜の気分
- `night_condition`: 夜の体調
- `night_note`: 夜のメモ

### quests (出力)
- `uuid`: ユーザーUUID
- `title`: クエストタイトル
- `description`: クエスト説明
- `completed`: 完了フラグ
- `day`: 日付

### mascots (出力)
- `uuid`: ユーザーUUID
- `status`: Sad / Bad / Okay / Good / Great
- `message`: マスコットからのメッセージ
