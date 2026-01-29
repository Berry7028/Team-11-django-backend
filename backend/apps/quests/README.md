# クエストAPI

ユーザーのメンタルヘルスをサポートするクエスト機能を提供します。AI生成された当日のクエストを取得し、ユーザーに提示します。

## 目次

- [APIエンドポイント](#apiエンドポイント)
- [リクエスト形式](#リクエスト形式)
- [レスポンス形式](#レスポンス形式)
- [使用例](#使用例)
- [エラーハンドリング](#エラーハンドリング)
- [データベーステーブル構成](#データベーステーブル構成)
- [完全なフロー](#完全なフロー)
- [注意事項](#注意事項)

## APIエンドポイント

### 当日分クエスト取得

```
GET /api/quests/get
```

当日分（`date.today().isoformat()`）のクエストをSupabaseから取得します。

### クエスト完了/取り消し

```
POST /api/quests/:quest_id/complete
```

指定されたクエストの`completed`フラグをトグル（反転）します。未完了の場合は完了に、完了の場合は未完了に変更します。

### Django ModelViewSet（既存）

```
GET    /api/quests/quests       # クエスト一覧取得
POST   /api/quests/quests       # クエスト作成
GET    /api/quests/quests/:id   # クエスト詳細取得
PUT    /api/quests/quests/:id   # クエスト更新
DELETE /api/quests/quests/:id   # クエスト削除
```

> **注意**: Django ModelViewSetは認証が必要です（`IsAuthenticated`）

## リクエスト形式

### 必須ヘッダー

| ヘッダー名 | 説明 | 例 |
|-----------|------|-----|
| `X-User-UUID` | Supabaseの`public.users`テーブルの`uuid` | `550e8400-e29b-41d4-a716-446655440000` |

### リクエストボディ

**GET /api/quests/get**: 不要

**POST /api/quests/:quest_id/complete**: 不要（quest_idはURLパラメータで指定）

## レスポンス形式

### GET /api/quests/get

#### 成功時（200 OK）

```json
[
  {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "5分間の深呼吸",
    "description": "朝の気分が少し重そうなので、リラックスのための深呼吸をおすすめします。",
    "completed": false,
    "day": "2026-01-29",
    "created_at": "2026-01-29T02:00:00.000Z",
    "updated_at": "2026-01-29T02:00:00.000Z"
  },
  {
    "id": 2,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "10分間の散歩",
    "description": "軽い運動で気分転換しましょう。",
    "completed": false,
    "day": "2026-01-29",
    "created_at": "2026-01-29T02:00:00.000Z",
    "updated_at": "2026-01-29T02:00:00.000Z"
  }
]
```

#### クエストが0件の場合（200 OK）

```json
[]
```

#### エラー時（400 Bad Request）

```json
{
  "detail": "X-User-UUID ヘッダーが必要です。"
}
```

#### エラー時（500 Internal Server Error）

```json
{
  "detail": "Supabase設定エラー",
  "error": "SUPABASE_URL または SUPABASE_KEY が未設定です。"
}
```

または

```json
{
  "detail": "Supabaseの取得に失敗しました。",
  "error": "エラーメッセージの詳細"
}
```

### POST /api/quests/:quest_id/complete

#### 成功時（200 OK）

```json
{
  "id": 123,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "title": "5分間の深呼吸",
  "description": "朝の気分が少し重そうなので、リラックスのための深呼吸をおすすめします。",
  "completed": true,
  "day": "2026-01-29",
  "created_at": "2026-01-29T02:00:00.000Z",
  "updated_at": "2026-01-29T04:00:00.000Z"
}
```

#### エラー時（400 Bad Request）

```json
{
  "detail": "X-User-UUID ヘッダーが必要です。"
}
```

#### エラー時（404 Not Found）

```json
{
  "detail": "クエストが見つかりません。"
}
```

#### エラー時（500 Internal Server Error）

```json
{
  "detail": "Supabase設定エラー",
  "error": "SUPABASE_URL または SUPABASE_KEY が未設定です。"
}
```

または

```json
{
  "detail": "Supabaseの操作に失敗しました。",
  "error": "エラーメッセージの詳細"
}
```

## 使用例

### cURL

#### クエスト取得

```bash
curl -X GET http://localhost:8000/api/quests/get \
  -H "X-User-UUID: 550e8400-e29b-41d4-a716-446655440000"
```

#### クエスト完了

```bash
curl -X POST http://localhost:8000/api/quests/123/complete \
  -H "X-User-UUID: 550e8400-e29b-41d4-a716-446655440000"
```

### JavaScript / TypeScript (fetch API)

```typescript
// 当日分クエスト取得
async function getTodayQuests(uuid: string) {
  const response = await fetch("http://localhost:8000/api/quests/get", {
    method: "GET",
    headers: {
      "X-User-UUID": uuid,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "クエスト取得に失敗しました");
  }

  return await response.json();
}

// クエスト完了/取り消し
async function toggleQuestComplete(uuid: string, questId: number) {
  const response = await fetch(`http://localhost:8000/api/quests/${questId}/complete`, {
    method: "POST",
    headers: {
      "X-User-UUID": uuid,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "クエスト完了に失敗しました");
  }

  return await response.json();
}

// 使用例
try {
  const quests = await getTodayQuests("550e8400-e29b-41d4-a716-446655440000");
  console.log("当日のクエスト:", quests);
  console.log(`${quests.length}件のクエストがあります`);
  
  // 最初のクエストを完了
  if (quests.length > 0) {
    const updatedQuest = await toggleQuestComplete(
      "550e8400-e29b-41d4-a716-446655440000",
      quests[0].id
    );
    console.log("クエスト完了:", updatedQuest);
  }
} catch (error) {
  console.error("エラー:", error);
}
```

### React Native (fetch API)

```typescript
import { useEffect, useState } from "react";

interface Quest {
  id: number;
  uuid: string;
  title: string;
  description: string;
  completed: boolean;
  day: string;
  created_at: string;
  updated_at: string;
}

function useQuests(userUuid: string) {
  const [quests, setQuests] = useState<Quest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchQuests() {
      try {
        const response = await fetch("http://localhost:8000/api/quests/get", {
          method: "GET",
          headers: {
            "X-User-UUID": userUuid,
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "クエスト取得に失敗しました");
        }

        const data = await response.json();
        setQuests(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "不明なエラー");
      } finally {
        setLoading(false);
      }
    }

    fetchQuests();
  }, [userUuid]);

  return { quests, loading, error };
}

// クエスト完了トグル関数
async function toggleQuestComplete(userUuid: string, questId: number): Promise<Quest> {
  const response = await fetch(`http://localhost:8000/api/quests/${questId}/complete`, {
    method: "POST",
    headers: {
      "X-User-UUID": userUuid,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "クエスト完了に失敗しました");
  }

  return await response.json();
}

// コンポーネントでの使用例
function QuestList({ userUuid }: { userUuid: string }) {
  const { quests, loading, error } = useQuests(userUuid);
  const [updating, setUpdating] = useState<number | null>(null);

  const handleToggleComplete = async (questId: number) => {
    try {
      setUpdating(questId);
      const updatedQuest = await toggleQuestComplete(userUuid, questId);
      
      // ローカルステートを更新
      setQuests(prevQuests =>
        prevQuests.map(q => q.id === questId ? updatedQuest : q)
      );
    } catch (err) {
      console.error("クエスト完了エラー:", err);
      alert(err instanceof Error ? err.message : "クエスト完了に失敗しました");
    } finally {
      setUpdating(null);
    }
  };

  if (loading) return <Text>読み込み中...</Text>;
  if (error) return <Text>エラー: {error}</Text>;
  if (quests.length === 0) return <Text>今日のクエストはありません</Text>;

  return (
    <View>
      {quests.map((quest) => (
        <TouchableOpacity
          key={quest.id}
          onPress={() => handleToggleComplete(quest.id)}
          disabled={updating === quest.id}
        >
          <Text>{quest.title}</Text>
          <Text>{quest.description}</Text>
          <Text>完了: {quest.completed ? "✓" : "✗"}</Text>
          {updating === quest.id && <Text>更新中...</Text>}
        </TouchableOpacity>
      ))}
    </View>
  );
}
```

## エラーハンドリング

### ステータスコード一覧

| ステータスコード | 説明 | 対象エンドポイント |
|----------------|------|--------------------|
| `200 OK` | リクエストが正常に処理されました | GET /api/quests/get, POST /api/quests/:quest_id/complete |
| `400 Bad Request` | リクエストが不正です（UUIDヘッダー未設定） | 全エンドポイント |
| `404 Not Found` | クエストが見つかりません | POST /api/quests/:quest_id/complete |
| `500 Internal Server Error` | サーバー内部エラー（Supabase接続エラーなど） | 全エンドポイント |

### エラーハンドリング例

```typescript
async function getTodayQuestsWithErrorHandling(uuid: string) {
  try {
    const response = await fetch("http://localhost:8000/api/quests/get", {
      method: "GET",
      headers: {
        "X-User-UUID": uuid,
      },
    });

    if (response.status === 400) {
      console.error("UUIDヘッダーが未設定です");
      return [];
    }

    if (response.status === 500) {
      console.error("サーバーエラーが発生しました");
      return [];
    }

    if (!response.ok) {
      console.error("予期しないエラー:", response.status);
      return [];
    }

    return await response.json();
  } catch (error) {
    console.error("ネットワークエラー:", error);
    return [];
  }
}

async function toggleQuestCompleteWithErrorHandling(uuid: string, questId: number) {
  try {
    const response = await fetch(`http://localhost:8000/api/quests/${questId}/complete`, {
      method: "POST",
      headers: {
        "X-User-UUID": uuid,
      },
    });

    if (response.status === 400) {
      throw new Error("UUIDヘッダーが未設定です");
    }

    if (response.status === 404) {
      throw new Error("クエストが見つかりません");
    }

    if (response.status === 500) {
      console.error("サーバーエラーが発生しました");
    if (response.status === 500) {
      throw new Error("サーバーエラーが発生しました");
    }

    if (!response.ok) {
      throw new Error("予期しないエラーが発生しました");
    }

    return await response.json();
  } catch (error) {
    console.error("ネットワークエラー:", error);
    throw error;
  }
}
```

## データベーステーブル構成

### quests テーブル（Supabase）

| カラム名 | 型 | 説明 |
|---------|-----|------|
| `id` | integer | クエストID（主キー） |
| `uuid` | text | Supabaseの`public.users`テーブルの`uuid` |
| `title` | text | クエストのタイトル |
| `description` | text | クエストの説明 |
| `completed` | boolean | 完了フラグ（`true`: 完了、`false`: 未完了） |
| `day` | text | 日付（ISO 8601形式: `"2026-01-29"`） |
| `created_at` | timestamp | レコード作成日時 |
| `updated_at` | timestamp | レコード更新日時 |

### データ保存の動作

- **日付判定**: `day`カラムは`date.today().isoformat()`で保存され、`"2026-01-29"`形式
- **取得条件**: `uuid == X-User-UUID` かつ `day == date.today().isoformat()`
- **完了トグル**: `completed`フラグを反転（`false` → `true` または `true` → `false`）
- **AI生成時の動作**:
  1. AIが5件のクエストを生成（`/api/ai/recommendations/`経由）
  2. 既存の当日分クエストを削除
  3. 新規クエストを5件挿入（`completed=false`で初期化）

### Quest モデル（Django - 既存）

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| `id` | integer | クエストID（主キー） |
| `title` | string | クエストのタイトル |
| `description` | text | クエストの説明 |
| `owner` | ForeignKey | ユーザー（`AUTH_USER_MODEL`への外部キー） |
| `is_active` | boolean | アクティブフラグ |
| `created_at` | datetime | レコード作成日時 |

> **注意**: Django Modelは開発中のモデルであり、Supabaseとは別の用途です。本番では`/api/quests/get`（Supabase）を使用してください。

## 完全なフロー

### 1. 朝・夜アンケート送信

```bash
# 朝アンケート
POST /api/questionnaire/morning
Headers: X-User-UUID: <uuid>
Body: { "mood": "普通", "condition": "軽い", "free_text": "" }

# 夜アンケート
POST /api/questionnaire/night
Headers: X-User-UUID: <uuid>
Body: { "mood": "モヤモヤ", "condition": "だるい", "free_text": "" }
```

### 2. AI レコメンデーション生成

```bash
POST /api/ai/recommendations/
Headers: X-User-UUID: <uuid>
```

**レスポンス例:**
```json
{
  "quests": [
    { "title": "5分間の深呼吸", "description": "..." },
    { "title": "10分間の散歩", "description": "..." },
    ...
  ],
  "mascot": {
    "status": "Okay",
    "message": "今日は少しゆっくりいこう！"
  }
}
```

**内部動作:**
- `users_condition`テーブルから最新のconditionを取得
- OpenAI APIで5件のクエストとマスコット状態を生成
- `quests`テーブルに保存（既存の当日分は削除）
- `mascots`テーブルに保存（既存があれば更新）

### 3. 当日分クエスト取得

```bash
GET /api/quests/get
Headers: X-User-UUID: <uuid>
```

**レスポンス例:**
```json
[
  {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "5分間の深呼吸",
    "description": "朝の気分が少し重そうなので、リラックスのための深呼吸をおすすめします。",
    "completed": false,
    "day": "2026-01-29"
  },
  ...
]
```

### 4. クエスト完了/取り消し

```bash
POST /api/quests/1/complete
Headers: X-User-UUID: <uuid>
```

**レスポンス例:**
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "title": "5分間の深呼吸",
  "description": "朝の気分が少し重そうなので、リラックスのための深呼吸をおすすめします。",
  "completed": true,
  "day": "2026-01-29"
}
```

## 注意事項

1. **認証**: 現在は認証不要（`AllowAny`）ですが、`X-User-UUID`ヘッダーは必須です
2. **日付判定**: `date.today().isoformat()`で当日分を判定（`"2026-01-29"`形式）
3. **Supabase設定**: `SUPABASE_URL`と`SUPABASE_KEY`の環境変数が設定されている必要があります
4. **AI生成が前提**: `/api/ai/recommendations/`でクエストが生成される前提です
5. **クエスト数**: AIは5件のクエストを生成しますが、取得時は0件以上の任意の件数が返される可能性があります
6. **完了トグル**: `/api/quests/:quest_id/complete`で`completed`フラグを反転できます
7. **セキュリティ**: UUIDで他ユーザーのクエストへのアクセスを防止しています

## 環境変数

| 変数名 | 説明 |
|--------|------|
| `SUPABASE_URL` | Supabase プロジェクトURL |
| `SUPABASE_KEY` | Supabase APIキー |

## 依存関係

```
supabase
```

## 関連ファイル

- `views.py`: APIビューの実装（`QuestsGetView`, `QuestCompleteView`, `QuestViewSet`）
- `supabase_client.py`: Supabaseクライアントの初期化
- `urls.py`: URLルーティング設定
- `models.py`: Djangoモデル定義（開発用）
- `serializers.py`: シリアライザー定義（開発用）
- `tests.py`: APIテスト

## 関連API

### AI レコメンデーション
- [AIアプリREADME](../ai/README.md) - `/api/ai/recommendations/`でクエストを生成

### 朝夜アンケート
- [questionnairesアプリREADME](../questionnaires/README.md) - `/api/questionnaire/morning`、`/api/questionnaire/night`でユーザー状態を保存

### マスコット状態取得
- 別途実装が必要（`mascots`テーブルから取得）

## テスト

```bash
# クエストAPIのテストを実行
python manage.py test backend.apps.quests.tests

# 特定のテストクラスのみ実行
python manage.py test backend.apps.quests.tests.QuestsGetViewTests
python manage.py test backend.apps.quests.tests.QuestCompleteViewTests
```

**テストカバレッジ:**

**QuestsGetViewTests:**
- ✓ X-User-UUIDヘッダーなしの場合400エラー
- ✓ 正常系: 当日分クエスト取得成功
- ✓ クエストが0件の場合、空配列返却
- ✓ Supabase未設定の場合500エラー
- ✓ Supabase通信エラーの場合500エラー

**QuestCompleteViewTests:**
- ✓ X-User-UUIDヘッダーなしの場合400エラー
- ✓ 正常系: 未完了→完了のトグル
- ✓ 正常系: 完了→未完了のトグル
- ✓ クエストが存在しない場合404エラー
- ✓ 他のユーザーのクエストの場合404エラー
- ✓ Supabase未設定の場合500エラー
- ✓ Supabase通信エラーの場合500エラー

## トラブルシューティング

### クエストが取得できない

1. **X-User-UUIDヘッダーが設定されているか確認**
   ```bash
   curl -X GET http://localhost:8000/api/quests/get \
     -H "X-User-UUID: YOUR_UUID_HERE" -v
   ```

2. **Supabase環境変数が設定されているか確認**
   ```bash
   echo $SUPABASE_URL
   echo $SUPABASE_KEY
   ```

3. **AIレコメンデーションが実行されたか確認**
   ```bash
   # AIレコメンデーションを手動実行
   curl -X POST http://localhost:8000/api/ai/recommendations/ \
     -H "X-User-UUID: YOUR_UUID_HERE"
   ```

4. **Supabaseテーブルに直接クエリ**
   - Supabaseダッシュボードで`quests`テーブルを確認
   - `uuid`と`day`が一致するレコードがあるか確認

### 空配列が返される

- 当日分のクエストがまだ生成されていない可能性があります
- `/api/ai/recommendations/`を実行してクエストを生成してください

### クエスト完了が反映されない

1. **正しいquest_idを指定しているか確認**
   ```bash
   # まずクエスト一覧を取得してIDを確認
   curl -X GET http://localhost:8000/api/quests/get \
     -H "X-User-UUID: YOUR_UUID_HERE"
   
   # 取得したIDで完了APIを呼び出し
   curl -X POST http://localhost:8000/api/quests/123/complete \
     -H "X-User-UUID: YOUR_UUID_HERE"
   ```

2. **404エラーが返される場合**
   - クエストIDが存在しないか、他のユーザーのクエストです
   - `/api/quests/get`で取得したIDを使用してください

3. **完了状態がトグルされない場合**
   - レスポンスの`completed`フィールドを確認してください
   - 未完了→完了、完了→未完了が正しく反転します

### 500エラーが発生する

- Supabase接続情報が正しいか確認
- Supabaseプロジェクトがアクティブか確認
- ネットワーク接続を確認
