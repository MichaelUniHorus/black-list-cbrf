# Быстрый старт

## Шаг 1: Установка зависимостей

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```powershell
cd frontend
npm install
```

## Шаг 2: Настройка окружения

Файл `.env` уже создан в корне проекта с вашим Yandex Maps API ключом.

## Шаг 3: Инициализация базы данных

```powershell
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Шаг 4: Запуск сервисов

### Вариант А: Docker Compose (рекомендуется)

```powershell
docker-compose up -d
```

Сервисы будут доступны:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower: http://localhost:5555

### Вариант Б: Ручной запуск

**Терминал 1 - Redis:**
```powershell
docker run -d -p 6379:6379 redis:7-alpine
```

**Терминал 2 - Backend:**
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Терминал 3 - Celery Worker:**
```powershell
cd backend
.\venv\Scripts\activate
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

**Терминал 4 - Celery Beat:**
```powershell
cd backend
.\venv\Scripts\activate
celery -A app.tasks.celery_app beat --loglevel=info
```

**Терминал 5 - Flower:**
```powershell
cd backend
.\venv\Scripts\activate
celery -A app.tasks.celery_app flower --port=5555
```

**Терминал 6 - Frontend:**
```powershell
cd frontend
npm run dev
```

## Шаг 5: Тестирование API (опционально)

Перед запуском всего проекта можно проверить работу API:

```powershell
cd backend
.\venv\Scripts\activate
python test_local.py
```

Этот скрипт проверит:
- ✅ Загрузку данных из ЦБ РФ
- ✅ Геокодирование адресов через Yandex Maps
- ✅ Поиск организаций через Yandex Maps

## Шаг 6: Загрузка данных из ЦБ РФ

### Вариант А: Через Swagger UI

Откройте http://localhost:8000/docs и выполните:

1. **POST `/api/admin/sync-cbr`** - загрузить данные из ЦБ РФ
2. Дождитесь завершения в Flower (http://localhost:5555)
3. **POST `/api/admin/enrich-all`** - обогатить ВСЕ организации через Yandex Maps
4. Следите за прогрессом в Flower

### Вариант Б: Через curl

```powershell
# 1. Синхронизация с ЦБ РФ
curl -X POST http://localhost:8000/api/admin/sync-cbr

# 2. Подождите ~1-2 минуты, затем обогатите данные
curl -X POST http://localhost:8000/api/admin/enrich-all
```

### Автоматическое расписание

После первоначальной настройки задачи будут запускаться автоматически:
- **02:00** - Синхронизация с ЦБ РФ
- **03:00** - Обогащение всех организаций через Yandex Maps

## Шаг 7: Открыть приложение

Откройте http://localhost:5173 в браузере

На карте появятся маркеры всех найденных точек нелегальных организаций.

## Полезные команды

### Просмотр логов Docker
```powershell
docker-compose logs -f
```

### Остановка всех сервисов
```powershell
docker-compose down
```

### Пересоздание контейнеров
```powershell
docker-compose up -d --build
```

### Создание новой миграции БД
```powershell
cd backend
alembic revision --autogenerate -m "описание изменений"
alembic upgrade head
```

## Troubleshooting

### Ошибка "Cannot connect to Redis"
Убедитесь что Redis запущен:
```powershell
docker ps | findstr redis
```

### Frontend lint ошибки
Это нормально до установки npm пакетов. Выполните:
```powershell
cd frontend
npm install
```

### Backend ошибки импорта
Убедитесь что виртуальное окружение активировано:
```powershell
cd backend
.\venv\Scripts\activate
```

### Celery не работает на Windows
Используйте параметр `--pool=solo`:
```powershell
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```
