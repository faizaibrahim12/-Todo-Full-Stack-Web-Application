# AI Chatbot Architecture Plan

**Feature:** AI Chatbot for Todo App
**Version:** 1.0.0
**Created:** 2025-12-30

## 1. Scope and Dependencies

### 1.1 In Scope
- OpenAI Agents SDK integration with MCP server
- MCP tools for task CRUD operations (add_task, list_tasks, complete_task, delete_task, update_task)
- Stateless `/api/{user_id}/chat` endpoint
- Conversation and Message database models
- Frontend ChatKit integration
- Conversation history persistence

### 1.2 Out of Scope
- Real-time streaming responses
- Voice/video interactions
- Advanced multi-agent orchestration
- Custom agent instructions per user
- Chat export functionality
- Message attachments/reactions

### 1.3 External Dependencies
| Dependency | Owner | Purpose |
|------------|-------|---------|
| OpenAI API | OpenAI | LLM inference |
| Neon DB | Self-hosted | PostgreSQL database |
| Better Auth | Internal | JWT authentication |

## 2. Key Decisions and Rationale

### 2.1 AI Framework Selection

**Decision:** Use OpenAI Agents SDK with MCP Server

**Options Considered:**
1. **OpenAI Agents SDK + MCP** - Native integration, structured outputs, tool calling
2. **LangChain Agents** - Flexible but more complex, larger dependency footprint
3. **Custom LLM wrapper** - Maximum control, high development effort

**Trade-offs:**
- OpenAI Agents SDK provides best native integration with GPT-4o
- MCP standardizes tool definitions across agents
- Less flexible than LangChain but higher developer velocity

**Rationale:** Given the constrained scope (5 tools only), OpenAI Agents SDK provides the right balance of capability and simplicity. MCP ensures interoperability if we need to add more tools later.

### 2.2 MCP Server Architecture

**Decision:** Implement MCP server as Python module loaded by FastAPI

**Options Considered:**
1. **Standalone MCP server process** - Separate process, more isolation
2. **MCP module in FastAPI** - Shared process, simpler deployment
3. **External MCP service** - Microservice, maximum scalability

**Trade-offs:**
- Standalone provides process isolation but adds deployment complexity
- Shared process is simplest but means MCP crashes take down API
- External service adds latency and operational overhead

**Rationale:** For a single-user todo app, process isolation is not required. A shared MCP module minimizes infrastructure complexity while maintaining separation of concerns.

### 2.3 Conversation Storage Strategy

**Decision:** Store conversations in PostgreSQL with User FK

**Options Considered:**
1. **PostgreSQL with User FK** - Relational integrity, query flexibility
2. **Vector DB for embeddings** - Semantic search capability
3. **In-memory cache only** - Fast but volatile

**Trade-offs:**
- PostgreSQL provides ACID guarantees and simple queries
- Vector DB enables semantic search but adds complexity
- In-memory is fast but loses history on restart

**Rationale:** Current requirements only need sequential message retrieval, not semantic search. PostgreSQL is already available and provides the needed functionality without additional infrastructure.

### 2.4 Context Window Management

**Decision:** Store full history, send last 20 messages to agent

**Options Considered:**
1. **Full history** - Maximum context, but may hit token limits
2. **Fixed window** - Consistent token usage, loses older context
3. **Semantic summarization** - Adaptive but complex

**Trade-offs:**
- Full history is simple but expensive for long conversations
- Fixed window is predictable but may lose important context
- Summarization is optimal but requires additional LLM calls

**Rationale:** Todo app conversations are typically short. 20 messages provides ample context while staying well within GPT-4o's 128k token window.

### 2.5 Frontend Chat UI

**Decision:** Use OpenAI ChatKit for React

**Options Considered:**
1. **OpenAI ChatKit** - Native to OpenAI ecosystem, easy integration
2. **Custom React components** - Full control, higher effort
3. **Third-party chat library** - Generic, may not fit design system

**Trade-offs:**
- ChatKit provides polished UI out-of-the-box
- Custom components allow exact design matching
- Generic libraries require customization anyway

