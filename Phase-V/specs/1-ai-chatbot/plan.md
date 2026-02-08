# Implementation Plan: AI Todo Chatbot (Phase III)

**Branch**: `1-ai-chatbot` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-ai-chatbot/spec.md`
**Constitution**: `.specify/memory/constitution.md` v3.0.0

## Summary

Integrate a natural-language AI chatbot into the existing FastAPI backend that allows authenticated users to manage their tasks (add, list, complete, update, delete) via conversational commands. The chatbot uses Cohere's chat API with tool calling support, persists conversation history to the database, and enforces user_id isolation on all operations.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Cohere Python SDK (`cohere`), Next.js 16+
**Storage**: Neon Serverless PostgreSQL (existing) + new Conversation/Message tables
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web application (monorepo: frontend + backend)
**Performance Goals**: <3s response for non-tool calls, <8s for tool calls (per spec SC-004, SC-005)
**Constraints**: Stateless server architecture, user_id isolation on all queries
**Scale/Scope**: 100 concurrent chat sessions (per spec SC-008)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Spec created via /sp.specify |
| II. Clean Code and Type Safety | ✅ PASS | Python type hints + TypeScript required |
| III. Multi-User Security and Isolation | ✅ PASS | user_id filtering on all tools (FR-017, FR-018) |
| IV. Authentication and Authorization | ✅ PASS | JWT verification on /api/chat (FR-001) |
| V. Persistent Storage with SQLModel | ✅ PASS | Conversation + Message tables (FR-024, FR-025) |
| VI. RESTful API Design | ✅ PASS | POST /api/chat follows REST conventions |
| VII. Monorepo Structure | ✅ PASS | Adding to existing /backend and /frontend |
| VIII. Frontend Technology Standards | ✅ PASS | Next.js + TypeScript + Tailwind |
| IX. Backend Technology Standards | ✅ PASS | FastAPI + SQLModel + **Cohere SDK** |
| X. Development Workflow | ✅ PASS | Following spec → plan → tasks flow |
| XI. AI Chatbot Integration | ✅ PASS | Cohere-only, same FastAPI app |
| XII. Conversation Persistence | ✅ PASS | DB-only state, no in-memory caching |
| XIII. MCP Tools Architecture | ✅ PASS | 5 tools defined with user_id enforcement |
| XIV. Environment Variables | ✅ PASS | COHERE_API_KEY required |

**Gate Status**: ✅ ALL GATES PASS

## Project Structure

### Documentation (this feature)

```text
specs/1-ai-chatbot/
├── spec.md              # Feature specification (created)
├── plan.md              # This file
├── research.md          # Phase 0 output - Cohere API research
├── data-model.md        # Phase 1 output - DB schema
├── quickstart.md        # Phase 1 output - Setup guide
├── contracts/           # Phase 1 output - API contracts
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
├── checklists/
│   └── requirements.md  # Validation checklist (created)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Existing
│   │   ├── user.py          # Existing
│   │   ├── tag.py           # Existing
│   │   ├── conversation.py  # NEW: Conversation model
│   │   └── message.py       # NEW: Message model
│   ├── services/
│   │   ├── task_service.py       # Existing
│   │   ├── task_query_service.py # Existing
│   │   ├── chat_service.py       # NEW: Cohere integration
│   │   └── tool_service.py       # NEW: MCP tool implementations
│   ├── api/
│   │   ├── tasks.py         # Existing
│   │   ├── tags.py          # Existing
│   │   ├── auth.py          # Existing
│   │   └── chat.py          # NEW: Chat endpoint
│   ├── tools/               # NEW: Tool definitions
│   │   ├── __init__.py
│   │   ├── definitions.py   # Cohere tool schemas
│   │   ├── add_task.py
│   │   ├── list_tasks.py
│   │   ├── complete_task.py
│   │   ├── update_task.py
│   │   └── delete_task.py
│   └── middleware/
│       └── auth.py          # Existing
└── tests/
    ├── unit/
    │   └── test_tools.py    # NEW
    ├── integration/
    │   └── test_chat.py     # NEW
    └── contract/
        └── test_chat_api.py # NEW

