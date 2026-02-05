<!-- SYNC IMPACT REPORT:
Version change: 2.0.0 → 3.0.0
Modified principles:
- IX. Backend Technology Standards → expanded to include Cohere integration
- X. Development Workflow → enhanced with agent-driven development workflow (spec → clarify → plan → tasks → agent implementation prompts)
Added sections:
- Single Source of Truth declaration (header)
- XI. AI Chatbot Integration (Cohere-Powered)
- XII. Conversation Persistence and State Management
- XIII. MCP Tools Architecture
- XIV. Environment Variables and Secrets (Phase III additions)
- "Differences from Phase II" section with detailed migration guidance:
  - AI Provider Change (OpenAI → Cohere)
  - Agent Pattern Reuse explanation
  - Integration into Existing Backend rationale
  - MCP Tools Architecture with Cohere execution flow
- Phase I vs Phase II vs Phase III comparison table
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated (no changes needed - generic enough)
- .specify/templates/spec-template.md ✅ updated (no changes needed - generic enough)
- .specify/templates/tasks-template.md ✅ updated (no changes needed - generic enough)
- CLAUDE.md ⚠ pending (user to update for Phase III context)
- backend/CLAUDE.md ⚠ pending (user to update for Cohere integration)
- README.md ⚠ pending (user to update)
Follow-up TODOs: None
-->

# Todo Application Constitution (Phase III)

> **⚠️ SINGLE SOURCE OF TRUTH**: This constitution is the authoritative document for ALL Phase III architectural decisions, technology choices, and implementation constraints. When in doubt, defer to this document. Any conflicting guidance in other files MUST be reconciled with this constitution.

## Project Identity

**Project Name**: hackathon-todo
**Architecture**: Full-Stack Web Application with AI Chatbot (Monorepo)
**Phase**: III - AI-Powered Conversational Todo Management

## Core Principles

### I. Spec-Driven Development
All development MUST follow the Spec-Kit Plus methodology. No manual coding outside of Claude Code agent. Every feature begins with a specification document in `/specs/`. The spec-driven workflow enforces: feature specification → clarification → implementation plan → task breakdown → implementation → validation. This ensures architectural consistency and traceable requirements.

### II. Clean Code and Type Safety
All code MUST follow language-specific style guidelines with mandatory type hints. TypeScript on frontend, Python with type hints on backend. Code MUST be modular, well-documented, and maintainable. Every function MUST have clear purpose, defined inputs/outputs, and be easily testable. No any types or untyped code.

### III. Multi-User Security and Isolation
Every user MUST see and modify only their own tasks. User data isolation is NON-NEGOTIABLE and MUST be enforced at the database query level. All operations MUST be filtered by authenticated user ID. There are no exceptions to user data isolation - any implementation that allows cross-user access is a critical security defect. This applies to BOTH REST API endpoints AND chatbot tool calls.

### IV. Authentication and Authorization
JWT-based authentication bridges Next.js (Better Auth) and FastAPI backend. The BETTER_AUTH_SECRET environment variable MUST be shared between frontend and backend for JWT verification. All API endpoints (including chat endpoint) MUST verify JWT tokens and reject requests without valid authentication. Better Auth handles frontend session management; backend verifies tokens on every request.

### V. Persistent Storage with SQLModel
All task data MUST be stored in Neon Serverless PostgreSQL using SQLModel. No in-memory storage in production. Database models MUST define proper relationships between users and tasks. Migrations MUST be versioned and applied automatically on startup. Foreign key constraints enforce referential integrity. Phase III adds Conversation and Message tables for chat history persistence.

### VI. RESTful API Design
All backend endpoints MUST follow RESTful conventions. Proper HTTP methods (GET, POST, PUT, DELETE), status codes, and error responses. API contracts MUST be documented and validated. Request/response validation using Pydantic models. Consistent error handling across all endpoints. The chat endpoint follows POST semantics for message submission.

### VII. Monorepo Structure and Code Organization
The project MUST maintain a clear monorepo structure:
- `/frontend` - Next.js application with ChatKit UI
- `/backend` - FastAPI application (includes chat endpoint + Cohere integration)
- `/specs` - Feature specifications and design documents
- `/shared` - Shared types and utilities (if needed)
Separate CLAUDE.md files at root, `/frontend`, and `/backend` for domain-specific guidance.

### VIII. Frontend Technology Standards
Frontend MUST use:
- Next.js 16+ with App Router
- TypeScript throughout
- Tailwind CSS for styling
- Better Auth for authentication
- OpenAI ChatKit (or equivalent) for chat UI component
- React Server Components where appropriate
Client-side MUST handle auth state and provide smooth user experience for both task management and conversational interfaces.

