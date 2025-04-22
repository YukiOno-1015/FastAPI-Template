# syntax=docker/dockerfile:1
# -*- coding: utf-8 -*-
# ----------------------------------------
# FastAPI アプリケーション用 Dockerfile (マルチステージ構成)
# - Python 3.12 ベース
# - 日本語ロケール対応
# - Poetry 依存管理
# - ビルドとランタイムを分離
# ----------------------------------------

# 1. Builder ステージ: 依存関係のインストール
FROM python:3.12 AS builder

# 環境変数・ロケール設定
ENV LANG=ja_JP.UTF-8 \
    LANGUAGE=ja_JP:ja \
    LC_ALL=ja_JP.UTF-8 \
    TZ=Asia/Tokyo \
    PYTHONUNBUFFERED=1

# ビルドに必要なパッケージとロケール生成
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      curl \
      locales && \
    # 日本語ロケールを生成
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Poetry インストールと依存解決
COPY src/pyproject.toml src/poetry.lock /app/
RUN pip install --upgrade pip setuptools poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev --no-interaction --no-ansi

# アプリケーションコードをコピー
COPY src/ /app/

# 2. Runtime ステージ: 軽量実行環境
FROM python:3.12

# 環境変数・ロケール設定
ENV LANG=ja_JP.UTF-8 \
    LANGUAGE=ja_JP:ja \
    LC_ALL=ja_JP.UTF-8 \
    TZ=Asia/Tokyo \
    PYTHONUNBUFFERED=1

# ランタイムに必要なパッケージとロケール生成
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      locales \
      libpq5 \
      less \
      iputils-ping && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Builder からビルド成果物と依存パッケージをコピー
COPY --from=builder /app /app
COPY --from=builder /usr/local /usr/local

# Poetry のキャッシュ設定 (仮想環境を作成しない)
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/app/.cache/pypoetry

# ポート公開
EXPOSE 8000

# ENTRYPOINT: 起動時にマイグレーション実行→アプリ起動
ENTRYPOINT ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers --log-config /app/logging_config.yaml"]