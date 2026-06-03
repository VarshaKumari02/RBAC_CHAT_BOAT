from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class RoleStatusEnum(str, Enum):
    active  = "active"
    blocked = "blocked"


# ── Base ──────────────────────────────────────────────────────────────────────

class RoleBase(BaseModel):
    name:        str
    description: Optional[str] = None


# ── Create ────────────────────────────────────────────────────────────────────

class RoleCreate(RoleBase):
    pass   # no extra fields needed


# ── Update ────────────────────────────────────────────────────────────────────

class RoleUpdate(BaseModel):
    name:        Optional[str]            = None
    description: Optional[str]            = None
    status:      Optional[RoleStatusEnum] = None


# ── Response ──────────────────────────────────────────────────────────────────

class RoleResponse(RoleBase):
    id:         int
    status:     RoleStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Assign Permissions ────────────────────────────────────────────────────────

class RoleAssignPermissions(BaseModel):
    permission_ids: list[int]


# ── Assign Role to User ───────────────────────────────────────────────────────

class UserRoleAssign(BaseModel):
    role_id:         int
    organization_id: Optional[int] = None


