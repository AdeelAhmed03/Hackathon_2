<!-- SYNC IMPACT REPORT:
Version change: 1.0.0 → 2.0.0
Modified principles:
- I. Clean Code and Type Safety → I. Spec-Driven Development
- II. Minimal Dependencies → II. Clean Code and Type Safety
- III. Test-First Approach → III. Multi-User Security and Isolation
- IV. Console-Based Interface → IV. Authentication and Authorization
- V. Memory-Only Storage → V. Persistent Storage with SQLModel
- VI. Task Management Structure → VI. RESTful API Design
Removed sections: "Console-Based Interface" (replaced with web-specific principles)
Added sections:
- VII. Monorepo Structure and Code Organization
- VIII. Frontend Technology Standards
- IX. Backend Technology Standards
- X. Development Workflow (enhanced)
Technology Stack and Constraints: Completely rewritten for full-stack web
Development Workflow: Enhanced for web application development
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated (no changes needed)
- .specify/templates/spec-template.md ✅ updated (no changes needed)
- .specify/templates/tasks-template.md ✅ updated (no changes needed)
- README.md ⚠ pending (user to update)
Follow-up TODOs: None
-->

# Todo Application Constitution (Phase II)

## Project Identity

**Project Name**: hackathon-todo
**Architecture**: Full-Stack Web Application (Monorepo)
**Phase**: II - Web Transformation

## Core Principles

### I. Spec-Driven Development
All development MUST follow the Spec-Kit Plus methodology. No manual coding outside of Claude Code agent. Every feature begins with a specification document in `/specs/`. The spec-driven workflow enforces: feature specification → implementation plan → task breakdown → implementation → validation. This ensures architectural consistency and traceable requirements.

### II. Clean Code and Type Safety
All code MUST follow language-specific style guidelines with mandatory type hints. TypeScript on frontend, Python with type hints on backend. Code MUST be modular, well-documented, and maintainable. Every function MUST have clear purpose, defined inputs/outputs, and be easily testable. No any types or untyped code.

### III. Multi-User Security and Isolation
Every user MUST see and modify only their own tasks. User data isolation is NON-NEGOTIABLE and MUST be enforced at the database query level. All operations MUST be filtered by authenticated user ID. There are no exceptions to user data isolation - any implementation that allows cross-user access is a critical security defect.

### IV. Authentication and Authorization
JWT-based authentication bridges Next.js (Better Auth) and FastAPI backend. The BETTER_AUTH_SECRET environment variable MUST be shared between frontend and backend for JWT verification. All API endpoints MUST verify JWT tokens and reject requests without valid authentication. Better Auth handles frontend session management; backend verifies tokens on every request.

### V. Persistent Storage with SQLModel
All task data MUST be stored in Neon Serverless PostgreSQL using SQLModel. No in-memory storage in production. Database models MUST define proper relationships between users and tasks. Migrations MUST be versioned and applied automatically on startup. Foreign key constraints enforce referential integrity.

### VI. RESTful API Design
All backend endpoints MUST follow RESTful conventions. Proper HTTP methods (GET, POST, PUT, DELETE), status codes, and error responses. API contracts MUST be documented and validated. Request/response validation using Pydantic models. Consistent error handling across all endpoints.

### VII. Monorepo Structure and Code Organization
The project MUST maintain a clear monorepo structure:
- `/frontend` - Next.js application
- `/backend` - FastAPI application
- `/specs` - Feature specifications and design documents
- `/shared` - Shared types and utilities
Separate CLAUDE.md files at root, `/frontend`, and `/backend` for domain-specific guidance.

### VIII. Frontend Technology Standards
Frontend MUST use:
- Next.js 16+ with App Router
- TypeScript throughout
- Tailwind CSS for styling
- Better Auth for authentication
- React Server Components where appropriate
Client-side MUST handle auth state and provide smooth user experience.

### IX. Backend Technology Standards
Backend MUST use:
- FastAPI with SQLModel
- TypeScript or Python with full type coverage
- Neon Serverless PostgreSQL
- JWT verification middleware
- Proper CORS configuration for frontend communication
- Environment-based configuration for all secrets

### X. Development Workflow
- Follow red-green-refactor TDD cycle for testable features
- All code MUST pass type checking (mypy/TypeScript compiler) and linting
- Pull requests require code review and passing tests
- Contract tests for API endpoints (backend testing frontend contracts)
- Integration tests for user journeys
- Docker Compose for local development environment

## Deliverables Structure

- Monorepo root with `.spec-kit/config.yaml`
- Organized `/specs` folder: overview, features, api, database, ui
- Separate CLAUDE.md files at root, `/frontend`, and `/backend`
- `docker-compose.yml` for local development (frontend + backend + optional db)
- Final `README.md` with architecture overview and run instructions

## Technology Stack (Non-Negotiable)

### Frontend
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth

### Backend
- FastAPI
- SQLModel
- Neon Serverless PostgreSQL

### Shared
- JWT authentication
- BETTER_AUTH_SECRET environment variable

## Governance

This constitution governs all development decisions for the Todo application. All code MUST comply with these principles. Amendments require documentation and team approval. All pull requests MUST verify compliance with these principles before merging.

**Version**: 2.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2026-01-13

---

## Phase I vs Phase II: Major Differences Summary

| Aspect | Phase I (Console) | Phase II (Web) |
|--------|-------------------|----------------|
| **Architecture** | Single-process CLI | Full-stack web (monorepo) |
| **Frontend** | None (console only) | Next.js 16+ with App Router |
| **Backend** | In-process Python | FastAPI REST API |
| **Database** | In-memory Python dict | Neon Serverless PostgreSQL |
| **Authentication** | None (single-user) | JWT + Better Auth (multi-user) |
| **User Isolation** | N/A | Mandatory per-user data isolation |
| **UI** | Text-based argparse | Tailwind CSS web interface |
| **Testing** | Unit tests only | Contract + integration + unit tests |
| **Deployment** | Local run | Containerized with Docker Compose |
| **Type Safety** | Python type hints | TypeScript (frontend) + Python (backend) |
| **Dependencies** | Standard library only | Full npm/pip dependency trees |
| **State Management** | Runtime memory only | Persistent database + session state |
| **API** | Direct function calls | RESTful HTTP endpoints |
| **Environment** | Local only | Environment variables + secrets |
