import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: Optional[str]
    tier: str
    is_active: bool


class RoleUpdateRequest(BaseModel):
    role: str  # buyer | supplier
