from sqlalchemy import Column, ForeignKey, Integer
from app.database.database import Base

class UserHasRole(Base):
    __tablename__ = "user_has_roles"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True, nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)