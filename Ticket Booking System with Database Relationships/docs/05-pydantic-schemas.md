# 05 - Pydantic Schemas for Data Validation

## 🎯 Learning Objectives

By the end of this section, you will:
- Understand the difference between SQLAlchemy models and Pydantic schemas
- Create request and response schemas
- Implement data validation with Pydantic
- Handle serialization between database objects and JSON

## 🤔 What Are Pydantic Schemas?

### **The Problem: Data Validation**

Without schemas, your API accepts any data:
```python
# User sends this JSON
{
  "name": "",           # Empty name - should be invalid
  "capacity": -100,     # Negative capacity - impossible
  "address": None       # Missing address - required field
}

# Your API blindly accepts it and crashes later
```

### **The Solution: Pydantic Schemas**

With schemas, data is validated automatically:
```python
# Pydantic automatically validates:
# ✅ name must be non-empty string
# ✅ capacity must be positive integer  
# ✅ address must be provided
# ❌ Returns validation error if invalid
```

### **Node.js Comparison**

| **Node.js** | **Python** | **Purpose** |
|-------------|------------|-------------|
| Joi schemas | Pydantic schemas | Data validation |
| TypeScript interfaces | Pydantic models | Type definitions |
| express-validator | Pydantic validators | Request validation |
| JSON.stringify() | Pydantic serialization | Response formatting |

## 🏗️ Schema Architecture

### **Two-Layer System**

```python
# Layer 1: Database (SQLAlchemy models)
class Venue(Base):                    # Database table structure
    __tablename__ = 'venues'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

# Layer 2: API (Pydantic schemas)  
class VenueCreate(BaseModel):         # Request validation
    name: str
    capacity: int

class VenueResponse(BaseModel):       # Response serialization
    id: int
    name: str
    capacity: int
```

### **Data Flow**
```
JSON Request → Pydantic Schema → SQLAlchemy Model → Database
Database → SQLAlchemy Model → Pydantic Schema → JSON Response
```

## 📝 Creating Schema Foundation

### **Step 1: Create schemas.py**

Create a new file called `schemas.py`:

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
```

### **Understanding the Imports**

| **Import** | **Purpose** | **Node.js Equivalent** |
|------------|-------------|------------------------|
| `BaseModel` | Base class for schemas | `class` or `interface` |
| `EmailStr` | Email validation | `validator.isEmail()` |
| `datetime` | Date/time handling | `Date` object |
| `List` | Array type hints | `Array<T>` |
| `Optional` | Nullable fields | `field?: type` |

## 🏢 Creating Venue Schemas

### **Step 2: Add Venue Schemas**

```python
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
```

### **Understanding Schema Inheritance**

#### **Base Schema Pattern**
```python
class VenueBase(BaseModel):
    name: str
    capacity: int  
    address: str
```

**Why use a base class?**
- **DRY principle** - Define common fields once
- **Consistency** - Same validation across create/update
- **Maintainability** - Change field in one place

#### **Create Schema**
```python
class VenueCreate(VenueBase):
    pass
```

**What this inherits:**
- All fields from `VenueBase` (name, capacity, address)
- All validation rules
- Type checking

**Why separate from base?**
- **Future flexibility** - Might add create-specific validation
- **Clear intent** - Obviously for creation requests
- **API documentation** - FastAPI generates separate docs

#### **Response Schema**
```python
class VenueResponse(VenueBase):
    id: int
    
    class Config:
        from_attributes = True
```

**Key differences from create:**
- **Includes `id`** - Database generates this after creation
- **Config class** - Enables SQLAlchemy object conversion

### **Understanding the Config Class**

```python
class Config:
    from_attributes = True
```

**What this enables:**
```python
# Without from_attributes = True
venue_dict = {"id": 1, "name": "MSG", "capacity": 20000, "address": "NYC"}
venue_response = VenueResponse(**venue_dict)  # ✅ Works with dict

venue_obj = session.query(Venue).first()
venue_response = VenueResponse(venue_obj)     # ❌ Error with SQLAlchemy object

