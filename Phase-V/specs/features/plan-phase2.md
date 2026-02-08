# Implementation Plan: Full-Stack Todo Application (Phase II)

**Branch**: `1-fullstack-todo` | **Date**: 2026-01-13 | **Spec**: [fullstack-todo-phase2.md](./fullstack-todo-phase2.md)
**Input**: Feature specification from `/specs/features/fullstack-todo-phase2.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform the existing in-memory console todo application into a modern full-stack web application with multi-user authentication, persistent storage, and responsive UI. The implementation will follow a monorepo structure with separate frontend (Next.js) and backend (FastAPI) applications, connected through JWT-based authentication and RESTful APIs. Key deliverables include user authentication flows, task CRUD operations with user isolation, and a modern responsive interface.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI backend), TypeScript/JavaScript (Next.js 16+ frontend)
**Primary Dependencies**: FastAPI, SQLModel, Neon PostgreSQL, Next.js 16+, Better Auth, Tailwind CSS
**Storage**: Neon Serverless PostgreSQL with SQLModel ORM and Alembic migrations
**Testing**: pytest (backend), Jest/Vitest (frontend), manual testing for user flows
**Target Platform**: Web application (cross-platform browser compatibility)
**Project Type**: Web - full-stack application with monorepo structure
**Performance Goals**: Sub-second API response times, 60fps UI interactions, support 1000+ concurrent users
**Constraints**: JWT authentication required on all endpoints, user data isolation enforced at database level, responsive design for mobile/desktop
**Scale/Scope**: Multi-user application supporting thousands of users with individual task management

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Verification

✅ **Spec-Driven Development**: Following Spec-Kit Plus methodology with feature specification as foundation
✅ **Clean Code and Type Safety**: TypeScript frontend with full type coverage, Python with type hints
✅ **Multi-User Security and Isolation**: JWT authentication and user ID filtering for all operations
✅ **Authentication and Authorization**: Better Auth + JWT verification with shared BETTER_AUTH_SECRET
✅ **Persistent Storage with SQLModel**: Neon PostgreSQL with SQLModel ORM and proper migrations
✅ **RESTful API Design**: Standard HTTP methods, proper status codes, OpenAPI contracts
✅ **Monorepo Structure**: Clear separation between frontend and backend directories
✅ **Frontend Technology Standards**: Next.js 16+ with App Router, TypeScript, Tailwind CSS
✅ **Backend Technology Standards**: FastAPI with SQLModel, proper middleware, CORS configuration
✅ **Development Workflow**: Docker Compose for local development, proper error handling

### No Violations Found
All constitution principles are fully supported by this implementation approach. The plan follows spec-driven development, maintains clean code standards, enforces security and isolation, and uses the specified technology stack.

## Project Structure

### Documentation (this feature)

```text
specs/features/fullstack-todo-phase2/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)
backend/
├── src/
│   ├── models/
│   │   ├── user.py          # User entity with authentication fields
│   │   ├── task.py          # Task entity with user relationship
│   │   └── base.py          # Base SQLModel configuration
│   ├── services/
│   │   ├── auth.py          # Authentication service and JWT handling
│   │   ├── user.py          # User management service
│   │   └── task.py          # Task CRUD operations with user isolation
│   ├── api/
│   │   ├── auth.py          # Authentication endpoints (/api/auth/*)
│   │   ├── users.py         # User management endpoints (/api/users/*)
│   │   ├── tasks.py         # Task endpoints (/api/tasks/*)
│   │   └── dependencies.py  # FastAPI dependency injection
│   ├── middleware/
│   │   └── auth.py          # JWT authentication middleware
│   ├── database/
│   │   ├── models.py        # SQLModel model definitions
│   │   ├── migrations/      # Alembic migration files
│   │   └── session.py       # Database session management
│   └── main.py              # FastAPI application entry point
└── tests/
    ├── contract/
    │   └── test_auth_contract.py
    ├── integration/
    │   ├── test_auth_flow.py
    │   ├── test_task_isolation.py
    │   └── test_user_workflows.py
    └── unit/
        ├── test_models.py
        ├── test_services.py
        └── test_api.py

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout with auth provider
│   │   ├── page.tsx           # Home/dashboard page
│   │   ├── auth/
│   │   │   ├── page.tsx       # Auth page (sign up/sign in)
│   │   │   └── layout.tsx     # Auth layout
│   │   ├── dashboard/
│   │   │   ├── page.tsx       # Task management dashboard
│   │   │   └── layout.tsx     # Dashboard layout
│   │   └── api/
│   │       └── route.ts       # API route handlers
│   ├── components/
│   │   ├── auth/
│   │   │   ├── SignInForm.tsx
│   │   │   ├── SignUpForm.tsx
│   │   │   └── SignOutButton.tsx
│   │   ├── task/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskFilters.tsx
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       └── Card.tsx
│   ├── hooks/
│   │   ├── useAuth.ts         # Authentication state management
│   │   ├── useTasks.ts        # Task data management
│   │   └── useApi.ts          # API client hook
│   ├── lib/
│   │   ├── api.ts             # API client implementation
│   │   ├── auth.ts            # Authentication utilities
│   │   └── types.ts           # TypeScript type definitions
│   └── middleware.ts          # Next.js middleware for auth protection
├── styles/
│   └── globals.css
└── tests/
    ├── integration/
    │   ├── test_auth_integration.tsx
    │   └── test_task_management.tsx
    └── unit/
        ├── components/
        ├── hooks/
        └── lib/

