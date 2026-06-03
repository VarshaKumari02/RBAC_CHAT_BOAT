from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    Date,
    DateTime,
    Integer,
    Text,
    ForeignKey
)
from datetime import datetime

from app.database.database import Base


class BookingTraveller(Base):
    __tablename__ = "booking_travellers"

    id = Column(BigInteger, primary_key=True, index=True)

    bookings_id = Column(
        BigInteger,
        ForeignKey("bookings.id"),
        nullable=False,
        index=True
    )

    booking_flights_id = Column(
        BigInteger,
        ForeignKey("flight_segments.id"),
        nullable=False,
        index=True
    )

    firstname = Column(String(127), nullable=False)

    middlename = Column(String(127))

    lastname = Column(String(127), nullable=False)

    email = Column(String(191))

    dob = Column(Date)

    mobile = Column(String(15))

    alternate_mobile = Column(String(15))

    full_address = Column(Text)

    age = Column(Integer)

    gender = Column(
        Enum(
            "M",
            "F",
            "U",
            name="gender_enum"
        )
    )

    traveller_type = Column(
        Enum(
            "ADT",
            "CNN",
            "INF",
            "STU",
            "SCP",
            name="traveller_type_enum"
        ),
        nullable=False
    )

    passport_number = Column(String(31))

    seat_number = Column(String(15))

    ticket_number = Column(String(127))

    pnr = Column(String(15))

    airline_pnr = Column(String(15))

    status = Column(
        Enum(
            "pending",
            "confirmed",
            "cancelled",
            "failed",
            name="traveller_status_enum"
        ),
        default="pending",
        nullable=False
    )

    organization_id = Column(
        BigInteger,
        nullable=True,
        index=True
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