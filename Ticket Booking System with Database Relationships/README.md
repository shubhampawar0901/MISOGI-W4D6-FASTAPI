# Ticket Booking System

A comprehensive ticket booking system built with FastAPI and SQLAlchemy, demonstrating database relationships and modern Python web development practices.

## Features

- **Venue Management**: Create and manage event venues
- **Event Management**: Schedule events at venues
- **Ticket Types**: Define different ticket categories (VIP, Standard, Economy)
- **Booking System**: Handle customer bookings with relationships
- **RESTful API**: Full CRUD operations with proper HTTP status codes
- **Database Relationships**: Demonstrates One-to-Many and Many-to-One relationships
- **Data Validation**: Pydantic schemas for request/response validation
- **Interactive Documentation**: Auto-generated API docs with Swagger UI

## Project Structure

```
app/
├── api/                    # API layer
│   ├── deps.py            # Dependencies
│   └── v1/                # API version 1
│       ├── endpoints/     # Individual route files
│       └── __init__.py    # Main API router
├── core/                  # Core functionality
│   └── config.py         # Settings management
├── models/               # SQLAlchemy models
│   ├── venue.py
│   ├── event.py
│   ├── ticket_type.py
│   └── booking.py
├── schemas/              # Pydantic schemas
│   ├── venue.py
│   ├── event.py
│   ├── ticket_type.py
│   └── booking.py
├── database.py           # Database configuration
└── main.py              # FastAPI application
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and configure as needed:
```bash
cp .env.example .env
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload
```

### 5. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Base URL**: http://localhost:8000/api/v1

## API Endpoints

### Venues
- `POST /api/v1/venues` - Create venue
- `GET /api/v1/venues` - List venues
- `GET /api/v1/venues/{id}` - Get venue
- `PUT /api/v1/venues/{id}` - Update venue
- `DELETE /api/v1/venues/{id}` - Delete venue
- `GET /api/v1/venues/{id}/events` - Get venue with events

### Events (Coming Soon)
- Event management endpoints

### Ticket Types (Coming Soon)
- Ticket type management endpoints

### Bookings (Coming Soon)
- Booking management endpoints

## Database Schema

The system uses SQLite with the following relationships:

```
Venues (1) ←→ (Many) Events (1) ←→ (Many) Bookings (Many) ←→ (1) TicketTypes
```

## Development

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints throughout
- Write descriptive docstrings
- Handle errors gracefully

### Testing
```bash
pytest tests/
```

## Production Considerations

- Replace SQLite with PostgreSQL for production
- Configure proper CORS origins
- Add authentication and authorization
- Implement logging and monitoring
- Use environment-specific configurations
