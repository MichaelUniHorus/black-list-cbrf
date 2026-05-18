import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CBRService:
    def __init__(self):
        self.blacklist_url = settings.CBR_BLACKLIST_URL
    
    async def fetch_blacklist(self) -> List[Dict[str, Any]]:
        """
        Загружает черный список из API ЦБ РФ
        Фильтрует только открытые организации (Closed = false)
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.blacklist_url)
                response.raise_for_status()
                data = response.json()
                
                # Извлекаем массив RC из ответа
                if isinstance(data, dict) and "RC" in data:
                    organizations = data["RC"]
                else:
                    organizations = data
                
                # Фильтруем только открытые организации
                open_orgs = [org for org in organizations if not org.get("Closed", False)]
                
                logger.info(f"Загружено {len(organizations)} организаций, из них открытых: {len(open_orgs)}")
                return open_orgs
                
        except httpx.HTTPError as e:
            logger.error(f"Ошибка при загрузке данных из ЦБ РФ: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке данных из ЦБ РФ: {e}")
            raise
    
    def parse_organization(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсит данные организации из формата ЦБ РФ
        
        Структура JSON от ЦБ:
        {
            "Id": 44292,
            "DT": "2026-05-15",
            "Name": "Access-Fortune, Accilent-Premium",
            "INN": "",
            "ADDR": null,
            "Site": "access-fortune.cc, accilent-premium.xyz",
            "Sign": "Признаки \"финансовой пирамиды\"",
            "Closed": false,
            "Comment": null,
            "DateUpdate": "2026-05-15T15:15:22.02",
            "OrgType": "Интернет-проект"
        }
        """
        # Название организации
        name = (item.get("Name") or "").strip()
        if not name:
            name = "Без названия"
        
        # ИНН (может быть пустой строкой или None)
        inn = (item.get("INN") or "").strip() or None
        
        # ОГРН (в данных ЦБ может не быть, но оставим для совместимости)
        ogrn = (item.get("OGRN") or "").strip() or None
        
        # Адрес (может быть null или пустым)
        addr_value = item.get("ADDR")
        address = addr_value.strip() if addr_value else None
        
        # Сайт (для интернет-проектов)
        site_value = item.get("Site")
        website = site_value.strip() if site_value else None
        
        # Дата добавления в список
        date_added = self._parse_date(item.get("DT"))
        
        # Признак нарушения
        sign_value = item.get("Sign")
        reason = sign_value.strip() if sign_value else None
        
        # Тип организации
        org_type_value = item.get("OrgType")
        org_type = org_type_value.strip() if org_type_value else None
        
        # Комментарий
        comment_value = item.get("Comment")
        comment = comment_value.strip() if comment_value else None
        
        # Объединяем категорию и комментарий
        category_parts = []
        if org_type:
            category_parts.append(org_type)
        if comment:
            category_parts.append(comment)
        category = " | ".join(category_parts) if category_parts else None
        
        return {
            "name": name,
            "inn": inn,
            "ogrn": ogrn,
            "legal_address": address,
            "website": website,
            "cbr_date_added": date_added,
            "cbr_reason": reason,
            "cbr_category": category,
        }
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Парсит дату из строки в формате ЦБ РФ
        Поддерживаемые форматы:
        - "2026-05-15" (ISO)
        - "15.05.2026" (DD.MM.YYYY)
        - "2026-05-15T15:15:22.02" (ISO с временем)
        """
        if not date_str:
            return None
        
        # Убираем время если есть
        date_str = date_str.split("T")[0]
        
        try:
            # Пробуем ISO формат (YYYY-MM-DD)
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                # Пробуем русский формат (DD.MM.YYYY)
                return datetime.strptime(date_str, "%d.%m.%Y")
            except ValueError:
                logger.warning(f"Не удалось распарсить дату: {date_str}")
                return None
