---
id: PHR-001
title: phase3-constitution-update
stage: constitution
date: 2026-02-04
surface: claude-code
model: claude-sonnet-4.5
feature: ai-chatbot
branch: master
user: Adeel Ahmed
command: /sp.constitution
labels: [phase3, cohere, ai-chatbot, constitution]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - path: .specify/memory/constitution.md
    action: updated
tests:
  - null
---

## Prompt

Create / update the project constitution.md file for the **full Phase III – AI Todo Chatbot** (integrated into existing full-stack application).

Project name: hackathon-todo (monorepo)

Current phase: Phase III – AI-powered conversational Todo management

Main objective:
Integrate a natural-language AI chatbot inside the **existing full-stack Todo web application** so that users can manage their tasks (add, list, update, delete, complete + all previous features) using everyday language.

The chatbot must be built **inside the same backend** (FastAPI) that already exists from Phase II — no separate microservice, no new repository.

Key technology decisions & constraints (very important — do NOT deviate):

• Frontend: Continue using Next.js (App Router) + add OpenAI ChatKit (or equivalent chat UI component) for the conversational interface
• Backend: SAME existing FastAPI application (do NOT create a new FastAPI instance)
• Database: SAME Neon Serverless PostgreSQL (add only Conversation & Message tables)
• ORM: SAME SQLModel
• Authentication: SAME Better Auth + JWT (chat endpoint must be protected)
• AI Provider: **Cohere API only** (use the Cohere API key from environment variables)
• Agent framework: Reuse patterns & concepts from **OpenAI Agents SDK** (tool calling, runner, multi-turn chat, system prompt, history management), but implement them using **Cohere's chat + tools API** (cohere.chat() with tool_use support)
• MCP Server: Keep the stateless MCP tools architecture (add_task, list_tasks, complete_task, delete_task, update_task) — expose them via the SAME FastAPI app
• Architecture: Fully stateless server — conversation state lives only in database (Conversation + Message tables)
• All task operations remain filtered by authenticated user_id (from JWT)

Non-negotiable rules:
- Do NOT use OpenAI API keys or OpenAI models anywhere in the project from now on
- Do NOT install or call openai python package
- Use cohere python sdk → cohere.Client() with COHERE_API_KEY
- Implement agent-like behavior using Cohere's tool calling + multi-turn chat
- Keep the same /api/{user_id}/chat endpoint (or /api/chat with user from JWT)
- Maintain strong user isolation — never let one user see/modify another user's tasks
- Follow strict spec-driven development: spec → plan → tasks → implement via Claude Code
- No manual coding outside of agent prompts

Monorepo structure reminders (must follow):
hackathon-todo/
├── .spec-kit/
├── specs/
│   ├── features/
│   ├── api/
│   ├── database/
│   └── ...
├── frontend/               # Next.js + ChatKit UI
├── backend/                # SAME FastAPI — add chat endpoint + cohere logic here
├── CLAUDE.md
├── frontend/CLAUDE.md
└── backend/CLAUDE.md

Deliverables expected from this constitution:
- Clear statement that AI chatbot is integrated into existing FastAPI backend
- Explicit switch from OpenAI → Cohere (with justification: cost, tool calling support, etc.)
- List of new environment variables needed: COHERE_API_KEY
- Reminder about stateless architecture & database persistence
- Security & ownership rules (JWT + user_id filtering on every tool)
- Development workflow reminder: spec → clarify → plan → tasks → implement

## Response snapshot

Updated constitution from v2.0.0 to v3.0.0 with the following changes:

**Added Principles:**
- XI. AI Chatbot Integration (Cohere-Powered) - Non-negotiable rules for Cohere-only AI
- XII. Conversation Persistence and State Management - Stateless server architecture
- XIII. MCP Tools Architecture - Tool definitions and security rules
- XIV. Environment Variables and Secrets - COHERE_API_KEY requirement

**Modified Principles:**
- IX. Backend Technology Standards - Added Cohere SDK requirement
- X. Development Workflow - Enhanced to: spec → clarify → plan → tasks → agent implementation prompts

**Added Sections:**
- Single Source of Truth declaration at document header
- "Differences from Phase II" section with detailed tables for:
  - AI Provider Change (OpenAI → Cohere) with rationale
  - Agent Pattern Reuse (OpenAI Agents SDK concepts → Cohere implementation)
  - Integration into Existing Backend (what TO DO vs what NOT to do)
  - MCP Tools Architecture with Cohere execution flow diagram

**Added Phase Evolution Table:**
- Extended comparison table to include Phase III column with all new AI capabilities

## Outcome

- ✅ Impact: Constitution updated to v3.0.0 establishing Phase III governance
- 🧪 Tests: N/A (documentation update)
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Update CLAUDE.md files for Phase III context; Create feature spec for AI chatbot
- 🧠 Reflection: Major version bump justified by fundamental capability addition (AI chatbot) and provider switch (OpenAI → Cohere)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
