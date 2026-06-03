from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    DECIMAL,
    DateTime,
    ForeignKey,
    Text
)
from datetime import datetime

from app.database.database import Base


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    transaction_code = Column(
        String(36),
        nullable=False,
        unique=True,
        index=True
    )

    wallet_id = Column(
        BigInteger,
        ForeignKey("wallets.id"),
        nullable=False,
        index=True
    )

    transaction_by = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    transaction_method = Column(
        Enum(
            "bank transfer",
            "card",
            "manual adjustment",
            name="transaction_method_enum"
        ),
        nullable=False
    )

    transaction_type = Column(
        Enum(
            "credit",
            "debit",
            "refund",
            "adjustment",
            name="transaction_type_enum"
        ),
        nullable=False
    )

    credit_source = Column(
        Enum(
            "credit card",
            "net banking",
            "debit card",
            "wallet",
            "upi",
            name="credit_source_enum"
        ),
        nullable=True
    )

    amount = Column(
        DECIMAL(12, 2),
        nullable=False
    )

    previous_balance = Column(
        DECIMAL(12, 2),
        nullable=True
    )

    current_balance = Column(
        DECIMAL(12, 2),
        nullable=True
    )

    description = Column(
        String(255),
        nullable=False
    )

    status = Column(
        Enum(
            "pending",
            "completed",
            "failed",
            "reversed",
            name="transaction_status_enum"
        ),
        nullable=False
    )

    transaction_utr = Column(
        String(32),
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