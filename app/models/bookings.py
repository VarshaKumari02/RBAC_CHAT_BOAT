from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    DECIMAL,
    Text,
    DateTime,
    ForeignKey
)
from datetime import datetime

from app.database.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True
    )

    organization_id = Column(
        BigInteger,
        nullable=True
    )

    booking_reference = Column(
        String(63),
        nullable=False,
        index=True
    )

    booking_type = Column(
        Enum(
            "flight",
            "hotel",
            "train",
            name="booking_type_enum"
        ),
        nullable=False
    )

    booking_status = Column(
        Enum(
            "pending",
            "confirmed",
            "cancelled",
            "expired",
            name="booking_status_enum"
        ),
        nullable=False
    )

    journey_type = Column(
        Enum(
            "one_way",
            "round_trip",
            "multi_cities",
            name="journey_type_enum"
        ),
        nullable=True
    )

    base_amount = Column(
        DECIMAL(10, 2),
        default=0.00,
        nullable=False
    )

    total_taxes = Column(
        DECIMAL(10, 2),
        default=0.00,
        nullable=False
    )

    total_fees = Column(
        DECIMAL(10, 2),
        default=0.00,
        nullable=True
    )

    total_amount = Column(
        DECIMAL(10, 2),
        default=0.00,
        nullable=False
    )

    remark = Column(
        Text,
        nullable=True
    )

    issuing_authority = Column(
        String(100),
        nullable=True
    )

    booking_resource = Column(
        String(100),
        nullable=True
    )

    booking_expires_at = Column(
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