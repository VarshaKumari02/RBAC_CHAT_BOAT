"""
app/controllers/auth_controller.py
────────────────────────────────────
Pure business logic — no FastAPI here, only DB + models + schemas.

Functions:
  • register_user  → create new user
  • login_user     → verify credentials, return JWT
  • get_my_profile → fetch current user's profile
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.users import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, AdminRegisterRequest
from app.schemas.users import UserResponse
from app.services.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    token_expires_in_seconds,
)
from app.models.ltc_user import LtcUser
from app.models.roles import Role
from app.models.user_has_role import UserHasRole
from app.models.wallets import Wallet
from app.models.organizations import Organization


# ── Register ──────────────────────────────────────────────────────────────────

def register_user(payload: RegisterRequest, db: Session) -> TokenResponse:
    # 1. Validation for non-B2C users
    if payload.user_type.value != "b2c":
        if not payload.firstname or not payload.lastname or not payload.gender:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Firstname, lastname, and gender are required for organizational users."
            )
        gender_val = payload.gender.lower()
        if gender_val not in ["m", "f", "o"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender must be one of 'm', 'f', or 'o'."
            )

    # 2. Check if user already exists
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    if db.query(User).filter(User.mobile == payload.mobile).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mobile number already registered",
        )

    # 3. Create User
    new_user = User(
        username  = payload.username,
        email     = payload.email,
        password  = hash_password(payload.password),
        mobile    = payload.mobile,
        name      = payload.name,
        user_type = payload.user_type,
        status    = "active",
        verified_at = datetime.now(timezone.utc),
    )
    db.add(new_user)
    db.flush()  # Populate new_user.id

    # 4. If non-B2C, create LtcUser record
    if payload.user_type.value != "b2c":
        # Check if the organization has an active/valid wallet
        wallet_access_val = "no"
        if payload.organization_id is not None:
            wallet_exists = db.query(Wallet).filter(
                Wallet.organization_id == payload.organization_id,
                Wallet.deleted_at == None
            ).first() is not None
            wallet_access_val = "yes" if wallet_exists else "no"

        ltc_detail = LtcUser(
            user_id=new_user.id,
            firstname=payload.firstname,
            middlename=payload.middlename,
            lastname=payload.lastname,
            gender=payload.gender.lower(),
            organization_id=payload.organization_id,
            department_id=payload.department_id,
            ltc_organization_name=payload.ltc_organization_name,
            ltc_department_name=payload.ltc_department_name,
            identification_number=payload.identification_number,
            wallet_access=wallet_access_val
        )
        db.add(ltc_detail)

    # 5. Map user to default 'User' role in user_has_roles
    default_role = db.query(Role).filter(Role.name == "User").first()
    role_id = default_role.id if default_role else 4
    
    user_role_mapping = UserHasRole(
        user_id=new_user.id,
        role_id=role_id,
        organization_id=payload.organization_id if payload.user_type.value != "b2c" else None
    )
    db.add(user_role_mapping)

    db.commit()
    db.refresh(new_user)

    return TokenResponse(
        message = "User registered successfully."
    )

def register_admin_user(payload: AdminRegisterRequest, db: Session) -> TokenResponse:
    # 1. Look up role
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with ID {payload.role_id} does not exist."
        )

    # 1.5. Validate organization if provided
    if payload.organization_id is not None:
        org = db.query(Organization).filter(Organization.id == payload.organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization with ID {payload.organization_id} does not exist."
            )

    # 2. Check if user already exists
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    if db.query(User).filter(User.mobile == payload.mobile).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mobile number already registered",
        )

    # 3. Create User with 'itdc' user_type
    new_user = User(
        username  = payload.username,
        email     = payload.email,
        password  = hash_password(payload.password),
        mobile    = payload.mobile,
        name      = payload.name,
        user_type = "itdc",
        status    = "active",
        verified_at = datetime.now(timezone.utc),
    )
    db.add(new_user)
    db.flush()  # Populate new_user.id

    # 4. Map user to the selected role in user_has_roles
    user_role_mapping = UserHasRole(
        user_id=new_user.id,
        role_id=role.id,
        organization_id=payload.organization_id
    )
    db.add(user_role_mapping)

    db.commit()
    db.refresh(new_user)

    return TokenResponse(
        message = f"ITDC Admin user registered successfully with role ID {payload.role_id}."
    )



# ── Login ─────────────────────────────────────────────────────────────────────

def login_user(payload: LoginRequest, db: Session) -> TokenResponse:

    # 1. Find user
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # 2. Verify password
    if not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # 3. Check status
    if user.status in ["blocked", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active. Please contact support.",
        )

    # 4. Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token({
        "sub":       str(user.id),
        "email":     user.email,
        "user_type": user.user_type,
    })

    return TokenResponse(
        access_token = token,
        expires_in   = token_expires_in_seconds(),
    )


# ── Get My Profile ────────────────────────────────────────────────────────────

def get_my_profile(current_user: User) -> UserResponse:
    """Return the currently logged-in user's profile."""
    return UserResponse.model_validate(current_user)
