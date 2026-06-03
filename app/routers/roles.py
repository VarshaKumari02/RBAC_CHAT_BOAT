"""
app/routers/roles.py
──────────────────────
FastAPI router for Role CRUD operations and permission assignment.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.services.auth_dependency import has_permission
from app.models.users import User
from app.schemas.roles import RoleCreate, RoleUpdate, RoleResponse, RoleAssignPermissions
from app.schemas.permissions import PermissionResponse
from app.controllers import roles_controller

router = APIRouter(
    prefix="/api/v1/roles",
    tags=["Roles"],
)

@router.get(
    "",
    response_model=List[RoleResponse],
    summary="List all roles",
)
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Roles")),
):
    """
    Get all system roles.
    Requires 'View Roles' permission.
    """
    return roles_controller.get_roles(db)

@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Create Roles")),
):
    """
    Create a new role with active status.
    Requires 'Create Roles' permission.
    """
    return roles_controller.create_role(payload, db)

@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get details of a specific role",
)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Roles")),
):
    """
    Retrieve details of a single role by ID.
    Requires 'View Roles' permission.
    """
    return roles_controller.get_role_by_id(role_id, db)

@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update details of a role",
)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Update Roles")),
):
    """
    Update a role's name, description, and status.
    Requires 'Update Roles' permission.
    """
    return roles_controller.update_role(role_id, payload, db)

@router.delete(
    "/{role_id}",
    summary="Delete a role",
)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Delete Roles")),
):
    """
    Delete a role and clean up its permission assignments.
    Requires 'Delete Roles' permission.
    """
    return roles_controller.delete_role(role_id, db)

@router.post(
    "/{role_id}/permissions",
    summary="Assign permissions to a role",
)
def assign_permissions(
    role_id: int,
    payload: RoleAssignPermissions,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Assign Permissions")),
):
    """
    Synchronize the role's permissions by replacing existing assignments with the new ones.
    Requires 'Assign Permissions' permission.
    """
    return roles_controller.assign_role_permissions(role_id, payload, db)

@router.get(
    "/{role_id}/permissions",
    response_model=List[PermissionResponse],
    summary="List all permissions assigned to a role",
)
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Roles")),
):
    """
    Retrieve list of permissions currently mapped to a specific role.
    Requires 'View Roles' permission.
    """
    return roles_controller.get_role_permissions(role_id, db)
