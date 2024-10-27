# ベースイメージにPython 3.12を指定
FROM python:3.12

# ルートユーザーで操作
USER root

# ワークディレクトリの設定
WORKDIR /app

# Debianリポジトリの設定と必要なパッケージのインストール
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y install \
    less \
    locales \
    vim && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 && \
    mkdir -p /var/log/backend && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 環境変数の設定 (日本語対応)
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV TZ=Asia/Tokyo
ENV TERM=xterm

# pipとsetuptoolsのアップグレード
RUN pip install --upgrade pip setuptools

# 依存関係のコピーとインストール
COPY ./backend/requirements.txt .

RUN pip install -r requirements.txt

# FastAPIアプリケーションの起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-config", "/app/logging_config.yaml"]
