from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db
from app.models.event import Event
from app.models.venue import Venue
from app.schemas.event import EventCreate, EventResponse, EventUpdate, EventWithDetails

router = APIRouter()


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    """Create a new event"""
    # Verify venue exists
    venue = db.query(Venue).filter(Venue.id == event.venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with id {event.venue_id} not found"
        )
    
    try:
        db_event = Event(**event.dict())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating event: {str(e)}"
        )


@router.get("/", response_model=List[EventResponse])
def get_events(
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    venue_id: Optional[int] = Query(None, description="Filter by venue ID"),
    upcoming: Optional[bool] = Query(None, description="Filter upcoming events only"),
    db: Session = Depends(get_db)
):
    """Get all events with optional filtering"""
    query = db.query(Event)
    
    if venue_id:
        query = query.filter(Event.venue_id == venue_id)
    
    if upcoming:
        query = query.filter(Event.event_date > datetime.utcnow())
    
    events = query.offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventWithDetails)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific event with venue and booking details"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db)
):
    """Update an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # If venue_id is being updated, verify new venue exists
    if event_update.venue_id and event_update.venue_id != event.venue_id:
        venue = db.query(Venue).filter(Venue.id == event_update.venue_id).first()
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venue with id {event_update.venue_id} not found"
            )
    
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    try:
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating event: {str(e)}"
        )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Delete an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    try:
        db.delete(event)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting event: {str(e)}"
        )


@router.get("/{event_id}/bookings", response_model=List[dict])
def get_event_bookings(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get all bookings for a specific event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event.bookings


@router.get("/{event_id}/stats")
def get_event_stats(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get event statistics (bookings, revenue, etc.)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    total_bookings = len(event.bookings)
    total_tickets = sum(booking.quantity for booking in event.bookings)
    total_revenue = sum(booking.total_price for booking in event.bookings)
    confirmed_bookings = len([b for b in event.bookings if b.status == "confirmed"])
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "total_tickets_sold": total_tickets,
        "total_revenue": total_revenue,
        "venue_capacity": event.venue.capacity,
        "capacity_utilization": (total_tickets / event.venue.capacity * 100) if event.venue.capacity > 0 else 0
    }
