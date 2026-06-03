from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class PermissionGroupStatusEnum(str, Enum):
    active  = "active"
    blocked = "blocked"


# ── Base ──────────────────────────────────────────────────────────────────────

class PermissionGroupBase(BaseModel):
    name:        str
    description: Optional[str] = None


# ── Create ────────────────────────────────────────────────────────────────────

class PermissionGroupCreate(PermissionGroupBase):
    pass


# ── Update ────────────────────────────────────────────────────────────────────

class PermissionGroupUpdate(BaseModel):
    name:        Optional[str]                      = None
    description: Optional[str]                      = None
    status:      Optional[PermissionGroupStatusEnum] = None


# ── Response ──────────────────────────────────────────────────────────────────

class PermissionGroupResponse(PermissionGroupBase):
    id:         int
    status:     PermissionGroupStatusEnum
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
