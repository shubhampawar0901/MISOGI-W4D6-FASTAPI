# 🔥 Pydantic Models for Node.js Developers
# This is like TypeScript interfaces + Joi validation + JSON serialization combined!

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum
import uvicorn

app = FastAPI(title="Pydantic Models Demo")

# ===== BASIC MODEL (like TypeScript interface) =====
# TypeScript:
# interface User {
#   id?: number;
#   name: string;
#   email: string;
#   age: number;
# }

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str  # We'll upgrade this to EmailStr later
    age: int

# ===== ADVANCED MODEL WITH VALIDATION (like Joi schema) =====
# Node.js with Joi:
# const userSchema = Joi.object({
#   name: Joi.string().min(2).max(50).required(),
#   email: Joi.string().email().required(),
#   age: Joi.number().min(18).max(120).required()
# });

class UserAdvanced(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Valid email address")
    age: int = Field(..., ge=18, le=120, description="Age must be between 18 and 120")
    
    # Custom validator (like custom Joi validation)
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or just spaces')
        return v.title()  # Capitalize each word

# ===== ENUM MODELS (like TypeScript enums) =====
# TypeScript:
# enum TicketType {
#   VIP = "VIP",
#   STANDARD = "STANDARD", 
#   ECONOMY = "ECONOMY"
# }

class TicketType(str, Enum):
    VIP = "VIP"
    STANDARD = "STANDARD"
    ECONOMY = "ECONOMY"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

# ===== NESTED MODELS (like nested TypeScript interfaces) =====
# TypeScript:
# interface Event {
#   id: number;
#   name: string;
#   venue: Venue;
#   tickets: TicketInfo[];
# }

class Venue(BaseModel):
    id: int
    name: str
    capacity: int = Field(..., gt=0, description="Venue capacity must be positive")
    address: str

class TicketInfo(BaseModel):
    type: TicketType
    price: float = Field(..., gt=0, description="Price must be positive")
    available: int = Field(..., ge=0, description="Available tickets cannot be negative")

class Event(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=200)
    venue: Venue  # Nested model!
    tickets: List[TicketInfo]  # List of nested models!
    event_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)

# ===== REQUEST/RESPONSE MODELS (like DTO patterns) =====
# Separate models for input vs output (best practice!)

class EventCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    venue_id: int
    event_date: datetime
    tickets: List[TicketInfo]

class EventResponse(BaseModel):
    id: int
    name: str
    venue: Venue
    tickets: List[TicketInfo]
    event_date: datetime
    created_at: datetime
    total_capacity: int  # Computed field
    
    # Computed field (like getters in classes)
    @validator('total_capacity', always=True)
    def calculate_total_capacity(cls, v, values):
        if 'tickets' in values:
            return sum(ticket.available for ticket in values['tickets'])
        return 0

# ===== SAMPLE DATA =====
sample_venue = Venue(
    id=1,
    name="Madison Square Garden",
    capacity=20000,
    address="4 Pennsylvania Plaza, New York, NY"
)

sample_tickets = [
    TicketInfo(type=TicketType.VIP, price=299.99, available=100),
    TicketInfo(type=TicketType.STANDARD, price=99.99, available=500),
    TicketInfo(type=TicketType.ECONOMY, price=49.99, available=1000)
]

events_db = []
event_counter = 1

# ===== API ENDPOINTS DEMONSTRATING PYDANTIC =====

@app.post("/events", response_model=EventResponse, status_code=201)
def create_event(event_data: EventCreateRequest):
    """
    This endpoint shows how Pydantic automatically:
    1. Validates the incoming JSON against EventCreateRequest model
    2. Converts the response to EventResponse model format
    3. Handles type conversion and validation errors
    """
    global event_counter
    
    # In a real app, you'd fetch venue from database
    # For demo, we'll use our sample venue
    new_event = Event(
        id=event_counter,
        name=event_data.name,
        venue=sample_venue,  # In real app: get_venue_by_id(event_data.venue_id)
        tickets=event_data.tickets,
        event_date=event_data.event_date
    )
    
    events_db.append(new_event)
    event_counter += 1
    
    # Pydantic automatically converts Event to EventResponse format!
    return new_event

@app.get("/events", response_model=List[EventResponse])
def get_events():
    """Returns all events in EventResponse format"""
    return events_db

@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int):
    """Get single event with automatic validation"""
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.post("/users", response_model=UserAdvanced, status_code=201)
def create_user(user: UserAdvanced):
    """
    Demonstrates advanced validation:
    - Name length validation
    - Email format validation  
    - Age range validation
    - Custom name formatting
    """
    # Pydantic has already validated everything by the time we get here!
    return user

# ===== DEMONSTRATION ENDPOINT =====
@app.get("/demo/validation-examples")
def validation_examples():
    """
    This endpoint shows what validation errors look like.
    Try sending invalid data to other endpoints to see Pydantic in action!
    """
    return {
        "message": "Try these invalid requests to see Pydantic validation:",
        "examples": [
            {
                "endpoint": "POST /users",
                "invalid_data": {"name": "", "email": "invalid-email", "age": 15},
                "expected_errors": ["name too short", "invalid email", "age too low"]
            },
            {
                "endpoint": "POST /events", 
                "invalid_data": {"name": "", "venue_id": "not-a-number"},
                "expected_errors": ["name required", "venue_id must be integer"]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

# 🎯 KEY TAKEAWAYS FOR NODE.JS DEVELOPERS:
# 1. Pydantic = TypeScript interfaces + Joi validation + serialization
# 2. Automatic JSON parsing and validation
# 3. Type conversion happens automatically
# 4. Custom validators for complex business logic
# 5. Separate request/response models for clean API design
# 6. Nested models work seamlessly
# 7. Enums provide type safety like TypeScript
# 8. Field() provides validation rules like Joi constraints
