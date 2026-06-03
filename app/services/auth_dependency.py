from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.users import User
from app.services.auth_utils import decode_access_token
from app.models.user_has_role import UserHasRole
from app.models.role_has_permissions import RoleHasPermission
from app.models.permission import Permission

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload malformed",
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload malformed",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}",
        )

    return user



def has_permission(required_permission: str):
    """
    Dependency factory that checks if the logged-in user's roles
    possess the specified permission.
    """
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 1. Fetch user roles
        role_mappings = db.query(UserHasRole).filter(UserHasRole.user_id == current_user.id).all()
        role_ids = [rm.role_id for rm in role_mappings]
        
        if not role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User has no roles assigned"
            )
            
        # 2. Check if any assigned role contains the permission
        has_perm = (
            db.query(Permission)
            .join(RoleHasPermission, Permission.id == RoleHasPermission.permission_id)
            .filter(
                RoleHasPermission.role_id.in_(role_ids),
                Permission.name == required_permission,
                Permission.status == "active"
            )
            .first() is not None
        )
        
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Missing required permission '{required_permission}'"
            )
            
        return current_user
        
    return dependency




def has_booking_permission(required_permission: str):
    """
    Smart dependency factory for booking endpoints:
    - Normal users (b2g, att, capf, ltc, b2c): only need to be authenticated.
      They will bypass database permission checks completely.
    - ITDC admin users: must have the specified permission.
    """
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        user_type_val = (
            current_user.user_type.value
            if hasattr(current_user.user_type, "value")
            else current_user.user_type
        )

        # Normal users — authentication is enough, no permission checks
        if user_type_val != "itdc":
            return current_user

        # ITDC users — must have the specified permission
        role_mappings = db.query(UserHasRole).filter(UserHasRole.user_id == current_user.id).all()
        role_ids = [rm.role_id for rm in role_mappings]

        if not role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: ITDC user has no roles assigned"
            )

        has_perm = (
            db.query(Permission)
            .join(RoleHasPermission, Permission.id == RoleHasPermission.permission_id)
            .filter(
                RoleHasPermission.role_id.in_(role_ids),
                Permission.name == required_permission,
                Permission.status == "active"
            )
            .first() is not None
        )

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: ITDC user is missing required permission '{required_permission}'"
            )

        return current_user

    return dependency
