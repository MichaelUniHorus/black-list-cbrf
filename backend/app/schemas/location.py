from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from app.models.location import LocationSource, LocationStatus

if TYPE_CHECKING:
    from app.schemas.organization import Organization


class LocationBase(BaseModel):
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: LocationSource = LocationSource.CBR
    status: LocationStatus = LocationStatus.PENDING
    yandex_org_id: Optional[str] = None
    phone: Optional[str] = None
    working_hours: Optional[str] = None


class LocationCreate(LocationBase):
    organization_id: int


class Location(LocationBase):
    id: int
    organization_id: int
    organization: Optional['Organization'] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
