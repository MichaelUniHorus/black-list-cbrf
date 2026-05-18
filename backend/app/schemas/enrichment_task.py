from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.enrichment_task import TaskStatus, TaskType


class EnrichmentTaskBase(BaseModel):
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING


class EnrichmentTaskCreate(EnrichmentTaskBase):
    organization_id: int


class EnrichmentTask(EnrichmentTaskBase):
    id: int
    organization_id: int
    celery_task_id: Optional[str] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
