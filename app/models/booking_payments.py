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

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    transaction_code = Column(
        String(45),
        nullable=False,
        unique=True,
        index=True
    )

    bookings_id = Column(
        BigInteger,
        ForeignKey("bookings.id"),
        nullable=False,
        index=True
    )

    wallet_transactions_id = Column(
        BigInteger,
        ForeignKey("wallet_transactions.id"),
        nullable=True,
        index=True
    )

    initiated_by = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    transaction_type = Column(
        Enum(
            "payment",
            "refund",
            name="payment_transaction_type_enum"
        ),
        nullable=False
    )

    amount = Column(
        DECIMAL(16, 2),
        nullable=False
    )

    gateway_transaction_id = Column(
        String(45)
    )

    parent_payment_transaction_id = Column(
        String(45)
    )

    remarks = Column(Text)

    payment_status = Column(
        String(255),
        nullable=False
    )

    gateway_request_body = Column(Text)

    gateway_response_body = Column(Text)

    device = Column(Text)

    payment_method_code = Column(
        String(100)
    )

    refund_details = Column(Text)

    transaction_mode = Column(
        Enum(
            "online",
            "offline",
            name="transaction_mode_enum"
        ),
        default="online",
        nullable=False
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