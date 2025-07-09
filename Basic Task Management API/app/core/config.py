import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    Similar to config management in Node.js with dotenv

    In Node.js, you might use:
    const config = {
        debug: process.env.DEBUG === 'true',
        port: parseInt(process.env.PORT) || 8000,
        projectName: process.env.PROJECT_NAME || 'Task Manager'
    };
    """

    # Application settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    PROJECT_NAME: str = "Task Manager API"
    PROJECT_DESCRIPTION: str = "A simple task management system with FastAPI"
    VERSION: str = "1.0.0"

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# Create global settings instance
settings = Settings()
