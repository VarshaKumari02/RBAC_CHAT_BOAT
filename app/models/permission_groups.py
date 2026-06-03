from sqlalchemy import Column, Integer, String, Enum, DateTime
from app.database.database import Base
from datetime import datetime

class PermissionGroup(Base):
    __tablename__ = "permission_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    status =  Column(Enum('active', 'blocked', name="permission_groups_status_enum"), default='active', nullable=False)
    created_at = Column(DateTime,default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime,default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
