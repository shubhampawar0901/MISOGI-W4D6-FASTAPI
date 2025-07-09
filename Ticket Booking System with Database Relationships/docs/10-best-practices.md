# 10 - Best Practices and Production Considerations

## 🎯 Learning Objectives

By the end of this section, you will:
- Understand production-grade coding standards
- Implement security best practices
- Optimize performance and scalability
- Set up proper monitoring and logging
- Follow industry standards for maintainable code

## 🔒 Security Best Practices

### **1. Environment Variables and Secrets Management**

#### **Never Hardcode Secrets**
```python
# ❌ Bad - Hardcoded secrets
DATABASE_URL = "postgresql://user:password123@localhost/db"
SECRET_KEY = "super-secret-key"

# ✅ Good - Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

#### **Use Pydantic Settings for Validation**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str = Field(..., min_length=32)
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('postgresql://', 'sqlite://')):
            raise ValueError('Invalid database URL')
        return v
```

### **2. Input Validation and Sanitization**

#### **Comprehensive Pydantic Validation**
```python
from pydantic import BaseModel, Field, EmailStr, validator

class BookingCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=200, regex=r'^[a-zA-Z\s]+$')
    customer_email: EmailStr
    quantity: int = Field(..., gt=0, le=10)  # Max 10 tickets per booking
    
    @validator('customer_name')
    def validate_name(cls, v):
        if any(char in v for char in ['<', '>', '&', '"', "'"]):
            raise ValueError('Name contains invalid characters')
        return v.strip()
```

#### **SQL Injection Prevention**
```python
# ✅ Good - Using SQLAlchemy ORM (automatically prevents SQL injection)
venues = db.query(Venue).filter(Venue.name.ilike(f"%{search_term}%")).all()

# ❌ Bad - Raw SQL (vulnerable to injection)
venues = db.execute(f"SELECT * FROM venues WHERE name LIKE '%{search_term}%'")
```

### **3. Authentication and Authorization**

#### **JWT Token Implementation**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected-endpoint")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello {current_user}"}
```

#### **Role-Based Access Control**
```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

