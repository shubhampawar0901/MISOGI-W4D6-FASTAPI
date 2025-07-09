from fastapi import APIRouter
from app.api.v1.endpoints import venues, events, ticket_types, bookings

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(ticket_types.router, prefix="/ticket-types", tags=["ticket-types"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])