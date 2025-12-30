# Tasks: AI Chatbot for Todo App

**Feature**: Phase 3 - AI Chatbot with Natural Language Task Management
**Input**: Design documents from `/specs/002-ai-chatbot/`
**Prerequisites**: spec.md, plan.md, conversation.py models

**Organization**: Tasks organized by: Database → Backend → Frontend → Integration
**Status**: Core infrastructure complete, remaining: testing & polish

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US01-US09)
- Exact file paths included in all descriptions

---

## Phase 3.1: Database & Models (COMPLETE)

**Purpose**: Conversation and Message models for chat history persistence
**Complexity**: Low | **Estimated Tasks**: 4

- [x] D001 Create `backend/models/conversation.py` with Conversation SQLModel (id, user_id FK, title, created_at, updated_at)
- [x] D002 Create `backend/models/conversation.py` with Message SQLModel (id, conversation_id FK, role, content, created_at)
- [x] D003 Create `backend/models/conversation.py` with MessageRole enum (user, assistant, system)
- [x] D004 Export Conversation, Message, MessageRole from `backend/models/__init__.py`

**Checkpoint**: Database models ready for chat persistence

---

## Phase 3.2: MCP Server Tools (COMPLETE)

**Purpose**: Model Context Protocol server exposing task management tools to AI agent
**Complexity**: Medium | **Estimated Tasks**: 6

- [x] M001 Create `backend/mcp/__init__.py` with MCP server exports
- [x] M002 Implement `add_task` MCP tool (title, user_id) in `backend/mcp/server.py`
- [x] M003 Implement `list_tasks` MCP tool (user_id, completed optional) in `backend/mcp/server.py`
- [x] M004 Implement `complete_task` MCP tool (task_id, user_id) in `backend/mcp/server.py`
- [x] M005 Implement `delete_task` MCP tool (task_id, user_id) in `backend/mcp/server.py`
- [x] M006 Implement `update_task` MCP tool (task_id, user_id, title?, completed?) in `backend/mcp/server.py`

**Checkpoint**: MCP server tools ready for agent integration

---

## Phase 3.3: Backend Chat Routes (COMPLETE)

**Purpose**: REST API endpoints for chat operations with OpenAI Agents SDK integration
**Complexity**: High | **Estimated Tasks**: 10

### Chat Schemas

- [x] C001 Create `backend/schemas/chat.py` with ChatRequest (message, conversation_id optional)
- [x] C002 Create `backend/schemas/chat.py` with ChatResponse (response, conversation_id, actions)
- [x] C003 Create `backend/schemas/chat.py` with ChatAction type for task operations
- [x] C004 Create `backend/schemas/chat.py` with ConversationResponse and MessageResponse
- [x] C005 Export all chat schemas from `backend/schemas/__init__.py`

### Chat Endpoint

- [x] C006 Create `backend/routes/chat.py` with OpenAI client initialization (lazy loading)
- [x] C007 Implement system prompt for todo assistant agent in `backend/routes/chat.py`
- [x] C008 Implement agent tools using `@function_tool` decorator (add_task_tool, list_tasks_tool, etc.)
- [x] C009 Implement `POST /api/{user_id}/chat` endpoint with JWT validation, conversation management, agent execution
- [x] C010 Implement `GET /api/{user_id}/conversations` endpoint for listing user's conversations
- [x] C011 Implement `GET /api/{user_id}/conversations/{conversation_id}/messages` endpoint
- [x] C012 Export chat_router from `backend/routes/__init__.py` and include in `main.py`

**Checkpoint**: Backend chat API ready for frontend integration

---

## Phase 3.4: Frontend Chat UI (COMPLETE)

**Purpose**: React components for chat interaction with AI assistant
**Complexity**: Medium | **Estimated Tasks**: 6

- [x] F001 Add chat types to `frontend/lib/types.ts` (ChatMessage, ChatAction, ChatResponse, ChatRequest, Conversation, ConversationList)
- [x] F002 Add `chat()` method to `frontend/lib/api.ts` APIClient with automatic JWT injection
- [x] F003 Add `getConversations()` method to `frontend/lib/api.ts`
- [x] F004 Create `frontend/components/chat/ChatPanel.tsx` with message display, input, loading states
- [x] F005 Integrate ChatPanel in `frontend/app/dashboard/page.tsx` with toggle visibility
- [x] F006 Fix TypeScript import issues (ChatPanel default export, toggleTaskComplete return type)

**Checkpoint**: Frontend chat UI integrated with dashboard

---

## Phase 3.5: Testing & Validation (PENDING)

**Purpose**: Verify end-to-end chat functionality works correctly
**Complexity**: Medium | **Estimated Tasks**: 8

### Backend Tests

- [ ] T001 Write unit tests for MCP tools in `backend/tests/test_mcp_tools.py`
  - Test add_task creates task for user
  - Test list_tasks returns user tasks only
  - Test complete_task marks task complete
  - Test delete_task removes task
  - Test update_task modifies task

- [ ] T002 Write integration tests for chat endpoints in `backend/tests/test_chat.py`
  - Test chat with new conversation
  - Test chat continuation with conversation_id
  - Test unauthorized access returns 401
  - Test conversation isolation between users

- [ ] T003 Write tests for conversation history in `backend/tests/test_history.py`
  - Test message persistence
  - Test history retrieval
  - Test conversation ordering by updated_at

### Frontend Tests

- [ ] T004 Test ChatPanel component renders correctly
- [ ] T005 Test send message flow and response display
- [ ] T006 Test error handling and display

### Validation

- [ ] T007 Test natural language commands:
  - "Add task: Buy groceries" creates task
  - "Show my tasks" lists tasks
  - "Mark task [id] as complete" marks complete
  - "Delete task [id]" removes task
  - "Update task [id] to [new title]" updates title

- [ ] T008 Verify OpenAI API integration works with valid API key

**Checkpoint**: All tests pass, chat functionality verified

---

## Phase 3.6: Polish & Documentation (PENDING)

**Purpose**: Final polish, error handling, and documentation
**Complexity**: Low | **Estimated Tasks**: 5

- [ ] P001 Add rate limiting to chat endpoint (20 msgs/min/user) in `backend/routes/chat.py`
- [ ] P002 Add structured logging for agent operations
- [ ] P003 Add error handling for OpenAI API failures with graceful degradation
- [ ] P004 Update `specs/002-ai-chatbot/spec.md` with implementation status table
- [ ] P005 Create `specs/002-ai-chatbot/quickstart.md` with setup instructions for AI features

**Checkpoint**: Feature complete and documented

---

## Summary

| Phase | Status | Tasks |
|-------|--------|-------|
| 3.1 Database & Models | ✅ Complete | 4 |
| 3.2 MCP Server Tools | ✅ Complete | 6 |
| 3.3 Backend Chat Routes | ✅ Complete | 12 |
| 3.4 Frontend Chat UI | ✅ Complete | 6 |
| 3.5 Testing & Validation | ⏳ Pending | 8 |
| 3.6 Polish & Documentation | ⏳ Pending | 5 |
| **Total** | **50%** | **41** |

---

## Dependencies

- OpenAI API key required in `backend/.env` as `OPENAI_API_KEY`
- Neon PostgreSQL connection (already configured in Phase 2)
- JWT authentication (already implemented in Phase 2)

## Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## Environment Variables Required

```bash
# backend/.env
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
OPENAI_API_KEY=sk-...  # Required for AI features
```
