"""
Chat API routes with OpenAI Agents SDK integration.
Supports both OpenAI API and local Ollama server.
"""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select
from uuid import UUID
from typing import List, Optional
import os

from database import get_session
from models import Conversation, Message
from schemas import ChatRequest, ChatResponse, ChatAction
from middleware.auth import get_current_user, verify_user_access
from utils.exceptions import NotFoundError

# Import TodoAgent from todo_agent.py
from todo_agent import (
    get_agent,
    get_openai_client,
    get_provider_name,
    is_llm_configured,
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool,
)

router = APIRouter(prefix="/api", tags=["Chat"])


def _get_or_create_conversation(session: Session, user_id: UUID, conversation_id: Optional[UUID] = None) -> Conversation:
    """Get existing conversation or create new one."""
    if conversation_id:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()
        if not conversation:
            raise NotFoundError("Conversation not found")
        return conversation

    # Create new conversation
    conversation = Conversation(user_id=user_id, title="New Conversation")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def _get_conversation_history(session: Session, conversation_id: UUID, limit: int = 20) -> List[dict]:
    """Get conversation history as message dicts."""
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).limit(limit)

    messages = session.exec(statement).all()
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


def _save_message(session: Session, conversation_id: UUID, role: str, content: str) -> Message:
    """Save a message to the conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@router.get("/health/llm")
async def llm_health():
    """Check if LLM provider is configured and reachable."""
    client = get_openai_client()
    if client is None:
        return {
            "status": "not_configured",
            "message": "No LLM provider configured",
            "options": [
                "Set OPENAI_API_KEY for OpenAI (paid)",
                "Set OLLAMA_BASE_URL for local Ollama (free)"
            ]
        }

    provider = get_provider_name()
    return {
        "status": "configured",
        "provider": provider,
        "model": os.getenv("LLM_MODEL", "gpt-4o for OpenAI, llama3.2 for Ollama")
    }


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: UUID = Path(...),
    current_user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Handle chat messages from users with AI-powered task management.

    - Validates JWT token
    - Gets or creates conversation
    - Processes message through OpenAI Agent
    - Stores conversation history
    - Returns agent response with actions taken
    """
    # Verify user access
    verify_user_access(user_id, current_user_id)

    # Check if LLM provider is configured
    agent = get_agent()
    if agent is None:
        provider_info = ""
        if os.getenv("OLLAMA_BASE_URL"):
            provider_info = "Ollama configured but not reachable. Start Ollama and try again."
        else:
            provider_info = "Set OPENAI_API_KEY (OpenAI) or OLLAMA_BASE_URL (local) in .env"

        raise HTTPException(
            status_code=503,
            detail=f"AI chat not configured. {provider_info}"
        )

    # Get or create conversation
    conversation = _get_or_create_conversation(session, user_id, request.conversation_id)

    # Save user message
    _save_message(session, conversation.id, "user", request.message)

    # Get conversation history
    history = _get_conversation_history(session, conversation.id)

    # Run the agent with the user's message
    try:
        result = agent.run(request.message, context={"user_id": str(user_id)})
        agent_response = result.output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Save assistant message
    _save_message(session, conversation.id, "assistant", agent_response)

    # Update conversation timestamp
    conversation.updated_at = __import__("datetime").datetime.utcnow()
    session.commit()

    # Parse actions from response (simplified - in production, use structured output)
    actions = _parse_actions_from_response(agent_response)

    return ChatResponse(
        response=agent_response,
        conversation_id=conversation.id,
        actions=actions
    )


def _parse_actions_from_response(response: str) -> List[ChatAction]:
    """Parse actions from agent response."""
    # This is a simplified implementation
    # In production, use structured outputs from the agent
    actions = []

    response_lower = response.lower()

    if "created" in response_lower and "task" in response_lower:
        actions.append(ChatAction(type="task_listed"))

    if "completed" in response_lower or "done" in response_lower:
        actions.append(ChatAction(type="task_completed"))

    if "deleted" in response_lower or "removed" in response_lower:
        actions.append(ChatAction(type="task_deleted"))

    if "updated" in response_lower or "changed" in response_lower:
        actions.append(ChatAction(type="task_updated"))

    return actions


@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: UUID = Path(...),
    current_user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all conversations for a user."""
    verify_user_access(user_id, current_user_id)

    statement = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc())

    conversations = session.exec(statement).all()

    return {
        "conversations": [
            {
                "id": str(c.id),
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            }
            for c in conversations
        ]
    }


@router.get("/{user_id}/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    user_id: UUID = Path(...),
    conversation_id: UUID = Path(...),
    current_user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get messages for a specific conversation."""
    verify_user_access(user_id, current_user_id)

    # Verify conversation belongs to user
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    conversation = session.exec(statement).first()
    if not conversation:
        raise NotFoundError("Conversation not found")

    # Get messages
    messages = _get_conversation_history(session, conversation_id, limit=100)

    return {"messages": messages}
