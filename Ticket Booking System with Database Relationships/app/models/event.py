from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Event(Base):
    """Event model for storing event information"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    event_date = Column(DateTime, nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)

    # Relationships
    venue = relationship("Venue", back_populates="events")
    bookings = relationship("Booking", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', venue_id={self.venue_id})>"