shared/
├── types/
│   └── api.ts                 # Shared API type definitions
└── utils/
    └── validation.ts          # Shared validation utilities

.env.example                    # Environment variable template
docker-compose.yml             # Local development environment
pyproject.toml                 # Python project configuration
package.json                   # Frontend dependencies
```

**Structure Decision**: The selected structure provides clear separation between frontend and backend concerns while maintaining the monorepo benefits. The backend uses FastAPI with SQLModel for robust API development and database management. The frontend uses Next.js 16+ with App Router for modern React development patterns. Shared utilities are isolated in a separate directory to avoid duplication.

## Phase 0: Research & Investigation

### Research Questions

1. **JWT Integration Best Practices**: Research optimal JWT token structure, expiration strategies, and secure storage patterns for Next.js + FastAPI integration
2. **SQLModel Migration Strategy**: Investigate Alembic migration patterns for SQLModel with Neon PostgreSQL in serverless environments
3. **Better Auth Configuration**: Research Best practices for Better Auth setup with JWT verification in FastAPI backend
4. **Error Handling Patterns**: Research consistent error handling and HTTP status code usage across full-stack applications
5. **Testing Strategy**: Investigate testing approaches for authenticated flows and user isolation in both frontend and backend

### Research Findings (research.md)

#### JWT Integration Best Practices
- **Decision**: Use 15-minute access tokens with 7-day refresh tokens
- **Rationale**: Balances security with user experience, requires refresh for long sessions
- **Implementation**: Store access tokens in memory, refresh tokens in httpOnly cookies
- **Alternatives considered**: Longer-lived tokens (security risk), shorter tokens (poor UX)

#### SQLModel Migration Strategy
- **Decision**: Use Alembic with target metadata approach for SQLModel
- **Rationale**: Provides database versioning and deployment safety
- **Implementation**: Generate migrations automatically, apply on startup in development
- **Alternatives considered**: Manual SQL scripts (error-prone), no migrations (data loss risk)

#### Better Auth Configuration
- **Decision**: Use JWT strategy with shared secret between frontend and backend
- **Rationale**: Enables seamless authentication across both layers
- **Implementation**: Better Auth handles frontend sessions, FastAPI verifies JWT tokens
- **Alternatives considered**: Session-based auth (complex for API), OAuth2 (overkill for todo app)

#### Error Handling Patterns
- **Decision**: Standardized error response format with consistent HTTP status codes
- **Rationale**: Provides predictable API behavior and better debugging
- **Implementation**: Custom exception handlers in FastAPI, error boundaries in Next.js
- **Alternatives considered**: Generic error responses (poor UX), no error handling (bad reliability)

#### Testing Strategy
- **Decision**: Contract tests for API endpoints, integration tests for auth flows, manual tests for complex user scenarios
- **Rationale**: Ensures API contracts are maintained while covering critical user journeys
- **Implementation**: pytest for backend, Jest for frontend, manual testing for end-to-end flows
- **Alternatives considered**: Unit tests only (insufficient coverage), full automation (overhead for simple app)

## Phase 1: Design & Contracts

### Data Model (data-model.md)

#### User Entity
```typescript
interface User {
  id: string              // UUID primary key
  email: string           // Unique email address
  name: string           // Display name
  password_hash: string  // Bcrypt hashed password
  created_at: Date       // Account creation timestamp
  updated_at: Date       // Last update timestamp