frontend/
├── src/
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx     # NEW: Chat page
│   ├── components/
│   │   └── chat/            # NEW: Chat UI components
│   │       ├── ChatContainer.tsx
│   │       ├── MessageList.tsx
│   │       ├── MessageInput.tsx
│   │       └── ChatMessage.tsx
│   ├── hooks/
│   │   └── useChat.ts       # NEW: Chat API hook
│   └── types/
│       └── chat.ts          # NEW: Chat types
└── tests/
    └── components/
        └── chat.test.tsx    # NEW
```

**Structure Decision**: Web application structure with additions to existing `/backend` and `/frontend` directories. No new top-level directories created.

---

## Phase 0: Research

### Research Topics

1. **Cohere Chat API with Tool Calling**
   - How to define tools in Cohere format
   - How to handle tool_calls in response
   - How to submit tool_results
   - Multi-turn conversation handling

2. **Cohere SDK for Python**
   - Installation and configuration
   - Client initialization with API key
   - Error handling patterns

3. **Chat History Format**
   - Cohere's chat_history parameter structure
   - Role types supported
   - Token limit considerations

### Research Findings → See [research.md](./research.md)

---

## Phase 1: Design

### 1.1 Database Extensions

**New Models** → See [data-model.md](./data-model.md)

- `Conversation`: id, user_id, title, created_at, updated_at
- `Message`: id, conversation_id, role, content, tool_calls, tool_results, created_at

### 1.2 Cohere Integration

**Environment Variable**:
```
COHERE_API_KEY=<your-cohere-api-key>
```

**Client Initialization**:
```python
import cohere
client = cohere.Client(os.getenv("COHERE_API_KEY"))
```

**Chat Call Structure**:
```python
response = client.chat(
    model="command-r-plus",
    preamble=SYSTEM_PROMPT,
    chat_history=formatted_history,
    message=user_message,
    tools=TOOL_DEFINITIONS
)
```

### 1.3 MCP Tools (Cohere Format)

**Tool Definition Structure**:
```python
{
    "name": "add_task",
    "description": "Create a new task for the user",
    "parameter_definitions": {
        "title": {
            "description": "Task title",
            "type": "str",
            "required": True
        },
        "priority": {
            "description": "Priority: low, medium, high",
            "type": "str",
            "required": False
        }
    }
}
```

**Tools to Implement**:
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `add_task` | Create task | title, description, priority, due_datetime, recurrence_rule, tag_names |
| `list_tasks` | List/filter tasks | status, priority, tag_names, search_query, limit |
| `complete_task` | Mark complete | task_id OR task_title |
| `update_task` | Update properties | task_id/title, new_* fields |
| `delete_task` | Delete task | task_id/title, confirmed |

### 1.4 Chat Endpoint Flow

```
POST /api/chat
├── 1. Verify JWT → extract user_id
├── 2. Get/create conversation for user
├── 3. Load message history from DB
├── 4. Format history for Cohere
├── 5. Call cohere.chat() with tools
├── 6. LOOP while response.tool_calls:
│   ├── a. Execute each tool with user_id
│   ├── b. Save tool call + result to DB
│   └── c. Call cohere.chat() with tool_results
├── 7. Save final assistant message to DB
└── 8. Return response to frontend
```

### 1.5 Frontend Chat UI

**Components**:
- `ChatContainer`: Main wrapper, manages state
- `MessageList`: Scrollable message display
- `ChatMessage`: Single message bubble (user/assistant)
- `MessageInput`: Text input with send button

**API Integration**:
```typescript
const sendMessage = async (content: string) => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: content,
      conversation_id: conversationId
    })
  });
  return response.json();
};
```

---

## Implementation Order (Recommended)

**Priority**: DB → Tools → Endpoint → Cohere Loop → Frontend

### Step 1: Database Extensions (Foundation)
1. Create `Conversation` model
2. Create `Message` model
3. Run migration / create_tables()
4. Test: verify tables exist

### Step 2: Tool Implementations (Core Logic)
1. Create tool definitions (Cohere format)
2. Implement `add_task_tool()` - reuse existing task_service
3. Implement `list_tasks_tool()` - reuse task_query_service
4. Implement `complete_task_tool()` - handle recurring
5. Implement `update_task_tool()`
6. Implement `delete_task_tool()` - confirmation logic
7. Test: unit tests for each tool with mock user_id

### Step 3: Cohere Integration Service
1. Add `cohere` to requirements.txt
2. Create `chat_service.py` with client initialization
3. Implement `format_history_for_cohere()`
4. Implement `call_cohere_chat()`
5. Test: mock Cohere responses

### Step 4: Tool Calling Loop
1. Implement tool executor dispatcher
2. Implement runner loop (call → execute → repeat)
3. Handle multi-tool calls in single turn
4. Test: integration test with mocked Cohere

### Step 5: Chat Endpoint
1. Create `/api/chat` route in `chat.py`
2. Wire up JWT auth (reuse `get_current_user`)
3. Implement conversation get/create
4. Implement message persistence
5. Wire up Cohere service + tool loop
6. Test: contract test against spec

### Step 6: Frontend Chat UI
1. Create chat types (`chat.ts`)
2. Create `useChat` hook
3. Create `ChatMessage` component
4. Create `MessageInput` component
5. Create `MessageList` component
6. Create `ChatContainer` component
7. Create `/chat` page
8. Test: component tests + manual testing

### Step 7: Polish & Error Handling
1. Add loading states
2. Add error handling (Cohere unavailable, tool failures)
3. Add rate limiting (optional)
4. End-to-end testing

---

## Testing Focus Areas

### Backend Tests

| Area | Test Type | Focus |
|------|-----------|-------|
| Tool implementations | Unit | user_id filtering, correct DB operations |
| Cohere integration | Unit | Response parsing, tool_calls handling |
| Chat endpoint | Integration | Auth, persistence, full flow |
| API contract | Contract | Request/response schema validation |

### Cohere Mocking Strategy

```python
# Mock Cohere response with tool call
mock_response = Mock()
mock_response.text = None
mock_response.tool_calls = [
    Mock(name="add_task", parameters={"title": "Test task"})
]

