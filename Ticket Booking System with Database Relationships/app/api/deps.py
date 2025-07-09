from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator:
    """
    Dependency function that yields database sessions.
    
    This function creates a new SQLAlchemy SessionLocal that will be used
    in a single request, and then close it once the request is finished.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
