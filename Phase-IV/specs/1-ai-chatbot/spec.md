# Feature Specification: AI Todo Chatbot (Phase III)

**Feature Branch**: `1-ai-chatbot`
**Created**: 2026-02-04
**Status**: Draft
**Constitution Reference**: `.specify/memory/constitution.md` v3.0.0

## Overview

Allow authenticated users to manage all their tasks using natural language conversation via a chat interface integrated into the existing Todo web application. The chatbot understands intent, executes task operations, and responds conversationally.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                             │
│  ┌─────────────────┐    ┌──────────────────────────────────────────────┐   │
│  │  Task List UI   │    │           Chat UI (ChatKit)                  │   │
│  │  (existing)     │    │  ┌─────────────────────────────────────────┐ │   │
│  └─────────────────┘    │  │ User: "Add a task to buy groceries"     │ │   │
│                         │  │ Bot:  "Done! Created task 'Buy          │ │   │
│                         │  │        groceries' with medium priority" │ │   │
│                         │  └─────────────────────────────────────────┘ │   │
│                         └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ POST /api/chat
                                        │ Authorization: Bearer <JWT>
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (SAME FastAPI App)                          │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        Chat Endpoint Handler                           │ │
│  │  1. Verify JWT → extract user_id                                       │ │
│  │  2. Load conversation history from DB                                  │ │
│  │  3. Call Cohere chat API with tools + history                          │ │
│  │  4. If tool_calls: execute tools with user_id → loop back to step 3    │ │
│  │  5. Persist messages to DB                                             │ │
│  │  6. Return assistant response                                          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│              ┌───────────────┼───────────────┐                              │
│              ▼               ▼               ▼                              │
│  ┌──────────────────┐ ┌─────────────┐ ┌──────────────┐                      │
│  │   Cohere API     │ │  MCP Tools  │ │   Database   │                      │
│  │   (chat +        │ │  add_task   │ │  (Neon PG)   │                      │
│  │    tool_use)     │ │  list_tasks │ │              │                      │
│  │                  │ │  complete   │ │  Tasks       │                      │
│  │  COHERE_API_KEY  │ │  delete     │ │  Users       │                      │
│  │                  │ │  update     │ │  Tags        │                      │
│  └──────────────────┘ └─────────────┘ │  Conversation│                      │
│                              │        │  Message     │                      │
│                              │        └──────────────┘                      │
│                              │               ▲                              │
│                              └───────────────┘                              │
│                           All queries filtered by user_id                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## User Scenarios & Testing

### User Story 1 - Add Task via Chat (Priority: P1)

An authenticated user opens the chat interface and types a natural language request to create a new task. The chatbot understands the intent, creates the task with extracted details, and confirms the creation.

**Why this priority**: Core value proposition - users can quickly add tasks without navigating forms.

**Independent Test**: User types "Add a task to call mom tomorrow" and sees confirmation with task details.

**Acceptance Scenarios**:

1. **Given** user is authenticated and on chat page, **When** user types "Add task buy groceries", **Then** system creates task with title "buy groceries", medium priority, and confirms creation
2. **Given** user is authenticated, **When** user types "Create a high priority task to finish report by Friday", **Then** system creates task with title "finish report", high priority, due date Friday, and confirms
3. **Given** user is authenticated, **When** user types "I need to remember to call the dentist", **Then** system interprets intent and creates task "call the dentist"
4. **Given** user is authenticated, **When** user types "Add daily recurring task: take vitamins", **Then** system creates recurring task with daily recurrence rule

---

### User Story 2 - List and Query Tasks (Priority: P1)

An authenticated user asks the chatbot to show their tasks, optionally filtered by status, priority, tags, or search terms. The chatbot retrieves and displays tasks in a readable format.

**Why this priority**: Essential for task management - users need to see their tasks.

**Independent Test**: User types "Show my tasks" and sees a formatted list of their tasks.

**Acceptance Scenarios**:

1. **Given** user has 5 tasks, **When** user types "Show my tasks", **Then** chatbot lists all 5 tasks with titles, priorities, and due dates
2. **Given** user has tasks with different priorities, **When** user types "Show high priority tasks", **Then** only high priority tasks are shown
3. **Given** user has completed and pending tasks, **When** user types "What tasks are pending?", **Then** only pending tasks are shown
4. **Given** user has tasks with tags, **When** user types "Show tasks tagged with work", **Then** only tasks with "work" tag are shown
5. **Given** user has many tasks, **When** user types "Find tasks about groceries", **Then** tasks matching "groceries" in title/description are shown

