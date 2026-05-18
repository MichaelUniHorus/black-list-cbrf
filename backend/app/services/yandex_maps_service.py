import httpx
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class YandexMapsService:
    def __init__(self):
        self.api_key = settings.YANDEX_MAPS_API_KEY
        self.geocoder_url = "https://geocode-maps.yandex.ru/1.x/"
        self.search_url = "https://search-maps.yandex.ru/v1/"
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Геокодирование адреса - получение координат
        Возвращает (latitude, longitude) или None
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "apikey": self.api_key,
                    "geocode": address,
                    "format": "json",
                    "results": 1,
                }
                
                response = await client.get(self.geocoder_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                feature_member = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
                
                if not feature_member:
                    logger.warning(f"Не найдены координаты для адреса: {address}")
                    return None
                
                pos = feature_member[0]["GeoObject"]["Point"]["pos"]
                lon, lat = map(float, pos.split())
                
                logger.info(f"Геокодирован адрес '{address}': ({lat}, {lon})")
                return (lat, lon)
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP ошибка при геокодировании '{address}': {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при геокодировании '{address}': {e}")
            return None
    
    async def search_organization(
        self, 
        query: str, 
        location: Optional[Tuple[float, float]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Поиск организаций по названию/ИНН
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "apikey": self.api_key,
                    "text": query,
                    "type": "biz",
                    "lang": "ru_RU",
                    "results": limit,
                }
                
                if location:
                    params["ll"] = f"{location[1]},{location[0]}"
                    params["spn"] = "0.5,0.5"
                
                response = await client.get(self.search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                features = data.get("features", [])
                organizations = []
                
                for feature in features:
                    props = feature.get("properties", {})
                    company_meta = props.get("CompanyMetaData", {})
                    geo = feature.get("geometry", {})
                    
                    org_data = {
                        "name": props.get("name", ""),
                        "description": props.get("description", ""),
                        "address": company_meta.get("address", ""),
                        "coordinates": geo.get("coordinates", []),
                        "phone": company_meta.get("Phones", [{}])[0].get("formatted") if company_meta.get("Phones") else None,
                        "hours": company_meta.get("Hours", {}).get("text"),
                        "categories": company_meta.get("Categories", []),
                        "yandex_id": company_meta.get("id"),
                    }
                    
                    organizations.append(org_data)
                
                logger.info(f"Найдено {len(organizations)} организаций по запросу '{query}'")
                return organizations
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP ошибка при поиске организации '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Ошибка при поиске организации '{query}': {e}")
            return []
    
    async def find_organization_branches(
        self, 
        organization_name: str,
        inn: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск всех филиалов организации
        """
        search_query = organization_name
        if inn:
            search_query = f"{organization_name} ИНН {inn}"
        
        return await self.search_organization(search_query, limit=50)
