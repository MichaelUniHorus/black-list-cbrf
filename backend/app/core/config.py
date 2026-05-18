from pydantic_settings import BaseSettings
from typing import List, Union
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "Open Black - Illegal Creditors Map"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    DEBUG: bool = True

    SECRET_KEY: str

    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379/0"

    YANDEX_MAPS_API_KEY: str

    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000,http://localhost:8001"

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            # Try to parse as JSON first
            try:
                return json.loads(self.CORS_ORIGINS)
            except:
                # If not JSON, split by comma
                return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    FLOWER_PORT: int = 5555
    FLOWER_BASIC_AUTH: str = "admin:password"

    CBR_BLACKLIST_URL: str = "https://cbr.ru/inside/warning-list/black-list-json"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
