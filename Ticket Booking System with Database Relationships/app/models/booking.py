from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Booking(Base):
    """Booking model for storing booking information"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, confirmed, cancelled

    # Foreign Keys
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="bookings")
    ticket_type = relationship("TicketType", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(id={self.id}, customer='{self.customer_name}', status='{self.status}')>"
