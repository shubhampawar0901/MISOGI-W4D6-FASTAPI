from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.booking import Booking
from app.models.event import Event
from app.models.ticket_type import TicketType
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate, BookingWithDetails

router = APIRouter()


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db)
):
    """Create a new booking with automatic price calculation"""
    # Verify event exists
    event = db.query(Event).filter(Event.id == booking.event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {booking.event_id} not found"
        )
    
    # Verify ticket type exists
    ticket_type = db.query(TicketType).filter(TicketType.id == booking.ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket type with id {booking.ticket_type_id} not found"
        )
    
    # Check venue capacity
    existing_bookings = db.query(Booking).filter(
        Booking.event_id == booking.event_id,
        Booking.status.in_(["confirmed", "pending"])
    ).all()
    
    total_existing_tickets = sum(b.quantity for b in existing_bookings)
    if total_existing_tickets + booking.quantity > event.venue.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough capacity. Available: {event.venue.capacity - total_existing_tickets}, Requested: {booking.quantity}"
        )
    
    # Calculate total price
    total_price = ticket_type.price * booking.quantity
    
    try:
        db_booking = Booking(
            **booking.dict(),
            total_price=total_price
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating booking: {str(e)}"
        )


@router.get("/", response_model=List[BookingResponse])
def get_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_id: Optional[int] = Query(None, description="Filter by event ID"),
    customer_email: Optional[str] = Query(None, description="Filter by customer email"),
    status: Optional[str] = Query(None, description="Filter by booking status"),
    db: Session = Depends(get_db)
):
    """Get all bookings with optional filtering"""
    query = db.query(Booking)
    
    if event_id:
        query = query.filter(Booking.event_id == event_id)
    if customer_email:
        query = query.filter(Booking.customer_email.ilike(f"%{customer_email}%"))
    if status:
        query = query.filter(Booking.status == status)
    
    bookings = query.offset(skip).limit(limit).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingWithDetails)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific booking with full details"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db)
):
    """Update a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # If quantity is being updated, check capacity
    if booking_update.quantity and booking_update.quantity != booking.quantity:
        existing_bookings = db.query(Booking).filter(
            Booking.event_id == booking.event_id,
            Booking.id != booking_id,
            Booking.status.in_(["confirmed", "pending"])
        ).all()
        
        total_other_tickets = sum(b.quantity for b in existing_bookings)
        if total_other_tickets + booking_update.quantity > booking.event.venue.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough capacity for {booking_update.quantity} tickets"
            )
        
        # Recalculate total price if quantity changed
        booking.total_price = booking.ticket_type.price * booking_update.quantity
    
    update_data = booking_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != "total_price":  # Don't allow manual total_price updates
            setattr(booking, field, value)
    
    try:
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating booking: {str(e)}"
        )


@router.put("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    new_status: str = Query(..., regex="^(pending|confirmed|cancelled)$"),
    db: Session = Depends(get_db)
):
    """Update booking status"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Business rule: Can't change from cancelled to other status
    if booking.status == "cancelled" and new_status != "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change status from cancelled"
        )
    
    booking.status = new_status
    
    try:
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating booking status: {str(e)}"
        )


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Delete a booking (cancel and remove)"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    try:
        db.delete(booking)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting booking: {str(e)}"
        )


@router.get("/customer/{customer_email}")
def get_customer_bookings(
    customer_email: str,
    db: Session = Depends(get_db)
):
    """Get all bookings for a specific customer"""
    bookings = db.query(Booking).filter(Booking.customer_email == customer_email).all()
    
    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bookings found for customer {customer_email}"
        )
    
    return {
        "customer_email": customer_email,
        "total_bookings": len(bookings),
        "bookings": bookings
    }
