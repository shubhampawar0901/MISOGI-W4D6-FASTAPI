from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database import Base


class TicketType(Base):
    """TicketType model for storing ticket type information"""
    __tablename__ = "ticket_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)  # VIP, Standard, Economy
    price = Column(Float, nullable=False)

    # Relationships
    bookings = relationship("Booking", back_populates="ticket_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TicketType(id={self.id}, name='{self.name}', price={self.price})>"
