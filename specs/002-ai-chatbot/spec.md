# AI Chatbot for Todo App - Phase 3

**Feature:** Natural Language Task Management Chatbot
**Version:** 1.0.0
**Status:** In Progress
**Created:** 2025-12-30
**Updated:** 2025-12-31

## 1. Overview

This document specifies the AI chatbot feature for the Todo App, enabling users to manage tasks through natural language conversations. The chatbot understands natural language commands and performs CRUD operations on tasks via an AI agent powered by OpenAI Agents SDK.

## 2. Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Database Models | ✅ Complete | `backend/models/conversation.py` |
| MCP Server Tools | ✅ Complete | `backend/mcp/server.py` |
| Chat API Endpoint | ✅ Complete | `backend/routes/chat.py` |
| Conversation Endpoints | ✅ Complete | `backend/routes/chat.py:303-353` |
| Frontend ChatPanel | ✅ Complete | `frontend/components/chat/ChatPanel.tsx` |
| API Client | ✅ Complete | `frontend/lib/api.ts:139-148` |
| ChatKit Integration | ⏳ Pending | Not implemented (using custom UI) |
| Conversation List UI | ⏳ Pending | Not implemented |
| End-to-End Testing | ⏳ Pending | Not implemented |

### 2.1 Database Schema

**Conversations Table** (`backend/models/conversation.py:18-30`):
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**Messages Table** (`backend/models/conversation.py:33-45`):
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

### 2.2 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Main chat endpoint with AI agent |
| GET | `/api/{user_id}/conversations` | List user's conversations |
| GET | `/api/{user_id}/conversations/{id}/messages` | Get conversation history |

## 3. User Stories

| ID | Priority | Story | Acceptance Criteria |
|----|----------|-------|---------------------|
| US-01 | P0 | As a user, I can chat with the AI to add tasks using natural language | - User types "Add task: Buy groceries" → task created<br>- User types "Remind me to call mom tomorrow" → task with title "Call mom" created<br>- AI confirms task creation with task details |
| US-02 | P0 | As a user, I can view my tasks through chat | - User types "Show my tasks" → list of tasks displayed<br>- User types "What do I have todo?" → task list shown |
| US-03 | P0 | As a user, I can mark tasks complete through chat | - User types "Mark task [task_id] as done" → task marked complete<br>- User types "I finished the groceries" → finds matching task and marks complete |
| US-04 | P0 | As a user, I can delete tasks through chat | - User types "Delete task [task_id]" → task deleted<br>- User types "Remove the grocery task" → finds and deletes matching task |
| US-05 | P0 | As a user, I can update tasks through chat | - User types "Change task [task_id] to [new_title]" → task updated<br>- User types "Rename 'Buy milk' to 'Buy almond milk'" → task title updated |
| US-06 | P1 | As a user, my conversation history is preserved | - Messages stored in database<br>- History maintained across sessions<br>- User can reference previous context |
| US-07 | P1 | As a user, I get natural language responses | - AI responds conversationally<br>- Confirms actions taken<br>- Asks for clarification when intent is unclear |
| US-08 | P2 | As a user, I can have multi-turn conversations | - AI remembers context within conversation<br>- Can reference "that task" or "the one I added" |
| US-09 | P2 | As a user, I see the chat UI integrated in dashboard | - Chat panel available in dashboard<br>- Messages scrollable<br>- Input field for typing |

## 3. Functional Requirements

### 3.1 Chat Operations

| Req ID | Requirement | Description |
|--------|-------------|-------------|
| FR-01 | Natural Language Understanding | Chatbot interprets natural language commands for task management |
| FR-02 | Task Creation | Parse intent to create tasks with appropriate titles |
| FR-03 | Task Listing | Query and display user's tasks in conversational format |
| FR-04 | Task Completion | Mark tasks as complete via chat commands |
| FR-05 | Task Deletion | Delete tasks via chat commands |
| FR-06 | Task Updates | Update task properties via chat commands |
| FR-07 | Conversation Persistence | Store all messages in database per user |
| FR-08 | Contextual Responses | Provide helpful, conversational responses |

### 3.2 MCP Server Tools