**Rationale:** ChatKit is designed specifically for this use case and provides a consistent experience with OpenAI's agent outputs.

## 3. Interfaces and API Contracts

### 3.1 Chat Endpoint

**Endpoint:** `POST /api/{user_id}/chat`

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```typescript
interface ChatRequest {
  message: string;           // User's message (1-2000 chars)
  conversation_id?: string;  // Optional: continue existing conversation
}
```

**Response:**
```typescript
interface ChatResponse {
  response: string;              // AI's response
  conversation_id: string;       // Conversation identifier
  actions: ChatAction[];         // Actions taken by the agent
}

interface ChatAction {
  type: 'task_created' | 'task_completed' | 'task_deleted' | 'task_updated' | 'task_listed';
  task_id?: string;
  task_title?: string;
  tasks?: Task[];
  message?: string;
}
```

**Error Responses:**

| Status | Error Code | Description |
|--------|------------|-------------|
| 400 | INVALID_MESSAGE | Message too short/long |
| 401 | UNAUTHORIZED | Missing or invalid JWT |
| 403 | FORBIDDEN | User cannot access this resource |
| 404 | CONVERSATION_NOT_FOUND | Invalid conversation_id |
| 429 | RATE_LIMITED | Too many requests |
| 500 | AGENT_ERROR | Agent processing failed |

### 3.2 MCP Tools Interface

**add_task**
```typescript
{
  name: "add_task",
  description: "Add a new task to the user's todo list",
  parameters: {
    type: "object",
    properties: {
      title: { type: "string", description: "Task title (max 500 chars)" },
      user_id: { type: "string", description: "User UUID" }
    },
    required: ["title", "user_id"]
  }
}
```

**list_tasks**
```typescript
{
  name: "list_tasks",
  description: "List the user's tasks, optionally filtered by completion status",
  parameters: {
    type: "object",
    properties: {
      user_id: { type: "string", description: "User UUID" },
      completed: { type: "boolean", description: "Filter by completion status" }
    },
    required: ["user_id"]
  }
}
```

**complete_task**
```typescript
{
  name: "complete_task",
  description: "Mark a task as completed",
  parameters: {
    type: "object",
    properties: {
      task_id: { type: "string", description: "Task UUID" },
      user_id: { type: "string", description: "User UUID" }
    },
    required: ["task_id", "user_id"]
  }
}
```

**delete_task**
```typescript
{
  name: "delete_task",
  description: "Delete a task from the user's todo list",
  parameters: {
    type: "object",
    properties: {
      task_id: { type: "string", description: "Task UUID" },
      user_id: { type: "string", description: "User UUID" }
    },
    required: ["task_id", "user_id"]
  }
}
```

**update_task**
```typescript
{
  name: "update_task",
  description: "Update a task's properties",
  parameters: {
    type: "object",
    properties: {
      task_id: { type: "string", description: "Task UUID" },
      user_id: { type: "string", description: "User UUID" },
      title: { type: "string", description: "New task title" },
      completed: { type: "boolean", description: "New completion status" }
    },
    required: ["task_id", "user_id"]
  }
}
```

## 4. Non-Functional Requirements

### 4.1 Performance Budgets
| Operation | Target (p95) | Target (p99) |
|-----------|--------------|--------------|
| Chat endpoint response | < 5s | < 10s |
| Tool execution | < 500ms | < 1s |
| Database queries | < 100ms | < 200ms |

### 4.2 Reliability Targets
| Metric | Target |
|--------|--------|
| Uptime | 99.5% |
| Success rate | 99% of requests succeed |
| Data loss | 0% (all messages persisted) |

### 4.3 Security Requirements
- All endpoints require valid JWT token
- User ID in path must match JWT subject
- All tool calls validate user ownership
- Message content sanitized for XSS
- Rate limiting: 20 msgs/min/user

### 4.4 Cost Budget
| Resource | Estimated Usage | Cost/Month |
|----------|-----------------|------------|
| OpenAI GPT-4o | ~1000 req/day | ~$50 |
| Neon DB | Standard tier | ~$25 |
| Compute | Minimal | ~$5 |

