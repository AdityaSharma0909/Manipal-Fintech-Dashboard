#!/bin/bash
set -e

echo "🚀 Starting deployment (DEV)..."

# Containers to stop/remove
CONTAINERS=(
  docker-manipal_app-1
  docker-manipal_app-2
)

IMAGE="manipal_app:development"
COMPOSE_FILE="docker/docker-compose-dev.yml"

echo "🛑 Stopping containers..."
for c in "${CONTAINERS[@]}"; do
  docker stop "$c" 2>/dev/null || true
done

echo "🧹 Removing containers..."
for c in "${CONTAINERS[@]}"; do
  docker rm "$c" 2>/dev/null || true
done

echo "🗑️ Removing image if exists..."
docker rmi "$IMAGE" 2>/dev/null || true

echo "🐳 Building & starting containers..."
docker compose --env-file .env -f "$COMPOSE_FILE" up -d --build


echo "🔁 Restarting gateway..."
sudo docker restart manipal_gateway

echo "✅ Deployment completed successfully!"

