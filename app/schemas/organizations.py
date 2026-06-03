from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class OrgTypeEnum(str, Enum):
    government = "government"
    psu        = "psu"


class OrgStatusEnum(str, Enum):
    active  = "active"
    blocked = "blocked"


# ── Base ──────────────────────────────────────────────────────────────────────

class OrganizationBase(BaseModel):
    name:              str
    description:       Optional[str] = None
    organization_type: OrgTypeEnum
    wallet_access:     bool = False


# ── Create ────────────────────────────────────────────────────────────────────

class OrganizationCreate(OrganizationBase):
    pass


# ── Update ────────────────────────────────────────────────────────────────────

class OrganizationUpdate(BaseModel):
    name:              Optional[str]           = None
    description:       Optional[str]           = None
    organization_type: Optional[OrgTypeEnum]   = None
    wallet_access:     Optional[bool]          = None
    status:            Optional[OrgStatusEnum] = None


# ── Response ──────────────────────────────────────────────────────────────────

class OrganizationResponse(OrganizationBase):
    id:         int
    status:     OrgStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
