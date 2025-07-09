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
