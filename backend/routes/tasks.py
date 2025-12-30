"""
Task CRUD routes with user_id filtering for multi-user isolation.
"""
from fastapi import APIRouter, Depends, Path
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from middleware.auth import get_current_user, verify_user_access
from utils.exceptions import NotFoundError
from database import get_session

router = APIRouter(prefix="/api/users/{user_id}/tasks", tags=["Tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: UUID = Path(...),
    current_user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    List all tasks for the authenticated user.

    - Verifies JWT token
    - Ensures user can only access their own tasks
    - Returns tasks sorted by creation date (newest first)
    """
    # Verify user access
    verify_user_access(user_id, current_user_id)

    # Query tasks for this user
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()

    return TaskListResponse(
        tasks=[TaskResponse.from_orm(task) for task in tasks], count=len(tasks)
    )


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    user_id: UUID = Path(...),
    current_user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new task for the authenticated user.

    - Verifies JWT token
    - Validates title (1-500 characters)
    - Creates task with default completed=False
    """
    # Verify user access
    verify_user_access(user_id, current_user_id)

    # Create new task
    new_task = Task(title=task_data.title, user_id=user_id, completed=False)

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return TaskResponse.from_orm(new_task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID = Path(...),
    current_user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Update a task (title and/or completed status).

    - Verifies JWT token
    - Ensures user owns the task
    - Updates only provided fields
    - Updates updated_at timestamp
    """
    # Verify user access
    verify_user_access(user_id, current_user_id)

    # Find task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise NotFoundError("Task not found")

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.completed is not None:
        task.completed = task_data.completed

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.from_orm(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    user_id: UUID = Path(...),
    current_user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a task.

    - Verifies JWT token
    - Ensures user owns the task
    - Permanently removes task from database
    """
    # Verify user access
    verify_user_access(user_id, current_user_id)

    # Find task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise NotFoundError("Task not found")

    session.delete(task)
    session.commit()

    return None  # 204 No Content
