# 09 - Testing and Deployment

## 🎯 Learning Objectives

By the end of this section, you will:
- Test your API thoroughly using different methods
- Write automated tests with pytest
- Understand deployment considerations
- Set up monitoring and logging
- Prepare your application for production

## 🧪 Manual Testing with FastAPI Docs

### **Step 1: Interactive API Testing**

Your FastAPI application automatically generates interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

#### **Testing Complete Workflow**

1. **Start your application:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Open Swagger UI** at `http://localhost:8000/docs`

3. **Test the complete booking flow:**

   **a) Create a Venue:**
   ```json
   POST /api/v1/venues
   {
     "name": "Madison Square Garden",
     "capacity": 20000,
     "address": "New York, NY"
   }
   ```

   **b) Create Ticket Types:**
   ```json
   POST /api/v1/ticket-types
   {
     "name": "VIP",
     "price": 299.99
   }
   ```
   ```json
   POST /api/v1/ticket-types
   {
     "name": "Standard",
     "price": 99.99
   }
   ```

   **c) Create an Event:**
   ```json
   POST /api/v1/events
   {
     "name": "Rock Concert",
     "event_date": "2025-01-15T20:00:00",
     "venue_id": 1
   }
   ```

   **d) Create Bookings:**
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

4. **Test Relationships:**
   - `GET /api/v1/events/1` - Should show venue details
   - `GET /api/v1/bookings/1` - Should show event and ticket type details
   - `GET /api/v1/venues/1/events` - Should show events at venue

## 🔧 Command Line Testing with curl

### **Step 2: Testing with curl Commands**

```bash
# Test venue creation
curl -X POST "http://localhost:8000/api/v1/venues" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Wembley Stadium",
       "capacity": 90000,
       "address": "London, UK"
     }'

# Test venue listing
curl -X GET "http://localhost:8000/api/v1/venues"

# Test venue by ID
curl -X GET "http://localhost:8000/api/v1/venues/1"

# Test filtering
curl -X GET "http://localhost:8000/api/v1/events?venue_id=1"

# Test pagination
curl -X GET "http://localhost:8000/api/v1/venues?skip=0&limit=10"
```

### **Expected Responses**

**Successful venue creation (201 Created):**
```json
{
  "id": 1,
  "name": "Wembley Stadium",
  "capacity": 90000,
  "address": "London, UK"
}
```

**Error response (404 Not Found):**
```json
{
  "detail": "Venue not found"
}
```

