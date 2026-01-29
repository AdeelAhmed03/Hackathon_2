# Claude Code Rules: hackathon-todo (Phase II)

This file contains specific instructions for Claude when working on the Full-Stack Todo application. Adhere to the Phase II - Web Transformation architecture.

## Project Context
The Todo application is a modern full-stack web application with a FastAPI backend and a Next.js App Router frontend. It uses persistence via Neon Serverless PostgreSQL and SQLModel.

## Code Standards
### Backend (Python)
- **Framework**: FastAPI with SQLModel (SQLAlchemy 2.0 based)
- **Validation**: Pydantic v2 schemas
- **Style**: PEP 8 compliance, mandatory type hints (Python 3.13+)
- **Security**: Data isolation per `user_id` is mandatory for all queries.

### Frontend (TypeScript)
- **Framework**: Next.js 16+ (App Router)
- **Styling**: Tailwind CSS
- **Auth**: Better Auth (JWT-based bridge to backend)
- **Types**: Mandatory TypeScript interfaces for all API entities.

## Monorepo Structure
- `backend/` - FastAPI service
  - `src/models/` - SQLModel entities
  - `src/api/` - Routes and controllers
  - `src/services/` - Business logic and query builders
- `frontend/` - Next.js service
  - `src/components/` - React components
  - `src/hooks/` - Custom hooks for API and state
  - `src/types/` - Shared TypeScript definitions
- `specs/` - Feature specifications and task lists

## Implementation Notes: Advanced Features
- **Priorities**: `low`, `medium` (default), `high`.
- **Tags**: Multi-select tags per task; global tag list stored in relational `Tag` entity.
- **Search**: Case-insensitive keyword search on title/description via `q` param.
- **Filter**: Intersection (AND) logic for multiple tags and priorities.
- **Sorting**: Priority-aware sorting (High > Low) and standard Date/Alpha fields.
- **Due Dates**: Optional datetime field with timezone support (TIMESTAMP WITH TIME ZONE); displays as relative time ("in 2 days", "tomorrow"); shows status badges (OVERDUE, DUE TODAY, DUE SOON).
- **Recurring Tasks**: Optional recurrence rule per task (daily/weekly/monthly/yearly); when completed, automatically creates new instance with shifted due date; preserves all properties (title, description, priority, tags).
- **Visual Indicators**: Badges for due date status and recurrence patterns.