### IX. Backend Technology Standards
Backend MUST use:
- FastAPI with SQLModel
- Python with full type coverage (3.13+)
- Neon Serverless PostgreSQL
- JWT verification middleware
- Proper CORS configuration for frontend communication
- Environment-based configuration for all secrets
- **Cohere Python SDK** for AI capabilities (NOT OpenAI)
- Tool calling via Cohere's chat API with tool_use support

### X. Development Workflow
- Follow spec-driven development: **spec → clarify → plan → tasks → agent implementation prompts**
- No manual coding outside of Claude Code agent prompts
- All code MUST pass type checking (mypy/TypeScript compiler) and linting
- Pull requests require code review and passing tests
- Contract tests for API endpoints (backend testing frontend contracts)
- Integration tests for user journeys (including chatbot flows)
- Docker Compose for local development environment

### XI. AI Chatbot Integration (Cohere-Powered)
The AI chatbot MUST be integrated into the SAME existing FastAPI backend. No separate microservice or new repository.

**Non-Negotiable AI Provider Rules:**
- MUST use Cohere API exclusively (via `cohere` Python SDK)
- MUST NOT use OpenAI API keys or OpenAI models anywhere in the project
- MUST NOT install or import the `openai` Python package
- MUST use `cohere.Client()` with `COHERE_API_KEY` environment variable
- MUST implement agent-like behavior using Cohere's tool calling + multi-turn chat capabilities

**Rationale for Cohere:**
- Native tool calling support in chat API
- Cost-effective for conversational AI
- Excellent multi-turn conversation handling
- No dependency on OpenAI ecosystem

### XII. Conversation Persistence and State Management
The chatbot architecture MUST be fully stateless on the server side.

**State Management Rules:**
- Conversation state lives ONLY in the database (Conversation + Message tables)
- Each chat request MUST load conversation history from database
- Each response MUST persist the new messages to database
- No in-memory conversation caching between requests
- Conversation MUST be scoped to authenticated user (user_id foreign key)

**Database Schema Additions:**
- `Conversation` table: id, user_id, created_at, updated_at, title (optional)
- `Message` table: id, conversation_id, role (user/assistant/tool), content, tool_calls (JSON), created_at

### XIII. MCP Tools Architecture
Task operations MUST be exposed as MCP-style tools callable by the Cohere chat agent.

**Required Tools:**
- `add_task` - Create a new task for the authenticated user
- `list_tasks` - List tasks with optional filters (priority, tags, status, search)
- `complete_task` - Mark a task as completed (handles recurring task regeneration)
- `delete_task` - Delete a task
- `update_task` - Update task properties (title, description, priority, tags, due_date)

**Tool Security Rules:**
- Every tool MUST receive `user_id` from the authenticated JWT (NOT from user input)
- Every database query within tools MUST filter by `user_id`
- Tools MUST NOT allow cross-user access under any circumstances
- Tool responses MUST be sanitized before returning to the chat model

### XIV. Environment Variables and Secrets (Phase III Additions)

**New Required Environment Variables:**
- `COHERE_API_KEY` - API key for Cohere AI services (REQUIRED)

**Existing Environment Variables (from Phase II):**
- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Shared secret for JWT verification
- `FRONTEND_URL` - Frontend origin for CORS configuration

**Forbidden Environment Variables:**
- `OPENAI_API_KEY` - MUST NOT be used or referenced in Phase III

## Deliverables Structure

- Monorepo root with `.spec-kit/config.yaml` (if using Spec-Kit)
- Organized `/specs` folder: overview, features, api, database, ui
- Separate CLAUDE.md files at root, `/frontend`, and `/backend`
- `docker-compose.yml` for local development (frontend + backend + optional db)
- Final `README.md` with architecture overview and run instructions
- Chat endpoint integrated into existing FastAPI application
- Conversation and Message database models
- MCP tools for task operations
- ChatKit UI component in frontend

## Technology Stack (Non-Negotiable)

### Frontend
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth
- OpenAI ChatKit (or equivalent chat UI library)

### Backend
- FastAPI (SAME existing application)
- SQLModel
- Neon Serverless PostgreSQL
- **Cohere Python SDK** (NOT OpenAI)

### Shared
- JWT authentication (Better Auth ↔ FastAPI)
- BETTER_AUTH_SECRET environment variable

### AI Integration
- Cohere API for chat and tool calling
- COHERE_API_KEY environment variable
- Agent patterns inspired by OpenAI Agents SDK (implemented via Cohere)

## Governance

This constitution governs all development decisions for the Todo application. All code MUST comply with these principles. Amendments require documentation and team approval. All pull requests MUST verify compliance with these principles before merging.

**Version**: 3.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2026-02-04

---

## Differences from Phase II (Key Phase III Changes)

This section highlights the critical architectural and technology decisions that differentiate Phase III from Phase II. **This constitution is the single source of truth for all Phase III decisions.**

### 1. AI Provider Change: OpenAI → Cohere

