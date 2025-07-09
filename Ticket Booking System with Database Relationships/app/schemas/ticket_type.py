from pydantic import BaseModel, Field
from typing import Optional, List


class TicketTypeBase(BaseModel):
    """Base ticket type schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Ticket type name")
    price: float = Field(..., gt=0, description="Ticket price (must be positive)")


class TicketTypeCreate(TicketTypeBase):
    """Schema for creating a new ticket type"""
    pass


class TicketTypeUpdate(BaseModel):
    """Schema for updating a ticket type"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)


class TicketTypeResponse(TicketTypeBase):
    """Schema for ticket type response"""
    id: int
    
    class Config:
        from_attributes = True


class TicketTypeWithBookings(TicketTypeResponse):
    """Schema for ticket type with related bookings"""
    bookings: List["BookingResponse"] = []
    
    class Config:
        from_attributes = True