# Mock final response (no tool calls)
mock_final = Mock()
mock_final.text = "Created task 'Test task'!"
mock_final.tool_calls = None
```

### Error Cases to Test

1. Invalid JWT → 401
2. Empty message → 400
3. Cohere API timeout → 503 with friendly message
4. Tool execution failure → conversational error
5. Non-existent task reference → "not found" (no cross-user leak)
6. Rate limit exceeded → 429

### Token Limit Handling

- Truncate conversation history if >4000 tokens (configurable)
- Keep most recent N messages
- Always include system prompt

---

## Environment Variables Summary

| Variable | Required | Description |
|----------|----------|-------------|
| `COHERE_API_KEY` | ✅ Yes | Cohere API key for chat |
| `DATABASE_URL` | ✅ Yes | Neon PostgreSQL (existing) |
| `BETTER_AUTH_SECRET` | ✅ Yes | JWT verification (existing) |
| `FRONTEND_URL` | ✅ Yes | CORS origin (existing) |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Cohere API changes | Pin SDK version, monitor changelog |
| Token limits | Implement history truncation |
| Slow responses | Add timeout, show loading states |
| Tool failures | Graceful error messages, logging |
| Cross-user access | Every tool filters by user_id from JWT |

---

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Approach | Rationale |
|--------|----------|-----------|
| Tool definitions | Centralized in `/tools/definitions.py` | Single source of truth for Cohere schemas |
| History format | Helper function | Cohere's format differs from DB storage |
| Runner loop | While loop with max iterations | Prevent infinite loops on malformed responses |

---

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement in order: DB → Tools → Endpoint → Frontend
3. Test each component before moving to next
