"""
Pydantic schemas for chat API.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    conversation_id: Optional[UUID] = Field(None, description="Continue existing conversation")


class ChatAction(BaseModel):
    """Action performed by the agent."""
    type: Literal["task_created", "task_completed", "task_deleted", "task_updated", "task_listed"]
    task_id: Optional[UUID] = None
    task_title: Optional[str] = None
    tasks: Optional[List[dict]] = None
    message: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    response: str = Field(..., description="AI's response")
    conversation_id: UUID = Field(..., description="Conversation identifier")
    actions: List[ChatAction] = Field(default_factory=list, description="Actions taken by agent")


class ConversationResponse(BaseModel):
    """Conversation metadata response."""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """Message response."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime


class ConversationListResponse(BaseModel):
    """List of conversations response."""
    conversations: List[ConversationResponse]
