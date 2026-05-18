from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import organizations, locations, admin, stats

Base.metadata.create_all(bind=engine)

# Rebuild Pydantic models for forward references
try:
    from app.schemas.organization import rebuild_models
    rebuild_models()
except:
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    organizations.router,
    prefix=f"{settings.API_V1_STR}/organizations",
    tags=["organizations"],
)

app.include_router(
    locations.router,
    prefix=f"{settings.API_V1_STR}/locations",
    tags=["locations"],
)

app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["admin"],
)

app.include_router(
    stats.router,
    prefix=f"{settings.API_V1_STR}/stats",
    tags=["stats"],
)


@app.get("/")
def root():
    return {
        "message": "Open Black API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
