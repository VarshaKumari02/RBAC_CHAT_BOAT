from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.schemas.users import UserTypeEnum


# ── Register Request ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username:  str
    email:     EmailStr
    password:  str
    mobile:    str
    name:      str
    user_type: UserTypeEnum

    # Optional fields for non-B2C users (ltc_users table)
    firstname:             Optional[str] = None
    middlename:            Optional[str] = None
    lastname:              Optional[str] = None
    gender:                Optional[str] = None  # "m", "f", "o"
    organization_id:       Optional[int] = None
    department_id:         Optional[int] = None
    ltc_organization_name: Optional[str] = None
    ltc_department_name:   Optional[str] = None
    identification_number: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 characters")
        return v


# ── Admin Register Request ────────────────────────────────────────────────────

class AdminRegisterRequest(BaseModel):
    name:      str
    username:  str
    email:     EmailStr
    password:  str
    mobile:    str
    role_id:   int
    organization_id: Optional[int] = None

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 characters")
        return v


# ── Login Request ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


# ── Token Response (returned after login / register) ─────────────────────────

class TokenResponse(BaseModel):
    access_token:  Optional[str] = None
    token_type:    str = "bearer"
    expires_in:    Optional[int] = None
    message:       Optional[str] = None


# ── Token Payload (decoded from JWT) ─────────────────────────────────────────

class TokenPayload(BaseModel):
    sub:       int              # user id
    email:     str
    user_type: str
    exp:       Optional[int] = None
