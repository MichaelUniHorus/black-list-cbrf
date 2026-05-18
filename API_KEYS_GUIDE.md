# Инструкции по получению API ключей

Для работы проекта необходимо получить API ключ только от Yandex Maps.

---

## 1. Yandex Maps API

**Лимиты:** Бесплатно до 25,000 запросов в день

### Шаги получения:

1. **Перейдите на страницу Yandex Developer**
   - URL: https://developer.tech.yandex.ru/

2. **Войдите в аккаунт Яндекс**
   - Если нет аккаунта - зарегистрируйтесь на https://passport.yandex.ru/

3. **Перейдите в раздел "Мои сервисы"**
   - URL: https://developer.tech.yandex.ru/services/

4. **Подключите JavaScript API и HTTP Геокодер**
   - Нажмите "Подключить API"
   - Выберите "JavaScript API" и "HTTP Геокодер"
   - Заполните форму:
     - Название проекта: "Карта нелегальных организаций"
     - Тип использования: "Веб-сервис"
     - Домены (для dev): `localhost`, `127.0.0.1`

5. **Получите API ключ**
   - После создания проекта скопируйте ключ
   - Ключ выглядит так: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

6. **Сохраните ключ в `.env`**
   ```env
   YANDEX_MAPS_API_KEY=ваш_ключ_здесь
   ```

### Документация:
- JavaScript API: https://yandex.ru/dev/maps/jsapi/doc/2.1/
- Геокодер: https://yandex.ru/dev/maps/geocoder/
- Organizations API: https://yandex.ru/dev/maps/geosearch/

### Дополнительные возможности Yandex Maps:

**Organizations API (Поиск организаций):**
- Позволяет искать организации по названию, ИНН, адресу
- Получать информацию о всех филиалах компании
- Извлекать контактные данные, часы работы
- Лимит входит в общий лимит 25,000 запросов/день

**Использование:**
```bash
# Поиск организации по названию
curl "https://search-maps.yandex.ru/v1/?text=Название+организации&type=biz&lang=ru_RU&apikey=ВАШ_КЛЮЧ"
```

---

## Итоговый файл `.env`

После получения ключа Yandex Maps создайте файл `.env` в корне проекта:

```env
# Database
DATABASE_URL=sqlite:///./app.db
# DATABASE_URL=postgresql://user:password@localhost:5432/openblack  # для production

# Redis
REDIS_URL=redis://localhost:6379/0

# Yandex Maps API
YANDEX_MAPS_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# App Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Flower (мониторинг Celery)
FLOWER_PORT=5555
FLOWER_BASIC_AUTH=admin:password
```

---

## Проверка работоспособности API

После получения ключей можно проверить их работу:

### Yandex Maps (геокодирование)
```bash
curl "https://geocode-maps.yandex.ru/1.x/?apikey=ВАШ_КЛЮЧ&geocode=Москва,+Тверская+улица,+7&format=json"
```

### Yandex Maps (поиск организации)
```bash
curl "https://search-maps.yandex.ru/v1/?text=микрозайм&type=biz&lang=ru_RU&apikey=ВАШ_КЛЮЧ"
```

---

## Важные замечания

1. **Безопасность:**
   - Никогда не коммитьте `.env` файл в Git
   - Добавьте `.env` в `.gitignore`
   - Используйте разные ключи для dev и production

2. **Лимиты:**
   - Следите за лимитами запросов
   - Используйте кеширование для экономии запросов
   - Добавьте rate limiting в приложение

3. **Мониторинг:**
   - Логируйте все API запросы
   - Отслеживайте ошибки и лимиты
   - Используйте Flower для мониторинга фоновых задач

---

## Полезные ссылки

- **Yandex Maps API:** https://yandex.ru/dev/maps/
- **Yandex Geocoder:** https://yandex.ru/dev/maps/geocoder/
- **Yandex Organizations API:** https://yandex.ru/dev/maps/geosearch/
- **Flower (Celery monitoring):** https://flower.readthedocs.io/
