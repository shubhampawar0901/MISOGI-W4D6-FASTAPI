import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./ticket_booking.db"
    DATABASE_ECHO: bool = False
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Ticket Booking System"
    PROJECT_DESCRIPTION: str = "A comprehensive ticket booking system with database relationships"
    VERSION: str = "1.0.0"
    
    # Application settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()