Ticket Booking System with Database Relationships
Requirements
Create a FastAPI application for ticket booking management with related database entities (Events, Venues, Ticket Types, Bookings).

API Endpoints to Implement
Events:
POST /events - Create new event
GET /events - Get all events
GET /events/{event_id}/bookings - Get all bookings for a specific event
GET /events/{event_id}/available-tickets - Get available tickets for an event
Venues:
POST /venues - Create new venue
GET /venues - Get all venues
GET /venues/{venue_id}/events - Get all events at a specific venue
Ticket Types:
POST /ticket-types - Create new ticket type (VIP, Standard, Economy)
GET /ticket-types - Get all ticket types
GET /ticket-types/{type_id}/bookings - Get all bookings for a specific ticket type
Bookings:
POST /bookings - Create new booking (requires existing event_id, venue_id, ticket_type_id)
GET /bookings - Get all bookings with event, venue, and ticket type details
PUT /bookings/{booking_id} - Update booking details
DELETE /bookings/{booking_id} - Cancel a booking
PATCH /bookings/{booking_id}/status - Update booking status (confirmed, cancelled, pending)
Advanced Queries:
GET /bookings/search?event=name&venue=name&ticket_type=type - Search bookings by event name, venue, and/or ticket type
GET /booking-system/stats - Get booking statistics (total bookings, events, venues, available tickets)
GET /events/{event_id}/revenue - Calculate total revenue for a specific event
GET /venues/{venue_id}/occupancy - Get venue occupancy statistics
UI Features
Events Section: Add events, view event list with booking counts and revenue
Venues Section: Add venues, view venues with event counts and capacity
Ticket Types Section: Add ticket types with pricing, view types with booking counts
Bookings Section: Create bookings with dropdowns for events/venues/ticket types, view all bookings
Search Interface: Filter bookings by event, venue, and ticket type
Statistics Dashboard: Show total counts, revenue, and occupancy rates
Relationship Display: Show booking details with event name, venue name, and ticket type
Calendar View: Display events by date with booking availability
Database Relationships to Demonstrate
One-to-Many: Event → Bookings, Venue → Events, Ticket Type → Bookings
Many-to-One: Bookings → Event, Events → Venue, Bookings → Ticket Type
Foreign Key Constraints: Prevent creating bookings with invalid event/venue/ticket type IDs
Cascade Operations: Understand what happens when deleting events/venues/ticket types
Join Operations: Fetch bookings with related event, venue, and ticket type data in single query
Complex Relationships: Handle venue capacity limits, ticket availability, and pricing calculations
Additional Features
Capacity Management: Track and enforce venue capacity limits
Pricing Logic: Calculate total booking cost based on ticket type and quantity
Availability Tracking: Real-time ticket availability updates
Booking Confirmations: Generate booking confirmation codes
Revenue Reporting: Track sales and revenue by event, venue, and time period