from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """
    Schema for creating a new task - similar to Joi validation in Node.js
    
    In Node.js with Joi, you might write:
    const taskCreateSchema = Joi.object({
        title: Joi.string().min(1).max(200).required(),
        description: Joi.string().max(1000).optional()
    });
    """
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        description="Task title (required, 1-200 characters)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="Task description (optional, max 1000 characters)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Complete FastAPI tutorial",
                "description": "Learn FastAPI by building a task manager application"
            }
        }
    )


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task
    All fields are optional for partial updates
    """
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=200, 
        description="Updated task title"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="Updated task description"
    )
    completed: Optional[bool] = Field(
        None, 
        description="Task completion status"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Complete FastAPI tutorial - Updated",
                "description": "Learn FastAPI by building a comprehensive task manager",
                "completed": True
            }
        }
    )


class TaskResponse(BaseModel):
    """
    Schema for task responses - what the API returns
    This ensures consistent output format
    """
    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Task completion status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Complete FastAPI tutorial",
                "description": "Learn FastAPI by building a task manager application",
                "completed": False,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


class TaskListResponse(BaseModel):
    """Schema for returning multiple tasks"""
    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Complete FastAPI tutorial",
                        "description": "Learn FastAPI by building a task manager",
                        "completed": False,
                        "created_at": "2024-01-15T10:30:00",
                        "updated_at": "2024-01-15T10:30:00"
                    }
                ],
                "total": 1
            }
        }
    )
