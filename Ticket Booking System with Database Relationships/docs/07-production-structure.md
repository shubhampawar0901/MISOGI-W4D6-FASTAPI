# 07 - Production-Grade Project Structure

## 🎯 Learning Objectives

By the end of this section, you will:
- Understand industry-standard project organization
- Restructure your code for scalability and maintainability
- Implement proper separation of concerns
- Configure environment-based settings
- Follow professional development practices

## 🚨 Problems with Current Structure

### **Current "Flat" Structure**
```
project/
├── main.py           # Everything mixed together
├── models.py         # All models in one file
├── schemas.py        # All schemas in one file
├── database.py       # Basic configuration
└── requirements.txt
```

### **Issues with This Approach**
1. **Poor scalability** - Files become huge as project grows
2. **No separation of concerns** - Business logic mixed with API logic
3. **Hard to test** - Difficult to mock individual components
4. **No environment management** - Hardcoded configuration
5. **Not team-friendly** - Merge conflicts on large files

## 🏗️ Industry-Standard Structure

### **Professional FastAPI Project Structure**
```
ticket-booking-system/
├── app/                          # Main application package
│   ├── __init__.py              # Makes it a Python package
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # Database connection
│   ├── models/                  # Database models (separate files)
│   │   ├── __init__.py
│   │   ├── venue.py
│   │   ├── event.py
│   │   ├── ticket_type.py
│   │   └── booking.py
│   ├── schemas/                 # Pydantic schemas (separate files)
│   │   ├── __init__.py
│   │   ├── venue.py
│   │   ├── event.py
│   │   ├── ticket_type.py
│   │   └── booking.py
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependencies
│   │   └── v1/                  # API version 1
│   │       ├── __init__.py
│   │       └── endpoints/       # Individual route files
│   │           ├── __init__.py
│   │           ├── venues.py
│   │           ├── events.py
│   │           ├── ticket_types.py
│   │           └── bookings.py
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   └── config.py            # Settings management
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── logger.py            # Logging configuration
├── tests/                       # Test files
│   ├── __init__.py
│   └── test_api/
│       ├── __init__.py
│       └── test_venues.py
├── .env                         # Environment variables
├── .env.example                 # Example environment file
├── .gitignore                   # Git ignore file
├── requirements.txt             # Dependencies
├── README.md                    # Project documentation
└── docker-compose.yml           # Docker configuration (optional)
```

## 🔧 Step-by-Step Restructuring

### **Step 1: Create Folder Structure**

```bash
# Create main app package
mkdir app
mkdir app/models
mkdir app/schemas  
mkdir app/api
mkdir app/api/v1
mkdir app/api/v1/endpoints
mkdir app/core
mkdir app/utils

# Create test directory
mkdir tests
mkdir tests/test_api

# Create package files
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/api/v1/endpoints/__init__.py
touch app/core/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
touch tests/test_api/__init__.py
```

### **Step 2: Environment Configuration**

Create `.env` file:
```env
# Database Configuration
DATABASE_URL=sqlite:///./ticket_booking.db
DATABASE_ECHO=False

# Application Configuration  
DEBUG=True
LOG_LEVEL=INFO
API_V1_STR=/api/v1

# Application Metadata
PROJECT_NAME=Ticket Booking System
PROJECT_DESCRIPTION=A comprehensive ticket booking system with database relationships
VERSION=1.0.0
```

Create `app/core/config.py`:
```python
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./ticket_booking.db"
    DATABASE_ECHO: bool = False
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Ticket Booking System"
    PROJECT_DESCRIPTION: str = "A comprehensive ticket booking system with database relationships"
    VERSION: str = "1.0.0"
    
    # Application settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
```

### **Understanding Environment-Based Configuration**

#### **Why Use Environment Variables?**
```python
# Bad - Hardcoded values
DATABASE_URL = "sqlite:///./ticket_booking.db"  # Can't change for production

# Good - Environment-based
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ticket_booking.db")
```

**Benefits:**
- **Different environments** - Development, staging, production
- **Security** - Keep secrets out of code
- **Flexibility** - Change settings without code changes
- **12-Factor App compliance** - Industry standard

#### **Pydantic Settings**
```python
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ticket_booking.db"
    
    class Config:
        env_file = ".env"
```

**What this provides:**
- **Type validation** - Ensures DATABASE_URL is a string
- **Default values** - Fallback if environment variable not set
- **Auto-loading** - Reads from .env file automatically
- **IDE support** - Autocomplete and type checking

### **Step 3: Update Database Configuration**

Update `app/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Create database engine with settings
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DATABASE_ECHO
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 📁 Separating Models

### **Step 4: Individual Model Files**

Create `app/models/__init__.py`:
```python
from app.database import Base
from .venue import Venue
from .event import Event  
from .ticket_type import TicketType
from .booking import Booking

__all__ = ["Base", "Venue", "Event", "TicketType", "Booking"]
```

Create `app/models/venue.py`:
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Venue(Base):
    """Venue model for storing venue information"""
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    address = Column(String, nullable=False)

    # Relationships
    events = relationship("Event", back_populates="venue", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venue(id={self.id}, name='{self.name}', capacity={self.capacity})>"
```

