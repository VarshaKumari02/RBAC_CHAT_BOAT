from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


# ── Enums (mirror your DB Enum values) ───────────────────────────────────────

class UserTypeEnum(str, Enum):
    b2c  = "b2c"
    att  = "att"
    b2g  = "b2g"
    capf = "capf"
    ltc  = "ltc"
    itdc = "itdc"


class UserStatusEnum(str, Enum):
    pending = "pending"
    active  = "active"
    blocked = "blocked"


# ── Base (shared fields, no password, no timestamps) ─────────────────────────

class UserBase(BaseModel):
    username:  str
    email:     EmailStr
    mobile:    str
    name:      str
    user_type: UserTypeEnum


# ── Create (POST /users — includes password) ──────────────────────────────────

class UserCreate(UserBase):
    password: str


# ── Update (PATCH /users/{id} — all fields optional) ─────────────────────────

class UserUpdate(BaseModel):
    name:      Optional[str]            = None
    mobile:    Optional[str]            = None
    email:     Optional[EmailStr]       = None
    status:    Optional[UserStatusEnum] = None
    user_type: Optional[UserTypeEnum]   = None


# ── Response (what the API returns — NO password field) ──────────────────────

class UserResponse(UserBase):
    id:            int
    status:        UserStatusEnum
    last_login_at: Optional[datetime] = None
    verified_at:   Optional[datetime] = None
    created_at:    datetime
    updated_at:    datetime

    class Config:
        from_attributes = True   # Pydantic v2 — converts SQLAlchemy ORM → schema
