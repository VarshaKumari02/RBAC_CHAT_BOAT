"""
app/routers/bookings.py
─────────────────────────
FastAPI router for Bookings and associated Wallet Payment transaction creation.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.services.auth_dependency import get_current_user, has_booking_permission
from app.models.users import User
from app.schemas.bookings import BookingCreate, BookingResponse, BookingWithDetailsCreate, BookingWithDetailsResponse
from app.controllers import bookings_controller

router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Bookings"],
)

@router.post(
    "",
    response_model=BookingWithDetailsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking with wallet payment, flight segments, and travellers",
)
def create_booking(
    payload: BookingWithDetailsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_booking_permission("Manage PNR")),
):
    """
    Create a new booking, including nested flight segments and traveller records, and automatically process its wallet payment:
    - If the user's organization has an **unlimited** wallet, the booking succeeds regardless of current balance.
    - If the organization has a **limited** wallet, the booking succeeds only if the wallet has sufficient balance.

    The transaction automatically:
    1. Creates the **Booking** details.
    2. Creates the nested **Flight Segment** records.
    3. Creates the nested **Booking Traveller** records (linked to their respective flights).
    4. Debits the amount from the **Wallet**.
    5. Creates a **WalletTransaction** (debit).
    6. Creates a **PaymentTransaction** mapping the booking to the wallet transaction.

    Handles both normal and ITDC users.
    """
    return bookings_controller.create_booking_with_wallet(payload, current_user, db)

@router.get(
    "",
    response_model=List[BookingResponse],
    summary="List all bookings",
)
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_booking_permission("View Booking Monitor")),
):
    """
    Retrieve all bookings.
    - Normal users (b2g, att, capf, ltc, b2c) see only their own / organization bookings.
    - ITDC admin users see all bookings.

    Handles both normal and ITDC users.
    """
    return bookings_controller.get_bookings(db, current_user)

@router.get(
    "/{booking_id}",
    response_model=BookingWithDetailsResponse,
    summary="Get details of a specific booking including flights and travellers",
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_booking_permission("View Booking Monitor")),
):
    """
    Retrieve a booking by ID including its flight segments and travellers.
    - Normal users can only access bookings they own or that belong to their organization.
    - ITDC admin users can access any booking.

    Handles both normal and ITDC users.
    """
    return bookings_controller.get_booking_by_id(booking_id, db, current_user)
