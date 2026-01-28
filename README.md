
## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install django==6.0.1
python manage.py migrate
python manage.py runserver
```

```

- **backend/**: Django + Django REST Framework による API サーバープロジェクト。
- **frontend/**: React Native アプリケーション用ディレクトリ。

### Django バックエンド (`backend/` 配下)

```text
backend/
├── apps/
│   ├── accounts/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── ai/
│   │   ├── apps.py
│   │   ├── migrations/
│   │   └── services.py
│   ├── conditions/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── logs/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── mascots/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── questionnaires/
│   │   ├── apps.py
│   │   ├── constants.py
│   │   ├── migrations/
│   │   ├── urls.py
│   │   └── views.py
│   └── quests/
│       ├── admin.py
│       ├── apps.py
│       ├── migrations/
│       ├── models.py
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── config/
│   ├── settings.py     # 単一ファイル構成の Django 設定
│   ├── urls.py         # /api/... 以下のルーティングを集約
│   ├── asgi.py
│   └── wsgi.py
├── manage.py           # バックエンド用 manage.py
└── requirements.txt    # バックエンドの Python 依存関係
```

- **backend/apps/**: ドメインごとの Django アプリをまとめたディレクトリ。
  - **accounts/**: 認証・アカウント管理関連。
  - **ai/**: AI 関連サービスロジック（`services.py` など）。
  - **conditions/**: 条件・状態管理に関するドメインモデル。
  - **logs/**: ログ・監査情報の管理。
  - **mascots/**: マスコットキャラクターなどのドメイン。
  - **questionnaires/**: アンケート・質問票機能。
  - **quests/**: クエスト
- **backend/config/**: バックエンドの Django プロジェクト設定。
- **backend/manage.py**: バックエンド用の Django 管理コマンドエントリポイント。
- **backend/requirements.txt**: バックエンドの Python 依存関係定義。

