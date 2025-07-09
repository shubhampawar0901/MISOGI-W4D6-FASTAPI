from pydantic import BaseModel, Field
from typing import Optional, List


class VenueBase(BaseModel):
    """Base venue schema with common fields"""
    name: str = Field(..., min_length=1, max_length=200, description="Venue name")
    capacity: int = Field(..., gt=0, description="Venue capacity (must be positive)")
    address: str = Field(..., min_length=1, max_length=500, description="Venue address")


class VenueCreate(VenueBase):
    """Schema for creating a new venue"""
    pass


class VenueUpdate(BaseModel):
    """Schema for updating a venue"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(None, gt=0)
    address: Optional[str] = Field(None, min_length=1, max_length=500)


class VenueResponse(VenueBase):
    """Schema for venue response"""
    id: int
    
    class Config:
        from_attributes = True


class VenueWithEvents(VenueResponse):
    """Schema for venue with related events"""
    events: List["EventResponse"] = []
    
    class Config:
        from_attributes = True