---

### User Story 3 - Complete Task via Chat (Priority: P2)

An authenticated user tells the chatbot to mark a task as complete. The chatbot identifies the task and marks it complete, handling recurring tasks appropriately.

**Why this priority**: Completing tasks is core functionality but requires list/add to be useful first.

**Independent Test**: User types "Complete the groceries task" and sees confirmation.

**Acceptance Scenarios**:

1. **Given** user has task "Buy groceries", **When** user types "Complete buy groceries task", **Then** task is marked complete and confirmed
2. **Given** user has task with ID 5, **When** user types "Mark task 5 as done", **Then** task 5 is completed
3. **Given** user has recurring daily task, **When** user types "Complete my vitamins task", **Then** task is completed AND new instance created for next day
4. **Given** user asks to complete non-existent task, **When** user types "Complete meeting task", **Then** chatbot responds task not found

---

### User Story 4 - Update Task via Chat (Priority: P2)

An authenticated user asks the chatbot to modify an existing task's properties (title, description, priority, due date, tags).

**Why this priority**: Important for task management but add/list/complete are more fundamental.

**Independent Test**: User types "Change priority of groceries task to high" and sees confirmation.

**Acceptance Scenarios**:

1. **Given** user has task "Buy groceries" with medium priority, **When** user types "Make groceries task high priority", **Then** task priority is updated and confirmed
2. **Given** user has task, **When** user types "Rename task 3 to 'Buy vegetables'", **Then** task title is updated
3. **Given** user has task, **When** user types "Set due date for report task to next Monday", **Then** due date is updated
4. **Given** user has task, **When** user types "Add work tag to the meeting task", **Then** tag is added to task

---

### User Story 5 - Delete Task via Chat (Priority: P3)

An authenticated user asks the chatbot to delete a task. The chatbot confirms before deletion for safety.

**Why this priority**: Destructive action - less frequently needed than other operations.

**Independent Test**: User types "Delete the old meeting task" and sees confirmation.

**Acceptance Scenarios**:

1. **Given** user has task "Old meeting", **When** user types "Delete old meeting task", **Then** chatbot asks for confirmation
2. **Given** user confirms deletion, **When** user types "Yes, delete it", **Then** task is deleted and confirmed
3. **Given** user declines deletion, **When** user types "No, keep it", **Then** task is not deleted

---

### User Story 6 - Conversation Context (Priority: P3)

The chatbot maintains conversation context across multiple messages, understanding references like "it", "that task", "the first one".

**Why this priority**: Enhances UX but core functionality works without it.

**Independent Test**: User lists tasks, then types "complete the first one" and correct task is completed.

**Acceptance Scenarios**:

1. **Given** user just listed 3 tasks, **When** user types "complete the first one", **Then** first listed task is completed
2. **Given** user just created a task, **When** user types "make it high priority", **Then** just-created task is updated
3. **Given** user mentions "groceries task" earlier, **When** user types "delete it", **Then** groceries task is referenced

---

### Edge Cases

- What happens when user sends empty message? → Chatbot prompts for input
- What happens when Cohere API is unavailable? → Graceful error message to user
- What happens when user references ambiguous task? → Chatbot asks for clarification
- What happens when tool execution fails? → Chatbot reports error conversationally
- What happens when user tries to access another user's task? → Tool returns "not found" (never reveals existence)
- What happens when conversation history is very long? → Truncate older messages, keep recent context
- What happens when user sends message without authentication? → 401 Unauthorized response

---

## Requirements

### Functional Requirements

**Chat Endpoint**
- **FR-001**: System MUST expose POST /api/chat endpoint protected by JWT authentication
- **FR-002**: System MUST extract user_id from JWT token (not from request body)
- **FR-003**: System MUST load conversation history from database before calling AI
- **FR-004**: System MUST persist all messages (user, assistant, tool calls, tool results) to database
- **FR-005**: System MUST return assistant response in JSON format with message content

