from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Task:
    """
    Task data model - similar to TypeScript interface
    
    In Node.js, you might define this as:
    interface Task {
        id: number;
        title: string;
        description?: string;
        completed: boolean;
        created_at: Date;
        updated_at: Date;
    }
    """
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Set timestamps if not provided (like default values in database)"""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def mark_completed(self):
        """Mark task as completed and update timestamp"""
        self.completed = True
        self.updated_at = datetime.now(timezone.utc)

    def mark_incomplete(self):
        """Mark task as incomplete and update timestamp"""
        self.completed = False
        self.updated_at = datetime.now(timezone.utc)

    def update_content(self, title: str = None, description: str = None):
        """Update task content and timestamp"""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
