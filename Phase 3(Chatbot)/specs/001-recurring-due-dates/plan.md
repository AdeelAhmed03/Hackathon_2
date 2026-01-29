# Implementation Plan: Advanced - Recurring Tasks & Due Dates

**Feature**: Advanced - Recurring Tasks & Due Dates
**Branch**: 001-recurring-due-dates
**Created**: 2026-01-15
**Status**: Draft

## Technical Context

### Overview
This plan implements due dates and recurring tasks functionality, extending the existing task management system with:
- Due date/time fields with timezone awareness
- Recurrence patterns (daily/weekly/monthly/yearly)
- Automatic task regeneration on completion
- Visual indicators for due date status and recurrence

### Architecture
- **Backend**: FastAPI with SQLModel (PostgreSQL)
- **Frontend**: Next.js 16+ with TypeScript
- **Authentication**: JWT-based with Better Auth
- **Database**: Neon Serverless PostgreSQL

### Dependencies
- **Backend**: FastAPI, SQLModel, Alembic (for migrations)
- **Frontend**: React, TypeScript, Tailwind CSS
- **Date Handling**: Python datetime for backend, date-fns/dayjs for frontend

### Unknowns
All technical unknowns have been resolved in research.md:
- Due date detection logic: Server-side calculation with client-side display
- Timezone handling: UTC storage with user's local timezone for display
- Recurrence failure handling: Graceful degradation with error logging

## Constitution Check

### Spec-Driven Development (I)
✅ Plan follows spec-driven approach with feature specification as source of truth

### Clean Code and Type Safety (II)
✅ All code will use type hints (Python) and TypeScript with proper interfaces

### Multi-User Security and Isolation (III)
✅ All due date and recurrence operations will be filtered by authenticated user ID with foreign key constraints ensuring data isolation

### Authentication and Authorization (IV)
✅ All API endpoints will verify JWT tokens and reject unauthenticated requests, maintaining the JWT bridge between Better Auth and FastAPI

### Persistent Storage with SQLModel (V)
✅ Will use SQLModel for database operations with proper foreign key constraints and timezone-aware timestamps

### RESTful API Design (VI)
✅ Will follow REST conventions with proper HTTP methods, status codes, and documented API contracts

### Monorepo Structure (VII)
✅ Will maintain clear separation between frontend and backend code in respective directories

### Frontend Technology Standards (VIII)
✅ Will use Next.js 16+, TypeScript, Tailwind CSS as specified

### Backend Technology Standards (IX)
✅ Will use FastAPI, SQLModel, Neon Serverless PostgreSQL with full type coverage

### Development Workflow (X)
✅ Will follow TDD principles where applicable with proper testing including contract and integration tests

## Gates

### Gate 1: Architecture Alignment
✅ Feature fits within existing monorepo architecture

### Gate 2: Constitution Compliance
✅ All constitutional principles can be satisfied

### Gate 3: Feasibility Assessment
✅ All technical requirements are achievable with current stack

## Phase 0: Research & Analysis

### R01: Timezone Handling Best Practices
**Decision**: Use UTC for storage, convert to user's local timezone for display
**Rationale**: UTC storage prevents issues with daylight saving time changes and allows for consistent calculations
**Alternatives considered**: Storing in user's local timezone (problematic with DST changes)

### R02: Due Date/Time Detection Logic Placement
**Decision**: Hybrid approach - server calculates status, client displays
**Rationale**: Server provides authoritative status, client provides responsive UI updates
**Alternatives considered**: Pure client-side (timezone issues), pure server-side (latency)

### R03: Recurrence Chain Failure Handling
**Decision**: Log failures but continue operation, implement retry mechanism
**Rationale**: Ensures system remains operational despite individual failures
**Alternatives considered**: Fail entire operation (too disruptive)

## Phase 1: Design & Contracts

### Data Model Changes

#### Task Entity Extension
```sql
-- Add to existing task table:
due_datetime TIMESTAMP WITH TIME ZONE NULL,
recurrence_rule VARCHAR(20) NULL CHECK (recurrence_rule IN ('daily', 'weekly', 'monthly', 'yearly')),
recurrence_parent_id INTEGER NULL REFERENCES tasks(id), -- For tracking recurrence chain
```

