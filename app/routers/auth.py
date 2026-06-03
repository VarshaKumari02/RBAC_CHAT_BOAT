"""
app/routers/auth.py
────────────────────
API routes for authentication:

  POST /api/v1/auth/register  → create account + return token
  POST /api/v1/auth/login     → login + return token
  GET  /api/v1/auth/me        → get current user profile (protected)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, AdminRegisterRequest
from app.schemas.users import UserResponse
from app.controllers.auth_controller import register_user, login_user, get_my_profile, register_admin_user
from app.services.auth_dependency import get_current_user, has_permission
from app.models.users import User

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new user",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new user account.
    Returns a JWT access token on success.
    """
    return register_user(payload, db)

@router.post(
    "/register-admin",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new ITDC admin user",
)
def register_admin(
    payload: AdminRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Create Admin Users")),
):
    """
    Create a new ITDC administrative user.
    The user is assigned the 'itdc' user type and mapped directly to their designated role in user_has_roles.
    """
    return register_admin_user(payload, db)



@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate with email + password.
    Returns a JWT access token on success.
    """
    return login_user(payload, db)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current logged-in user profile",
)
def me(
    current_user: User = Depends(get_current_user),
):
    """
    Protected route — requires Authorization: Bearer <token>
    Returns the currently authenticated user's profile.
    """
    return get_my_profile(current_user)
