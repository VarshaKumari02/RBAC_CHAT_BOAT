from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from enum import Enum
from decimal import Decimal


# ── Enums ─────────────────────────────────────────────────────────────────────

class FlightStatusEnum(str, Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"
    failed    = "failed"


class LayoverEnum(str, Enum):
    yes = "yes"
    no  = "no"


class TripTypeEnum(str, Enum):
    international = "international"
    domestic      = "domestic"


class GenderEnum(str, Enum):
    M = "M"
    F = "F"
    U = "U"


class TravellerTypeEnum(str, Enum):
    ADT = "ADT"   # Adult
    CNN = "CNN"   # Child
    INF = "INF"   # Infant
    STU = "STU"   # Student
    SCP = "SCP"   # Senior Citizen / Special


class TravellerStatusEnum(str, Enum):
    pending   = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    failed    = "failed"


# ─────────────────────────────────────────────────────────────────────────────
# FlightSegment Schemas
# ─────────────────────────────────────────────────────────────────────────────

class FlightSegmentBase(BaseModel):
    booking_id:         int
    flight_number:      str
    governing_carrier:  Optional[str]     = None
    departure_airport:  str
    departure_terminal: Optional[str]     = None
    arrival_airport:    str
    arrival_terminal:   Optional[str]     = None
    departure_date:     datetime
    arrival_date:       datetime
    elapsed_time:       int
    seat_class:         str
    ticket_price:       Decimal           = Decimal("0.00")
    brand_name:         Optional[str]     = None
    pnr:                Optional[str]     = None
    airline_pnr:        Optional[str]     = None
    country_code:       str
    from_city:          str
    to_city:            str
    is_layover:         LayoverEnum       = LayoverEnum.no
    issuing_authority:  Optional[str]     = None
    booking_resource:   Optional[str]     = None
    balance_due:        Decimal           = Decimal("0.00")
    segment_order:      Optional[int]     = None
    segments:           Optional[int]     = None
    trip_type:          TripTypeEnum
    journey_type:       Optional[str]     = None


class FlightSegmentCreate(FlightSegmentBase):
    pass


class FlightSegmentUpdate(BaseModel):
    status:         Optional[FlightStatusEnum] = None
    pnr:            Optional[str]              = None
    airline_pnr:    Optional[str]              = None
    cancelled_at:   Optional[datetime]         = None
    balance_due:    Optional[Decimal]          = None


class FlightSegmentResponse(FlightSegmentBase):
    id:           int
    status:       FlightStatusEnum
    cancelled_at: Optional[datetime] = None
    created_at:   datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# BookingTraveller Schemas
# ─────────────────────────────────────────────────────────────────────────────

class BookingTravellerBase(BaseModel):
    bookings_id:         int
    booking_flights_id:  int
    firstname:           str
    middlename:          Optional[str]  = None
    lastname:            str
    email:               Optional[str]  = None
    dob:                 Optional[date] = None
    mobile:              Optional[str]  = None
    alternate_mobile:    Optional[str]  = None
    full_address:        Optional[str]  = None
    age:                 Optional[int]  = None
    gender:              Optional[GenderEnum]       = None
    traveller_type:      TravellerTypeEnum
    passport_number:     Optional[str]  = None
    seat_number:         Optional[str]  = None
    organization_id:     Optional[int]  = None


class BookingTravellerCreate(BookingTravellerBase):
    pass


class BookingTravellerUpdate(BaseModel):
    status:          Optional[TravellerStatusEnum] = None
    ticket_number:   Optional[str]                 = None
    pnr:             Optional[str]                 = None
    airline_pnr:     Optional[str]                 = None
    seat_number:     Optional[str]                 = None


class BookingTravellerResponse(BookingTravellerBase):
    id:            int
    status:        TravellerStatusEnum
    ticket_number: Optional[str]     = None
    pnr:           Optional[str]     = None
    airline_pnr:   Optional[str]     = None
    created_at:    datetime
    updated_at:    datetime

    class Config:
        from_attributes = True
