import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=5000)


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=5000)


class ClientResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr | None
    phone: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
