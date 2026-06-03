"""
app/controllers/roles_controller.py
──────────────────────────────────────
Pure business logic for Role-related endpoints.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.roles import Role
from app.models.permission import Permission
from app.models.role_has_permissions import RoleHasPermission
from app.schemas.roles import RoleCreate, RoleUpdate, RoleAssignPermissions

def get_roles(db: Session):
    return db.query(Role).all()

def get_role_by_id(role_id: int, db: Session) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    return role

def create_role(payload: RoleCreate, db: Session) -> Role:
    existing = db.query(Role).filter(Role.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role with name '{payload.name}' already exists"
        )
    
    new_role = Role(
        name=payload.name,
        description=payload.description,
        status="active"
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

def update_role(role_id: int, payload: RoleUpdate, db: Session) -> Role:
    role = get_role_by_id(role_id, db)
    
    if payload.name is not None and payload.name != role.name:
        existing = db.query(Role).filter(Role.name == payload.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role with name '{payload.name}' already exists"
            )
        role.name = payload.name
        
    if payload.description is not None:
        role.description = payload.description
        
    if payload.status is not None:
        role.status = payload.status.value
        
    role.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(role)
    return role

def delete_role(role_id: int, db: Session):
    role = get_role_by_id(role_id, db)
    
    # Optional: Check if there are users with this role before deleting
    # In a production system, we might prevent deleting if in use, or cascade.
    # Here, we will clean up role_has_permissions mappings first
    db.query(RoleHasPermission).filter(RoleHasPermission.role_id == role_id).delete()
    
    db.delete(role)
    db.commit()
    return {"message": f"Role {role_id} deleted successfully"}

def assign_role_permissions(role_id: int, payload: RoleAssignPermissions, db: Session):
    # 1. Verify role exists
    get_role_by_id(role_id, db)
    
    # 2. Verify all permission_ids exist
    if payload.permission_ids:
        existing_count = db.query(Permission).filter(Permission.id.in_(payload.permission_ids)).count()
        if existing_count != len(set(payload.permission_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more permission IDs are invalid"
            )
            
    # 3. Remove existing permissions for this role
    db.query(RoleHasPermission).filter(RoleHasPermission.role_id == role_id).delete()
    
    # 4. Add new permissions
    for perm_id in set(payload.permission_ids):
        db.add(RoleHasPermission(role_id=role_id, permission_id=perm_id))
        
    db.commit()
    return {"message": "Permissions assigned to role successfully"}

def get_role_permissions(role_id: int, db: Session):
    # Verify role exists
    get_role_by_id(role_id, db)
    
    # Query permissions assigned to role
    permissions = (
        db.query(Permission)
        .join(RoleHasPermission, Permission.id == RoleHasPermission.permission_id)
        .filter(RoleHasPermission.role_id == role_id)
        .all()
    )
    return permissions
