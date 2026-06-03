from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Integer,
    Boolean,
    Enum,
    DateTime,
    DECIMAL,
    Text,
    ForeignKey
)

from datetime import datetime

from app.database.database import Base


class FlightSegment(Base):
    __tablename__ = "flight_segments"

    id = Column(BigInteger, primary_key=True, index=True)

    booking_id = Column(
        BigInteger,
        ForeignKey("bookings.id"),
        nullable=False,
        index=True
    )

    flight_number = Column(
        String(8),
        nullable=False
    )

    governing_carrier = Column(
        String(3),
        nullable=True
    )

    departure_airport = Column(
        String(3),
        nullable=False,
        index=True
    )

    departure_terminal = Column(
        String(10),
        nullable=True
    )

    arrival_airport = Column(
        String(3),
        nullable=False,
        index=True
    )

    arrival_terminal = Column(
        String(10),
        nullable=True
    )

    departure_date = Column(
        DateTime,
        nullable=False
    )

    arrival_date = Column(
        DateTime,
        nullable=False
    )

    elapsed_time = Column(
        Integer,
        nullable=False
    )

    seat_class = Column(
        String(31),
        nullable=False
    )

    ticket_price = Column(
        DECIMAL(12, 2),
        default=0.00,
        nullable=False
    )

    brand_name = Column(
        String(255),
        nullable=True
    )

    pnr = Column(
        String(15),
        nullable=True
    )

    airline_pnr = Column(
        String(15),
        nullable=True
    )

    country_code = Column(
        String(3),
        nullable=False
    )

    status = Column(
        Enum(
            "scheduled",
            "cancelled",
            "completed",
            "failed",
            name="flight_segment_status_enum"
        ),
        default="scheduled",
        nullable=False
    )

    from_city = Column(
        String(63),
        nullable=False
    )

    to_city = Column(
        String(63),
        nullable=False
    )

    is_layover = Column(
        Enum(
            "yes",
            "no",
            name="layover_enum"
        ),
        default="no",
        nullable=False
    )

    issuing_authority = Column(
        String(50),
        nullable=True
    )

    booking_resource = Column(
        String(50),
        nullable=True
    )

    balance_due = Column(
        DECIMAL(12, 2),
        default=0.00
    )

    segment_order = Column(
        Integer,
        nullable=True
    )

    segments = Column(
        Integer,
        nullable=True
    )

    trip_type = Column(
        Enum(
            "international",
            "domestic",
            name="trip_type_enum"
        ),
        nullable=False
    )

    journey_type = Column(
        String(63),
        nullable=True
    )

    cancelled_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )