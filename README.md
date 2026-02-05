# koko - メンタル連動型フィットネスアプリ（バックエンド）

**koko** は、マスコット「ココ」によるメンタル可視化・朝夜アンケート・クエスト・すれ違い機能を組み合わせ、  
「変わりたいけど、傷つきたくない」層の運動・メンタル継続を支えるアプリです。  
本リポジトリはその API サーバーで、Django + Django REST Framework で実装し、Supabase をデータベース・認証に利用しています。

### プロジェクト体制

- **開発実装メンバー**: 3人
  - **Berry7028**: 要件定義・実装・デザイン・デバック・レビュー
  - **Kamon-Tahara-504**: 要件定義・実装・デバック・レビュー
  - **motokiyamaguchi1026-dev**: 主にバックエンドを担当

- **資料制作メンバー**: 3人
  - **tokio0429**: 要件定義・市場調査・企画背景・アプリ概要・
  - **iizuka**: 要件定義・ターゲット層
  - **com-lang**: 要件定義・ペルソナ作成

### プロジェクト工程

- **開発開始日**: 2025/1/28
- **開発完了日**: 2025/2/4

## 主要機能

- 認証・アカウント連携（Supabase）
- 朝・夜のアンケート API（取得・回答保存）
- AI によるクエスト生成・レコメンデーション
- クエストの取得・完了管理 API
- すれ違い（StreetPass）ログ・データの提供

## 技術スタック

- Python 3.x / Django 6.x / Django REST Framework
- Supabase（データベース・認証）
- OpenAI API（クエスト生成）
- django-cors-headers / python-dotenv / supabase（Python SDK）

## プロジェクト構造

```
Team-11-django-backend/
├── backend/                         # Django プロジェクト本体
│   ├── apps/                        # ドメイン別 Django アプリ（/api/... で公開）
│   │   ├── __init__.py
│   │   ├── ai/                      # AI サービス（クエスト生成・レコメンド）
│   │   │   ├── apps.py
│   │   │   ├── urls.py
│   │   │   ├── views.py             # AI 関連エンドポイント
│   │   │   ├── services.py          # OpenAI 呼び出し等のビジネスロジック
│   │   │   ├── supabase_client.py   # Supabase 連携
│   │   │   ├── migrations/
│   │   │   └── README.md
│   │   │
│   │   ├── common/                  # 共通ルーティング・ユーティリティ
│   │   │   └── routers.py           # 共通ルーター定義
│   │   │
│   │   ├── questionnaires/          # アンケート（朝・夜の質問票）API
│   │   │   ├── apps.py
│   │   │   ├── admin.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   ├── constants.py         # 質問内容などの定数
│   │   │   ├── supabase_client.py
│   │   │   ├── migrations/
│   │   │   └── README.md
│   │   │
│   │   └── quests/                  # クエスト API（取得・完了・一覧）
│   │       ├── apps.py
│   │       ├── admin.py
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── urls.py
│   │       ├── views.py
│   │       ├── supabase_client.py
│   │       ├── migrations/
│   │       └── README.md
│   │
│   ├── config/                      # Django プロジェクト設定
│   │   ├── settings.py              # 設定（DB・CORS・Supabase・OpenAI 等）
│   │   ├── urls.py                  # ルート URL 設定（/api/... の集約）
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── manage.py                    # Django 管理コマンドのエントリポイント
│   └── requirements.txt             # Python 依存関係
│
├── frontend/                        # フロント用参照（API クライアント等）
│   └── api/
│       └── client.ts
│
├── .env.example                     # 環境変数サンプル
└── README.md
```

### ディレクトリの役割

- **backend/apps/**  
  ドメインごとの Django アプリ。各アプリは `urls.py` でルートを定義し、`config/urls.py` から `/api/...` でマウントされる。`views.py` で API、`serializers.py` で入出力のシリアライズ、Supabase を使うアプリは `supabase_client.py` で DB アクセスを行う。

- **backend/apps/ai/**  
  OpenAI を利用したクエスト生成・レコメンデーション。`services.py` に AI 呼び出しロジック、`views.py` で HTTP エンドポイントを提供。

- **backend/apps/common/**  
  複数アプリで共有するルーターやユーティリティ。`routers.py` で共通のルート定義を行う。

- **backend/apps/questionnaires/**  
  朝・夜のアンケート（質問票）の取得・回答保存。`constants.py` に質問文や選択肢などの定数を定義。

- **backend/apps/quests/**  
  クエストの一覧取得・取得・完了などの CRUD。Supabase のクエスト関連テーブルと連携。

- **backend/config/**  
  Django プロジェクトの設定。`settings.py` で DB・認証・CORS・環境変数を読み込み、`urls.py` で各アプリの URL を集約。

- **frontend/**  
  バックエンドリポジトリ内のフロント向け参照用（API クライアント定義など）。メインのフロントアプリは別リポジトリ（React Native）で管理。

## 補足

- API のルートは `config/urls.py` で `/api/...` に集約されています。
- 本番では `DJANGO_DEBUG=false` と適切な `DJANGO_ALLOWED_HOSTS` を設定してください。
