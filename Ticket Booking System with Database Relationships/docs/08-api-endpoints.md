# 08 - Complete API Endpoints Implementation

## 🎯 Learning Objectives

By the end of this section, you will:
- Implement complete CRUD operations for all models
- Handle complex relationships in API responses
- Add advanced features like pagination and filtering
- Implement business logic for booking calculations
- Create comprehensive API documentation

## 🏗️ Building Complete Event Endpoints

### **Step 1: Create Event Model and Schema Files**

First, complete the remaining model files. Create `app/models/event.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Event(Base):
    """Event model for storing event information"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    event_date = Column(DateTime, nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)

    # Relationships
    venue = relationship("Venue", back_populates="events")
    bookings = relationship("Booking", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', venue_id={self.venue_id})>"
```

Create `app/schemas/event.py`:

```python
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
```

### **Step 2: Create Event Endpoints**

Create `app/api/v1/endpoints/events.py`:

```python
from typing import List
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
    db: Session = Depends(get_db)
):
    """Get all events with optional filtering"""
    query = db.query(Event)
    
    if venue_id:
        query = query.filter(Event.venue_id == venue_id)
    
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
```

### **Understanding Advanced Query Features**

#### **Query Parameters with Validation**
```python
skip: int = Query(0, ge=0, description="Number of events to skip"),
limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
```

**What this provides:**
- **Automatic validation** - `ge=0` ensures skip is not negative
- **Documentation** - Description appears in API docs
- **Type conversion** - String query params become integers

#### **Optional Filtering**
```python
venue_id: Optional[int] = Query(None, description="Filter by venue ID"),

# In the function
if venue_id:
    query = query.filter(Event.venue_id == venue_id)
```

**Usage examples:**
- `GET /events` - All events
- `GET /events?venue_id=1` - Events at venue 1
- `GET /events?skip=10&limit=5` - Pagination

#### **Foreign Key Validation**
```python
# Verify venue exists before creating event
venue = db.query(Venue).filter(Venue.id == event.venue_id).first()
if not venue:
    raise HTTPException(status_code=404, detail="Venue not found")
```

**Why this matters:**
- **Better error messages** - "Venue not found" vs generic foreign key error
- **Data integrity** - Prevents orphaned records
- **User experience** - Clear feedback on what went wrong

## 🎫 Implementing TicketType Endpoints

### **Step 3: Complete TicketType Implementation**

Create `app/models/ticket_type.py`:

```python
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database import Base


class TicketType(Base):
    """TicketType model for storing ticket type information"""
    __tablename__ = "ticket_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)  # VIP, Standard, Economy
    price = Column(Float, nullable=False)

    # Relationships
    bookings = relationship("Booking", back_populates="ticket_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TicketType(id={self.id}, name='{self.name}', price={self.price})>"
```

Create `app/schemas/ticket_type.py`:

```python
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
```

## 📋 Implementing Booking Endpoints with Business Logic

### **Step 4: Advanced Booking Implementation**

Create `app/models/booking.py`:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Booking(Base):
    """Booking model for storing booking information"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, confirmed, cancelled

    # Foreign Keys
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="bookings")
    ticket_type = relationship("TicketType", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(id={self.id}, customer='{self.customer_name}', status='{self.status}')>"
```

Create `app/schemas/booking.py`:

```python
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
```

### **Step 5: Booking Endpoints with Business Logic**

Create `app/api/v1/endpoints/bookings.py`:

```python
from typing import List
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


@router.put("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    status: str = Field(..., regex="^(pending|confirmed|cancelled)$"),
    db: Session = Depends(get_db)
):
    """Update booking status"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking.status = status
    
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
```

### **Understanding Business Logic Implementation**

#### **Automatic Price Calculation**
```python
# Calculate total price
total_price = ticket_type.price * booking.quantity

db_booking = Booking(
    **booking.dict(),
    total_price=total_price  # Override with calculated value
)
```

**Why calculate server-side:**
- **Security** - Client can't manipulate prices
- **Consistency** - Price changes don't affect calculation logic
- **Business rules** - Can add discounts, taxes, etc.

#### **Multiple Filter Support**
```python
if event_id:
    query = query.filter(Booking.event_id == event_id)
if customer_email:
    query = query.filter(Booking.customer_email.ilike(f"%{customer_email}%"))
```

**Usage examples:**
- `GET /bookings?event_id=1` - All bookings for event 1
- `GET /bookings?customer_email=john` - Bookings containing "john" in email
- `GET /bookings?status=confirmed&event_id=1` - Confirmed bookings for event 1

## 🔗 Updating API Router

### **Step 6: Include All Endpoints**

Update `app/api/v1/__init__.py`:

```python
from fastapi import APIRouter
from app.api.v1.endpoints import venues, events, ticket_types, bookings

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(ticket_types.router, prefix="/ticket-types", tags=["ticket-types"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
```

## 🧪 Testing Complete API

### **Step 7: Test Full Workflow**

1. **Create a venue:**
   ```json
   POST /api/v1/venues
   {
     "name": "Madison Square Garden",
     "capacity": 20000,
     "address": "New York, NY"
   }
   ```

2. **Create ticket types:**
   ```json
   POST /api/v1/ticket-types
   {
     "name": "VIP",
     "price": 299.99
   }
   ```

3. **Create an event:**
   ```json
   POST /api/v1/events
   {
     "name": "Rock Concert",
     "event_date": "2025-01-15T20:00:00",
     "venue_id": 1
   }
   ```

4. **Create a booking:**
   ```json
   POST /api/v1/bookings
   {
     "customer_name": "John Doe",
     "customer_email": "john@example.com",
     "quantity": 2,
     "event_id": 1,
     "ticket_type_id": 1
   }
   ```

## 📚 Key Takeaways

### **Advanced API Features**
1. **Business logic** - Server-side price calculation
2. **Data validation** - Foreign key existence checks
3. **Flexible filtering** - Multiple query parameters
4. **Rich responses** - Nested relationship data

### **Production Considerations**
1. **Error handling** - Comprehensive exception management
2. **Data integrity** - Validation before database operations
3. **Performance** - Pagination for large datasets
4. **Security** - Server-side calculations prevent manipulation

## 🚀 Next Steps

Your complete API is now functional:

1. ✅ **All CRUD operations implemented**
2. ✅ **Business logic integrated**
3. ✅ **Advanced filtering and pagination**
4. ✅ **Comprehensive error handling**

**Next: [09 - Testing and Deployment →](09-testing-and-deployment.md)**

---

**Previous: [← 07 - Production Structure](07-production-structure.md) | Next: [09 - Testing and Deployment →](09-testing-and-deployment.md)**
