from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(500), nullable=False, index=True)
    inn = Column(String(12), nullable=True, index=True)
    ogrn = Column(String(15), nullable=True, index=True)
    
    legal_address = Column(Text, nullable=True)
    website = Column(Text, nullable=True)
    
    cbr_date_added = Column(DateTime, nullable=True)
    cbr_reason = Column(Text, nullable=True)
    cbr_category = Column(String(200), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    locations = relationship("Location", back_populates="organization", cascade="all, delete-orphan")
    enrichment_tasks = relationship("EnrichmentTask", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', inn='{self.inn}')>"
