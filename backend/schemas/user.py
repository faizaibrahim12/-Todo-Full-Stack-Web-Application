"""
User-related request and response schemas.
"""
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str  # Plain text, will be hashed


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (no password)."""

    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication response with JWT token."""

    user: UserResponse
    token: str
