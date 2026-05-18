from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.location import Location
    from app.schemas.enrichment_task import EnrichmentTask


class OrganizationBase(BaseModel):
    name: str
    inn: Optional[str] = None
    ogrn: Optional[str] = None
    legal_address: Optional[str] = None
    website: Optional[str] = None
    cbr_date_added: Optional[datetime] = None
    cbr_reason: Optional[str] = None
    cbr_category: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class OrganizationDetail(Organization):
    locations: List["Location"] = []
    enrichment_tasks: List["EnrichmentTask"] = []
    
    model_config = ConfigDict(from_attributes=True)


# Rebuild models after all imports
def rebuild_models():
    from app.schemas.location import Location
    from app.schemas.enrichment_task import EnrichmentTask
    OrganizationDetail.model_rebuild()
