from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Venue(Base):
    __tablename__ = 'venues'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    
    # Relationship: One venue can have many events
    events = relationship("Event", back_populates="venue")

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)
    
    # Relationships
    venue = relationship("Venue", back_populates="events")
    bookings = relationship("Booking", back_populates="event")

class TicketType(Base):
    __tablename__ = 'ticket_types'
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationship: One ticket type can have many bookings
    bookings = relationship("Booking", back_populates="ticket_type")

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    
    # Foreign Keys
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey('ticket_types.id'), nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="bookings")
    ticket_type = relationship("TicketType", back_populates="bookings")