# With from_attributes = True
venue_obj = session.query(Venue).first()
venue_response = VenueResponse.from_orm(venue_obj)  # ✅ Works with SQLAlchemy object
```

## 🎪 Creating Event Schemas

### **Step 3: Add Event Schemas**

```python
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
```

### **Understanding Nested Schemas**

```python
venue: VenueResponse  # Nested venue information
```

**What this creates:**
```json
{
  "id": 1,
  "name": "Rock Concert",
  "event_date": "2025-01-15T20:00:00",
  "venue_id": 1,
  "venue": {
    "id": 1,
    "name": "Madison Square Garden",
    "capacity": 20000,
    "address": "New York, NY"
  }
}
```

**Benefits:**
- **Rich responses** - Client gets venue details without extra request
- **Type safety** - Pydantic validates nested structure
- **Auto-documentation** - FastAPI shows nested schema in docs

## 🎫 Creating TicketType Schemas

### **Step 4: Add TicketType Schemas**

```python
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
```

### **Understanding Data Types**

| **Pydantic Type** | **Python Type** | **JSON Type** | **Validation** |
|-------------------|-----------------|---------------|----------------|
| `str` | `str` | `"string"` | Must be string |
| `int` | `int` | `123` | Must be integer |
| `float` | `float` | `123.45` | Must be number |
| `bool` | `bool` | `true/false` | Must be boolean |
| `datetime` | `datetime` | `"2025-01-15T20:00:00"` | Must be valid datetime |

## 📋 Creating Booking Schemas

### **Step 5: Add Booking Schemas**

```python
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
```

### **Understanding Complex Nested Schemas**

```python
event: EventResponse
ticket_type: TicketTypeResponse
```

**This creates deeply nested JSON:**
```json
{
  "id": 1,
  "customer_name": "John Doe",
  "customer_email": "john@email.com",
  "quantity": 2,
  "total_price": 599.98,
  "booking_date": "2025-01-10T10:30:00",
  "status": "confirmed",
  "event": {
    "id": 1,
    "name": "Rock Concert",
    "event_date": "2025-01-15T20:00:00",
    "venue_id": 1,
    "venue": {
      "id": 1,
      "name": "Madison Square Garden",
      "capacity": 20000,
      "address": "New York, NY"
    }
  },
  "ticket_type": {
    "id": 1,
    "name": "VIP",
    "price": 299.99
  }
}
```

## ✅ Adding Data Validation

### **Step 6: Enhanced Schemas with Validation**

Replace your basic schemas with validated versions:

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

# Enhanced Venue Schemas
class VenueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Venue name")
    capacity: int = Field(..., gt=0, description="Venue capacity (must be positive)")
    address: str = Field(..., min_length=1, max_length=500, description="Venue address")

class VenueCreate(VenueBase):
    pass

class VenueUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(None, gt=0)
    address: Optional[str] = Field(None, min_length=1, max_length=500)

class VenueResponse(VenueBase):
    id: int
    
    class Config:
        from_attributes = True
```

### **Understanding Field Validation**

#### **Required Fields**
```python
name: str = Field(..., min_length=1, max_length=200)
```
- **`...`** - Field is required (Ellipsis object)
- **`min_length=1`** - Must have at least 1 character
- **`max_length=200`** - Cannot exceed 200 characters

#### **Numeric Validation**
```python
capacity: int = Field(..., gt=0)
```
- **`gt=0`** - Greater than 0 (positive numbers only)
- **Other options**: `ge=0` (≥), `lt=100` (<), `le=100` (≤)

#### **Optional Fields**
```python
name: Optional[str] = Field(None, min_length=1)
```
- **`Optional[str]`** - Can be string or None
- **`None`** - Default value if not provided
- **Still validates** when provided

#### **Email Validation**
```python
customer_email: EmailStr
```
- **Automatic email validation** - Rejects invalid emails
- **Requires `email-validator`** package: `pip install email-validator`

## 🧪 Testing Your Schemas

### **Step 7: Test Schema Validation**

Create a test file `test_schemas.py`:

```python
from schemas import VenueCreate, VenueResponse
from pydantic import ValidationError

# Test valid data
try:
    venue_data = VenueCreate(
        name="Madison Square Garden",
        capacity=20000,
        address="New York, NY"
    )
    print("✅ Valid venue data:", venue_data)
except ValidationError as e:
    print("❌ Validation error:", e)

# Test invalid data
try:
    invalid_venue = VenueCreate(
        name="",           # Empty name - should fail
        capacity=-100,     # Negative capacity - should fail
        address="NYC"
    )
    print("❌ This shouldn't print")
except ValidationError as e:
    print("✅ Caught validation error:", e)
```

