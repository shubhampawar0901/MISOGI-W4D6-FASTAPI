from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.ticket_type import TicketType
from app.schemas.ticket_type import TicketTypeCreate, TicketTypeResponse, TicketTypeUpdate, TicketTypeWithBookings

router = APIRouter()


@router.post("/", response_model=TicketTypeResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_type(
    ticket_type: TicketTypeCreate,
    db: Session = Depends(get_db)
):
    """Create a new ticket type"""
    # Check if ticket type with same name already exists
    existing_ticket_type = db.query(TicketType).filter(TicketType.name == ticket_type.name).first()
    if existing_ticket_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket type with name '{ticket_type.name}' already exists"
        )
    
    try:
        db_ticket_type = TicketType(**ticket_type.dict())
        db.add(db_ticket_type)
        db.commit()
        db.refresh(db_ticket_type)
        return db_ticket_type
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating ticket type: {str(e)}"
        )


@router.get("/", response_model=List[TicketTypeResponse])
def get_ticket_types(
    skip: int = Query(0, ge=0, description="Number of ticket types to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of ticket types to return"),
    db: Session = Depends(get_db)
):
    """Get all ticket types with pagination"""
    ticket_types = db.query(TicketType).offset(skip).limit(limit).all()
    return ticket_types


@router.get("/{ticket_type_id}", response_model=TicketTypeResponse)
def get_ticket_type(
    ticket_type_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific ticket type by ID"""
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    return ticket_type


@router.get("/{ticket_type_id}/bookings", response_model=TicketTypeWithBookings)
def get_ticket_type_with_bookings(
    ticket_type_id: int,
    db: Session = Depends(get_db)
):
    """Get a ticket type with all its bookings"""
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    return ticket_type


@router.put("/{ticket_type_id}", response_model=TicketTypeResponse)
def update_ticket_type(
    ticket_type_id: int,
    ticket_type_update: TicketTypeUpdate,
    db: Session = Depends(get_db)
):
    """Update a ticket type"""
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    # Check if new name conflicts with existing ticket type
    if ticket_type_update.name and ticket_type_update.name != ticket_type.name:
        existing_ticket_type = db.query(TicketType).filter(
            TicketType.name == ticket_type_update.name,
            TicketType.id != ticket_type_id
        ).first()
        if existing_ticket_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ticket type with name '{ticket_type_update.name}' already exists"
            )
    
    update_data = ticket_type_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket_type, field, value)
    
    try:
        db.commit()
        db.refresh(ticket_type)
        return ticket_type
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating ticket type: {str(e)}"
        )


@router.delete("/{ticket_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_type(
    ticket_type_id: int,
    db: Session = Depends(get_db)
):
    """Delete a ticket type"""
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    # Check if ticket type has associated bookings
    if ticket_type.bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete ticket type with existing bookings"
        )
    
    try:
        db.delete(ticket_type)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting ticket type: {str(e)}"
        )


@router.get("/{ticket_type_id}/stats")
def get_ticket_type_stats(
    ticket_type_id: int,
    db: Session = Depends(get_db)
):
    """Get ticket type statistics (bookings, revenue, etc.)"""
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    total_bookings = len(ticket_type.bookings)
    total_tickets_sold = sum(booking.quantity for booking in ticket_type.bookings)
    total_revenue = sum(booking.total_price for booking in ticket_type.bookings)
    confirmed_bookings = len([b for b in ticket_type.bookings if b.status == "confirmed"])
    
    return {
        "ticket_type_id": ticket_type_id,
        "ticket_type_name": ticket_type.name,
        "price": ticket_type.price,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "total_tickets_sold": total_tickets_sold,
        "total_revenue": total_revenue,
        "average_tickets_per_booking": total_tickets_sold / total_bookings if total_bookings > 0 else 0
    }