The MCP server exposes the following tools for the AI agent:

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_task` | `title: string`, `user_id: string` | Create a new task for the user |
| `list_tasks` | `user_id: string`, `completed?: boolean` | List user's tasks, optionally filtered |
| `complete_task` | `task_id: string`, `user_id: string` | Mark a task as complete |
| `delete_task` | `task_id: string`, `user_id: string` | Delete a task |
| `update_task` | `task_id: string`, `title?: string`, `completed?: boolean`, `user_id: string` | Update task properties |

### 3.3 API Endpoint

**Endpoint:** `POST /api/{user_id}/chat`

**Request:**
```json
{
  "message": "string",
  "conversation_id?: string"
}
```

**Response:**
```json
{
  "response": "string",
  "conversation_id": "string",
  "actions": [
    {
      "type": "task_created" | "task_completed" | "task_deleted" | "task_updated" | "task_listed",
      "task_id?: string",
      "task_title?: string",
      "tasks?: Task[]"
    }
  ]
}
```

## 4. Data Models

### 4.1 Conversation Model

```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255, default="New Conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4.2 Message Model

```python
class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # "user" | "assistant" | "system"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## 5. Technical Architecture

### 5.1 Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐   │
│  │  ChatPanel.tsx  │  │  useChatStore.ts / useChatHook.ts   │   │
│  └────────┬────────┘  └─────────────────────────────────────┘   │
└───────────┼─────────────────────────────────────────────────────┘
            │ HTTP
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ POST /api/{user_id}/chat                                  │  │
│  │ - Validates JWT token                                     │  │
│  │ - Manages conversation history                            │  │
│  └──────────────────────────┬──────────────────────────────────┘
│                             │
│                             ▼
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ OpenAI Agents SDK + MCP Server                            │  │
│  │ ┌─────────────┐  ┌─────────────────────────────────────┐  │  │
│  │ │ Agent       │  │ MCP Server (Tools)                   │  │  │
│  │ │ - GPT-4o    │  │ - add_task                          │  │  │
│  │ │ - Handoffs  │  │ - list_tasks                        │  │  │
│  │ │ - Context   │  │ - complete_task                     │  │  │
│  │ └─────────────┘  │ - delete_task                       │  │  │
│  │                  │ - update_task                        │  │  │
│  │                  └─────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Database (PostgreSQL)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │  Users   │  │  Tasks   │  │Conversations│ │  Messages   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Technology Stack

| Component | Technology |
|-----------|------------|
| AI Framework | OpenAI Agents SDK |
| LLM Model | GPT-4o |
| MCP Server | Model Context Protocol |
| Frontend | React + ChatKit |
| Backend | FastAPI |
| Database | PostgreSQL (Neon) |

## 6. Non-Functional Requirements

### 6.1 Performance

| Metric | Target |
|--------|--------|
| Chat response time (p95) | < 5 seconds |
| Tool execution time (p95) | < 1 second |
| Concurrent chat sessions | 100+ |

### 6.2 Reliability

| Metric | Target |
|--------|--------|
| Uptime | 99.5% |
| Message delivery rate | 100% |
| Data consistency | Eventual (messages stored async) |

### 6.3 Security

- JWT token required for all chat requests
- User isolation enforced for all tool calls
- Input sanitization for chat messages
- No sensitive data in conversation logs

### 6.4 Constraints

- Stateless chat endpoint (except for history retrieval)
- Conversations stored per user
- Maximum message length: 2000 characters
- Rate limiting: 20 messages/minute/user

## 7. Out of Scope

The following are explicitly NOT in scope for Phase 3:

- Voice input/output
- Image input
- Advanced multi-agent workflows
- Custom agent instructions
- Chat export functionality
- Real-time streaming responses
- Message reactions/attachments
- Group chats or shared conversations

## 8. Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| openai-agents | ^0.0.1 | AI agent framework |
| mcp | ^1.0.0 | Model Context Protocol |
| @openai/chatkit | ^1.0.0 | Frontend chat UI |
| psycopg2-binary | ^2.9.9 | PostgreSQL adapter |

## 9. Open Questions

| ID | Question | Status |
|----|----------|--------|
| OQ-01 | Should conversation history be included in agent context? | Open |
| OQ-02 | Maximum conversation length to include in context? | Open |
| OQ-03 | How to handle ambiguous task matches in natural language? | Open |

## 10. Definition of Done

- [ ] All user stories meet acceptance criteria
- [ ] Unit tests for MCP tools
- [ ] Integration tests for chat endpoint
- [ ] Frontend chat component tested
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Security review passed
- [ ] Deployed to staging
- [ ] User acceptance testing complete
