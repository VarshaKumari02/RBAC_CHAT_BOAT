"""
app/routers/organizations.py
──────────────────────────────
FastAPI router for Organization endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.services.auth_dependency import has_permission
from app.models.users import User
from app.schemas.organizations import OrganizationCreate, OrganizationResponse
from app.controllers import organizations_controller

router = APIRouter(
    prefix="/api/v1/organizations",
    tags=["Organizations"],
)

@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization and generate its wallet",
)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("Create Organizations")),
):
    """
    Create a new organization.
    This also automatically creates a wallet for the organization:
    - If organization type is **government**, the wallet is set to **unlimited**.
    - Otherwise (e.g. **psu**), the wallet is set to **limited**.

    Requires 'Create Organizations' permission.
    """
    return organizations_controller.create_organization_with_wallet(payload, db)

@router.get(
    "",
    response_model=List[OrganizationResponse],
    summary="List all organizations",
)
def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Organizations")),
):
    """
    Retrieve all registered organizations.
    Requires 'View Organizations' permission.
    """
    return organizations_controller.get_organizations(db)

@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Get details of a specific organization",
)
def get_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("View Organizations")),
):
    """
    Retrieve details of a single organization by ID.
    Requires 'View Organizations' permission.
    """
    return organizations_controller.get_organization_by_id(org_id, db)
