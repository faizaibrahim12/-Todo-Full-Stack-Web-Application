"""
Task-related request and response schemas.
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=500)


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: UUID
    title: str
    completed: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for listing tasks."""

    tasks: List[TaskResponse]
    count: int
