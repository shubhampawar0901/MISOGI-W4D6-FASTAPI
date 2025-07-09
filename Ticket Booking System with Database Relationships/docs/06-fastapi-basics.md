# 06 - FastAPI Basics and Your First API

## 🎯 Learning Objectives

By the end of this section, you will:
- Create your first FastAPI application
- Build CRUD endpoints for venues
- Understand dependency injection with database sessions
- Handle HTTP status codes and error responses
- Test your API with interactive documentation

## 🚀 Creating Your FastAPI Application

### **Step 1: Create main.py**

Create a new file called `main.py`:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, get_db
from models import Venue, Event, TicketType, Booking
from schemas import (
    VenueCreate, VenueResponse,
    EventCreate, EventResponse, 
    TicketTypeCreate, TicketTypeResponse,
    BookingCreate, BookingResponse
)

# Create FastAPI application
app = FastAPI(
    title="Ticket Booking System",
    description="A comprehensive ticket booking system with database relationships",
    version="1.0.0"
)

# Create database tables on startup
from models import Base
Base.metadata.create_all(bind=engine)
```

### **Understanding FastAPI Application Setup**

#### **FastAPI Instance**
```python
app = FastAPI(
    title="Ticket Booking System",
    description="A comprehensive ticket booking system with database relationships", 
    version="1.0.0"
)
```

**What this creates:**
- **Web application instance** (like `const app = express()` in Node.js)
- **Automatic documentation** - Title and description appear in `/docs`
- **OpenAPI schema** - Auto-generated API specification

#### **Database Table Creation**
```python
Base.metadata.create_all(bind=engine)
```

**What this does:**
- **Creates tables** if they don't exist
- **Safe to run multiple times** - Only creates missing tables
- **Runs on app startup** - Tables ready before first request

### **Node.js Comparison**

| **FastAPI** | **Express.js** | **Purpose** |
|-------------|----------------|-------------|
| `app = FastAPI()` | `app = express()` | Create app instance |
| `@app.get("/")` | `app.get("/", ...)` | Define route |
| `Depends(get_db)` | Middleware | Dependency injection |
| `response_model=VenueResponse` | Manual serialization | Auto response formatting |

## 🏢 Creating Venue Endpoints

### **Step 2: Add Venue CRUD Operations**

Add these endpoints to your `main.py`:

```python
# Venue Endpoints
@app.post("/venues", response_model=VenueResponse, status_code=201)
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
    """Create a new venue"""
    # Create SQLAlchemy model instance
    db_venue = Venue(
        name=venue.name,
        capacity=venue.capacity,
        address=venue.address
    )
    
    # Add to database
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)  # Get the generated ID
    
    return db_venue

@app.get("/venues", response_model=List[VenueResponse])
def get_venues(db: Session = Depends(get_db)):
    """Get all venues"""
    venues = db.query(Venue).all()
    return venues

