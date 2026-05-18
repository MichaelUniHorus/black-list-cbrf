"""
Быстрый запуск демо-версии с тестовыми данными
Запуск: python run_demo.py
"""
import os
import sys
import asyncio
from pathlib import Path

# Устанавливаем переменные окружения ДО импорта приложения
os.environ.setdefault("SECRET_KEY", "demo-secret-key-change-in-production")
os.environ.setdefault("DATABASE_URL", "sqlite:///./demo.db")
os.environ.setdefault("YANDEX_MAPS_API_KEY", "b32b31d1-1157-4757-a682-66b6dbd87544")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

print("="*60)
print("🚀 ЗАПУСК ДЕМО-ВЕРСИИ OPEN BLACK")
print("="*60)
print()
print("📝 Используются тестовые настройки:")
print(f"   DATABASE: SQLite (demo.db)")
print(f"   API KEY: {os.environ['YANDEX_MAPS_API_KEY'][:20]}...")
print()

# Создаем БД
from app.core.database import Base, engine
from app.models import Organization, Location, EnrichmentTask

print("📦 Создание таблиц БД...")
Base.metadata.create_all(bind=engine)
print("✅ Таблицы созданы")
print()

# Загружаем тестовые данные
from app.core.database import SessionLocal
from app.services.cbr_service import CBRService
from app.models.location import LocationSource, LocationStatus

async def load_demo_data():
    print("📥 Загрузка демо-данных из ЦБ РФ (Алтайский край)...")
    
    db = SessionLocal()
    
    # Проверяем существующие данные
    existing_orgs = db.query(Organization).count()
    existing_locs = db.query(Location).count()
    if existing_orgs > 0:
        print(f"ℹ️  В БД уже есть {existing_orgs} организаций и {existing_locs} адресов")
        print(f"� Проверяем новые записи из ЦБ РФ...")
    
    try:
        cbr = CBRService()
        data = await cbr.fetch_blacklist()
        
        # Фильтруем только организации из Алтайского края
        altay_region = "алтайский край"
        filtered_data = [
            item for item in data 
            if item.get("ADDR") and altay_region in item.get("ADDR", "").lower()
        ]
        
        print(f"📊 Найдено {len(filtered_data)} организаций в Алтайском крае из {len(data)} всего")
        
        # Загружаем только организации из Алтайского края
        new_orgs_count = 0
        new_locs_count = 0
        skipped_orgs = 0
        skipped_locs = 0
        
        for item in filtered_data:
            org_data = cbr.parse_organization(item)
            
            # Проверяем существующую организацию по INN
            existing_org = db.query(Organization).filter(
                Organization.inn == org_data.get("inn")
            ).first()
            
            if existing_org:
                org = existing_org
                skipped_orgs += 1
            else:
                org = Organization(**org_data)
                db.add(org)
                db.flush()  # Чтобы получить ID организации
                new_orgs_count += 1
            
            # Создаем адреса для организации (может быть несколько)
            if org_data.get("legal_address"):
                # Разбиваем адрес по точке с запятой (может быть несколько адресов)
                raw_address = org_data["legal_address"]
                # Разделяем по ; и \r\n
                addresses = [addr.strip() for addr in raw_address.replace('\r\n', ';').split(';') if addr.strip()]
                
                for address in addresses:
                    # Проверяем существующий location по адресу
                    existing_loc = db.query(Location).filter(
                        Location.organization_id == org.id,
                        Location.address == address
                    ).first()
                    
                    if existing_loc:
                        skipped_locs += 1
                        continue  # Пропускаем если адрес уже существует
                    
                    try:
                        from app.services.yandex_maps_service import YandexMapsService
                        yandex = YandexMapsService()
                        
                        # Геокодируем адрес
                        coords = await yandex.geocode_address(address)
                        
                        if coords:
                            lat, lon = coords
                            location = Location(
                                organization=org,
                                address=address,
                                latitude=lat,
                                longitude=lon,
                                source=LocationSource.CBR,
                                status=LocationStatus.VERIFIED,
                            )
                            db.add(location)
                            new_locs_count += 1
                        else:
                            # Если не удалось геокодировать, сохраняем без координат
                            location = Location(
                                organization=org,
                                address=address,
                                source=LocationSource.CBR,
                                status=LocationStatus.PENDING,
                            )
                            db.add(location)
                            new_locs_count += 1
                            print(f"   ⚠️  НЕ ГЕОКОДИРОВАНО: {address}")
                        
                    except Exception as e:
                        print(f"   ❌ ОШИБКА ГЕОКОДИРОВАНИЯ: {address}")
                        print(f"      Причина: {e}")
                        # Сохраняем без координат
                        location = Location(
                            organization=org,
                            address=address,
                            source=LocationSource.CBR,
                            status=LocationStatus.PENDING,
                        )
                        db.add(location)
                        new_locs_count += 1
        
        db.commit()
        print(f"✅ Загружено {new_orgs_count} новых организаций (пропущено {skipped_orgs} существующих)")
        print(f"✅ Загружено {new_locs_count} новых адресов (пропущено {skipped_locs} существующих)")
        
    except Exception as e:
        import traceback
        print(f"⚠️  Ошибка при загрузке данных: {e}")
        print("   Traceback:")
        traceback.print_exc()
        print("   Продолжаем без данных...")
        db.rollback()
    finally:
        db.close()

# Загружаем данные
asyncio.run(load_demo_data())

print()
print("="*60)
print("🌐 ЗАПУСК ВЕБ-СЕРВЕРА")
print("="*60)
print()
print("📍 Сервер будет доступен по адресу:")
print("   🔗 http://localhost:8001")
print("   📖 API Docs: http://localhost:8001/docs")
print()
print("⚠️  ВАЖНО:")
print("   - Это ДЕМО-версия только для тестирования")
print("   - Используется SQLite вместо PostgreSQL")
print("   - Celery и Redis НЕ запущены (фоновые задачи не работают)")
print("   - Для полноценной работы используйте docker-compose")
print()
print("🛑 Для остановки нажмите Ctrl+C")
print("="*60)
print()

# Запускаем сервер
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