## 5. Data Management

### 5.1 Source of Truth
- PostgreSQL database is the authoritative source for all data
- Conversations and messages are appended-only

### 5.2 Schema Evolution
- New fields added as nullable in Message table
- Migrations performed via Alembic or SQLModel auto-migration

### 5.3 Data Retention
- Messages: Retained indefinitely
- Conversations: Soft delete via `is_active` flag (future)

### 5.4 Migration Strategy
```python
# New tables added
class Conversation(SQLModel, table=True):
    # ... fields from spec

class Message(SQLModel, table=True):
    # ... fields from spec
```

## 6. Operational Readiness

### 6.1 Observability

**Metrics to emit:**
- `chat.request.count` - Total chat requests
- `chat.request.latency` - Request latency in ms
- `chat.tool.execution.count` - Tool invocations by type
- `chat.error.count` - Errors by type
- `chat.token.usage` - Tokens consumed per request

**Logs:**
- Request/response summary at INFO level
- Tool execution details at DEBUG level
- Errors at ERROR level with full context

### 6.2 Alerting

| Alert | Threshold | On-Call |
|-------|-----------|---------|
| High error rate | > 5% errors for 5min | Backend |
| High latency | p95 > 10s for 5min | Backend |
| API down | 95% requests failing | Infrastructure |

### 6.3 Runbooks

**Chat API Not Responding:**
1. Check FastAPI service health
2. Check OpenAI API status
3. Review logs for errors
4. Restart service if needed

**Agent Producing Errors:**
1. Check OpenAI API key validity
2. Review recent error logs
3. Verify MCP tool signatures
4. Test tools individually

### 6.4 Deployment Strategy
- Blue-green deployment via Docker
- Health checks on `/health` endpoint
- Zero-downtime rolling updates
- Rollback to previous image on failed health check

## 7. Risk Analysis

### 7.1 Top Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| OpenAI API latency/instability | High | Medium | Add timeout, cache common responses, alert on high latency |
| Prompt injection attacks | High | Low | Input sanitization, system prompt hardening |
| Token usage runaway | Medium | Low | Rate limiting, max context window enforcement |
| Data model breaking changes | Medium | Low | Version API responses, backward compatibility |
| MCP tool schema mismatch | Medium | Low | Integration tests for all tools |

### 7.2 Blast Radius
- Agent errors affect single user only
- OpenAI outage affects all chat functionality
- Database failure affects all persistent data

### 7.3 Kill Switches
- Feature flag: `ENABLE_CHATBOT`
- Rate limiter by user_id
- Circuit breaker for OpenAI API calls

## 8. Implementation Plan

### Phase 3.1: Database & Models
- [ ] Create Conversation and Message models
- [ ] Add migration script
- [ ] Create schemas for API serialization
- [ ] Write unit tests for models

### Phase 3.2: MCP Server
- [ ] Create MCP tool implementations
- [ ] Build MCP server module
- [ ] Write integration tests for tools
- [ ] Document tool interfaces

### Phase 3.3: Chat Endpoint
- [ ] Create `/api/{user_id}/chat` endpoint
- [ ] Implement conversation history management
- [ ] Integrate with OpenAI Agents SDK
- [ ] Write integration tests

### Phase 3.4: Frontend
- [ ] Install OpenAI ChatKit
- [ ] Create ChatPanel component
- [ ] Integrate with existing dashboard
- [ ] Add error handling and loading states
- [ ] Write component tests

### Phase 3.5: Testing & Polish
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Security review
- [ ] Documentation

## 9. Architectural Decisions to Document (ADRs)

Potential ADR topics:
- ADR-001: OpenAI Agents SDK + MCP for AI interactions
- ADR-002: PostgreSQL for conversation storage
- ADR-003: Stateless chat endpoint design
- ADR-004: Context window management strategy

## 10. References

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io)
- [OpenAI ChatKit](https://github.com/openai/chatkit)
- Phase 2 Architecture: `specs/001-frontend-todo/plan.md`
