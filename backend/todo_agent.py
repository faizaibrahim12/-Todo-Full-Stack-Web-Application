"""
OpenAI Agents SDK setup for Todo App.

This module provides the TodoAgent that uses MCP tools for task management.
"""
from typing import Optional, List
import os

try:
    from agents import Agent, function_tool
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    # Create dummy classes if agents is not available
    class Agent:
        def __init__(self, *args, **kwargs):
            raise ImportError("openai-agents package is not installed. Install it with: pip install openai-agents")
    
    def function_tool(func):
        return func

from openai import OpenAI


# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful todo list assistant. You help users manage their tasks through natural conversation.

Your capabilities:
- Add tasks to the user's todo list
- List the user's current tasks
- Mark tasks as complete
- Delete tasks
- Update task titles or completion status

When the user wants to manage tasks:
- Use natural language to understand their intent
- Confirm actions before executing them when uncertain
- Provide clear feedback about what was done
- Be friendly and conversational

Keep responses concise but helpful. If the user asks about something outside task management, politely redirect them."""


# Lazy initialization for OpenAI client
_openai_client: Optional[OpenAI] = None


def get_openai_client() -> Optional[OpenAI]:
    """Get or create OpenAI/Ollama client."""
    global _openai_client
    if _openai_client is None:
        base_url = os.getenv("OLLAMA_BASE_URL")
        api_key = os.getenv("OPENAI_API_KEY", "ollama")

        if base_url:
            # Use Ollama (local/free)
            _openai_client = OpenAI(base_url=base_url, api_key=api_key)
        elif os.getenv("OPENAI_API_KEY"):
            # Use OpenAI (paid)
            _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _openai_client


def get_provider_name() -> str:
    """Return the LLM provider name for display."""
    if os.getenv("OLLAMA_BASE_URL"):
        return "Ollama (Local)"
    elif os.getenv("OPENAI_API_KEY"):
        return "OpenAI"
    return "None"


def is_llm_configured() -> bool:
    """Check if LLM provider is configured."""
    return get_openai_client() is not None


# Import get_session for tool functions
from database import get_session
from models import Task
from uuid import UUID
from sqlmodel import select


@function_tool
def add_task_tool(title: str, user_id: str) -> str:
    """Add a new task to the user's todo list."""
    session = next(get_session())
    try:
        task = Task(title=title, user_id=UUID(user_id), completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)
        return f"Task created successfully: '{task.title}' (ID: {task.id})"
    finally:
        session.close()


@function_tool
def list_tasks_tool(user_id: str, completed: Optional[bool] = None) -> str:
    """List the user's tasks, optionally filtered by completion status."""
    session = next(get_session())
    try:
        statement = select(Task).where(Task.user_id == UUID(user_id))
        if completed is not None:
            statement = statement.where(Task.completed == completed)
        statement = statement.order_by(Task.created_at.desc())

        tasks = session.exec(statement).all()

        if not tasks:
            return "You have no tasks."

        task_list = []
        for t in tasks:
            status = "[x]" if t.completed else "[ ]"
            task_list.append(f"{status} {t.title} (ID: {t.id})")

        return f"You have {len(tasks)} task(s):\n" + "\n".join(task_list)
    finally:
        session.close()


@function_tool
def complete_task_tool(task_id: str, user_id: str) -> str:
    """Mark a task as completed."""
    session = next(get_session())
    try:
        task = session.get(Task, UUID(task_id))
        if not task:
            return f"Task not found: {task_id}"
        if task.user_id != UUID(user_id):
            return "Access denied"

        task.completed = True
        session.commit()
        return f"Task marked as complete: '{task.title}'"
    finally:
        session.close()


@function_tool
def delete_task_tool(task_id: str, user_id: str) -> str:
    """Delete a task from the user's todo list."""
    session = next(get_session())
    try:
        task = session.get(Task, UUID(task_id))
        if not task:
            return f"Task not found: {task_id}"
        if task.user_id != UUID(user_id):
            return "Access denied"

        title = task.title
        session.delete(task)
        session.commit()
        return f"Task deleted: '{title}'"
    finally:
        session.close()


@function_tool
def update_task_tool(
    task_id: str,
    user_id: str,
    title: Optional[str] = None,
    completed: Optional[bool] = None,
) -> str:
    """Update a task's properties."""
    session = next(get_session())
    try:
        task = session.get(Task, UUID(task_id))
        if not task:
            return f"Task not found: {task_id}"
        if task.user_id != UUID(user_id):
            return "Access denied"

        changes = []
        if title is not None:
            task.title = title
            changes.append(f"title to '{title}'")
        if completed is not None:
            task.completed = completed
            status = "complete" if completed else "incomplete"
            changes.append(f"status to {status}")

        session.commit()

        if changes:
            return f"Task updated: changed {', '.join(changes)}"
        return "No changes specified"
    finally:
        session.close()


# All available tools for the agent
TODO_TOOLS = [
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool,
]

# Lazy initialization for agent
_agent: Optional[Agent] = None


def get_agent() -> Optional[Agent]:
    """Get or create the TodoAgent, returns None if OpenAI is not configured."""
    if not AGENTS_AVAILABLE:
        return None
    global _agent
    if _agent is None:
        if get_openai_client():
            _agent = Agent(
                name="Todo Assistant",
                instructions=SYSTEM_PROMPT,
                tools=TODO_TOOLS,
            )
    return _agent


def create_agent(client: Optional[OpenAI] = None) -> Optional[Agent]:
    """Create a new TodoAgent with the provided client or default client."""
    if not AGENTS_AVAILABLE:
        return None
    if client is None:
        client = get_openai_client()

    if client is None:
        return None

    return Agent(
        name="Todo Assistant",
        instructions=SYSTEM_PROMPT,
        tools=TODO_TOOLS,
    )


def reset_agent():
    """Reset the agent (useful for testing)."""
    global _agent
    _agent = None


def reset_client():
    """Reset the OpenAI client (useful for testing)."""
    global _openai_client
    _openai_client = None
    reset_agent()
