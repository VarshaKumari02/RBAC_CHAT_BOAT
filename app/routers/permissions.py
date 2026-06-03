"""
app/routers/permissions.py
────────────────────────────
FastAPI router for Permission and Permission Group CRUD operations.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.services.auth_dependency import has_permission
from app.models.users import User
from app.schemas.permissions import PermissionCreate, PermissionUpdate, PermissionResponse
from app.schemas.permission_groups import PermissionGroupCreate, PermissionGroupUpdate, PermissionGroupResponse
from app.controllers import permissions_controller

router = APIRouter(
    prefix="/api/v1/permissions",
    tags=["Permissions & Groups"],
)

# ── Permission Groups CRUD ────────────────────────────────────────────────────

@router.get(
    "/groups",
    response_model=List[PermissionGroupResponse],
    summary="List all permission groups",
)
def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Permissions")),
):
    """
    Get all active permission groups.
    Requires 'View Roles' permission.
    """
    return permissions_controller.get_permission_groups(db)

@router.post(
    "/groups",
    response_model=PermissionGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new permission group",
)
def create_group(
    payload: PermissionGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Create Permissions")),
):
    """
    Create a new permission group.
    Requires 'Create Roles' permission.
    """
    return permissions_controller.create_permission_group(payload, db)

@router.get(
    "/groups/{group_id}",
    response_model=PermissionGroupResponse,
    summary="Get details of a permission group",
)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Permissions")),
):
    """
    Retrieve details of a single permission group by ID.
    Requires 'View Roles' permission.
    """
    return permissions_controller.get_permission_group_by_id(group_id, db)

@router.put(
    "/groups/{group_id}",
    response_model=PermissionGroupResponse,
    summary="Update details of a permission group",
)
def update_group(
    group_id: int,
    payload: PermissionGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Update Permissions")),
):
    """
    Update a permission group's name, description, and status.
    Requires 'Update Roles' permission.
    """
    return permissions_controller.update_permission_group(group_id, payload, db)

@router.delete(
    "/groups/{group_id}",
    summary="Delete a permission group",
)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Delete Permissions")),
):
    """
    Soft-delete a permission group. Only allowed if group contains no active permissions.
    Requires 'Delete Roles' permission.
    """
    return permissions_controller.delete_permission_group(group_id, db)


# ── Permissions CRUD ──────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=List[PermissionResponse],
    summary="List all permissions",
)
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Permissions")),
):
    """
    Get all active/blocked permissions.
    Requires 'View Roles' permission.
    """
    return permissions_controller.get_permissions(db)

@router.post(
    "",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new permission",
)
def create_permission(
    payload: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Create Permissions")),
):
    """
    Create a new permission inside an existing group.
    Requires 'Create Roles' permission.
    """
    return permissions_controller.create_permission(payload, db)

@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Get details of a specific permission",
)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Permissions")),
):
    """
    Retrieve details of a single permission by ID.
    Requires 'View Roles' permission.
    """
    return permissions_controller.get_permission_by_id(permission_id, db)

@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Update details of a permission",
)
def update_permission(
    permission_id: int,
    payload: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Update Permissions")),
):
    """
    Update a permission's name, description, group, or status.
    Requires 'Update Roles' permission.
    """
    return permissions_controller.update_permission(permission_id, payload, db)

@router.delete(
    "/{permission_id}",
    summary="Delete a permission",
)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Delete Permissions")),
):
    """
    Soft-delete a permission and clean up its mapping to any roles.
    Requires 'Delete Roles' permission.
    """
    return permissions_controller.delete_permission(permission_id, db)
