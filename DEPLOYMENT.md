# Развертывание на сервере

## Структура директорий

```
/var/www/
├── mikesdemos.ru/
│   ├── black-list/          # Текущий проект
│   │   ├── backend/
│   │   ├── frontend/
│   │   ├── docker-compose.prod.yml
│   │   └── .env
│   ├── project2/            # Другие проекты
│   └── project3/
└── ssl/
    ├── mikesdemos.ru.crt
    └── mikesdemos.ru.key
```

## Требования к серверу

- Ubuntu
- Docker & Docker Compose
- nginx
- PostgreSQL (внешняя на сервере, не в Docker)
- SSL сертификаты

## Установка PostgreSQL на сервере

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создать пользователя и БД
sudo -u postgres psql
CREATE DATABASE openblack;
CREATE USER openblack WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE openblack TO openblack;
\q
```

## Путь проекта

- Домен: mikesdemos.ru
- Путь: /black-list
- Frontend: https://mikesdemos.ru/black-list
- Backend API: https://mikesdemos.ru/black-list/api

## Пошаговый деплой

### Шаг 1: Загрузка в GitHub (локально)

```bash
# Инициализировать git репозиторий (если еще не инициализирован)
git init

# Добавить файлы в git
git add DEPLOYMENT.md docker-compose.prod.yml nginx.conf deploy.sh frontend/nginx.conf frontend/Dockerfile .env.example

# Коммит
git commit -m "Добавить конфигурации для продакшена"

# Создать репозиторий на GitHub (вручную через github.com)

# Добавить remote (заменить на ваш URL)
git remote add origin https://github.com/ваш-username/ваш-репозиторий.git

# Пуш в GitHub
git branch -M main
git push -u origin main
```

### Шаг 2: Подготовка сервера

```bash
# SSH на сервер
ssh user@your-server-ip

# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Шаг 3: Установить PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создать БД и пользователя
sudo -u postgres psql
CREATE DATABASE openblack;
CREATE USER openblack WITH PASSWORD 'ваш-надежный-пароль';
GRANT ALL PRIVILEGES ON DATABASE openblack TO openblack;
\q
```

### Шаг 4: Установить nginx

```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Шаг 5: Создать структуру директорий

```bash
sudo mkdir -p /var/www/mikesdemos.ru/black-list
sudo chown -R $USER:$USER /var/www/mikesdemos.ru
```

### Шаг 6: Получить SSL сертификат через Let's Encrypt

```bash
# Установить certbot
sudo apt install certbot python3-certbot-nginx -y

# Получить сертификат (nginx должен быть запущен)
sudo certbot --nginx -d mikesdemos.ru

# Сертификаты будут автоматически установлены в /etc/letsencrypt/live/mikesdemos.ru/
```

### Шаг 7: Клонировать репозиторий

```bash
cd /var/www/mikesdemos.ru/black-list
git clone https://github.com/ваш-username/ваш-репозиторий.git .
```

### Шаг 8: Настроить .env

```bash
cp .env.example .env
nano .env
# Изменить:
# - DATABASE_URL (пароль от PostgreSQL)
# - YANDEX_MAPS_API_KEY
# - SECRET_KEY
```

### Шаг 9: Настроить nginx

```bash
sudo cp nginx.conf /etc/nginx/sites-available/mikesdemos.ru
sudo ln -s /etc/nginx/sites-available/mikesdemos.ru /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

**Важно:** Сначала certbot настроит nginx автоматически, потом мы заменим конфиг на наш с проксированием.

### Шаг 10: Запустить проект

```bash
cd /var/www/mikesdemos.ru/black-list
docker-compose -f docker-compose.prod.yml up -d --build
```

### Шаг 11: Применить миграции

```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Шаг 12: Проверить

Открыть в браузере: https://mikesdemos.ru/black-list

## Обновление

```bash
cd /var/www/mikesdemos.ru/black-list
./deploy.sh
```
