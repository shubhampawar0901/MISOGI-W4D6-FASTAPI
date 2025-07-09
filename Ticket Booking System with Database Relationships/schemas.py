from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# Venue Schemas
class VenueBase(BaseModel):
    name: str
    capacity: int
    address: str

class VenueCreate(VenueBase):
    pass  # Inherits all fields from VenueBase

class VenueResponse(VenueBase):
    id: int
    
    class Config:
        from_attributes = True

# Event Schemas  
class EventBase(BaseModel):
    name: str
    event_date: datetime
    venue_id: int

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    venue: VenueResponse  # Nested venue information
    
    class Config:
        from_attributes = True

# TicketType Schemas
class TicketTypeBase(BaseModel):
    name: str
    price: float

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketTypeResponse(TicketTypeBase):
    id: int
    
    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    customer_name: str
    customer_email: str
    quantity: int
    event_id: int
    ticket_type_id: int

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    total_price: float
    booking_date: datetime
    status: str
    event: EventResponse
    ticket_type: TicketTypeResponse
    
    class Config:
        from_attributes = True