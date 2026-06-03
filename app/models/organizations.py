from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from app.database.database import Base
from datetime import datetime

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    organization_type = Column(Enum('government', 'psu', name="organizations_type_enum"), nullable=False)
    wallet_access = Column(Boolean, default=False, nullable=False)
    status =  Column(Enum('active', 'blocked', name="organizations_status_enum"), default='active', nullable=False)
    created_at = Column(DateTime,default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime,default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)