**AI Integration (Cohere)**
- **FR-006**: System MUST use Cohere API exclusively via `cohere` Python SDK
- **FR-007**: System MUST NOT use OpenAI API or `openai` package
- **FR-008**: System MUST configure Cohere client with COHERE_API_KEY environment variable
- **FR-009**: System MUST implement tool calling via Cohere's chat API with tools parameter
- **FR-010**: System MUST loop until AI returns response without tool calls (runner pattern)
- **FR-011**: System MUST support multi-tool calls in single turn when Cohere returns multiple

**MCP Tools**
- **FR-012**: System MUST implement `add_task` tool - creates task for authenticated user
- **FR-013**: System MUST implement `list_tasks` tool - lists tasks with optional filters
- **FR-014**: System MUST implement `complete_task` tool - marks task complete, handles recurring
- **FR-015**: System MUST implement `delete_task` tool - deletes task after confirmation
- **FR-016**: System MUST implement `update_task` tool - updates task properties
- **FR-017**: Every tool MUST receive user_id from authenticated context (NOT from AI parameters)
- **FR-018**: Every tool MUST filter database queries by user_id

**Frontend Chat UI**
- **FR-019**: Frontend MUST display chat interface accessible to authenticated users
- **FR-020**: Frontend MUST send messages to /api/chat with JWT in Authorization header
- **FR-021**: Frontend MUST display conversation history loaded from backend
- **FR-022**: Frontend MUST show loading state while waiting for response
- **FR-023**: Frontend MUST handle and display error messages gracefully

**Data Persistence**
- **FR-024**: System MUST store conversations in Conversation table (id, user_id, title, timestamps)
- **FR-025**: System MUST store messages in Message table (id, conversation_id, role, content, tool_calls, timestamp)
- **FR-026**: System MUST scope all conversation/message queries by user_id

### Key Entities

**Conversation**
- Represents a chat session between user and AI
- Attributes: id, user_id (foreign key to User), title (optional), created_at, updated_at
- Relationship: belongs to User, has many Messages

**Message**
- Represents a single message in a conversation
- Attributes: id, conversation_id (foreign key), role (user/assistant/tool), content (text), tool_calls (JSON, nullable), tool_results (JSON, nullable), created_at
- Relationship: belongs to Conversation

---

## Tool Definitions

### add_task

**Description**: Create a new task for the user

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Task title |
| description | string | No | Task description |
| priority | string | No | Priority: low, medium (default), high |
| due_datetime | string | No | Due date in ISO format |
| recurrence_rule | string | No | Recurrence: daily, weekly, monthly, yearly |
| tag_names | array | No | List of tag names to attach |

**Returns**: Created task details or error message

---

### list_tasks

**Description**: List user's tasks with optional filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status: pending, in_progress, completed |
| priority | string | No | Filter by priority: low, medium, high |
| tag_names | array | No | Filter by tag names (AND logic) |
| search_query | string | No | Search in title/description |
| limit | integer | No | Max results (default: 20) |

**Returns**: List of tasks with id, title, priority, status, due_date, tags

---

### complete_task

**Description**: Mark a task as completed

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | integer | No | Task ID to complete |
| task_title | string | No | Task title to match (if ID unknown) |

**Returns**: Completion confirmation, new recurring instance if applicable

---

### delete_task

**Description**: Delete a task

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | integer | No | Task ID to delete |
| task_title | string | No | Task title to match |
| confirmed | boolean | No | Whether deletion is confirmed |

**Returns**: Deletion confirmation or request for confirmation

---

### update_task

**Description**: Update task properties

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | integer | No | Task ID to update |
| task_title | string | No | Task title to match |
| new_title | string | No | New title |
| new_description | string | No | New description |
| new_priority | string | No | New priority |
| new_due_datetime | string | No | New due date |
| new_recurrence_rule | string | No | New recurrence |
| add_tags | array | No | Tags to add |
| remove_tags | array | No | Tags to remove |

**Returns**: Updated task details

---

## Natural Language Examples

