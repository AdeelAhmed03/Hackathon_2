---
id: PHR-004
title: ai-chatbot-task-breakdown
stage: tasks
date: 2026-02-04
surface: claude-code
model: claude-sonnet-4.5
feature: 1-ai-chatbot
branch: 1-ai-chatbot
user: Adeel Ahmed
command: /sp.tasks
labels: [phase3, cohere, ai-chatbot, tasks, implementation]
links:
  spec: specs/1-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/1-ai-chatbot/tasks.md
    action: created
tests:
  - null
---

## Prompt

Create detailed task breakdown for Phase III AI Chatbot with Cohere integration.

Break into small steps (recommended order):
- Add Conversation and Message SQLModel classes
- Create & apply database migration for new tables
- Install cohere python sdk in backend
- Add COHERE_API_KEY to .env.example & documentation
- Define Cohere-compatible tool schemas (JSON) for add_task, list_tasks, etc.
- Implement tool execution functions (add_task_impl, etc.) with user_id check
- Create cohere_chat_helper function (messages, tools, model)
- Implement tool calling loop (execute tools → feed results back → repeat)
- Add POST /api/chat endpoint (JWT protected)
- Implement full stateless flow: fetch history → Cohere call → persist messages
- Add confirmation & error handling wrappers
- Frontend: add chat page / component
- Connect frontend to /api/chat with auth token

Prioritize: database + tools + endpoint first.

## Response snapshot

Created comprehensive task breakdown with **85 tasks** across 10 phases:

**Phase Structure:**
- Phase 1: Setup (4 tasks) - Dependencies, env config
- Phase 2: Foundational (23 tasks) - DB models, Cohere service, tool framework, chat endpoint
- Phase 3-8: User Stories (39 tasks total)
  - US1: Add Task (5 tasks)
  - US2: List Tasks (8 tasks)
  - US3: Complete Task (7 tasks)
  - US4: Update Task (9 tasks)
  - US5: Delete Task (7 tasks)
  - US6: Context (3 tasks)
- Phase 9: Frontend (12 tasks) - Types, hooks, components, page
- Phase 10: Polish (7 tasks) - Error handling, loading states

**Key Features:**
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- Parallel opportunities marked with [P]
- User story labels [US1-US6] for story-phase tasks
- MVP scope identified: Phases 1-4 + Phase 9 (~45 tasks)
- Dependency graph showing execution order
- Execution commands for running tasks via Claude

## Outcome

- ✅ Impact: Complete task breakdown ready for implementation
- 🧪 Tests: Not included (not explicitly requested)
- 📁 Files: 1 file created (tasks.md)
- 🔁 Next prompts: Execute tasks starting with Phase 1 & 2
- 🧠 Reflection: Prioritized DB → Tools → Endpoint → Frontend as requested

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Format validation PASS (all 85 tasks follow checklist format)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