def require_role(required_role: UserRole):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in [required_role, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

@app.delete("/venues/{venue_id}")
def delete_venue(venue_id: int, user: dict = Depends(require_role(UserRole.ADMIN))):
    # Only admins can delete venues
    pass
```

## 🚀 Performance Optimization

### **4. Database Optimization**

#### **Connection Pooling**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to maintain
    max_overflow=30,       # Additional connections when pool is full
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600,     # Recycle connections every hour
)
```

#### **Query Optimization**
```python
# ✅ Good - Eager loading to prevent N+1 queries
from sqlalchemy.orm import joinedload

events = db.query(Event).options(
    joinedload(Event.venue),
    joinedload(Event.bookings)
).all()

# ❌ Bad - Lazy loading causes N+1 queries
events = db.query(Event).all()
for event in events:
    print(event.venue.name)  # Triggers separate query for each event
```

#### **Database Indexing**
```python
class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, nullable=False, index=True)  # Frequently searched
    booking_date = Column(DateTime, default=datetime.utcnow, index=True)  # For date ranges
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    
    # Composite index for common query patterns
    __table_args__ = (
        Index('idx_booking_event_date', 'event_id', 'booking_date'),
        Index('idx_booking_email_status', 'customer_email', 'status'),
    )
```

### **5. Caching Strategies**

#### **Redis Caching**
```python
import redis
from functools import wraps
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)  # Cache for 10 minutes
def get_popular_events():
    return db.query(Event).join(Booking).group_by(Event.id).order_by(func.count(Booking.id).desc()).limit(10).all()
```

#### **HTTP Caching Headers**
```python
from fastapi import Response

@app.get("/venues")
def get_venues(response: Response):
    venues = db.query(Venue).all()
    
    # Set cache headers
    response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes
    response.headers["ETag"] = f'"{hash(str(venues))}"'
    
    return venues
```

## 📊 Monitoring and Logging

### **6. Structured Logging**

#### **Logging Configuration**
```python
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

logger = setup_logging()
```

#### **Request Logging Middleware**
```python
import time
import uuid
from fastapi import Request, Response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Log request
    start_time = time.time()
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent"),
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": process_time,
        }
    )
    
    return response
```

### **7. Health Checks and Metrics**

#### **Comprehensive Health Check**
```python
from sqlalchemy import text

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "checks": {}
    }
    
    # Database check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis check (if using Redis)
    try:
        redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return Response(
        content=json.dumps(health_status),
        status_code=status_code,
        media_type="application/json"
    )
```

#### **Prometheus Metrics**
```python
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🏗️ Code Quality and Maintainability

### **8. Error Handling**

#### **Custom Exception Classes**
```python
class TicketBookingException(Exception):
    """Base exception for ticket booking system"""
    pass

class VenueNotFoundError(TicketBookingException):
    """Raised when venue is not found"""
    pass

class InsufficientCapacityError(TicketBookingException):
    """Raised when venue doesn't have enough capacity"""
    pass

class BookingValidationError(TicketBookingException):
    """Raised when booking validation fails"""
    pass
```

#### **Global Exception Handler**
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(VenueNotFoundError)
async def venue_not_found_handler(request: Request, exc: VenueNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "error_type": "venue_not_found"}
    )

@app.exception_handler(InsufficientCapacityError)
async def insufficient_capacity_handler(request: Request, exc: InsufficientCapacityError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": "insufficient_capacity"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_type": "internal_error"}
    )
```

### **9. Code Documentation**

#### **Comprehensive Docstrings**
```python
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db)
) -> BookingResponse:
    """
    Create a new booking with automatic price calculation.
    
    Args:
        booking: Booking data including customer info, event, and ticket type
        db: Database session dependency
        
    Returns:
        BookingResponse: Created booking with calculated total price
        
    Raises:
        HTTPException: 404 if event or ticket type not found
        HTTPException: 400 if booking validation fails
        HTTPException: 400 if insufficient venue capacity
        
    Example:
        ```python
        booking_data = BookingCreate(
            customer_name="John Doe",
            customer_email="john@example.com",
            quantity=2,
            event_id=1,
            ticket_type_id=1
        )
        booking = create_booking(booking_data, db)
        ```
    """
    # Implementation here
    pass
```

#### **API Documentation**
```python
@app.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=201,
    summary="Create a new booking",
    description="Create a new booking with automatic price calculation based on ticket type and quantity",
    response_description="The created booking with calculated total price",
    tags=["bookings"]
)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    """Create a new booking endpoint"""
    pass
```

### **10. Testing Best Practices**

#### **Test Organization**
```python
# tests/conftest.py - Shared fixtures
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_venue():
    return {
        "name": "Test Venue",
        "capacity": 1000,
        "address": "Test Address"
    }

# tests/test_venues.py - Venue-specific tests
class TestVenues:
    def test_create_venue_success(self, test_client, sample_venue):
        """Test successful venue creation"""
        pass
    
    def test_create_venue_validation_error(self, test_client):
        """Test venue creation with invalid data"""
        pass
    
    def test_get_venue_not_found(self, test_client):
        """Test getting non-existent venue"""
        pass
```

#### **Comprehensive Test Coverage**
```python
# Test all CRUD operations
def test_venue_crud_operations(test_client, sample_venue):
    # Create
    create_response = test_client.post("/api/v1/venues", json=sample_venue)
    assert create_response.status_code == 201
    venue_id = create_response.json()["id"]
    
    # Read
    get_response = test_client.get(f"/api/v1/venues/{venue_id}")
    assert get_response.status_code == 200
    
    # Update
    update_data = {**sample_venue, "name": "Updated Venue"}
    update_response = test_client.put(f"/api/v1/venues/{venue_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Venue"
    
    # Delete
    delete_response = test_client.delete(f"/api/v1/venues/{venue_id}")
    assert delete_response.status_code == 204
    
    # Verify deletion
    get_deleted_response = test_client.get(f"/api/v1/venues/{venue_id}")
    assert get_deleted_response.status_code == 404
```

## 📋 Production Deployment Checklist

### **11. Pre-Deployment Checklist**

#### **Security**
- [ ] All secrets moved to environment variables
- [ ] HTTPS enabled with valid SSL certificates
- [ ] CORS configured for specific origins
- [ ] Rate limiting implemented
- [ ] Input validation comprehensive
- [ ] SQL injection prevention verified
- [ ] Authentication and authorization implemented

#### **Performance**
- [ ] Database connection pooling configured
- [ ] Query optimization completed
- [ ] Caching strategy implemented
- [ ] Static file serving optimized
- [ ] Gzip compression enabled
- [ ] Database indexes created

#### **Monitoring**
- [ ] Structured logging implemented
- [ ] Health check endpoints created
- [ ] Metrics collection configured
- [ ] Error tracking set up (Sentry)
- [ ] Performance monitoring enabled
- [ ] Alerting rules configured

#### **Reliability**
- [ ] Database backups automated
- [ ] Graceful shutdown handling
- [ ] Circuit breakers implemented
- [ ] Retry logic for external services
- [ ] Failover mechanisms tested
- [ ] Disaster recovery plan documented

## 📚 Key Takeaways

### **Security First**
1. **Never trust user input** - Validate everything
2. **Use environment variables** - Keep secrets out of code
3. **Implement proper authentication** - JWT tokens, role-based access
4. **Follow OWASP guidelines** - Stay updated on security best practices

### **Performance Matters**
1. **Database optimization** - Indexing, connection pooling, query optimization
2. **Caching strategies** - Redis, HTTP caching, application-level caching
3. **Monitoring and profiling** - Identify bottlenecks early
4. **Load testing** - Verify performance under stress

### **Code Quality**
1. **Comprehensive testing** - Unit, integration, and end-to-end tests
2. **Clear documentation** - Code comments, API docs, README files
3. **Error handling** - Graceful degradation, meaningful error messages
4. **Code organization** - Separation of concerns, modular design

### **Production Readiness**
1. **Monitoring and logging** - Observability into system behavior
2. **Health checks** - Automated monitoring of system health
3. **Deployment automation** - CI/CD pipelines, infrastructure as code
4. **Disaster recovery** - Backup strategies, failover procedures

## 🚀 Congratulations!

You've completed the comprehensive Ticket Booking System tutorial! You now have:

1. ✅ **Production-grade FastAPI application**
2. ✅ **Proper database relationships and models**
3. ✅ **Comprehensive API with CRUD operations**
4. ✅ **Security best practices implemented**
5. ✅ **Performance optimization techniques**
6. ✅ **Monitoring and logging setup**
7. ✅ **Testing strategies and deployment readiness**

### **Next Steps for Continued Learning**
- Implement advanced features (search, analytics, reporting)
- Add real-time features with WebSockets
- Integrate with external payment systems
- Build a frontend application (React, Vue.js)
- Explore microservices architecture
- Learn about Kubernetes deployment

---

**Previous: [← 09 - Testing and Deployment](09-testing-and-deployment.md)**

**🎉 Tutorial Complete! You're now ready to build production-grade FastAPI applications!**