**Validation error (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "capacity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

## 🧪 Automated Testing with pytest

### **Step 3: Setting Up Test Environment**

Install testing dependencies:
```bash
pip install pytest pytest-asyncio httpx
```

Create `tests/conftest.py`:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app.core.config import settings

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_venue_data():
    return {
        "name": "Test Venue",
        "capacity": 1000,
        "address": "Test Address"
    }


@pytest.fixture
def sample_event_data():
    return {
        "name": "Test Event",
        "event_date": "2025-01-15T20:00:00",
        "venue_id": 1
    }
```

### **Step 4: Writing API Tests**

Create `tests/test_api/test_venues.py`:
```python
import pytest
from fastapi.testclient import TestClient


def test_create_venue(client: TestClient, sample_venue_data):
    """Test venue creation"""
    response = client.post("/api/v1/venues", json=sample_venue_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_venue_data["name"]
    assert data["capacity"] == sample_venue_data["capacity"]
    assert data["address"] == sample_venue_data["address"]
    assert "id" in data


def test_get_venues(client: TestClient, sample_venue_data):
    """Test venue listing"""
    # Create a venue first
    client.post("/api/v1/venues", json=sample_venue_data)
    
    # Get venues
    response = client.get("/api/v1/venues")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == sample_venue_data["name"]


def test_get_venue_by_id(client: TestClient, sample_venue_data):
    """Test getting specific venue"""
    # Create venue
    create_response = client.post("/api/v1/venues", json=sample_venue_data)
    venue_id = create_response.json()["id"]
    
    # Get venue by ID
    response = client.get(f"/api/v1/venues/{venue_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == venue_id
    assert data["name"] == sample_venue_data["name"]


def test_get_nonexistent_venue(client: TestClient):
    """Test 404 for nonexistent venue"""
    response = client.get("/api/v1/venues/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_venue_validation_error(client: TestClient):
    """Test validation errors"""
    invalid_data = {
        "name": "",  # Empty name
        "capacity": -100,  # Negative capacity
        "address": "Test Address"
    }
    response = client.post("/api/v1/venues", json=invalid_data)
    assert response.status_code == 422


def test_update_venue(client: TestClient, sample_venue_data):
    """Test venue update"""
    # Create venue
    create_response = client.post("/api/v1/venues", json=sample_venue_data)
    venue_id = create_response.json()["id"]
    
    # Update venue
    update_data = {
        "name": "Updated Venue",
        "capacity": 2000,
        "address": "Updated Address"
    }
    response = client.put(f"/api/v1/venues/{venue_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["capacity"] == update_data["capacity"]


def test_delete_venue(client: TestClient, sample_venue_data):
    """Test venue deletion"""
    # Create venue
    create_response = client.post("/api/v1/venues", json=sample_venue_data)
    venue_id = create_response.json()["id"]
    
    # Delete venue
    response = client.delete(f"/api/v1/venues/{venue_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/api/v1/venues/{venue_id}")
    assert get_response.status_code == 404
```

### **Step 5: Testing Relationships**

Create `tests/test_api/test_relationships.py`:
```python
import pytest
from fastapi.testclient import TestClient


def test_event_venue_relationship(client: TestClient, sample_venue_data, sample_event_data):
    """Test event-venue relationship"""
    # Create venue
    venue_response = client.post("/api/v1/venues", json=sample_venue_data)
    venue_id = venue_response.json()["id"]
    
    # Create event
    event_data = {**sample_event_data, "venue_id": venue_id}
    event_response = client.post("/api/v1/events", json=event_data)
    assert event_response.status_code == 201
    
    # Get event with venue details
    event_id = event_response.json()["id"]
    get_response = client.get(f"/api/v1/events/{event_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["venue"]["id"] == venue_id
    assert data["venue"]["name"] == sample_venue_data["name"]


def test_booking_calculation(client: TestClient, sample_venue_data, sample_event_data):
    """Test booking price calculation"""
    # Create venue
    venue_response = client.post("/api/v1/venues", json=sample_venue_data)
    venue_id = venue_response.json()["id"]
    
    # Create ticket type
    ticket_type_data = {"name": "VIP", "price": 100.0}
    ticket_response = client.post("/api/v1/ticket-types", json=ticket_type_data)
    ticket_type_id = ticket_response.json()["id"]
    
    # Create event
    event_data = {**sample_event_data, "venue_id": venue_id}
    event_response = client.post("/api/v1/events", json=event_data)
    event_id = event_response.json()["id"]
    
    # Create booking
    booking_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "quantity": 3,
        "event_id": event_id,
        "ticket_type_id": ticket_type_id
    }
    booking_response = client.post("/api/v1/bookings", json=booking_data)
    assert booking_response.status_code == 201
    
    # Verify price calculation
    booking = booking_response.json()
    expected_total = ticket_type_data["price"] * booking_data["quantity"]
    assert booking["total_price"] == expected_total
```

### **Step 6: Running Tests**

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api/test_venues.py

# Run with coverage
pip install pytest-cov
pytest --cov=app tests/

# Run tests and generate HTML coverage report
pytest --cov=app --cov-report=html tests/
```

**Expected output:**
```
========================= test session starts =========================
collected 8 items

tests/test_api/test_venues.py::test_create_venue PASSED        [ 12%]
tests/test_api/test_venues.py::test_get_venues PASSED          [ 25%]
tests/test_api/test_venues.py::test_get_venue_by_id PASSED     [ 37%]
tests/test_api/test_venues.py::test_get_nonexistent_venue PASSED [ 50%]
tests/test_api/test_venues.py::test_create_venue_validation_error PASSED [ 62%]
tests/test_api/test_venues.py::test_update_venue PASSED        [ 75%]
tests/test_api/test_venues.py::test_delete_venue PASSED        [ 87%]
tests/test_api/test_relationships.py::test_event_venue_relationship PASSED [100%]

========================= 8 passed in 2.34s =========================
```

## 📊 Performance Testing

### **Step 7: Load Testing with locust**

Install locust:
```bash
pip install locust
```

Create `locustfile.py`:
```python
from locust import HttpUser, task, between


class TicketBookingUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup test data"""
        # Create venue
        venue_data = {
            "name": "Load Test Venue",
            "capacity": 50000,
            "address": "Load Test Address"
        }
        response = self.client.post("/api/v1/venues", json=venue_data)
        self.venue_id = response.json()["id"]
        
        # Create ticket type
        ticket_data = {"name": "Standard", "price": 50.0}
        response = self.client.post("/api/v1/ticket-types", json=ticket_data)
        self.ticket_type_id = response.json()["id"]
        
        # Create event
        event_data = {
            "name": "Load Test Event",
            "event_date": "2025-01-15T20:00:00",
            "venue_id": self.venue_id
        }
        response = self.client.post("/api/v1/events", json=event_data)
        self.event_id = response.json()["id"]
    
    @task(3)
    def get_venues(self):
        """Test venue listing"""
        self.client.get("/api/v1/venues")
    
    @task(2)
    def get_events(self):
        """Test event listing"""
        self.client.get("/api/v1/events")
    
    @task(1)
    def create_booking(self):
        """Test booking creation"""
        booking_data = {
            "customer_name": "Load Test User",
            "customer_email": "loadtest@example.com",
            "quantity": 1,
            "event_id": self.event_id,
            "ticket_type_id": self.ticket_type_id
        }
        self.client.post("/api/v1/bookings", json=booking_data)
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## 🚀 Deployment Preparation

### **Step 8: Production Configuration**

Create `app/core/config.py` for production:
```python
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "sqlite:///./ticket_booking.db"
    DATABASE_ECHO: bool = False
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Ticket Booking System"
    PROJECT_DESCRIPTION: str = "A comprehensive ticket booking system"
    VERSION: str = "1.0.0"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ALLOWED_HOSTS: list = ["*"]
    
    # Application settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### **Step 9: Docker Configuration**

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/ticketdb
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ticketdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### **Step 10: Production Checklist**

#### **Security**
- [ ] Change default secret keys
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Add rate limiting

#### **Database**
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Add database migrations (Alembic)

#### **Monitoring**
- [ ] Add logging
- [ ] Set up health checks
- [ ] Configure error tracking (Sentry)
- [ ] Add metrics collection

#### **Performance**
- [ ] Enable gzip compression
- [ ] Add caching (Redis)
- [ ] Optimize database queries
- [ ] Set up CDN for static files

## 📚 Key Takeaways

### **Testing Strategy**
1. **Manual testing** - Interactive docs for quick verification
2. **Automated testing** - pytest for regression prevention
3. **Load testing** - locust for performance validation
4. **Integration testing** - Test relationships and business logic

### **Deployment Considerations**
1. **Environment configuration** - Separate dev/staging/production settings
2. **Database migration** - SQLite → PostgreSQL for production
3. **Security hardening** - Secrets management, HTTPS, CORS
4. **Monitoring setup** - Logging, health checks, error tracking

### **Production Readiness**
1. **Scalability** - Horizontal scaling with load balancers
2. **Reliability** - Database backups, error handling
3. **Observability** - Metrics, logs, tracing
4. **Security** - Authentication, authorization, input validation

## 🚀 Next Steps

Your application is now thoroughly tested and deployment-ready:

1. ✅ **Manual testing completed**
2. ✅ **Automated test suite created**
3. ✅ **Performance testing configured**
4. ✅ **Production deployment prepared**

**Next: [10 - Best Practices →](10-best-practices.md)**

---

**Previous: [← 08 - API Endpoints](08-api-endpoints.md) | Next: [10 - Best Practices →](10-best-practices.md)**
