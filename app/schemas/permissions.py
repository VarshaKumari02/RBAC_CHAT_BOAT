from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class PermissionStatusEnum(str, Enum):
    active  = "active"
    blocked = "blocked"
    deleted = "deleted"


# ── Base ──────────────────────────────────────────────────────────────────────

class PermissionBase(BaseModel):
    name:                str
    description:         Optional[str] = None
    permission_group_id: int


# ── Create ────────────────────────────────────────────────────────────────────

class PermissionCreate(PermissionBase):
    pass


# ── Update ────────────────────────────────────────────────────────────────────

class PermissionUpdate(BaseModel):
    name:                Optional[str]                  = None
    description:         Optional[str]                  = None
    permission_group_id: Optional[int]                  = None
    status:              Optional[PermissionStatusEnum] = None


# ── Response ──────────────────────────────────────────────────────────────────

class PermissionResponse(PermissionBase):
    id:         int
    status:     PermissionStatusEnum
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
