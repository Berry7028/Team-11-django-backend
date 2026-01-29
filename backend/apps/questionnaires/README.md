# 朝夜アンケートAPI

朝と夜のアンケート回答を受け付けるAPIエンドポイントです。Supabaseの`users_condition`テーブルに気分と体調のデータを保存します。

## 目次

- [APIエンドポイント](#apiエンドポイント)
- [リクエスト形式](#リクエスト形式)
- [レスポンス形式](#レスポンス形式)
- [使用例](#使用例)
- [エラーハンドリング](#エラーハンドリング)
- [データベーステーブル構成](#データベーステーブル構成)
- [注意事項](#注意事項)

## APIエンドポイント

### 朝アンケート送信

```
POST /api/questionnaire/morning
```

### 夜アンケート送信

```
POST /api/questionnaire/night
```

## リクエスト形式

### 必須ヘッダー

| ヘッダー名 | 説明 | 例 |
|-----------|------|-----|
| `X-User-UUID` | Supabaseの`public.users`テーブルの`uuid` | `550e8400-e29b-41d4-a716-446655440000` |
| `Content-Type` | リクエストボディの形式 | `application/json` |

### リクエストボディ

```json
{
  "mood": "普通",
  "condition": "軽い",
  "free_text": ""
}
```

#### フィールド説明

| フィールド名 | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `mood` | string | 必須 | 気分（選択肢: `"絶好調"`, `"普通"`, `"モヤモヤ"`, `"つらい"`） |
| `condition` | string | 必須 | 体調（選択肢: `"軽い"`, `"ふつう"`, `"だるい"`） |
| `free_text` | string | 任意 | 自由入力テキスト（最大1000文字、現在は未使用） |

## レスポンス形式

### 成功時（201 Created）

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "morning_mood": "普通",
  "morning_condition": "軽い",
  "night_mood": null,
  "night_condition": null,
  "created_at": "2026-01-29T02:00:00.000Z",
  "updated_at": "2026-01-29T02:00:00.000Z"
}
```

### エラー時（400 Bad Request）

```json
{
  "detail": "X-User-UUID ヘッダーが必要です。"
}
```

または

```json
{
  "mood": ["このフィールドは必須です。"],
  "condition": ["有効な選択肢ではありません。"]
}
```

### エラー時（500 Internal Server Error）

```json
{
  "detail": "Supabaseの保存に失敗しました。",
  "error": "エラーメッセージの詳細"
}
```

## 使用例

### cURL

#### 朝アンケート送信

```bash
curl -X POST http://localhost:8000/api/questionnaire/morning \
  -H "Content-Type: application/json" \
  -H "X-User-UUID: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{
    "mood": "普通",
    "condition": "軽い",
    "free_text": ""
  }'
```

#### 夜アンケート送信

```bash
curl -X POST http://localhost:8000/api/questionnaire/night \
  -H "Content-Type: application/json" \
  -H "X-User-UUID: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{
    "mood": "モヤモヤ",
    "condition": "だるい",
    "free_text": ""
  }'
```

### JavaScript / TypeScript (fetch API)

```typescript
// 朝アンケート送信
async function submitMorningQuestionnaire(
  uuid: string,
  mood: "絶好調" | "普通" | "モヤモヤ" | "つらい",
  condition: "軽い" | "ふつう" | "だるい"
) {
  const response = await fetch("http://localhost:8000/api/questionnaire/morning", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-UUID": uuid,
    },
    body: JSON.stringify({
      mood,
      condition,
      free_text: "",
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "アンケート送信に失敗しました");
  }

  return await response.json();
}

// 使用例
try {
  const result = await submitMorningQuestionnaire(
    "550e8400-e29b-41d4-a716-446655440000",
    "普通",
    "軽い"
  );
  console.log("保存成功:", result);
} catch (error) {
  console.error("エラー:", error);
}
```

### React Native (既存のApiClientを使用)

```typescript
import { ApiClient } from "../../api/client";

const client = new ApiClient({
  baseUrl: "http://localhost:8000",
  getAuthToken: async () => null, // 認証不要のため
});

// カスタムヘッダーを追加する必要があるため、直接fetchを使用
async function submitMorningQuestionnaire(
  uuid: string,
  mood: "絶好調" | "普通" | "モヤモヤ" | "つらい",
  condition: "軽い" | "ふつう" | "だるい"
) {
  const response = await fetch("http://localhost:8000/api/questionnaire/morning", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-UUID": uuid,
    },
    body: JSON.stringify({
      mood,
      condition,
      free_text: "",
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "アンケート送信に失敗しました");
  }

  return await response.json();
}
```

## エラーハンドリング

### ステータスコード一覧

| ステータスコード | 説明 |
|----------------|------|
| `201 Created` | アンケート回答が正常に保存されました |
| `400 Bad Request` | リクエストが不正です（UUIDヘッダー未設定、バリデーションエラーなど） |
| `500 Internal Server Error` | サーバー内部エラー（Supabase接続エラーなど） |

### バリデーションエラー

以下の場合に`400 Bad Request`が返されます：

- `X-User-UUID`ヘッダーが未設定
- `mood`フィールドが未設定、または選択肢外の値
- `condition`フィールドが未設定、または選択肢外の値

### エラーレスポンス例

```json
{
  "mood": ["このフィールドは必須です。"],
  "condition": ["有効な選択肢ではありません。"]
}
```

## データベーステーブル構成

### users_condition テーブル

| カラム名 | 型 | 説明 |
|---------|-----|------|
| `uuid` | text | Supabaseの`public.users`テーブルの`uuid`（主キー） |
| `morning_mood` | text | 朝の気分（`"絶好調"`, `"普通"`, `"モヤモヤ"`, `"つらい"`のいずれか） |
| `morning_condition` | text | 朝の体調（`"軽い"`, `"ふつう"`, `"だるい"`のいずれか） |
| `night_mood` | text | 夜の気分（`"絶好調"`, `"普通"`, `"モヤモヤ"`, `"つらい"`のいずれか） |
| `night_condition` | text | 夜の体調（`"軽い"`, `"ふつう"`, `"だるい"`のいずれか） |
| `created_at` | timestamp | レコード作成日時 |
| `updated_at` | timestamp | レコード更新日時 |

### データ保存の動作

1. **同じ日の既存レコードがある場合**:
   - 既存レコードを削除してから新規レコードを作成
   - 朝アンケート送信時: `morning_mood`と`morning_condition`を更新、`night_mood`と`night_condition`は既存値を保持（なければ`null`）
   - 夜アンケート送信時: `night_mood`と`night_condition`を更新、`morning_mood`と`morning_condition`は既存値を保持（なければ`null`）

2. **同じ日の既存レコードがない場合**:
   - 新規レコードを作成
   - 朝アンケート送信時: `morning_mood`と`morning_condition`を設定、`night_mood`と`night_condition`は`null`
   - 夜アンケート送信時: `night_mood`と`night_condition`を設定、`morning_mood`と`morning_condition`は`null`

## 注意事項

1. **認証**: 現在は認証不要（`AllowAny`）ですが、`X-User-UUID`ヘッダーは必須です
2. **自由入力**: `free_text`フィールドは現在未使用です。将来的に別テーブルで管理する予定です
3. **日付判定**: 同じ日かどうかの判定はUTC基準で行われます
4. **Supabase設定**: `SUPABASE_URL`と`SUPABASE_KEY`の環境変数が設定されている必要があります
5. **データ更新**: 同じ日の既存レコードは削除してから新規作成されます（最新1件のみ保持）

## 関連ファイル

- `views.py`: APIビューの実装
- `serializers.py`: リクエスト/レスポンスのシリアライザー
- `supabase_client.py`: Supabaseクライアントの初期化
- `urls.py`: URLルーティング設定
