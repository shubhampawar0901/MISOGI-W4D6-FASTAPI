from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class BookingBase(BaseModel):
    """Base booking schema with common fields"""
    customer_name: str = Field(..., min_length=1, max_length=200, description="Customer name")
    customer_email: EmailStr = Field(..., description="Customer email address")
    quantity: int = Field(..., gt=0, description="Number of tickets (must be positive)")
    event_id: int = Field(..., gt=0, description="Event ID")
    ticket_type_id: int = Field(..., gt=0, description="Ticket type ID")


class BookingCreate(BookingBase):
    """Schema for creating a new booking"""
    pass


class BookingUpdate(BaseModel):
    """Schema for updating a booking"""
    customer_name: Optional[str] = Field(None, min_length=1, max_length=200)
    customer_email: Optional[EmailStr] = None
    quantity: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, regex="^(pending|confirmed|cancelled)$")


class BookingResponse(BookingBase):
    """Schema for booking response"""
    id: int
    total_price: float
    booking_date: datetime
    status: str
    
    class Config:
        from_attributes = True


class BookingWithDetails(BookingResponse):
    """Schema for booking with event and ticket type details"""
    event: "EventResponse"
    ticket_type: "TicketTypeResponse"
    
    class Config:
        from_attributes = True