Run the test:
```bash
python test_schemas.py
```

**Expected output:**
```
✅ Valid venue data: name='Madison Square Garden' capacity=20000 address='New York, NY'
✅ Caught validation error: 2 validation errors for VenueCreate
name
  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)
capacity
  ensure this value is greater than 0 (type=value_error.number.not_gt; limit_value=0)
```

## 🔄 Request/Response Flow

### **Complete Data Flow Example**

```python
# 1. User sends JSON request
POST /venues
{
  "name": "Wembley Stadium",
  "capacity": 90000,
  "address": "London, UK"
}

# 2. FastAPI validates with VenueCreate schema
venue_data = VenueCreate(**request_json)  # Automatic validation

# 3. Convert to SQLAlchemy model
db_venue = Venue(**venue_data.dict())

# 4. Save to database
db.add(db_venue)
db.commit()
db.refresh(db_venue)  # Get generated ID

# 5. Convert to response schema
venue_response = VenueResponse.from_orm(db_venue)

# 6. Return JSON response
{
  "id": 2,
  "name": "Wembley Stadium",
  "capacity": 90000,
  "address": "London, UK"
}
```

## 🚨 Common Issues and Solutions

### **Issue 1: Circular Import with Nested Schemas**

**Problem:**
```python
# In schemas.py
class EventResponse(EventBase):
    venue: VenueResponse  # VenueResponse not defined yet
```

**Solution:**
```python
# Use forward references
class EventResponse(EventBase):
    venue: "VenueResponse"  # String reference

# Or update forward references at end of file
EventResponse.model_rebuild()
```

### **Issue 2: from_attributes Not Working**

**Problem:**
```python
venue_obj = session.query(Venue).first()
venue_response = VenueResponse(venue_obj)  # Error
```

**Solution:**
```python
# Ensure Config class is properly defined
class VenueResponse(VenueBase):
    id: int
    
    class Config:
        from_attributes = True  # This line is crucial

# Use from_orm method
venue_response = VenueResponse.from_orm(venue_obj)
```

### **Issue 3: Email Validation Not Working**

**Problem:**
```python
ImportError: email-validator must be installed to use EmailStr
```

**Solution:**
```bash
# Install email validator
pip install email-validator

# Or use regular string with custom validation
from pydantic import validator

class BookingBase(BaseModel):
    customer_email: str
    
    @validator('customer_email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
```

## 📚 Key Takeaways

### **Schema Design Patterns**
1. **Base → Create → Response** - Standard inheritance pattern
2. **Validation at boundaries** - Validate input, trust internal data
3. **Nested schemas** - Rich responses with related data
4. **Optional updates** - Partial updates with Optional fields

### **Pydantic vs Node.js Validation**

| **Feature** | **Pydantic** | **Joi (Node.js)** |
|-------------|--------------|-------------------|
| **Type hints** | `name: str` | `name: Joi.string()` |
| **Required fields** | `Field(...)` | `required()` |
| **Validation** | `Field(min_length=1)` | `min(1)` |
| **Nested objects** | `venue: VenueResponse` | `venue: Joi.object()` |
| **Error handling** | `ValidationError` | `error.details` |

### **Best Practices**
1. **Separate create/update schemas** - Different validation rules
2. **Use Field() for validation** - Better error messages
3. **Descriptive field names** - `customer_email` not just `email`
4. **Consistent naming** - `VenueCreate`, `VenueResponse` pattern

## 🚀 Next Steps

Your data validation layer is now complete:

1. ✅ **Request schemas created** (VenueCreate, EventCreate, etc.)
2. ✅ **Response schemas created** (VenueResponse, EventResponse, etc.)
3. ✅ **Validation rules implemented** (Field constraints, email validation)
4. ✅ **Nested schemas configured** (Rich response data)

**Next: [06 - FastAPI Basics →](06-fastapi-basics.md)**

---

**Previous: [← 04 - Models and Relationships](04-models-and-relationships.md) | Next: [06 - FastAPI Basics →](06-fastapi-basics.md)**
