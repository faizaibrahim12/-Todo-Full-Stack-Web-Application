"""
MCP Server with task management tools.
"""
from typing import Optional, List
from uuid import UUID
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from database import get_session
from models import Task, Conversation, Message, MessageRole
from schemas import TaskCreate, TaskUpdate


# Create MCP server instance
app = Server(name="todo-chatbot-mcp")


def _verify_user_access(user_id: UUID, task_id: UUID) -> bool:
    """Verify that the task belongs to the user."""
    session = next(get_session())
    try:
        task = session.get(Task, task_id)
        return task is not None and task.user_id == user_id
    finally:
        session.close()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="add_task",
            description="Add a new task to the user's todo list",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (max 500 chars)",
                        "maxLength": 500
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User UUID"
                    }
                },
                "required": ["title", "user_id"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List the user's tasks, optionally filtered by completion status",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User UUID"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Filter by completion status (true=completed, false=pending)"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task UUID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User UUID"
                    }
                },
                "required": ["task_id", "user_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task from the user's todo list",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task UUID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User UUID"
                    }
                },
                "required": ["task_id", "user_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update a task's properties (title or completion status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task UUID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User UUID"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (max 500 chars)",
                        "maxLength": 500
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "New completion status"
                    }
                },
                "required": ["task_id", "user_id"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls from the agent."""
    session = next(get_session())

    try:
        if name == "add_task":
            title = arguments["title"]
            user_id = UUID(arguments["user_id"])

            task_data = TaskCreate(title=title)
            task = Task(**task_data.model_dump(), user_id=user_id)
            session.add(task)
            session.commit()
            session.refresh(task)

            return [TextContent(
                type="text",
                text=f"Task created successfully with ID: {task.id}"
            )]

        elif name == "list_tasks":
            user_id = UUID(arguments["user_id"])
            completed_filter = arguments.get("completed")

            query = session.query(Task).filter(Task.user_id == user_id)
            if completed_filter is not None:
                query = query.filter(Task.completed == completed_filter)

            tasks = query.order_by(Task.created_at.desc()).all()

            if not tasks:
                return [TextContent(type="text", text="No tasks found.")]

            task_list = []
            for t in tasks:
                status = "completed" if t.completed else "pending"
                task_list.append(f"- [{status}] {t.title} (ID: {t.id})")

            result = f"You have {len(tasks)} task(s):\n" + "\n".join(task_list)
            return [TextContent(type="text", text=result)]

        elif name == "complete_task":
            task_id = UUID(arguments["task_id"])
            user_id = UUID(arguments["user_id"])

            task = session.get(Task, task_id)
            if not task:
                return [TextContent(type="text", text=f"Task {task_id} not found.")]
            if task.user_id != user_id:
                return [TextContent(type="text", text="Access denied.")]

            task.completed = True
            session.commit()

            return [TextContent(
                type="text",
                text=f"Task '{task.title}' marked as completed."
            )]

        elif name == "delete_task":
            task_id = UUID(arguments["task_id"])
            user_id = UUID(arguments["user_id"])

            task = session.get(Task, task_id)
            if not task:
                return [TextContent(type="text", text=f"Task {task_id} not found.")]
            if task.user_id != user_id:
                return [TextContent(type="text", text="Access denied.")]

            title = task.title
            session.delete(task)
            session.commit()

            return [TextContent(
                type="text",
                text=f"Task '{title}' has been deleted."
            )]

        elif name == "update_task":
            task_id = UUID(arguments["task_id"])
            user_id = UUID(arguments["user_id"])
            title = arguments.get("title")
            completed = arguments.get("completed")

            task = session.get(Task, task_id)
            if not task:
                return [TextContent(type="text", text=f"Task {task_id} not found.")]
            if task.user_id != user_id:
                return [TextContent(type="text", text="Access denied.")]

            changes = []
            if title is not None:
                task.title = title
                changes.append(f"title to '{title}'")
            if completed is not None:
                task.completed = completed
                status = "completed" if completed else "pending"
                changes.append(f"status to {status}")

            session.commit()

            if changes:
                return [TextContent(
                    type="text",
                    text=f"Task updated: changed {', '.join(changes)}."
                )]
            return [TextContent(type="text", text="No changes specified.")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    finally:
        session.close()


async def run_server():
    """Run the MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_server())
