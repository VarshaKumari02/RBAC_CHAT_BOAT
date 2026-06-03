from sqlalchemy import Column, BigInteger, String, Enum, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime

class LtcUser(Base):
    __tablename__ = "ltc_users"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True, nullable=False)
    firstname = Column(String(127), nullable=False)
    middlename = Column(String(63), nullable=True)
    lastname = Column(String(127), nullable=False)
    gender = Column(Enum("m", "f", "o", name="ltc_user_gender_enum"), nullable=False)
    organization_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=True, index=True)
    department_id = Column(BigInteger, nullable=True, index=True)
    ltc_organization_name = Column(String(127), nullable=True)
    ltc_department_name = Column(String(127), nullable=True)
    identification_number = Column(String(31), nullable=True)
    wallet_access = Column(Enum("yes", "no", name="ltc_user_wallet_access_enum"), default="no", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
