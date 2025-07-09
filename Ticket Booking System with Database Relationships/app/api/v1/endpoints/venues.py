from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.venue import Venue
from app.schemas.venue import VenueCreate, VenueResponse, VenueUpdate, VenueWithEvents

router = APIRouter()


@router.post("/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue: VenueCreate,
    db: Session = Depends(get_db)
):
    """Create a new venue"""
    try:
        db_venue = Venue(**venue.dict())
        db.add(db_venue)
        db.commit()
        db.refresh(db_venue)
        return db_venue
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating venue: {str(e)}"
        )


@router.get("/", response_model=List[VenueResponse])
def get_venues(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all venues with pagination"""
    venues = db.query(Venue).offset(skip).limit(limit).all()
    return venues


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific venue by ID"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    return venue


@router.get("/{venue_id}/events", response_model=VenueWithEvents)
def get_venue_with_events(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """Get a venue with all its events"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    return venue


@router.put("/{venue_id}", response_model=VenueResponse)
def update_venue(
    venue_id: int,
    venue_update: VenueUpdate,
    db: Session = Depends(get_db)
):
    """Update a venue"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    update_data = venue_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venue, field, value)
    
    try:
        db.commit()
        db.refresh(venue)
        return venue
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating venue: {str(e)}"
        )


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """Delete a venue"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    try:
        db.delete(venue)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting venue: {str(e)}"
        )
