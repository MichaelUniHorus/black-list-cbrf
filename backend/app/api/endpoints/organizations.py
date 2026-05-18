from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.dependencies import get_db
from app.models import Organization, Location
from app.schemas import organization as schemas
from app.tasks import enrich_organization_addresses

router = APIRouter()


@router.get("/", response_model=List[schemas.Organization])
def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Получить список организаций с пагинацией и поиском
    """
    query = db.query(Organization).filter(Organization.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Organization.name.ilike(search_filter)) |
            (Organization.inn.ilike(search_filter)) |
            (Organization.ogrn.ilike(search_filter))
        )
    
    organizations = query.offset(skip).limit(limit).all()
    return organizations


@router.get("/{organization_id}", response_model=schemas.OrganizationDetail)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить детальную информацию об организации
    """
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.post("/{organization_id}/enrich")
def enrich_organization(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Запустить обогащение данных организации
    """
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    task = enrich_organization_addresses.delay(organization_id)
    
    return {
        "message": "Enrichment task started",
        "task_id": task.id,
        "organization_id": organization_id,
    }
