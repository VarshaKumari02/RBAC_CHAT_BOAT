from sqlalchemy import Column, Integer, ForeignKey
from app.database.database import Base

class RoleHasPermission(Base):
    __tablename__ = "role_has_permissions"

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True, nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True, nullable=False)