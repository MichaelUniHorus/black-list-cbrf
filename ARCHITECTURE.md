# Архитектура проекта

## Принципы работы с внешними API

### ⚠️ Важно: Запросы только по расписанию

Все запросы к внешним API (ЦБ РФ и Yandex Maps) выполняются **ТОЛЬКО по расписанию** через Celery Beat:

- **02:00 UTC** - Синхронизация с ЦБ РФ (`sync_cbr_data`)
- **03:00 UTC** - Обогащение всех организаций (`enrich_all_organizations`)

Это сделано для:
1. ✅ Экономии лимитов API (25,000 запросов/день для Yandex Maps)
2. ✅ Предотвращения rate limiting
3. ✅ Централизованного управления обновлениями
4. ✅ Минимизации нагрузки на внешние сервисы

## Структура базы данных

### Таблица `organizations`

Хранит информацию об организациях из черного списка ЦБ РФ.

```sql
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    inn VARCHAR(12),
    ogrn VARCHAR(15),
    legal_address TEXT,
    cbr_date_added DATETIME,
    cbr_reason TEXT,
    cbr_category VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Таблица `locations`

**Отдельная таблица** для хранения всех адресов организаций.

Связь: `locations.organization_id` → `organizations.id` (One-to-Many)

```sql
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL,  -- FK к organizations
    address TEXT NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    source ENUM('cbr', 'yandex_geocode', 'yandex_search'),
    status ENUM('pending', 'verified', 'failed'),
    yandex_org_id VARCHAR(100),
    phone VARCHAR(50),
    working_hours TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

**Источники данных (`source`):**
- `cbr` - юридический адрес из ЦБ РФ
- `yandex_geocode` - геокодированный адрес из ЦБ
- `yandex_search` - найденный филиал через Yandex Maps

### Таблица `enrichment_tasks`

Хранит историю задач обогащения данных.

```sql
CREATE TABLE enrichment_tasks (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    task_type ENUM('geocode', 'search_branches', 'full_enrichment'),
    status ENUM('pending', 'running', 'completed', 'failed'),
    celery_task_id VARCHAR(100),
    result TEXT,
    error_message TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

## Процесс обработки данных

### 1. Синхронизация с ЦБ РФ (ежедневно в 02:00)

```
sync_cbr_data()
    ↓
Загрузка JSON из https://cbr.ru/inside/warning-list/black-list-json
    ↓
Для каждой организации:
    ├─ Поиск по ИНН/ОГРН
    ├─ UPDATE если существует
    └─ CREATE если новая
        └─ Создать Location с юридическим адресом (source='cbr')
```

### 2. Обогащение данных (ежедневно в 03:00)

```
enrich_all_organizations()
    ↓
Для каждой активной организации:
    ├─ Геокодирование адресов без координат
    │   └─ Yandex Geocoder API
    │       └─ UPDATE location: latitude, longitude, source='yandex_geocode'
    │
    └─ Поиск филиалов
        └─ Yandex Organizations API
            └─ Для каждого найденного филиала:
                ├─ Проверка на дубликаты (по координатам)
                └─ CREATE новый Location (source='yandex_search')
```

## API Endpoints

### Публичные

- `GET /api/organizations` - список организаций
- `GET /api/organizations/{id}` - детали организации
- `GET /api/locations` - все точки для карты
- `GET /api/stats` - статистика

### Административные

- `POST /api/admin/sync-cbr` - ручной запуск синхронизации с ЦБ
- `POST /api/admin/enrich-all` - ручной запуск обогащения всех организаций

### Устаревшие (deprecated)

- `POST /api/organizations/{id}/enrich` - не делает запросы к API, только возвращает статус

## Celery задачи

### Периодические (Celery Beat)

```python
celery_app.conf.beat_schedule = {
    "sync-cbr-daily": {
        "task": "app.tasks.enrichment_tasks.sync_cbr_data",
        "schedule": crontab(hour=2, minute=0),  # 02:00 UTC
    },
    "enrich-all-organizations-daily": {
        "task": "app.tasks.enrichment_tasks.enrich_all_organizations",
        "schedule": crontab(hour=3, minute=0),  # 03:00 UTC
    },
}
```

### Ручные

- `sync_cbr_data()` - синхронизация с ЦБ РФ
- `enrich_all_organizations()` - обогащение всех организаций
- `enrich_organization_addresses(org_id)` - deprecated, только для обратной совместимости

## Мониторинг

### Flower (http://localhost:5555)

Веб-интерфейс для мониторинга Celery:
- Активные задачи
- История выполнения
- Статистика workers
- Графики производительности

### Логирование

Все задачи логируют:
- Начало/завершение выполнения
- Количество обработанных записей
- Ошибки с полным traceback

## Оптимизация запросов

### Дедупликация

Перед созданием новой локации проверяется:
1. Существует ли организация с таким ИНН/ОГРН
2. Существует ли локация с такими координатами

### Batch processing

Обогащение выполняется пакетно:
- Все организации обрабатываются в одной задаче
- Commit в БД после каждой организации (для сохранения прогресса)
- Ошибки одной организации не останавливают обработку остальных

### Rate limiting

Yandex Maps API имеет лимит 25,000 запросов/день:
- При ~1000 организациях и ~5 филиалах каждая = ~6000 запросов/день
- Запас: ~19,000 запросов для роста базы

## Тестирование

### Локальное тестирование API

```bash
cd backend
python test_local.py
```

Проверяет:
- ✅ Доступность ЦБ РФ API
- ✅ Работу Yandex Maps геокодера
- ✅ Работу Yandex Maps поиска организаций

### Ручной запуск задач

```bash
# Синхронизация с ЦБ
curl -X POST http://localhost:8000/api/admin/sync-cbr

# Обогащение всех организаций
curl -X POST http://localhost:8000/api/admin/enrich-all
```

## Масштабирование

### Горизонтальное

Можно запустить несколько Celery workers:

```bash
celery -A app.tasks.celery_app worker --concurrency=4
```

### Вертикальное

Увеличить лимиты задач:

```python
task_time_limit=60 * 60  # 1 час вместо 30 минут
```

### Партиционирование

Для больших объемов можно разделить обогащение:
- По регионам
- По дате добавления в ЦБ
- По алфавиту

## Безопасность

1. **API ключи** хранятся в `.env` (не коммитятся в Git)
2. **Rate limiting** на уровне Celery (не более 1 задачи обогащения одновременно)
3. **Валидация данных** через Pydantic схемы
4. **SQL injection** защита через SQLAlchemy ORM

## Будущие улучшения

- [ ] Кеширование результатов геокодирования
- [ ] Webhooks для уведомлений о новых организациях
- [ ] Экспорт данных в различных форматах
- [ ] Интеграция с другими источниками данных
- [ ] ML для определения вероятности нелегальной деятельности
