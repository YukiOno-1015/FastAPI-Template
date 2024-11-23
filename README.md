# FastAPI Template

このリポジトリは、[FastAPI](https://fastapi.tiangolo.com/)を使用したWebアプリケーションの開発を効率化するテンプレートです。Docker、Nginx、環境変数管理の仕組みを備え、開発環境から本番環境まで対応しています。

## 特徴

- **FastAPIフレームワーク対応**: モダンで高速なAPI開発をサポート。
- **Docker対応**: 開発と本番環境用に分かれたDocker Compose構成。
- **Nginxリバースプロキシ**: 本番環境でセキュアなトラフィック管理を実現。
- **クリーンアップスクリプト**: `clean_docker.sh`を使用して、Docker環境を簡単にリセット可能。

---

## ディレクトリ構成

```bash
FastAPI-Template/
├── backend/                 # FastAPIアプリケーションのソースコード
├── nginx/                   # Nginx設定ファイル
├── .env.dev                 # 開発環境用の環境変数
├── .env.prod                # 本番環境用の環境変数
├── .gitignore               # Git無視ファイルリスト
├── README.md                # このドキュメント
├── docker-compose.dev.yml   # 開発環境用Docker Compose設定
├── docker-compose.prod.yml  # 本番環境用Docker Compose設定
└── clean_docker.sh          # Docker環境クリーンアップスクリプト
```

---

## 環境のセットアップ

### 必要条件

- **Docker** および **Docker Compose** がインストールされていること。

---

### 開発環境の構築

1. **リポジトリをクローン**:

   ```bash
   git clone https://github.com/YukiOno-1015/FastAPI-Template.git
   cd FastAPI-Template
   ```

2. **環境変数を設定**:
   `.env.dev` を必要に応じて編集します。

3. **Docker Composeで起動**:

   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

4. **アクセス**:
   ブラウザで [http://127.0.0.1:8000](http://127.0.0.1:8000) を開いて、FastAPIの起動を確認します。

---

### 本番環境の構築

1. **環境変数を設定**:
   `.env.prod` を編集します。

2. **Docker Composeで起動**:

   ```bash
   docker compose -f docker-compose.prod.yml up --build -d
   ```

3. **Nginx設定**:
   `nginx/` フォルダ内の設定ファイルを確認し、必要に応じて編集してください。

---

## クリーンアップスクリプト

`clean_docker.sh` は、Docker環境をリセットし、開発環境を再構築するスクリプトです。

### 使用方法

1. **実行**

   ```bash
   bash clean_docker.sh
   ```

2. **スクリプトが行うこと**:
   - 現在のDocker Composeサービスを停止し、すべてのイメージとボリュームを削除
   - システム全体で未使用のDockerリソース（イメージ、ネットワーク、ボリュームなど）を削除
   - 開発環境を再構築し、起動

---

## 環境変数

`.env.dev` および `.env.prod` で以下の変数を設定します。

| 変数名         | 説明                                  | 例                                   |
| -------------- | ------------------------------------- | ------------------------------------ |
| `APP_ENV`      | 環境のタイプ (development/production) | `development`                        |
| `DATABASE_URL` | データベース接続URL                   | `postgresql://user:pass@db:5432/app` |
| その他         | 必要に応じて追加してください          |                                      |

---

## 貢献方法

このプロジェクトへの貢献は大歓迎です！以下の手順に従ってください：

1. **リポジトリをフォーク**。
2. **フィーチャーブランチを作成**:

   ```bash
   git checkout -b feature/your-feature
   ```

3. **変更をコミット**:

   ```bash
   git commit -m "Add your feature"
   ```

4. **リモートリポジトリへプッシュ**:

   ```bash
   git push origin feature/your-feature
   ```

5. **プルリクエストを作成**。

---

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。