@app.get("/venues/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """Get a specific venue by ID"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue
```

### **Understanding Each Endpoint**

#### **POST /venues (Create Venue)**

```python
@app.post("/venues", response_model=VenueResponse, status_code=201)
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
```

**Decorator parameters:**
- **`@app.post("/venues")`** - Handle POST requests to `/venues`
- **`response_model=VenueResponse`** - Serialize response using VenueResponse schema
- **`status_code=201`** - Return 201 Created (instead of default 200 OK)

**Function parameters:**
- **`venue: VenueCreate`** - Request body validated against VenueCreate schema
- **`db: Session = Depends(get_db)`** - Inject database session

**Database operations:**
```python
# Create SQLAlchemy object from Pydantic data
db_venue = Venue(name=venue.name, capacity=venue.capacity, address=venue.address)

# Alternative shorthand
db_venue = Venue(**venue.dict())

# Save to database
db.add(db_venue)        # Stage for insertion
db.commit()             # Actually save to database
db.refresh(db_venue)    # Reload to get generated ID
```

#### **GET /venues (List All Venues)**

```python
@app.get("/venues", response_model=List[VenueResponse])
def get_venues(db: Session = Depends(get_db)):
```

**Key points:**
- **`List[VenueResponse]`** - Returns array of venue objects
- **`db.query(Venue).all()`** - SELECT * FROM venues
- **Automatic serialization** - SQLAlchemy objects → Pydantic schemas → JSON

#### **GET /venues/{venue_id} (Get Single Venue)**

```python
@app.get("/venues/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
```

**Path parameters:**
- **`{venue_id}`** - URL path parameter
- **`venue_id: int`** - Automatic type conversion and validation

**Error handling:**
```python
if not venue:
    raise HTTPException(status_code=404, detail="Venue not found")
```

## 🔧 Understanding Dependency Injection

### **What is `Depends(get_db)`?**

```python
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
```

**How it works:**
1. **FastAPI calls `get_db()`** before your endpoint function
2. **`get_db()` yields a database session**
3. **FastAPI passes session** as `db` parameter
4. **After endpoint completes**, `get_db()` closes the session

**Node.js equivalent:**
```javascript
// Express middleware pattern
app.post('/venues', async (req, res) => {
  const db = createSession();  // Manual session creation
  try {
    // Your endpoint logic
    const venue = await db.venue.create(req.body);
    res.json(venue);
  } finally {
    await db.close();  // Manual cleanup
  }
});
```

### **Benefits of Dependency Injection**
1. **Automatic cleanup** - Session always closed
2. **Testability** - Easy to mock database
3. **Reusability** - Same pattern across all endpoints
4. **Type safety** - IDE knows `db` is a Session

## 🧪 Testing Your API

### **Step 3: Start the Development Server**

```bash
# Start FastAPI development server
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1234] using StatReload
INFO:     Started server process [5678]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### **Step 4: Access Interactive Documentation**

Open your browser and visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### **Step 5: Test Venue Creation**

In the Swagger UI:

1. **Click on "POST /venues"**
2. **Click "Try it out"**
3. **Enter this JSON in the request body:**
   ```json
   {
     "name": "Madison Square Garden",
     "capacity": 20000,
     "address": "New York, NY"
   }
   ```
4. **Click "Execute"**

**Expected response:**
```json
{
  "id": 1,
  "name": "Madison Square Garden",
  "capacity": 20000,
  "address": "New York, NY"
}
```

### **Step 6: Test Venue Listing**

1. **Click on "GET /venues"**
2. **Click "Try it out"**
3. **Click "Execute"**

**Expected response:**
```json
[
  {
    "id": 1,
    "name": "Madison Square Garden",
    "capacity": 20000,
    "address": "New York, NY"
  }
]
```

## 🚨 Error Handling

### **Adding Proper Error Handling**

Update your endpoints with better error handling:

```python
@app.post("/venues", response_model=VenueResponse, status_code=201)
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
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
            status_code=400,
            detail=f"Error creating venue: {str(e)}"
        )

@app.get("/venues/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """Get a specific venue by ID"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=404,
            detail=f"Venue with id {venue_id} not found"
        )
    return venue
```

### **Understanding HTTP Status Codes**

| **Status Code** | **Meaning** | **When to Use** |
|-----------------|-------------|-----------------|
| **200 OK** | Success | GET requests (default) |
| **201 Created** | Resource created | POST requests |
| **400 Bad Request** | Invalid input | Validation errors |
| **404 Not Found** | Resource not found | GET by ID fails |
| **500 Internal Server Error** | Server error | Unhandled exceptions |

## 🔄 Adding Update and Delete Operations

### **Step 7: Complete CRUD Operations**

Add these endpoints to complete your venue CRUD:

```python
@app.put("/venues/{venue_id}", response_model=VenueResponse)
def update_venue(venue_id: int, venue_update: VenueCreate, db: Session = Depends(get_db)):
    """Update a venue"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Update fields
    venue.name = venue_update.name
    venue.capacity = venue_update.capacity
    venue.address = venue_update.address
    
    try:
        db.commit()
        db.refresh(venue)
        return venue
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating venue: {str(e)}")

@app.delete("/venues/{venue_id}", status_code=204)
def delete_venue(venue_id: int, db: Session = Depends(get_db)):
    """Delete a venue"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    try:
        db.delete(venue)
        db.commit()
        return None  # 204 No Content
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting venue: {str(e)}")
```

## 📊 Testing Complete CRUD Operations

### **Test Update (PUT)**

1. **Create a venue first** (if you haven't already)
2. **Use PUT /venues/1** with this JSON:
   ```json
   {
     "name": "Updated Venue Name",
     "capacity": 25000,
     "address": "Updated Address"
   }
   ```

### **Test Delete (DELETE)**

1. **Use DELETE /venues/1**
2. **Should return 204 No Content**
3. **Try GET /venues/1** - should return 404 Not Found

## 🎯 API Design Best Practices

### **RESTful URL Patterns**

| **HTTP Method** | **URL** | **Purpose** | **Request Body** | **Response** |
|-----------------|---------|-------------|------------------|--------------|
| **GET** | `/venues` | List all venues | None | Array of venues |
| **POST** | `/venues` | Create venue | Venue data | Created venue |
| **GET** | `/venues/{id}` | Get specific venue | None | Single venue |
| **PUT** | `/venues/{id}` | Update venue | Updated data | Updated venue |
| **DELETE** | `/venues/{id}` | Delete venue | None | No content |

### **Response Model Benefits**

```python
@app.get("/venues", response_model=List[VenueResponse])
```

**What `response_model` provides:**
1. **Automatic serialization** - SQLAlchemy → Pydantic → JSON
2. **Data filtering** - Only includes fields defined in schema
3. **Type validation** - Ensures response matches schema
4. **Documentation** - Shows response format in `/docs`

## 🚨 Common Issues and Solutions

### **Issue 1: Database Session Not Closing**

**Problem:**
```
sqlalchemy.exc.InvalidRequestError: This Session's transaction has been rolled back
```

**Solution:**
```python
# Always use Depends(get_db) - never create sessions manually
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):  # ✅ Good
    
# Avoid manual session management
def create_venue(venue: VenueCreate):  # ❌ Bad
    db = SessionLocal()
    # ... forgot to close session
```

### **Issue 2: Validation Errors Not Showing**

**Problem:**
```
422 Unprocessable Entity with unclear error message
```

**Solution:**
```python
# Pydantic automatically validates request body
# Check your schema definitions match the request data

# Example: If schema expects 'capacity: int' but you send 'capacity: "string"'
# FastAPI will return detailed validation error
```

### **Issue 3: Foreign Key Constraint Errors**

**Problem:**
```
FOREIGN KEY constraint failed
```

**Solution:**
```python
# Ensure referenced records exist before creating relationships
# Example: Create venue before creating events at that venue

# 1. Create venue first
venue = Venue(name="MSG", capacity=20000, address="NYC")
db.add(venue)
db.commit()

# 2. Then create event with valid venue_id
event = Event(name="Concert", event_date=datetime.now(), venue_id=venue.id)
```

## 📚 Key Takeaways

### **FastAPI vs Express.js**

| **Feature** | **FastAPI** | **Express.js** |
|-------------|-------------|----------------|
| **Route definition** | `@app.get("/")` | `app.get("/", ...)` |
| **Request validation** | Automatic (Pydantic) | Manual (Joi, etc.) |
| **Response serialization** | Automatic | Manual |
| **Documentation** | Auto-generated | Manual (Swagger) |
| **Type safety** | Built-in | TypeScript needed |

### **Key Concepts**
1. **Dependency injection** - `Depends(get_db)` for database sessions
2. **Automatic validation** - Pydantic schemas validate requests
3. **Response models** - Control what data is returned
4. **HTTP status codes** - Use appropriate codes for different scenarios

## 🚀 Next Steps

Your basic API is now functional:

1. ✅ **FastAPI application created**
2. ✅ **Complete CRUD operations** for venues
3. ✅ **Error handling implemented**
4. ✅ **Interactive documentation working**

**Next: [07 - Production Structure →](07-production-structure.md)**

---

**Previous: [← 05 - Pydantic Schemas](05-pydantic-schemas.md) | Next: [07 - Production Structure →](07-production-structure.md)**