  // Relationships
  tasks: Task[]          // User's tasks (one-to-many)
}
```

#### Task Entity
```typescript
interface Task {
  id: string              // UUID primary key
  title: string           // Task title (max 200 chars)
  description: string     // Task description (optional, max 1000 chars)
  completed: boolean      // Completion status
  created_at: Date        // Task creation timestamp
  updated_at: Date        // Last update timestamp

  // Relationships
  user_id: string         // Foreign key to User
  user: User              // Associated user (many-to-one)
}
```

#### Database Schema
```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

### API Contracts (contracts/)

#### Authentication Endpoints

**POST /api/auth/sign-up**
```yaml
request:
  content:
    application/json:
      schema:
        type: object
        required: [email, name, password]
        properties:
          email:
            type: string
            format: email
          name:
            type: string
            minLength: 2
            maxLength: 255
          password:
            type: string
            minLength: 8

response:
  201:
    content:
      application/json:
        schema:
          type: object
          properties:
            message:
              type: string
            user:
              $ref: '#/components/schemas/User'
```

**POST /api/auth/sign-in**
```yaml
request:
  content:
    application/json:
      schema:
        type: object
        required: [email, password]
        properties:
          email:
            type: string
            format: email
          password:
            type: string

response:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            message:
              type: string
            user:
              $ref: '#/components/schemas/User'
```

**POST /api/auth/sign-out**
```yaml
response:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            message:
              type: string
```

#### Task Endpoints

**GET /api/tasks**
```yaml
parameters:
  - name: completed
    in: query
    schema:
      type: boolean

response:
  200:
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/Task'
```

**POST /api/tasks**
```yaml
request:
  content:
    application/json:
      schema:
        type: object
        required: [title]
        properties:
          title:
            type: string
            maxLength: 200
          description:
            type: string
            maxLength: 1000
          completed:
            type: boolean
            default: false

response:
  201:
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Task'
```

**PUT /api/tasks/{id}**
```yaml
parameters:
  - name: id
    in: path
    required: true
    schema:
      type: string
      format: uuid

response:
  200:
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Task'
```

**DELETE /api/tasks/{id}**
```yaml
parameters:
  - name: id
    in: path
    required: true
    schema:
      type: string
      format: uuid

response:
  204: {}
```

### Quickstart Guide (quickstart.md)

#### Development Setup

1. **Prerequisites**
   - Node.js 18+ installed
   - Python 3.11+ installed
   - Docker for local database (optional)

2. **Environment Setup**
   ```bash
   # Copy environment template
   cp .env.example .env.local

   # Set required environment variables
   echo "NEXTAUTH_URL=http://localhost:3000" >> .env.local
   echo "DATABASE_URL=postgresql://user:password@localhost:5432/todo_app" >> .env.local
   echo "BETTER_AUTH_SECRET=your-secret-key-here" >> .env.local
   ```

