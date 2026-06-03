"""
app/controllers/bookings_controller.py
──────────────────────────────────────────
Pure business logic for Bookings with Wallet debit transactions.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.models.bookings import Booking
from app.models.wallets import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.models.booking_payments import PaymentTransaction
from app.models.user_has_role import UserHasRole
from app.models.users import User
from app.models.booking_flights import FlightSegment
from app.models.booking_travellers import BookingTraveller
from app.schemas.bookings import BookingWithDetailsCreate
from app.models.ltc_user import LtcUser

def create_booking_with_wallet(payload: BookingWithDetailsCreate, current_user: User, db: Session):
    # 1. Resolve organization_id
    user_org_id = None
    ltc_user = db.query(LtcUser).filter(LtcUser.user_id == current_user.id).first()
    if ltc_user and ltc_user.organization_id:
        user_org_id = ltc_user.organization_id
    else:
        user_role = db.query(UserHasRole).filter(UserHasRole.user_id == current_user.id).first()
        if user_role and user_role.organization_id:
            user_org_id = user_role.organization_id

    # If the user is not ITDC, they must book for their own organization
    user_type_val = current_user.user_type.value if hasattr(current_user.user_type, "value") else current_user.user_type
    if user_type_val != "itdc":
        if payload.organization_id and payload.organization_id != user_org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You cannot create bookings for another organization."
            )
        org_id = user_org_id
    else:
        org_id = payload.organization_id or user_org_id

    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID is required as user is not mapped to any organization"
        )

    # 2. Retrieve Organization's Wallet
    wallet = db.query(Wallet).filter(
        Wallet.organization_id == org_id, 
        Wallet.deleted_at == None
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for the organization"
        )
        
    if wallet.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Organization wallet is currently {wallet.status}"
        )

    # 3. Check Wallet Type and Balance
    # If the wallet type is 'limited', we enforce balance check.
    # If the wallet type is 'unlimited', we proceed regardless of balance.
    if wallet.wallet_type == "limited":
        if wallet.balance < payload.total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient wallet balance. Required: {payload.total_amount}, Available: {wallet.balance}"
            )

    # 4. Perform database transactions
    try:
        # Resolve or generate booking reference (e.g. BKG-F39D2C8A1B)
        booking_ref = f"BKG-{uuid.uuid4().hex[:10].upper()}"

        # Create Booking
        new_booking = Booking(
            user_id=current_user.id,
            organization_id=org_id,
            booking_reference=booking_ref,
            booking_type=payload.booking_type.value,
            booking_status="confirmed",
            journey_type=payload.journey_type.value if payload.journey_type else None,
            base_amount=payload.base_amount,
            total_taxes=payload.total_taxes,
            total_fees=payload.total_fees,
            total_amount=payload.total_amount,
            remark=payload.remark,
            issuing_authority=payload.issuing_authority,
            booking_resource=payload.booking_resource,
            booking_expires_at=payload.booking_expires_at
        )
        db.add(new_booking)
        db.flush()  # Populate new_booking.id

        # Create Flight Segments
        inserted_segments = []
        for index, flight_data in enumerate(payload.flights):
            segment = FlightSegment(
                booking_id=new_booking.id,
                flight_number=flight_data.flight_number,
                governing_carrier=flight_data.governing_carrier,
                departure_airport=flight_data.departure_airport,
                departure_terminal=flight_data.departure_terminal,
                arrival_airport=flight_data.arrival_airport,
                arrival_terminal=flight_data.arrival_terminal,
                departure_date=flight_data.departure_date,
                arrival_date=flight_data.arrival_date,
                elapsed_time=flight_data.elapsed_time,
                seat_class=flight_data.seat_class,
                ticket_price=flight_data.ticket_price,
                brand_name=flight_data.brand_name,
                pnr=flight_data.pnr,
                airline_pnr=flight_data.airline_pnr,
                country_code=flight_data.country_code,
                from_city=flight_data.from_city,
                to_city=flight_data.to_city,
                is_layover=flight_data.is_layover.value,
                issuing_authority=flight_data.issuing_authority,
                booking_resource=flight_data.booking_resource,
                balance_due=flight_data.balance_due,
                segment_order=flight_data.segment_order if flight_data.segment_order is not None else (index + 1),
                segments=flight_data.segments,
                trip_type=flight_data.trip_type.value,
                journey_type=flight_data.journey_type
            )
            db.add(segment)
            db.flush()
            inserted_segments.append(segment)

        # Create Travellers mapped to Flight Segments
        inserted_travellers = []
        for trav_data in payload.travellers:
            if trav_data.flight_index < 0 or trav_data.flight_index >= len(inserted_segments):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid flight_index {trav_data.flight_index} for traveller {trav_data.firstname}"
                )
            
            associated_flight = inserted_segments[trav_data.flight_index]
            
            traveller = BookingTraveller(
                bookings_id=new_booking.id,
                booking_flights_id=associated_flight.id,
                firstname=trav_data.firstname,
                middlename=trav_data.middlename,
                lastname=trav_data.lastname,
                email=trav_data.email,
                dob=trav_data.dob,
                mobile=trav_data.mobile,
                alternate_mobile=trav_data.alternate_mobile,
                full_address=trav_data.full_address,
                age=trav_data.age,
                gender=trav_data.gender.value if trav_data.gender else None,
                traveller_type=trav_data.traveller_type.value,
                passport_number=trav_data.passport_number,
                seat_number=trav_data.seat_number,
                pnr=associated_flight.pnr,
                airline_pnr=associated_flight.airline_pnr,
                status="confirmed" if new_booking.booking_status == "confirmed" else "pending",
                organization_id=trav_data.organization_id if trav_data.organization_id is not None else org_id
            )
            db.add(traveller)
            db.flush()
            inserted_travellers.append(traveller)

        # Update Wallet Balance (can go negative if unlimited)
        previous_balance = wallet.balance
        wallet.balance -= payload.total_amount
        current_balance = wallet.balance
        db.flush()

        # Create Wallet Transaction (Debit)
        wallet_txn = WalletTransaction(
            transaction_code=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            wallet_id=wallet.id,
            transaction_by=current_user.id,
            transaction_method="manual adjustment",
            transaction_type="debit",
            credit_source="wallet",
            amount=payload.total_amount,
            previous_balance=previous_balance,
            current_balance=current_balance,
            description=f"Debit for Booking Ref: {booking_ref}",
            status="completed"
        )
        db.add(wallet_txn)
        db.flush()  # Populate wallet_txn.id

        # Create Payment Transaction linking Booking and Wallet Transaction
        payment_txn = PaymentTransaction(
            transaction_code=f"PAY-{uuid.uuid4().hex[:12].upper()}",
            bookings_id=new_booking.id,
            wallet_transactions_id=wallet_txn.id,
            initiated_by=current_user.id,
            transaction_type="payment",
            amount=payload.total_amount,
            remarks=f"Wallet payment for Booking Ref: {booking_ref}",
            payment_status="completed",
            transaction_mode="online"
        )
        db.add(payment_txn)

        db.commit()
        db.refresh(new_booking)
        
        # Refresh all inserted list items to bind them to current session states
        for s in inserted_segments:
            db.refresh(s)
        for t in inserted_travellers:
            db.refresh(t)

        return {
            "booking": new_booking,
            "flights": inserted_segments,
            "travellers": inserted_travellers
        }

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the booking: {str(e)}"
        )

def get_bookings(db: Session, current_user: User):
    user_type_val = current_user.user_type.value if hasattr(current_user.user_type, "value") else current_user.user_type
    if user_type_val == "itdc":
        return db.query(Booking).all()
    
    # Non-ITDC users (normal users)
    # Try to resolve organization
    org_id = None
    ltc = db.query(LtcUser).filter(LtcUser.user_id == current_user.id).first()
    if ltc and ltc.organization_id:
        org_id = ltc.organization_id
    else:
        user_role = db.query(UserHasRole).filter(UserHasRole.user_id == current_user.id).first()
        if user_role and user_role.organization_id:
            org_id = user_role.organization_id

    if org_id:
        # Show bookings from the organization or directly by this user
        return db.query(Booking).filter(
            (Booking.organization_id == org_id) | (Booking.user_id == current_user.id)
        ).all()
    else:
        # User not mapped to an organization (e.g. B2C user), only show their own bookings
        return db.query(Booking).filter(Booking.user_id == current_user.id).all()

def get_booking_by_id(booking_id: int, db: Session, current_user: User):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    user_type_val = current_user.user_type.value if hasattr(current_user.user_type, "value") else current_user.user_type
    if user_type_val != "itdc":
        # Check ownership or organization mapping
        org_id = None
        ltc = db.query(LtcUser).filter(LtcUser.user_id == current_user.id).first()
        if ltc and ltc.organization_id:
            org_id = ltc.organization_id
        else:
            user_role = db.query(UserHasRole).filter(UserHasRole.user_id == current_user.id).first()
            if user_role and user_role.organization_id:
                org_id = user_role.organization_id

        # Allow access if they own the booking or it belongs to their organization
        is_owner = booking.user_id == current_user.id
        is_org_booking = org_id is not None and booking.organization_id == org_id
        
        if not (is_owner or is_org_booking):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not have permission to view this booking."
            )
            
    flights = db.query(FlightSegment).filter(FlightSegment.booking_id == booking_id).all()
    travellers = db.query(BookingTraveller).filter(BookingTraveller.bookings_id == booking_id).all()
    
    return {
        "booking": booking,
        "flights": flights,
        "travellers": travellers
    }
