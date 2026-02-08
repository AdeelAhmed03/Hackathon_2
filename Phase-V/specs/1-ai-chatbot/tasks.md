# Tasks: AI Todo Chatbot (Phase III)

**Input**: Design documents from `/specs/1-ai-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Status**: ✅ ALL PHASES COMPLETE (2026-02-04)

**Tests**: Optional (not explicitly requested in spec)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Tests**: `backend/tests/`, `frontend/tests/`

---

## Phase 1: Setup (Project Initialization) ✅ COMPLETE

**Purpose**: Install dependencies and configure environment

- [x] T001 [P] Add `cohere` to backend/requirements.txt
- [x] T002 [P] Create backend/.env.example with COHERE_API_KEY placeholder
- [x] T003 [P] Create backend/src/tools/__init__.py (empty module init)
- [x] T004 Verify COHERE_API_KEY is set in backend/.env (manual check)

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

### Database Models

- [x] T005 [P] Create Conversation model in backend/src/models/conversation.py
- [x] T006 [P] Create Message model in backend/src/models/message.py
- [x] T007 Update backend/src/models/__init__.py to export Conversation and Message
- [x] T008 Add `conversations` relationship to User model in backend/src/models/user.py
- [x] T009 Verify tables created on backend startup (run backend, check logs)

### Cohere Integration Service

- [x] T010 Create chat_service.py with Cohere client initialization in backend/src/services/chat_service.py
- [x] T011 Implement `format_history_for_cohere()` function in backend/src/services/chat_service.py
- [x] T012 Implement `call_cohere_chat()` function in backend/src/services/chat_service.py
- [x] T013 Define SYSTEM_PROMPT constant in backend/src/services/chat_service.py

### Tool Definitions (Cohere Format)

- [x] T014 Create tool schema for `add_task` in backend/src/tools/definitions.py
- [x] T015 [P] Create tool schema for `list_tasks` in backend/src/tools/definitions.py
- [x] T016 [P] Create tool schema for `complete_task` in backend/src/tools/definitions.py
- [x] T017 [P] Create tool schema for `update_task` in backend/src/tools/definitions.py
- [x] T018 [P] Create tool schema for `delete_task` in backend/src/tools/definitions.py
- [x] T019 Export ALL_TOOLS list in backend/src/tools/definitions.py

### Tool Execution Framework

- [x] T020 Create tool executor dispatcher in backend/src/services/tool_service.py
- [x] T021 Implement runner loop (tool_calls → execute → repeat) in backend/src/services/tool_service.py

### Chat Endpoint (Core)

- [x] T022 Create chat router in backend/src/api/chat.py
- [x] T023 Implement POST /chat endpoint with JWT auth in backend/src/api/chat.py
- [x] T024 Implement get_or_create_conversation() in backend/src/api/chat.py
- [x] T025 Implement message persistence (save user + assistant messages) in backend/src/api/chat.py
- [x] T026 Register chat router in backend/src/api/__init__.py
- [x] T027 Wire up full flow: JWT → history → Cohere → tools → persist → response in backend/src/api/chat.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add Task via Chat (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Users can create tasks by typing natural language commands like "Add task buy groceries"

**Independent Test**: Type "Add a task to call mom tomorrow" and see confirmation with task details

### Implementation for User Story 1

- [x] T028 [US1] Implement add_task tool handler in backend/src/tools/add_task.py
- [x] T029 [US1] Add user_id filtering to add_task (get from context, not AI params) in backend/src/tools/add_task.py
- [x] T030 [US1] Handle optional parameters (priority, due_date, tags, recurrence) in backend/src/tools/add_task.py
- [x] T031 [US1] Return formatted confirmation message from add_task in backend/src/tools/add_task.py
- [x] T032 [US1] Register add_task in tool executor dispatcher in backend/src/services/tool_service.py

**Checkpoint**: User Story 1 complete - users can add tasks via chat

---

## Phase 4: User Story 2 - List and Query Tasks (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Users can view and search their tasks with filters

**Independent Test**: Type "Show my tasks" and see formatted list of tasks

### Implementation for User Story 2

- [x] T033 [US2] Implement list_tasks tool handler in backend/src/tools/list_tasks.py
- [x] T034 [US2] Add user_id filtering (MUST filter by owner_id) in backend/src/tools/list_tasks.py
- [x] T035 [US2] Implement status filter (pending, completed, in_progress) in backend/src/tools/list_tasks.py
- [x] T036 [US2] Implement priority filter (low, medium, high) in backend/src/tools/list_tasks.py
- [x] T037 [US2] Implement tag filter (AND logic for multiple tags) in backend/src/tools/list_tasks.py
- [x] T038 [US2] Implement search_query (search title/description) in backend/src/tools/list_tasks.py
- [x] T039 [US2] Format task list as readable text response in backend/src/tools/list_tasks.py
- [x] T040 [US2] Register list_tasks in tool executor dispatcher in backend/src/services/tool_service.py

**Checkpoint**: User Story 2 complete - users can list and filter tasks via chat

---

## Phase 5: User Story 3 - Complete Task via Chat (Priority: P2) ✅ COMPLETE

**Goal**: Users can mark tasks as complete using natural language

**Independent Test**: Type "Complete the groceries task" and see confirmation

### Implementation for User Story 3

- [x] T041 [US3] Implement complete_task tool handler in backend/src/tools/complete_task.py
- [x] T042 [US3] Add user_id filtering (only complete own tasks) in backend/src/tools/complete_task.py
- [x] T043 [US3] Support task lookup by ID or title in backend/src/tools/complete_task.py
- [x] T044 [US3] Handle recurring task regeneration (create next instance) in backend/src/tools/complete_task.py
- [x] T045 [US3] Return confirmation with task details in backend/src/tools/complete_task.py
- [x] T046 [US3] Handle "task not found" case gracefully in backend/src/tools/complete_task.py
- [x] T047 [US3] Register complete_task in tool executor dispatcher in backend/src/services/tool_service.py

**Checkpoint**: User Story 3 complete - users can complete tasks via chat

---

## Phase 6: User Story 4 - Update Task via Chat (Priority: P2) ✅ COMPLETE

**Goal**: Users can modify task properties via natural language

**Independent Test**: Type "Change priority of groceries task to high" and see confirmation

### Implementation for User Story 4

- [x] T048 [US4] Implement update_task tool handler in backend/src/tools/update_task.py
- [x] T049 [US4] Add user_id filtering (only update own tasks) in backend/src/tools/update_task.py
- [x] T050 [US4] Support task lookup by ID or title in backend/src/tools/update_task.py
- [x] T051 [US4] Handle title update (new_title parameter) in backend/src/tools/update_task.py
- [x] T052 [US4] Handle priority update (new_priority parameter) in backend/src/tools/update_task.py
- [x] T053 [US4] Handle due_date update (new_due_datetime parameter) in backend/src/tools/update_task.py
- [x] T054 [US4] Handle tag updates (add_tags, remove_tags parameters) in backend/src/tools/update_task.py
- [x] T055 [US4] Return confirmation with updated fields in backend/src/tools/update_task.py
- [x] T056 [US4] Register update_task in tool executor dispatcher in backend/src/services/tool_service.py

**Checkpoint**: User Story 4 complete - users can update tasks via chat

---

## Phase 7: User Story 5 - Delete Task via Chat (Priority: P3) ✅ COMPLETE

**Goal**: Users can delete tasks with confirmation step

**Independent Test**: Type "Delete the old meeting task" and see confirmation request

### Implementation for User Story 5

- [x] T057 [US5] Implement delete_task tool handler in backend/src/tools/delete_task.py
- [x] T058 [US5] Add user_id filtering (only delete own tasks) in backend/src/tools/delete_task.py
- [x] T059 [US5] Support task lookup by ID or title in backend/src/tools/delete_task.py
- [x] T060 [US5] Implement confirmation flow (confirmed=false → ask, confirmed=true → delete) in backend/src/tools/delete_task.py
- [x] T061 [US5] Return "Are you sure?" message when not confirmed in backend/src/tools/delete_task.py
- [x] T062 [US5] Return deletion confirmation when confirmed in backend/src/tools/delete_task.py
- [x] T063 [US5] Register delete_task in tool executor dispatcher in backend/src/services/tool_service.py

**Checkpoint**: User Story 5 complete - users can delete tasks via chat with confirmation

---

## Phase 8: User Story 6 - Conversation Context (Priority: P3) ✅ COMPLETE

**Goal**: Chatbot understands references like "it", "the first one" based on conversation history

**Independent Test**: List tasks, then type "complete the first one" and correct task is completed

### Implementation for User Story 6

- [x] T064 [US6] Ensure full conversation history is loaded before Cohere call in backend/src/api/chat.py
- [x] T065 [US6] Implement history truncation for long conversations (keep last 20 messages) in backend/src/services/chat_service.py
- [x] T066 [US6] Add context hints to SYSTEM_PROMPT about handling references in backend/src/services/chat_service.py

**Checkpoint**: User Story 6 complete - chatbot understands conversation context

---

## Phase 9: Frontend Chat UI ✅ COMPLETE

**Purpose**: Add chat interface to Next.js frontend

### Types and Hooks

- [x] T067 [P] Create chat types (ChatMessage, ChatResponse, etc.) in frontend/src/types/chat.ts
- [x] T068 Create useChat hook with sendMessage function in frontend/src/hooks/useChat.ts
- [x] T069 Add loading state management to useChat in frontend/src/hooks/useChat.ts
- [x] T070 Add error handling to useChat in frontend/src/hooks/useChat.ts

### Components

- [x] T071 [P] Create ChatMessage component (user/assistant bubbles) in frontend/src/components/chat/ChatMessage.tsx
- [x] T072 [P] Create MessageInput component (text input + send button) in frontend/src/components/chat/MessageInput.tsx
- [x] T073 Create MessageList component (scrollable message list) in frontend/src/components/chat/MessageList.tsx
- [x] T074 Create ChatContainer component (main wrapper) in frontend/src/components/chat/ChatContainer.tsx

### Page

- [x] T075 Create chat page at /chat route in frontend/src/app/chat/page.tsx
- [x] T076 Add authentication guard to chat page in frontend/src/app/chat/page.tsx
- [x] T077 Wire up ChatContainer to useChat hook in frontend/src/app/chat/page.tsx

### Navigation

- [x] T078 Add "Chat" link to navigation menu in frontend/src/components/common/Navbar.tsx

**Checkpoint**: Frontend complete - users can access chat UI

---

## Phase 10: Polish & Error Handling ✅ COMPLETE

**Purpose**: Improvements that affect multiple user stories

- [x] T079 [P] Add loading spinner while waiting for Cohere response in frontend/src/components/chat/ChatContainer.tsx
- [x] T080 [P] Add error message display for API failures in frontend/src/components/chat/ChatContainer.tsx
- [x] T081 Implement Cohere API error handling (503 → friendly message) in backend/src/services/chat_service.py
- [x] T082 Implement rate limiting hint in error response in backend/src/api/chat.py
- [x] T083 Add empty message validation (400 if empty) in backend/src/api/chat.py
- [x] T084 [P] Update quickstart.md with final setup instructions in specs/1-ai-chatbot/quickstart.md
- [x] T085 E2E testing completed: Backend verified, Cohere working, tools functional (see TEST_REPORT.md)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
┌───────────────────────────────────────────┐
│  User Stories can proceed in parallel:    │
│                                           │
│  Phase 3 (US1: Add)    ← MVP              │
│  Phase 4 (US2: List)   ← MVP              │
│  Phase 5 (US3: Complete)                  │
│  Phase 6 (US4: Update)                    │
│  Phase 7 (US5: Delete)                    │
│  Phase 8 (US6: Context)                   │
└───────────────────────────────────────────┘
    ↓
Phase 9 (Frontend) ← Can start after Phase 2, parallel with backend tools
    ↓
Phase 10 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Add) | Phase 2 | T027 |
| US2 (List) | Phase 2 | T027 |
| US3 (Complete) | Phase 2 | T027 |
| US4 (Update) | Phase 2 | T027 |
| US5 (Delete) | Phase 2 | T027 |
| US6 (Context) | Phase 2 | T027 |
| Frontend | Phase 2 | T027 |

### Parallel Opportunities

**Within Phase 2**:
- T005, T006 (models) can run in parallel
- T014-T018 (tool schemas) can run in parallel

**Across User Stories**:
- All US1-US6 tool implementations can run in parallel after Phase 2
- Frontend (Phase 9) can run in parallel with backend tools (Phase 3-8)

**Within Frontend**:
- T067, T071, T072 can run in parallel (no dependencies)

---

## MVP Scope (Recommended)

**Minimum Viable Product = Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) + Phase 9**

This delivers:
- ✅ Add tasks via chat
- ✅ List/search tasks via chat
- ✅ Working frontend UI
- ✅ Full conversation persistence

**MVP Task Count**: ~45 tasks (T001-T027 + T028-T040 + T067-T078)

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1 | T001-T004 | Setup (4 tasks) |
| Phase 2 | T005-T027 | Foundational (23 tasks) |
| Phase 3 | T028-T032 | US1: Add Task (5 tasks) |
| Phase 4 | T033-T040 | US2: List Tasks (8 tasks) |
| Phase 5 | T041-T047 | US3: Complete Task (7 tasks) |
| Phase 6 | T048-T056 | US4: Update Task (9 tasks) |
| Phase 7 | T057-T063 | US5: Delete Task (7 tasks) |
| Phase 8 | T064-T066 | US6: Context (3 tasks) |
| Phase 9 | T067-T078 | Frontend (12 tasks) |
| Phase 10 | T079-T085 | Polish (7 tasks) |
| **Total** | **85 tasks** | |

---

## Execution Commands

### Run Single Task

```bash
# Example: Execute T005
claude "Execute task T005: Create Conversation model in backend/src/models/conversation.py"
```

### Run Phase

```bash
# Example: Execute all Phase 2 tasks
claude "Execute all Phase 2 Foundational tasks from specs/1-ai-chatbot/tasks.md"
```

### Run User Story

```bash
# Example: Execute US1 (Add Task)
claude "Execute all US1 tasks (T028-T032) from specs/1-ai-chatbot/tasks.md"
```