3. **Backend Setup**
   ```bash
   cd backend
   pip install -e .
   alembic upgrade head
   uvicorn src.main:app --reload
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Local Database (Optional)**
   ```bash
   docker-compose up -d postgres
   ```

#### Running the Application

- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

#### First Steps

1. Navigate to http://localhost:3000
2. Sign up for a new account
3. Create your first task
4. Explore the task management features

## Phase 1: Agent Context Update

### Agent-Specific File Updates

The agent context has been updated to include the new technologies and patterns:

**Backend Technologies Added:**
- FastAPI with SQLModel
- Neon PostgreSQL configuration
- JWT authentication patterns
- Alembic migration strategies
- RESTful API design principles

**Frontend Technologies Added:**
- Next.js 16+ with App Router
- Better Auth integration
- Tailwind CSS patterns
- React Server Components usage
- Modern React hooks patterns

**Architecture Patterns:**
- Monorepo structure best practices
- User data isolation implementation
- JWT-based authentication flows
- Full-stack testing strategies

## Constitution Check (Post-Design)

*Re-evaluated after Phase 1 design completion*

### Updated Compliance Verification

✅ **Spec-Driven Development**: All implementation details derived from feature specification
✅ **Clean Code and Type Safety**: TypeScript interfaces and Python type hints defined
✅ **Multi-User Security and Isolation**: JWT authentication and user_id filtering implemented
✅ **Authentication and Authorization**: Better Auth + JWT verification architecture designed
✅ **Persistent Storage with SQLModel**: Neon PostgreSQL schema with proper relationships
✅ **RESTful API Design**: OpenAPI contracts with standard HTTP methods and status codes
✅ **Monorepo Structure**: Clear separation with shared utilities
✅ **Frontend Technology Standards**: Next.js 16+ with modern patterns
✅ **Backend Technology Standards**: FastAPI with proper middleware and error handling
✅ **Development Workflow**: Docker Compose and development scripts defined

### Design Validation

The Phase 1 design maintains full compliance with all constitution principles. The data model enforces user isolation through foreign key relationships. API contracts follow RESTful principles with proper authentication requirements. The monorepo structure provides clear separation while enabling shared utilities.

## Implementation Order Recommendation

### Phase 1: Foundation (Week 1)
1. **Database & Models** (2 days)
   - Set up Neon PostgreSQL connection
   - Create SQLModel models for User and Task
   - Configure Alembic migrations
   - Test database operations

2. **Authentication Backend** (2 days)
   - Implement JWT middleware
   - Create auth endpoints (/api/auth/*)
   - Set up password hashing and validation
   - Test authentication flows

3. **Task CRUD Backend** (2 days)
   - Implement task endpoints (/api/tasks/*)
   - Add user isolation logic
   - Create API contracts and documentation
   - Test CRUD operations

### Phase 2: Frontend Integration (Week 2)
4. **Auth Frontend Integration** (2 days)
   - Set up Next.js project structure
   - Implement Better Auth configuration
   - Create sign-up/sign-in forms
   - Test authentication flows

5. **Task UI Frontend** (3 days)
   - Create task management dashboard
   - Implement task CRUD forms
   - Add responsive design with Tailwind
   - Test user interface

### Phase 3: Polish & Testing (Week 3)
6. **Error Handling & Validation** (1 day)
   - Add comprehensive error handling
   - Implement client-side validation
   - Create error boundaries

7. **Testing & Documentation** (2 days)
   - Write integration tests
   - Create comprehensive documentation
   - Performance optimization

8. **Deployment Preparation** (1 day)
   - Configure production environment
   - Set up Docker Compose for local development
   - Create deployment scripts

## Complexity Tracking

> **No violations found** - All constitution principles are fully supported by this implementation approach.

## Next Steps

The implementation plan is complete and ready for execution. The next command should be `/sp.tasks` to generate the detailed task breakdown organized by user story and implementation phases.