| Aspect | Phase II | Phase III |
|--------|----------|-----------|
| **AI Provider** | N/A (no AI) | **Cohere API only** |
| **Python SDK** | N/A | `cohere` (NOT `openai`) |
| **API Key** | N/A | `COHERE_API_KEY` |
| **Forbidden** | N/A | `openai` package, `OPENAI_API_KEY` |

**Why Cohere?**
- Native tool calling support via `cohere.chat()` with `tools` parameter
- Cost-effective for conversational AI workloads
- Excellent multi-turn conversation handling with `chat_history`
- No vendor lock-in to OpenAI ecosystem
- Simpler API surface for tool-based agents

### 2. Agent Pattern Reuse (OpenAI Agents SDK → Cohere Implementation)

Phase III reuses the **conceptual patterns** from OpenAI Agents SDK but implements them using Cohere's API:

| OpenAI Agents SDK Concept | Cohere Implementation |
|---------------------------|----------------------|
| `Agent` with tools | `cohere.chat()` with `tools` parameter |
| `Runner.run()` loop | Custom loop calling `cohere.chat()` until no tool calls |
| Tool definitions (JSON Schema) | Cohere tool definitions (similar JSON structure) |
| `tool_calls` in response | `tool_calls` in Cohere response |
| `tool_results` submission | `tool_results` in next `cohere.chat()` call |
| System prompt | `preamble` parameter in Cohere chat |
| Conversation history | `chat_history` parameter (loaded from DB) |

**Key Implementation Notes:**
- Implement a "runner" function that loops until the model stops requesting tools
- Pass `user_id` to every tool execution (from JWT, NOT from model)
- Persist all messages (user, assistant, tool) to database after each turn

### 3. Integration into Existing Backend (NOT Separate Service)

| Aspect | What NOT to Do | What TO Do |
|--------|----------------|------------|
| **Backend** | Create new FastAPI app | Add `/api/chat` to EXISTING FastAPI |
| **Database** | New database instance | Add tables to EXISTING Neon PostgreSQL |
| **Auth** | New auth system | Reuse EXISTING Better Auth + JWT |
| **Models** | Separate SQLModel base | Extend EXISTING SQLModel models |

**Rationale:** Single deployment, shared database connection pool, unified authentication, simpler operations.

### 4. MCP Tools Architecture (Powered by Cohere Tool Calls)

Phase III continues the MCP-style tools pattern but executes them via Cohere:

```
User Message → Cohere Chat API → Tool Call Request → Execute Tool (with user_id) → Tool Result → Cohere Chat API → Final Response
```

**Tool Execution Flow:**
1. Frontend sends user message to `/api/chat`
2. Backend loads conversation history from database
3. Backend calls `cohere.chat()` with tools + history
4. If response contains `tool_calls`:
   - Execute each tool with `user_id` from JWT
   - Call `cohere.chat()` again with tool results
   - Repeat until no more tool calls
5. Persist all messages to database
6. Return final assistant response to frontend

**Security Invariant:** Tools receive `user_id` from the authenticated JWT token, NEVER from the AI model's tool call parameters.

---

## Phase Evolution Summary

| Aspect | Phase I (Console) | Phase II (Web) | Phase III (AI Chatbot) |
|--------|-------------------|----------------|------------------------|
| **Architecture** | Single-process CLI | Full-stack web (monorepo) | Full-stack + AI chatbot |
| **Frontend** | None (console only) | Next.js 16+ with App Router | Next.js + ChatKit UI |
| **Backend** | In-process Python | FastAPI REST API | SAME FastAPI + chat endpoint |
| **Database** | In-memory Python dict | Neon Serverless PostgreSQL | SAME Neon + Conversation/Message tables |
| **Authentication** | None (single-user) | JWT + Better Auth (multi-user) | SAME JWT + Better Auth |
| **User Isolation** | N/A | Mandatory per-user data isolation | SAME + tool-level enforcement |
| **UI** | Text-based argparse | Tailwind CSS web interface | Web UI + conversational chat |
| **AI Provider** | N/A | N/A | **Cohere API** (NOT OpenAI) |
| **Agent Framework** | N/A | N/A | Cohere tool calling + multi-turn chat |
| **State Management** | Runtime memory only | Persistent database + session | Stateless server + DB persistence |
| **Chat Persistence** | N/A | N/A | Conversation + Message tables |
| **MCP Tools** | N/A | N/A | add/list/complete/delete/update_task |
| **Testing** | Unit tests only | Contract + integration + unit | + chatbot integration tests |
| **Deployment** | Local run | Containerized Docker Compose | SAME Docker Compose |
| **Type Safety** | Python type hints | TypeScript + Python | SAME TypeScript + Python |
| **Dependencies** | Standard library only | Full npm/pip trees | + cohere Python SDK |
| **API** | Direct function calls | RESTful HTTP endpoints | REST + /api/chat endpoint |
| **Environment** | Local only | Environment variables | + COHERE_API_KEY |
