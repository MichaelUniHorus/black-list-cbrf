from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.api.dependencies import get_db
from app.models import Location
from app.schemas import location as schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Location])
def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    has_coordinates: bool = Query(True),
    db: Session = Depends(get_db),
):
    """
    Получить список локаций для отображения на карте
    """
    query = db.query(Location).options(joinedload(Location.organization))
    
    if has_coordinates:
        query = query.filter(
            Location.latitude.isnot(None),
            Location.longitude.isnot(None),
        )
    
    locations = query.offset(skip).limit(limit).all()
    return locations


@router.get("/failed", response_model=List[schemas.Location])
def get_failed_locations(
    db: Session = Depends(get_db),
):
    """
    Получить список адресов без координат (не удалось геокодировать)
    """
    from app.models.location import LocationStatus
    
    locations = db.query(Location).options(joinedload(Location.organization)).filter(
        Location.status == LocationStatus.PENDING
    ).all()
    
    return locations
