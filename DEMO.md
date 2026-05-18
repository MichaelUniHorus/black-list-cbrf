# 🚀 Быстрый запуск ДЕМО

## Вариант 1: Один клик (Windows)

Просто запустите файл:
```
RUN_DEMO.bat
```

Дважды кликните на `RUN_DEMO.bat` в корне проекта.

## Вариант 2: Вручную

### Шаг 1: Запустите backend

```powershell
cd backend
python run_demo.py
```

### Шаг 2: Откройте демо-страницу

Откройте в браузере:
```
frontend/public/demo.html
```

Или перейдите по адресу:
```
http://localhost:8000/docs
```

## Что произойдет?

1. ✅ Автоматически создастся БД SQLite
2. ✅ Загрузятся первые 50 организаций из ЦБ РФ
3. ✅ Запустится API сервер на http://localhost:8000
4. ✅ Вы сможете открыть карту и посмотреть данные

## Доступные страницы

- **Демо-карта**: `frontend/public/demo.html`
- **API документация**: http://localhost:8000/docs
- **Статистика**: http://localhost:8000/api/stats
- **Список организаций**: http://localhost:8000/api/organizations

## Загрузка данных из ЦБ

После запуска сервера выполните:

```powershell
curl -X POST http://localhost:8000/api/admin/sync-cbr
```

Или через Swagger UI:
1. Откройте http://localhost:8000/docs
2. Найдите `POST /api/admin/sync-cbr`
3. Нажмите "Try it out" → "Execute"

## Остановка

Нажмите `Ctrl+C` в терминале где запущен сервер.

## Примечания

⚠️ **Это демо-версия:**
- Используется SQLite (не PostgreSQL)
- Celery и Redis НЕ запущены
- Фоновые задачи не работают
- Только для быстрого просмотра

✅ **Для полноценной работы используйте:**
```powershell
docker-compose up -d
```
