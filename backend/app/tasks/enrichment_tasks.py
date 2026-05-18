from celery import Task
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models import Organization, Location, EnrichmentTask
from app.models.location import LocationSource, LocationStatus
from app.models.enrichment_task import TaskStatus, TaskType
from app.services import CBRService, YandexMapsService
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    _db: Session = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask)
def sync_cbr_data(self):
    """
    Синхронизация данных с черным списком ЦБ РФ
    """
    logger.info("Начало синхронизации с ЦБ РФ")
    
    cbr_service = CBRService()
    
    try:
        blacklist_data = asyncio.run(cbr_service.fetch_blacklist())
        
        new_count = 0
        updated_count = 0
        
        for item in blacklist_data:
            org_data = cbr_service.parse_organization(item)
            
            inn = org_data.get("inn")
            ogrn = org_data.get("ogrn")
            
            existing_org = None
            if inn:
                existing_org = self.db.query(Organization).filter(Organization.inn == inn).first()
            if not existing_org and ogrn:
                existing_org = self.db.query(Organization).filter(Organization.ogrn == ogrn).first()
            
            if existing_org:
                for key, value in org_data.items():
                    setattr(existing_org, key, value)
                existing_org.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                new_org = Organization(**org_data)
                self.db.add(new_org)
                new_count += 1
                
                if org_data.get("legal_address"):
                    location = Location(
                        organization=new_org,
                        address=org_data["legal_address"],
                        source=LocationSource.CBR,
                        status=LocationStatus.PENDING,
                    )
                    self.db.add(location)
        
        self.db.commit()
        
        logger.info(f"Синхронизация завершена: новых={new_count}, обновлено={updated_count}")
        return {"new": new_count, "updated": updated_count}
        
    except Exception as e:
        self.db.rollback()
        logger.error(f"Ошибка при синхронизации с ЦБ РФ: {e}")
        raise


@celery_app.task(bind=True, base=DatabaseTask)
def enrich_all_organizations(self):
    """
    Обогащение ВСЕХ организаций через Yandex Maps API
    Запускается по расписанию (раз в день)
    """
    logger.info("Начало обогащения всех организаций")
    
    yandex_service = YandexMapsService()
    
    organizations = self.db.query(Organization).filter(Organization.is_active == True).all()
    
    total_processed = 0
    total_locations_added = 0
    errors = 0
    
    for org in organizations:
        try:
            logger.info(f"Обработка организации ID={org.id}: {org.name}")
            
            locations_found = 0
            
            # 1. Геокодирование существующих адресов без координат
            for location in org.locations:
                if location.latitude is None and location.address:
                    coords = asyncio.run(yandex_service.geocode_address(location.address))
                    if coords:
                        location.latitude, location.longitude = coords
                        location.status = LocationStatus.VERIFIED
                        if location.source == LocationSource.CBR:
                            location.source = LocationSource.YANDEX_GEOCODE
                        locations_found += 1
                        logger.info(f"  Геокодирован адрес: {location.address[:50]}...")
            
            # 2. Поиск филиалов организации
            branches = asyncio.run(yandex_service.find_organization_branches(org.name, org.inn))
            
            for branch in branches:
                coords = branch.get("coordinates", [])
                if len(coords) == 2:
                    lon, lat = coords
                    
                    # Проверка на дубликаты по координатам
                    existing = self.db.query(Location).filter(
                        Location.organization_id == org.id,
                        Location.latitude == lat,
                        Location.longitude == lon,
                    ).first()
                    
                    if not existing:
                        new_location = Location(
                            organization_id=org.id,
                            address=branch.get("address", ""),
                            latitude=lat,
                            longitude=lon,
                            source=LocationSource.YANDEX_SEARCH,
                            status=LocationStatus.VERIFIED,
                            yandex_org_id=branch.get("yandex_id"),
                            phone=branch.get("phone"),
                            working_hours=branch.get("hours"),
                        )
                        self.db.add(new_location)
                        locations_found += 1
                        logger.info(f"  Найден филиал: {branch.get('address', '')[:50]}...")
            
            self.db.commit()
            
            total_processed += 1
            total_locations_added += locations_found
            
            logger.info(f"  Организация ID={org.id}: добавлено {locations_found} локаций")
            
        except Exception as e:
            self.db.rollback()
            errors += 1
            logger.error(f"Ошибка при обработке организации ID={org.id}: {e}")
            continue
    
    result = {
        "total_processed": total_processed,
        "total_locations_added": total_locations_added,
        "errors": errors,
    }
    
    logger.info(f"Обогащение завершено: {result}")
    return result


@celery_app.task(bind=True, base=DatabaseTask)
def enrich_organization_addresses(self, organization_id: int):
    """
    DEPRECATED: Используется только для ручного запуска через API
    Для автоматического обогащения используйте enrich_all_organizations
    
    Эта задача НЕ делает запросы к API, только возвращает статус
    """
    logger.info(f"Ручной запрос обогащения организации ID={organization_id}")
    
    org = self.db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        logger.error(f"Организация ID={organization_id} не найдена")
        return {"error": "Organization not found"}
    
    # Просто возвращаем текущее состояние
    locations_count = self.db.query(Location).filter(
        Location.organization_id == organization_id
    ).count()
    
    return {
        "message": "Обогащение происходит автоматически раз в день по расписанию",
        "organization_id": organization_id,
        "current_locations": locations_count,
        "note": "Для немедленного обогащения дождитесь запуска задачи enrich_all_organizations"
    }