| User Input | Expected Tool Call | Expected Response |
|------------|-------------------|-------------------|
| "Add task buy milk" | add_task(title="buy milk") | "Created task 'buy milk' with medium priority" |
| "Create high priority task finish report by Friday" | add_task(title="finish report", priority="high", due_datetime="2026-02-07") | "Created high priority task 'finish report' due Friday" |
| "Show my tasks" | list_tasks() | "You have 5 tasks: 1. Buy milk (medium)..." |
| "What's pending?" | list_tasks(status="pending") | "You have 3 pending tasks..." |
| "Find tasks about groceries" | list_tasks(search_query="groceries") | "Found 2 tasks matching 'groceries'..." |
| "Complete the milk task" | complete_task(task_title="milk") | "Marked 'buy milk' as complete!" |
| "Mark task 5 done" | complete_task(task_id=5) | "Task #5 completed!" |
| "Change groceries to high priority" | update_task(task_title="groceries", new_priority="high") | "Updated 'buy groceries' to high priority" |
| "Delete the old meeting task" | delete_task(task_title="old meeting") | "Delete 'old meeting'? Reply 'yes' to confirm" |

---

## Cohere Integration Approach

### Chat Call Structure

```
cohere.chat(
    model="command-r-plus",
    preamble="<system prompt with personality and rules>",
    chat_history=[<previous messages from DB>],
    message="<current user message>",
    tools=[<tool definitions>],
    tool_results=[<results from previous tool calls if any>]
)
```

### Tool Definition Format (Cohere)

```json
{
    "name": "add_task",
    "description": "Create a new task for the user",
    "parameter_definitions": {
        "title": {
            "description": "Task title",
            "type": "str",
            "required": true
        },
        "priority": {
            "description": "Priority level: low, medium, high",
            "type": "str",
            "required": false
        }
    }
}
```

### Runner Loop Pattern

```
1. Receive user message
2. Load chat_history from DB
3. Call cohere.chat() with tools
4. While response has tool_calls:
   a. Execute each tool with user_id from JWT
   b. Collect tool_results
   c. Call cohere.chat() again with tool_results
5. Persist all messages to DB
6. Return final assistant response
```

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create a task via chat in under 5 seconds end-to-end
- **SC-002**: Chatbot correctly interprets user intent 90%+ of the time for standard commands
- **SC-003**: Users can complete full task management flow (add, list, complete) via chat only
- **SC-004**: Chat response time is under 3 seconds for non-tool-call responses
- **SC-005**: Chat response time is under 8 seconds for tool-call responses (includes DB + AI)
- **SC-006**: Zero cross-user data leakage - users can only access their own tasks
- **SC-007**: Chat history persists across browser sessions for the same user
- **SC-008**: System handles 100 concurrent chat sessions without degradation

---

## Security Notes

### Authentication & Authorization

1. **JWT Verification**: Every /api/chat request MUST include valid JWT in Authorization header
2. **User ID Extraction**: user_id MUST be extracted from verified JWT, never from request body or AI parameters
3. **Tool Execution**: Every tool receives user_id from authenticated context, not from AI

### Data Isolation

1. **Query Filtering**: ALL database queries in tools MUST include `WHERE owner_id = :user_id`
2. **Not Found vs Forbidden**: If task exists but belongs to another user, return "not found" (never reveal existence)
3. **Conversation Scoping**: Users can only access their own conversations and messages

### Input Validation

1. **Sanitization**: Tool parameters from AI MUST be validated before database queries
2. **SQL Injection Prevention**: Use parameterized queries via SQLModel (built-in)
3. **Content Length**: Limit message length to prevent abuse (max 2000 characters)

### API Security

1. **Rate Limiting**: Implement rate limiting on /api/chat (suggestion: 30 requests/minute per user)
2. **Error Messages**: Never expose internal errors or stack traces to users
3. **Logging**: Log all tool executions with user_id for audit trail

---

## Assumptions

1. Cohere's command-r-plus model supports tool calling with the defined format
2. Existing Task, User, Tag models remain unchanged
3. Frontend will use a chat UI library (ChatKit or equivalent) - specific library TBD
4. Conversation history is loaded in full for context (may need truncation strategy for very long conversations)
5. Better Auth JWT structure includes user ID in "sub" claim (confirmed from existing auth middleware)
6. Tags referenced in chat will be created if they don't exist (consistent with existing behavior)

---

## Out of Scope

- Voice input/output
- Real-time collaborative editing of tasks
- Push notifications for task reminders
- Offline chat functionality
- File attachments in chat
- Multi-language support (English only for Phase III)
- Analytics dashboard for chat usage
