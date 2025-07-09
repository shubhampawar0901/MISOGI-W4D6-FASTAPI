#!/usr/bin/env python3
"""
Task Manager Application Entry Point

This is the main entry point for the Task Manager application.
Similar to having a main server.js file in Node.js projects.

Usage:
    python main.py              # Run development server
    uvicorn app.main:app --reload  # Alternative way to run
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📍 Server will be available at: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🎨 Web Interface: http://{settings.HOST}:{settings.PORT}/ui/tasks")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
