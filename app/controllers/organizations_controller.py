"""
app/controllers/organizations_controller.py
──────────────────────────────────────────────
Pure business logic for Organization and associated Wallet creation.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.models.organizations import Organization
from app.models.wallets import Wallet
from app.schemas.organizations import OrganizationCreate, OrgTypeEnum

def create_organization_with_wallet(payload: OrganizationCreate, db: Session):
    # 1. Check if organization name already exists
    existing = db.query(Organization).filter(Organization.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization with name '{payload.name}' already exists"
        )
    
    # 2. Create the Organization
    new_org = Organization(
        name=payload.name,
        description=payload.description,
        organization_type=payload.organization_type.value,
        wallet_access=payload.wallet_access,
        status="active"
    )
    db.add(new_org)
    db.flush()  # Generate the ID for new_org before commit so we can link the wallet
    
    # 3. Determine Wallet Type based on organization type
    # If organization_type is government -> unlimited, otherwise -> limited
    if payload.organization_type == OrgTypeEnum.government:
        wallet_type = "unlimited"
    else:
        wallet_type = "limited"
        
    # Generate unique wallet code
    wallet_code = f"WLT-{uuid.uuid4().hex[:12].upper()}"
    
    # 4. Create the Wallet
    new_wallet = Wallet(
        wallet_code=wallet_code,
        organization_id=new_org.id,
        status="active",
        balance=0.00,
        currency_code="INR",
        wallet_type=wallet_type,
        wallet_limit_value=None
    )
    db.add(new_wallet)
    
    # Commit transaction
    db.commit()
    db.refresh(new_org)
    
    return new_org

def get_organizations(db: Session):
    return db.query(Organization).all()

def get_organization_by_id(org_id: int, db: Session):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {org_id} not found"
        )
    return org
