from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal


# ── Enums ─────────────────────────────────────────────────────────────────────

class BookingTypeEnum(str, Enum):
    flight = "flight"
    hotel  = "hotel"
    train  = "train"


class BookingStatusEnum(str, Enum):
    pending   = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    expired   = "expired"


class JourneyTypeEnum(str, Enum):
    one_way      = "one_way"
    round_trip   = "round_trip"
    multi_cities = "multi_cities"


# ── Base ──────────────────────────────────────────────────────────────────────

class BookingBase(BaseModel):
    user_id:           Optional[int]              = None
    organization_id:   Optional[int]              = None
    booking_reference: str
    booking_type:      BookingTypeEnum
    booking_status:    BookingStatusEnum
    journey_type:      Optional[JourneyTypeEnum]  = None
    base_amount:       Decimal                    = Decimal("0.00")
    total_taxes:       Decimal                    = Decimal("0.00")
    total_fees:        Optional[Decimal]          = None
    total_amount:      Decimal                    = Decimal("0.00")
    remark:            Optional[str]              = None
    issuing_authority: Optional[str]              = None
    booking_resource:  Optional[str]              = None
    booking_expires_at: Optional[datetime]        = None


# ── Create ────────────────────────────────────────────────────────────────────

class BookingCreate(BookingBase):
    pass


# ── Update ────────────────────────────────────────────────────────────────────

class BookingUpdate(BaseModel):
    booking_status:    Optional[BookingStatusEnum] = None
    journey_type:      Optional[JourneyTypeEnum]   = None
    base_amount:       Optional[Decimal]           = None
    total_taxes:       Optional[Decimal]           = None
    total_fees:        Optional[Decimal]           = None
    total_amount:      Optional[Decimal]           = None
    remark:            Optional[str]               = None
    booking_expires_at: Optional[datetime]         = None


# ── Response ──────────────────────────────────────────────────────────────────

class BookingResponse(BookingBase):
    id:         int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Nested Creation Schemas ───────────────────────────────────────────────────
from datetime import date
from typing import List
from app.schemas.booking_flights import LayoverEnum, TripTypeEnum, GenderEnum, TravellerTypeEnum

class FlightSegmentNestedCreate(BaseModel):
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

class BookingTravellerNestedCreate(BaseModel):
    flight_index:       int  # 0-based index of the flight segment in the "flights" array
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

class BookingWithDetailsCreate(BaseModel):
    booking_reference: Optional[str] = None
    booking_type:      BookingTypeEnum
    booking_status:    BookingStatusEnum
    journey_type:      Optional[JourneyTypeEnum]  = None
    base_amount:       Decimal                    = Decimal("0.00")
    total_taxes:       Decimal                    = Decimal("0.00")
    total_fees:        Optional[Decimal]          = None
    total_amount:      Decimal                    = Decimal("0.00")
    remark:            Optional[str]              = None
    issuing_authority: Optional[str]              = None
    booking_resource:  Optional[str]              = None
    booking_expires_at: Optional[datetime]        = None
    organization_id:   Optional[int]              = None
    
    flights:           List[FlightSegmentNestedCreate]
    travellers:        List[BookingTravellerNestedCreate]


from app.schemas.booking_flights import FlightSegmentResponse, BookingTravellerResponse

class BookingWithDetailsResponse(BaseModel):
    booking: BookingResponse
    flights: List[FlightSegmentResponse]
    travellers: List[BookingTravellerResponse]


