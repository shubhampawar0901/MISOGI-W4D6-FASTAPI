from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class EventBase(BaseModel):
    """Base event schema with common fields"""
    name: str = Field(..., min_length=1, max_length=200, description="Event name")
    event_date: datetime = Field(..., description="Event date and time")
    venue_id: int = Field(..., gt=0, description="Venue ID")


class EventCreate(EventBase):
    """Schema for creating a new event"""
    pass


class EventUpdate(BaseModel):
    """Schema for updating an event"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    event_date: Optional[datetime] = None
    venue_id: Optional[int] = Field(None, gt=0)


class EventResponse(EventBase):
    """Schema for event response"""
    id: int
    
    class Config:
        from_attributes = True


class EventWithDetails(EventResponse):
    """Schema for event with venue and booking details"""
    venue: "VenueResponse"
    bookings: List["BookingResponse"] = []
    
    class Config:
        from_attributes = True
