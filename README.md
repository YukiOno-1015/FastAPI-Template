# FastAPI Template

このリポジトリは、[FastAPI](https://fastapi.tiangolo.com/) を使った Web アプリケーション開発を効率化するテンプレートです。
開発環境から本番環境まで、**Docker**、**Nginx**、**環境変数管理**を備えた構成になっています。
さらに**Firebase Auth**を利用した認証機能も標準で組み込まれています。

---

## 🌟 特徴

- **FastAPI フレームワーク対応**  
  モダンで高速な REST API の開発をサポート。
- **API バージョン管理**  
  [fastapi-versioning](https://pypi.org/project/fastapi-versioning/) を利用し、`v{major}_{minor}` 形式のバージョンプレフィックスを自動付与（例: `/v0_1`）。さらに `enable_latest=True` を設定済みのため、常に最新バージョンを `/latest` でも呼び出せます。
- **Firebase Authentication対応**  
  Firebase Auth を用いたユーザー認証機能を内蔵。メール/パスワード認証、Google アカウント認証など各種認証方法をサポートしています。
- **Docker 対応**  
  単一の `docker-compose.yml` でバックエンド (`backend`) と PostgreSQL (`db`) を含むサービスを同時に起動可能。
- **Nginx リバースプロキシ**  
  セキュアかつ高速なトラフィック管理を実現。
- **環境変数管理**  
  プロジェクトルートの `.env` で設定を一本化。
- **クリーンアップスクリプト**  
  `clean_docker.sh` で Docker 環境を一括リセット。

---

## 📂 ディレクトリ構成

```bash
FastAPI-Template/                         # プロジェクトルート
├── backend/                              # FastAPI アプリケーションコード
│   └── src/
│       └── utils/ 　　　　　　　　　　　　　# 共通ユーティリティ
│              └── firebase_service_account.json  # Firebase サービスアカウント　JSON                       
├── nginx/                                # Nginx 設定ファイル
├── .env                                  # 環境変数ファイル
├── docker-compose.yml                    # Docker Compose 設定
├── clean_docker.sh                       # Docker 環境リセットスクリプト (sudo 必須)
├── .gitignore                            # Git 無視設定
├── LICENSE                               # ライセンス情報
└── README.md                             # このファイル
```

---

## ⚙️ 環境のセットアップ

### 🔧 必要条件

- Docker
- Docker Compose
- Git
- Firebase プロジェクト（認証用）

### 📥 リポジトリをクローン

```bash
git clone -b main https://github.com/YukiOno-1015/FastAPI-Template.git
cd FastAPI-Template
```

### 📝 環境変数の準備

プロジェクトルートの `.env` ファイルを編集し、以下の内容を設定します。例:

```env
# アプリケーション環境 (development/production)
ENVIRONMENT=development

# 外部公開用 NGINX ポート
NGINX_PORT=8080
# 外部公開用 PostgreSQL ポート
POSTGRES_PORT=54320

# DB 名、ユーザ、パスワード
POSTGRES_DB=fastapi
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password

# Docker ネットワーク名
NETWORK_NAME=myapp_net

# Backend 固定リッスンポート（Docker内部）
BACKEND_PORT=8000

# アプリ接続用 DATABASE_URL
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# タイムゾーン
TZ=Asia/Tokyo
```

### 🔒 Firebase サービスアカウントの配置

1. Firebase コンソールを開き、プロジェクト設定 > サービスアカウント から新しい秘密鍵を生成し、JSON ファイルをダウンロード。
2. ダウンロードした `serviceAccountKey.json` を `backend/src/utils/firebase_service_account.json` として配置。

### 🚀 サーバーの起動

```bash
docker compose up --build
```

起動後、以下の URL にアクセスできます:

- **API エンドポイント (バージョン 0.1)**  
  `http://127.0.0.1:8000/v0_1/`

- **API エンドポイント (最新版)**  
  `http://127.0.0.1:8000/latest/`

- **Swagger UI (バージョン 0.1)**  
  `http://127.0.0.1:8000/v0_1/docs`

- **Swagger UI (最新版)**  
  `http://127.0.0.1:8000/latest/docs`

- **ReDoc UI (バージョン 0.1)**  
  `http://127.0.0.1:8000/v0_1/redoc`

- **ReDoc UI (最新版)**  
  `http://127.0.0.1:8000/latest/redoc`

---

## 🧹 クリーンアップスクリプト

`clean_docker.sh` を使うと、以下を自動で実行します:

1. すべてのコンテナ停止＆削除  
2. イメージ・ボリューム・ネットワークの未使用リソース削除  
3. 開発環境を再構築＆起動  

```bash
# ※このコマンドには sudo 権限が必要です
sudo bash clean_docker.sh
```

---

## 🌱 環境変数

以下の変数を `.env` ファイルに定義します。

| 変数名               | 説明                                       | 例                                               |
|----------------------|--------------------------------------------|--------------------------------------------------|
| `ENVIRONMENT`        | アプリケーション環境 (development/production) | `development`                                   |
| `NGINX_PORT`         | 外部公開用 Nginx ポート                    | `8080`                                           |
| `POSTGRES_PORT`      | 外部公開用 PostgreSQL ポート               | `54320`                                          |
| `POSTGRES_DB`        | データベース名                             | `fastapi`                                        |
| `POSTGRES_USER`      | データベースユーザ                         | `dev_user`                                       |
| `POSTGRES_PASSWORD`  | データベースパスワード                     | `dev_password`                                   |
| `NETWORK_NAME`       | Docker ネットワーク名                      | `myapp_net`                                      |
| `BACKEND_PORT`       | Backend 固定リッスンポート（Docker内部）    | `8000`                                           |
| `DATABASE_URL`       | アプリ接続用 DB URL                        | `postgresql://dev_user:dev_password@db:5432/fastapi` |
| `TZ`                 | コンテナ内のタイムゾーン                   | `Asia/Tokyo`                                     |

---

## 💡 貢献方法

1. リポジトリをフォーク  
2. `feature/xxx` ブランチを作成  
   ```bash
   git checkout -b feature/your-feature
   ```
3. 変更をコミット  
   ```bash
   git commit -m "Add your feature"
   ```
4. プッシュ＆プルリクエスト作成  

---

## 📜 ライセンス

MIT ライセンスのもとで公開しています。詳細は [LICENSE](LICENSE) を参照してください。

---

## 🔗 参考サイト

- FastAPI: https://fastapi.tiangolo.com/  
- Uvicorn: https://www.uvicorn.org/  
- Docker: https://docs.docker.com/  
- Docker Compose: https://docs.docker.com/compose/  
- Nginx: https://nginx.org/en/docs/  
- Python dotenv: https://pypi.org/project/python-dotenv/  
- pytest: https://docs.pytest.org/  
- Firebase Authentication: https://firebase.google.com/docs/auth  
