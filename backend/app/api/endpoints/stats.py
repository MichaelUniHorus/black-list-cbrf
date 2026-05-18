from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.dependencies import get_db
from app.models import Organization, Location

router = APIRouter()


@router.get("/")
def get_stats(db: Session = Depends(get_db)):
    """
    Получить статистику
    """
    total_organizations = db.query(func.count(Organization.id)).filter(
        Organization.is_active == True
    ).scalar()
    
    total_locations = db.query(func.count(Location.id)).filter(
        Location.latitude.isnot(None),
        Location.longitude.isnot(None),
    ).scalar()
    
    organizations_with_locations = db.query(func.count(func.distinct(Location.organization_id))).filter(
        Location.latitude.isnot(None),
        Location.longitude.isnot(None),
    ).scalar()
    
    return {
        "total_organizations": total_organizations,
        "total_locations": total_locations,
        "organizations_with_locations": organizations_with_locations,
        "coverage_percent": round((organizations_with_locations / total_organizations * 100), 2) if total_organizations > 0 else 0,
    }
