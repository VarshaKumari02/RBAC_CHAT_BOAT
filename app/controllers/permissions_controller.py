"""
app/controllers/permissions_controller.py
─────────────────────────────────────────────
Pure business logic for Permission and Permission Group endpoints.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.permission import Permission
from app.models.permission_groups import PermissionGroup
from app.models.role_has_permissions import RoleHasPermission
from app.schemas.permissions import PermissionCreate, PermissionUpdate
from app.schemas.permission_groups import PermissionGroupCreate, PermissionGroupUpdate

# ── Permissions CRUD ──────────────────────────────────────────────────────────

def get_permissions(db: Session):
    return db.query(Permission).filter(Permission.status != "deleted").all()

def get_permission_by_id(permission_id: int, db: Session) -> Permission:
    permission = db.query(Permission).filter(Permission.id == permission_id, Permission.status != "deleted").first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID {permission_id} not found"
        )
    return permission

def create_permission(payload: PermissionCreate, db: Session) -> Permission:
    # Verify permission group exists
    group = db.query(PermissionGroup).filter(PermissionGroup.id == payload.permission_group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission group with ID {payload.permission_group_id} does not exist"
        )

    existing = db.query(Permission).filter(Permission.name == payload.name).first()
    if existing:
        if existing.status == "deleted":
            # Resurrect the deleted permission
            existing.status = "active"
            existing.description = payload.description
            existing.permission_group_id = payload.permission_group_id
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission with name '{payload.name}' already exists"
            )
            
    new_perm = Permission(
        name=payload.name,
        description=payload.description,
        permission_group_id=payload.permission_group_id,
        status="active"
    )
    db.add(new_perm)
    db.commit()
    db.refresh(new_perm)
    return new_perm

def update_permission(permission_id: int, payload: PermissionUpdate, db: Session) -> Permission:
    permission = get_permission_by_id(permission_id, db)
    
    if payload.permission_group_id is not None:
        group = db.query(PermissionGroup).filter(PermissionGroup.id == payload.permission_group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission group with ID {payload.permission_group_id} does not exist"
            )
        permission.permission_group_id = payload.permission_group_id

    if payload.name is not None and payload.name != permission.name:
        existing = db.query(Permission).filter(Permission.name == payload.name).first()
        if existing and existing.id != permission_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission with name '{payload.name}' already exists"
            )
        permission.name = payload.name
        
    if payload.description is not None:
        permission.description = payload.description
        
    if payload.status is not None:
        permission.status = payload.status.value
        
    permission.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(permission)
    return permission

def delete_permission(permission_id: int, db: Session):
    permission = get_permission_by_id(permission_id, db)
    
    # Soft delete
    permission.status = "deleted"
    permission.deleted_at = datetime.now(timezone.utc)
    
    # Remove from role mapping
    db.query(RoleHasPermission).filter(RoleHasPermission.permission_id == permission_id).delete()
    
    db.commit()
    return {"message": f"Permission {permission_id} soft-deleted successfully"}


# ── Permission Groups CRUD ────────────────────────────────────────────────────

def get_permission_groups(db: Session):
    return db.query(PermissionGroup).filter(PermissionGroup.deleted_at == None).all()

def get_permission_group_by_id(group_id: int, db: Session) -> PermissionGroup:
    group = db.query(PermissionGroup).filter(PermissionGroup.id == group_id, PermissionGroup.deleted_at == None).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission Group with ID {group_id} not found"
        )
    return group

def create_permission_group(payload: PermissionGroupCreate, db: Session) -> PermissionGroup:
    existing = db.query(PermissionGroup).filter(PermissionGroup.name == payload.name).first()
    if existing:
        if existing.deleted_at is not None:
            # Resurrect deleted group
            existing.deleted_at = None
            existing.description = payload.description
            existing.status = "active"
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission Group with name '{payload.name}' already exists"
            )
            
    new_group = PermissionGroup(
        name=payload.name,
        description=payload.description,
        status="active"
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def update_permission_group(group_id: int, payload: PermissionGroupUpdate, db: Session) -> PermissionGroup:
    group = get_permission_group_by_id(group_id, db)
    
    if payload.name is not None and payload.name != group.name:
        existing = db.query(PermissionGroup).filter(PermissionGroup.name == payload.name).first()
        if existing and existing.id != group_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission Group with name '{payload.name}' already exists"
            )
        group.name = payload.name
        
    if payload.description is not None:
        group.description = payload.description
        
    if payload.status is not None:
        group.status = payload.status.value
        
    group.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(group)
    return group

def delete_permission_group(group_id: int, db: Session):
    group = get_permission_group_by_id(group_id, db)
    
    # Check if there are active permissions inside this group
    permissions_count = db.query(Permission).filter(
        Permission.permission_group_id == group_id, 
        Permission.status != "deleted"
    ).count()
    if permissions_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete group. It contains {permissions_count} active permissions. Delete or reassign them first."
        )
        
    # Soft delete
    group.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": f"Permission Group {group_id} deleted successfully"}
