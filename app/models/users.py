from sqlalchemy import Column, Integer, String, Enum, DateTime
from app.database.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    mobile = Column(String(10), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    user_type = Column(Enum("b2c","att","b2g","capf","ltc","itdc", name="users_type_enum"), nullable=False)
    status = Column(Enum('pending','active', 'blocked', name="users_status_enum"), default='pending', nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime,default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime,default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    
    