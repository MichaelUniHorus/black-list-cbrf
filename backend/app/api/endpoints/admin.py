from fastapi import APIRouter
from app.tasks import sync_cbr_data, enrich_all_organizations

router = APIRouter()


@router.post("/sync-cbr")
def trigger_cbr_sync():
    """
    Запустить синхронизацию с ЦБ РФ
    Загружает данные из черного списка и создает/обновляет организации
    """
    task = sync_cbr_data.delay()
    
    return {
        "message": "CBR sync task started",
        "task_id": task.id,
        "note": "После завершения этой задачи запустите /admin/enrich-all для обогащения данных"
    }


@router.post("/enrich-all")
def trigger_enrich_all():
    """
    Запустить обогащение ВСЕХ организаций через Yandex Maps
    Геокодирует адреса и ищет филиалы
    """
    task = enrich_all_organizations.delay()
    
    return {
        "message": "Enrichment task started for all organizations",
        "task_id": task.id,
        "note": "Эта задача может занять продолжительное время. Следите за прогрессом в Flower (http://localhost:5555)"
    }
