#!/bin/bash

# Docker Compose 関連を削除
docker compose -f docker-compose.dev.yml down --rmi all -v

# システム全体のクリーンアップ
docker system prune -a --volumes -f

echo "Docker environment has been cleaned up!"

docker compose -f docker-compose.dev.yml up --build -d