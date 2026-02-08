---
id: PHR-002
title: ai-chatbot-spec-creation
stage: spec
date: 2026-02-04
surface: claude-code
model: claude-sonnet-4.5
feature: 1-ai-chatbot
branch: 1-ai-chatbot
user: Adeel Ahmed
command: /sp.specify
labels: [phase3, cohere, ai-chatbot, spec, mcp-tools]
links:
  spec: specs/1-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/1-ai-chatbot/spec.md
    action: created
  - path: specs/1-ai-chatbot/checklists/requirements.md
    action: created
tests:
  - null
---

## Prompt

Create a new feature specification file for Phase III: AI Todo Chatbot integrated into the existing full-stack Todo application.

Key requirements:
- Chat logic inside existing FastAPI backend
- Frontend: ChatKit or equivalent chat UI
- AI provider: Cohere ONLY (cohere.Client with COHERE_API_KEY)
- Reuse OpenAI Agents SDK patterns via Cohere API
- Stateless architecture with DB persistence (Conversation + Message tables)
- Endpoint: POST /api/chat protected by JWT
- MCP-style tools: add_task, list_tasks, complete_task, delete_task, update_task
- All tools enforce user_id ownership from JWT
- Support multi-tool calls, conversation context
- Friendly, confirmatory responses

Include: architecture diagram, database models, Cohere integration approach, tool definitions, NL examples, acceptance criteria, security notes.

## Response snapshot

Created comprehensive feature specification with:

**6 User Stories (P1-P3)**:
- US1: Add Task via Chat (P1)
- US2: List and Query Tasks (P1)
- US3: Complete Task (P2)
- US4: Update Task (P2)
- US5: Delete Task (P3)
- US6: Conversation Context (P3)

**26 Functional Requirements** covering:
- Chat endpoint (FR-001 to FR-005)
- AI Integration/Cohere (FR-006 to FR-011)
- MCP Tools (FR-012 to FR-018)
- Frontend Chat UI (FR-019 to FR-023)
- Data Persistence (FR-024 to FR-026)

**5 Tool Definitions** with Cohere parameter_definitions format:
- add_task, list_tasks, complete_task, delete_task, update_task

**Key Sections**:
- High-level architecture diagram (ASCII)
- Cohere integration approach (chat call structure, runner loop)
- Natural language examples table
- Security notes (JWT, data isolation, input validation)
- Success criteria (8 measurable outcomes)

## Outcome

- ✅ Impact: Complete spec ready for planning phase
- 🧪 Tests: N/A (spec phase)
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: /sp.clarify (if needed) or /sp.plan
- 🧠 Reflection: Spec follows constitution v3.0.0, Cohere-only compliance verified

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All checklist items PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
