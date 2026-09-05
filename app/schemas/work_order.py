import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.work_order import Priority, WorkOrderStatus


class WorkOrderCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str | None = Field(default=None, max_length=10000)
    client_id: uuid.UUID | None = None
    assigned_to_id: uuid.UUID | None = None
    priority: Priority = Priority.medium
    due_at: datetime | None = None


class WorkOrderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=180)
    description: str | None = Field(default=None, max_length=10000)
    client_id: uuid.UUID | None = None
    assigned_to_id: uuid.UUID | None = None
    status: WorkOrderStatus | None = None
    priority: Priority | None = None
    due_at: datetime | None = None


class WorkOrderResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID | None
    created_by_id: uuid.UUID
    assigned_to_id: uuid.UUID | None
    title: str
    description: str | None
    status: WorkOrderStatus
    priority: Priority
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
