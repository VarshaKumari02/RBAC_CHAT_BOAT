from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    status =  Column(Enum('active', 'blocked', 'deleted', name="permissions_status_enum"), default='active', nullable=False)
    permission_group_id = Column(Integer, ForeignKey('permission_groups.id'), nullable=False)
    created_at = Column(DateTime,default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime,default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    