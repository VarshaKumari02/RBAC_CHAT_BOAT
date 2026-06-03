from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    DateTime,
    DECIMAL,
    ForeignKey
)
from datetime import datetime

from app.database.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    wallet_code = Column(
        String(63),
        nullable=False,
        unique=True,
        index=True
    )

    organization_id = Column(
        BigInteger,
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    status = Column(
        Enum(
            "active",
            "pending",
            "blocked",
            "inactive",
            name="wallet_status_enum"
        ),
        default="pending",
        nullable=False
    )

    balance = Column(
        DECIMAL(12, 2),
        default=0.00,
        nullable=False
    )

    currency_code = Column(
        String(4),
        default="INR",
        nullable=False
    )

    wallet_type = Column(
        Enum(
            "limited",
            "unlimited",
            name="wallet_type_enum"
        ),
        nullable=False
    )

    wallet_limit_value = Column(
        DECIMAL(12, 2),
        nullable=True
    )

    last_transaction_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    deleted_at = Column(
        DateTime,
        nullable=True
    )