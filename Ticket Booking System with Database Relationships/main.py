from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, get_db
from models import Venue, Event, TicketType, Booking
from schemas import (
    VenueCreate, VenueResponse,
    EventCreate, EventResponse, 
    TicketTypeCreate, TicketTypeResponse,
    BookingCreate, BookingResponse
)