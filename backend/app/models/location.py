from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class LocationSource(str, enum.Enum):
    CBR = "cbr"
    YANDEX_GEOCODE = "yandex_geocode"
    YANDEX_SEARCH = "yandex_search"


class LocationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    address = Column(Text, nullable=False)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    source = Column(Enum(LocationSource), nullable=False, default=LocationSource.CBR)
    status = Column(Enum(LocationStatus), nullable=False, default=LocationStatus.PENDING)
    
    yandex_org_id = Column(String(100), nullable=True)
    
    phone = Column(String(50), nullable=True)
    working_hours = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="locations")
    
    def __repr__(self):
        return f"<Location(id={self.id}, address='{self.address[:50]}...', source='{self.source}')>"
