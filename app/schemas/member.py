import uuid

from pydantic import BaseModel, EmailStr

from app.models.membership import Role


class MemberResponse(BaseModel):
    membership_id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: EmailStr
    role: Role
    is_active: bool


class MemberRoleUpdate(BaseModel):
    role: Role