### **Benefits of Separate Model Files**
1. **Single responsibility** - Each file handles one model
2. **Easier navigation** - Find specific model quickly
3. **Reduced conflicts** - Multiple developers can work simultaneously
4. **Better organization** - Related code grouped together

## 📋 Separating Schemas

### **Step 5: Individual Schema Files**

Create `app/schemas/__init__.py`:
```python
from .venue import VenueCreate, VenueResponse, VenueUpdate
from .event import EventCreate, EventResponse, EventUpdate
from .ticket_type import TicketTypeCreate, TicketTypeResponse, TicketTypeUpdate
from .booking import BookingCreate, BookingResponse, BookingUpdate

__all__ = [
    "VenueCreate", "VenueResponse", "VenueUpdate",
    "EventCreate", "EventResponse", "EventUpdate", 
    "TicketTypeCreate", "TicketTypeResponse", "TicketTypeUpdate",
    "BookingCreate", "BookingResponse", "BookingUpdate"
]
```

Create `app/schemas/venue.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional, List


class VenueBase(BaseModel):
    """Base venue schema with common fields"""
    name: str = Field(..., min_length=1, max_length=200, description="Venue name")
    capacity: int = Field(..., gt=0, description="Venue capacity (must be positive)")
    address: str = Field(..., min_length=1, max_length=500, description="Venue address")


class VenueCreate(VenueBase):
    """Schema for creating a new venue"""
    pass


class VenueUpdate(BaseModel):
    """Schema for updating a venue"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(None, gt=0)
    address: Optional[str] = Field(None, min_length=1, max_length=500)


class VenueResponse(VenueBase):
    """Schema for venue response"""
    id: int
    
    class Config:
        from_attributes = True
```

## 🌐 API Structure with Versioning

### **Step 6: API Dependencies**

Create `app/api/deps.py`:
```python
from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator:
    """
    Dependency function that yields database sessions.
    
    This function creates a new SQLAlchemy SessionLocal that will be used
    in a single request, and then close it once the request is finished.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
```

### **Step 7: Individual Endpoint Files**

Create `app/api/v1/endpoints/venues.py`:
```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.venue import Venue
from app.schemas.venue import VenueCreate, VenueResponse, VenueUpdate

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
```

### **Step 8: API Router Assembly**

Create `app/api/v1/__init__.py`:
```python
from fastapi import APIRouter
from app.api.v1.endpoints import venues

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])

# TODO: Add other routers when created
# api_router.include_router(events.router, prefix="/events", tags=["events"])
# api_router.include_router(ticket_types.router, prefix="/ticket-types", tags=["ticket-types"])
# api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
```

### **Understanding API Versioning**

```python
# URL structure: /api/v1/venues
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
```

**Benefits of versioning:**
- **Backward compatibility** - v1 continues working when v2 is released
- **Gradual migration** - Clients can upgrade at their own pace
- **Clear organization** - Different versions in separate folders

## 🚀 New Main Application

### **Step 9: Production-Ready Main App**

Create `app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_router
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_url": settings.API_V1_STR
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
```

### **Understanding the New Structure**

#### **Configuration-Driven**
```python
title=settings.PROJECT_NAME,
openapi_url=f"{settings.API_V1_STR}/openapi.json",
```
- **All settings from environment** - Easy to change per environment
- **No hardcoded values** - Configuration centralized

#### **CORS Middleware**
```python
app.add_middleware(CORSMiddleware, ...)
```
- **Cross-Origin Resource Sharing** - Allows frontend apps to call API
- **Production consideration** - Replace `["*"]` with specific domains

#### **Health Check Endpoint**
```python
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
```
- **Monitoring support** - Load balancers can check if app is healthy
- **DevOps requirement** - Standard in production environments

## 🧪 Testing the New Structure

### **Step 10: Run the Restructured Application**

```bash
# Install new dependencies
pip install pydantic-settings

# Run the new application
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1234] using StatReload
INFO:     Started server process [5678]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### **Test the New API Structure**

Visit these URLs:
- **Root**: `http://localhost:8000/` - Should show welcome message
- **Health**: `http://localhost:8000/health` - Should show health status
- **Docs**: `http://localhost:8000/docs` - Should show API documentation
- **Venues**: `http://localhost:8000/api/v1/venues` - Should work as before

## 📚 Key Benefits of New Structure

### **Scalability**
- **Easy to add new features** - Create new endpoint files
- **Team collaboration** - Multiple developers can work without conflicts
- **Code organization** - Related code grouped together

### **Maintainability**
- **Single responsibility** - Each file has one purpose
- **Easy debugging** - Know exactly where to look for issues
- **Clear dependencies** - Import structure shows relationships

### **Professional Standards**
- **Industry patterns** - Follows FastAPI best practices
- **Environment management** - Production-ready configuration
- **API versioning** - Supports multiple API versions
- **Documentation** - Self-documenting code structure

## 🚀 Next Steps

Your project now follows industry standards:

1. ✅ **Professional folder structure**
2. ✅ **Environment-based configuration**
3. ✅ **Separated concerns** (models, schemas, endpoints)
4. ✅ **API versioning** (/api/v1/)
5. ✅ **Production-ready setup**

**Next: [08 - API Endpoints →](08-api-endpoints.md)**

---

**Previous: [← 06 - FastAPI Basics](06-fastapi-basics.md) | Next: [08 - API Endpoints →](08-api-endpoints.md)**
