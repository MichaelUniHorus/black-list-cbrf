"""
Скрипт для локального тестирования API интеграций
Запуск: python test_local.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.cbr_service import CBRService
from app.services.yandex_maps_service import YandexMapsService
from app.core.config import settings


async def test_cbr_api():
    """Тест загрузки данных из ЦБ РФ"""
    print("\n" + "="*60)
    print("ТЕСТ: Загрузка данных из ЦБ РФ")
    print("="*60)
    
    cbr = CBRService()
    
    try:
        data = await cbr.fetch_blacklist()
        print(f"✅ Успешно загружено открытых организаций: {len(data)}")
        
        if data:
            print("\n" + "-"*60)
            print("Примеры записей:")
            print("-"*60)
            
            # Показываем первые 3 записи
            for i, item in enumerate(data[:3], 1):
                print(f"\n{i}. Исходные данные от ЦБ:")
                print(f"   Name: {item.get('Name')}")
                print(f"   INN: {item.get('INN') or '(нет)'}")
                print(f"   ADDR: {item.get('ADDR') or '(нет)'}")
                print(f"   Site: {item.get('Site') or '(нет)'}")
                print(f"   Sign: {item.get('Sign')}")
                print(f"   OrgType: {item.get('OrgType')}")
                print(f"   Closed: {item.get('Closed')}")
                
                parsed = cbr.parse_organization(item)
                print(f"\n   Обработанные данные:")
                for key, value in parsed.items():
                    if value:
                        print(f"   {key}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_yandex_geocode():
    """Тест геокодирования адреса"""
    print("\n" + "="*60)
    print("ТЕСТ: Геокодирование адреса через Yandex Maps")
    print("="*60)
    
    yandex = YandexMapsService()
    test_address = "Москва, Красная площадь, 1"
    
    print(f"Адрес: {test_address}")
    
    try:
        coords = await yandex.geocode_address(test_address)
        if coords:
            print(f"✅ Координаты: {coords[0]}, {coords[1]}")
            print(f"   Google Maps: https://www.google.com/maps?q={coords[0]},{coords[1]}")
            return True
        else:
            print("❌ Координаты не найдены")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def test_yandex_search():
    """Тест поиска организации"""
    print("\n" + "="*60)
    print("ТЕСТ: Поиск организации через Yandex Maps")
    print("="*60)
    
    yandex = YandexMapsService()
    test_query = "Сбербанк Москва"
    
    print(f"Запрос: {test_query}")
    
    try:
        orgs = await yandex.search_organization(test_query, limit=3)
        print(f"✅ Найдено организаций: {len(orgs)}")
        
        for i, org in enumerate(orgs[:3], 1):
            print(f"\n  {i}. {org.get('name')}")
            print(f"     Адрес: {org.get('address')}")
            if org.get('phone'):
                print(f"     Телефон: {org.get('phone')}")
            if org.get('coordinates'):
                print(f"     Координаты: {org.get('coordinates')}")
        
        return len(orgs) > 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def main():
    print("\n" + "="*60)
    print("ПРОВЕРКА ЛОКАЛЬНОЙ РАБОТЫ API")
    print("="*60)
    print(f"\nYandex Maps API Key: {settings.YANDEX_MAPS_API_KEY[:20]}...")
    print(f"CBR URL: {settings.CBR_BLACKLIST_URL}")
    
    results = []
    
    # Тест ЦБ РФ
    results.append(("ЦБ РФ API", await test_cbr_api()))
    
    # Тест Yandex геокодинг
    results.append(("Yandex Геокодинг", await test_yandex_geocode()))
    
    # Тест Yandex поиск
    results.append(("Yandex Поиск", await test_yandex_search()))
    
    # Итоги
    print("\n" + "="*60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 Все тесты пройдены! API работают корректно.")
    else:
        print("\n⚠️  Некоторые тесты не прошли. Проверьте API ключи и подключение к интернету.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
