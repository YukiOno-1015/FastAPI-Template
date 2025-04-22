#!/usr/bin/env bash
# -*- coding: utf-8 -*-

: <<『DOCUMENTATION』
このスクリプトは Docker 環境をクリーンアップし、再構築します。
以下の機能を含みます:  
 1. root 権限チェック  
 2. 必要パッケージ (docker, docker-compose, gettext) のインストール  
 3. Docker Compose の停止・削除・プルーン  
 4. コンテナのビルド・起動  
 5. ネットワーク未存在時は作成  

Usage:  
  sudo ./clean_docker.sh  

環境: Ubuntu/Debian もしくは AlmaLinux/CentOS/RHEL 系をサポート
『DOCUMENTATION』

set -euo pipefail

#------------------------------
# 1. root 権限チェック
#------------------------------
if [[ "$EUID" -ne 0 ]]; then
  echo "[ERROR] root 権限が必要です。sudo で実行してください。"
  exit 1
fi

echo "[INFO] Starting Docker environment cleanup..."

# Docker ネットワーク名 (必要に応じて変更)
NETWORK_NAME="myapp_net"

#------------------------------
# 2. ネットワーク確認および作成
#------------------------------
if ! docker network ls --format '{{.Name}}' | grep -q "^${NETWORK_NAME}$"; then
  echo "[WARN] ネットワーク '${NETWORK_NAME}' が存在しないため作成します。"
  docker network create ${NETWORK_NAME}
  echo "[INFO] ネットワーク '${NETWORK_NAME}' を作成しました。"
else
  echo "[INFO] ネットワーク '${NETWORK_NAME}' は既に存在します。"
fi

#------------------------------
# 3. 必要パッケージのインストール
#------------------------------
echo "[INFO] Checking package manager and installing dependencies..."
if command -v apt-get &> /dev/null; then
  echo "[INFO] Detected APT package manager (Ubuntu/Debian)。"
  apt-get update
  apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    gettext-base

  # Docker リポジトリ設定
  mkdir -p /etc/apt/keyrings
  curl -fsSL "https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg" \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/$(. /etc/os-release && echo "$ID") \
    $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

elif command -v dnf &> /dev/null; then
  echo "[INFO] Detected DNF package manager (AlmaLinux/CentOS/RHEL)。"
  dnf install -y \
    yum-utils \
    device-mapper-persistent-data \
    lvm2 \
    gettext

  # Docker リポジトリ追加
  yum-config-manager --add-repo \
    https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/docker-ce.repo
  dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  systemctl enable --now docker
else
  echo "[ERROR] 対応していないパッケージマネージャーです。Docker と gettext を手動でインストールしてください。"
  exit 1
fi

echo "[INFO] Dependencies installation completed."

#------------------------------
# 4. Docker Compose down & prune
#------------------------------
echo "[INFO] Stopping and removing containers, images, volumes..."
docker compose down --rmi all -v

echo "[INFO] Pruning system..."
docker system prune -a --volumes -f

#------------------------------
# 5. Docker Compose up
#------------------------------
echo "[INFO] Rebuilding and starting containers..."
docker compose up --build -d

echo "[SUCCESS] Docker 環境のクリーンアップおよび再起動が完了しました！"