#### New Fields Semantics
- `due_datetime`: Nullable timestamp with timezone for task deadline
- `recurrence_rule`: Enum-like field for recurrence interval
- `recurrence_parent_id`: Links child tasks to their parent in recurrence chain

### API Contract Updates

#### GET /api/tasks
**Request**: No changes to query parameters
**Response**: Add `due_datetime`, `recurrence_rule`, `recurrence_parent_id`, `is_overdue`, `is_due_soon`, `is_due_today`

#### POST /api/tasks
**Request**: Add optional `due_datetime`, `recurrence_rule` fields
**Response**: Return created task with all fields

#### PUT /api/tasks/{id}
**Request**: Add optional `due_datetime`, `recurrence_rule` fields
**Response**: Return updated task with all fields

#### PATCH /api/tasks/{id}/complete
**Request**: No changes
**Response**: For recurring tasks, return both completed task and newly created instance

### Frontend Type Extensions
```typescript
interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  owner_id: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  due_datetime?: string; // ISO 8601 format
  recurrence_rule?: 'daily' | 'weekly' | 'monthly' | 'yearly';
  recurrence_parent_id?: number;
  is_overdue?: boolean;
  is_due_soon?: boolean; // Within 48 hours
  is_due_today?: boolean;
}
```

## Phase 2: Implementation Sequence

### Step 1: Database Schema Changes
1. Create Alembic migration for new columns
2. Apply migration to database
3. Update SQLModel Task definition

### Step 2: Backend Logic
1. Update Pydantic schemas with new fields
2. Add due date validation logic
3. Implement recurrence helper functions
4. Update task completion endpoint with recurrence logic
5. Add due date status calculation functions

### Step 3: API Endpoints
1. Update GET /api/tasks to return new fields
2. Update POST/PUT endpoints to accept new fields
3. Update PATCH /api/tasks/{id}/complete with recurrence creation

### Step 4: Frontend Components
1. Update task interface
2. Implement date/time picker component
3. Create recurrence selector component
4. Add visual indicators for due dates and recurrence
5. Update task creation/editing forms

### Step 5: UI Enhancements
1. Add relative time formatting
2. Update task list sorting to handle null due dates
3. Implement visual indicators for overdue/due soon/due today

## Phase 3: Testing Focus Areas

### T01: Recurrence Chain Integrity
- Verify new instances inherit all properties from parent
- Ensure original task remains completed
- Test edge cases like recurrence in the past

### T02: Timezone Handling
- Test due date calculations across different timezones
- Verify consistent behavior during DST transitions
- Ensure proper display of relative times

### T03: Due Date Status Calculation
- Test overdue detection accuracy
- Verify due-soon threshold (≤48h)
- Confirm due-today boundary conditions

### T04: Data Isolation
- Verify users can't access others' due dates/recurrences
- Test recurrence creation respects ownership
- Ensure proper filtering in all queries

## Risk Mitigation

### RISK-001: Timezone Calculation Errors
**Mitigation**: Store all times in UTC, convert only for display, use robust timezone library

### RISK-002: Recurrence Chain Infinite Loops
**Mitigation**: Implement depth limits, add validation for recurrence rules

### RISK-003: Performance Degradation
**Mitigation**: Add indexes on new date fields, optimize queries with due date filters

## Success Criteria Validation

### SC-001: Task Creation Speed
**Target**: Under 30 seconds for task with due date
**Verification**: Measure form completion to save time

### SC-002: Due Date Status Recognition
**Target**: 95% accuracy in identifying due date status
**Verification**: UI tests with visual indicators

### SC-003: Recurring Task Creation
**Target**: Single form submission for recurring tasks
**Verification**: End-to-end test of recurrence creation

### SC-004: Recurrence Chain Accuracy
**Target**: 100% of completions create correct next instance
**Verification**: Automated tests for recurrence logic

### SC-005: Visual Differentiation
**Target**: Clear identification of recurring tasks
**Verification**: UI tests for recurrence indicators

### SC-006: Due Date Sorting
**Target**: 99% accuracy, nulls at bottom
**Verification**: Integration tests for sorting behavior

### SC-007: Productivity Improvement
**Target**: 30% reduction in routine task recreation
**Verification**: User feedback and usage analytics