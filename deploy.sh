#!/bin/bash

# Скрипт деплоя для black-list проекта на mikesdemos.ru

echo "Начинаем деплой..."

# Перейти в директорию проекта
cd /var/www/mikesdemos.ru/black-list || exit 1

# Pull из git
echo "Pull из git..."
git pull origin main

# Остановить старые контейнеры
echo "Остановка старых контейнеров..."
docker-compose -f docker-compose.prod.yml down

# Сборка и запуск новых контейнеров
echo "Сборка и запуск контейнеров..."
docker-compose -f docker-compose.prod.yml up -d --build

# Применение миграций
echo "Применение миграций..."
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

echo "Деплой завершен!"
