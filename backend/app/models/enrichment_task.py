from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, enum.Enum):
    GEOCODE = "geocode"
    SEARCH_BRANCHES = "search_branches"
    FULL_ENRICHMENT = "full_enrichment"


class EnrichmentTask(Base):
    __tablename__ = "enrichment_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    
    celery_task_id = Column(String(100), nullable=True, index=True)
    
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="enrichment_tasks")
    
    def __repr__(self):
        return f"<EnrichmentTask(id={self.id}, type='{self.task_type}', status='{self.status}')>"
