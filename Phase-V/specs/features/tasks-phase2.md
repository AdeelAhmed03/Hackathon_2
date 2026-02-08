# Tasks: Full-Stack Todo Application (Phase II)

**Input**: Design documents from `/specs/features/fullstack-todo-phase2/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are omitted per the guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **Include exact file paths in descriptions**

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow the monorepo structure defined in plan-phase2.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create monorepo project structure with backend/ and frontend/ directories
- [ ] T002 [P] Initialize backend Python project with FastAPI dependencies in backend/pyproject.toml
- [ ] T003 [P] Initialize frontend Next.js project with TypeScript in frontend/package.json
- [ ] T004 [P] Configure shared environment variable template (.env.example) with BETTER_AUTH_SECRET and DATABASE_URL
- [ ] T005 [P] Create Docker Compose configuration for local development in docker-compose.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 [P] Set up SQLModel models for User and Task entities in backend/src/models/user.py and backend/src/models/task.py
- [ ] T007 [P] Configure Neon PostgreSQL database connection and session management in backend/src/database/session.py
- [ ] T008 [P] Set up Alembic migration configuration for SQLModel in backend/src/database/migrations/
- [ ] T009 [P] Implement JWT authentication middleware in backend/src/middleware/auth.py
- [ ] T010 [P] Create global error handlers and standardized response format in backend/src/main.py
- [ ] T011 [P] Set up dependency injection framework for FastAPI in backend/src/api/dependencies.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication (Priority: P1) 🎯 MVP

**Goal**: As a user I can sign up / sign in / sign out using modern auth flows

**Independent Test**: User can create account, sign in, access protected resources, and sign out successfully

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create authentication service with JWT handling in backend/src/services/auth.py
- [ ] T013 [P] [US1] Implement user management service in backend/src/services/user.py
- [ ] T014 [US1] Create authentication endpoints (/api/auth/*) in backend/src/api/auth.py
- [ ] T015 [P] [US1] Set up Better Auth configuration in frontend/src/lib/auth.ts
- [ ] T016 [US1] Create sign-up form component in frontend/src/components/auth/SignUpForm.tsx
- [ ] T017 [US1] Create sign-in form component in frontend/src/components/auth/SignInForm.tsx
- [ ] T018 [US1] Create sign-out button component in frontend/src/components/auth/SignOutButton.tsx
- [ ] T019 [US1] Create authentication page layout in frontend/src/app/auth/layout.tsx
- [ ] T020 [US1] Implement authentication page with forms in frontend/src/app/auth/page.tsx
- [ ] T021 [US1] Add authentication state management hook in frontend/src/hooks/useAuth.ts
- [ ] T022 [US1] Create API client for authentication in frontend/src/lib/api.ts
- [ ] T023 [US1] Integrate authentication middleware with Next.js middleware.ts

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task Management (Priority: P2)

**Goal**: As an authenticated user I can create, read, update, delete my own tasks

**Independent Test**: Authenticated user can perform all CRUD operations on their own tasks

### Implementation for User Story 2

- [ ] T024 [P] [US2] Implement task service with user isolation logic in backend/src/services/task.py
- [ ] T025 [US2] Create task endpoints (/api/tasks/*) in backend/src/api/tasks.py
- [ ] T026 [P] [US2] Create task list component in frontend/src/components/task/TaskList.tsx
- [ ] T027 [P] [US2] Create individual task item component in frontend/src/components/task/TaskItem.tsx
- [ ] T028 [P] [US2] Create task form component for create/edit in frontend/src/components/task/TaskForm.tsx
- [ ] T029 [US2] Create task filters component in frontend/src/components/task/TaskFilters.tsx
- [ ] T030 [US2] Create task management dashboard page in frontend/src/app/dashboard/page.tsx
- [ ] T031 [US2] Create dashboard layout in frontend/src/app/dashboard/layout.tsx
- [ ] T032 [US2] Implement task data management hook in frontend/src/hooks/useTasks.ts
- [ ] T033 [US2] Add task CRUD operations to API client in frontend/src/lib/api.ts
- [ ] T034 [US2] Integrate task operations with authentication state

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Task Completion Toggle (Priority: P3)

**Goal**: As an authenticated user I can mark tasks as complete/incomplete

**Independent Test**: Authenticated user can toggle task completion status with immediate UI feedback

### Implementation for User Story 3

- [ ] T035 [P] [US3] Enhance task completion toggle functionality in backend/src/api/tasks.py
- [ ] T036 [P] [US3] Create completion toggle component in frontend/src/components/task/TaskToggle.tsx
- [ ] T037 [US3] Update task item component to include completion toggle in frontend/src/components/task/TaskItem.tsx
- [ ] T038 [US3] Enhance task data management hook with completion methods in frontend/src/hooks/useTasks.ts
- [ ] T039 [US3] Update task list to show completion status visually in frontend/src/components/task/TaskList.tsx
- [ ] T040 [US3] Add optimistic updates for completion toggles in frontend/src/hooks/useTasks.ts

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Data Isolation (Priority: P4)

**Goal**: As an authenticated user I can only see and modify my own tasks (strong isolation)

**Independent Test**: Users with different accounts cannot access each other's tasks

### Implementation for User Story 4

- [ ] T041 [US4] Enhance all task endpoints with user ID validation in backend/src/api/tasks.py
- [ ] T042 [US4] Add database-level user isolation verification in backend/src/services/task.py
- [ ] T043 [US4] Create security testing scenarios for user isolation
- [ ] T044 [US4] Add additional error handling for unauthorized access attempts
- [ ] T045 [US4] Verify frontend properly handles isolation errors from backend

**Checkpoint**: All user stories should work with complete data isolation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T046 [P] Add comprehensive error handling components in frontend/src/components/ui/ErrorBoundary.tsx
- [ ] T047 [P] Implement client-side form validation utilities in frontend/src/lib/validation.ts
- [ ] T048 [P] Add responsive design improvements with Tailwind CSS in frontend/styles/globals.css
- [ ] T049 [P] Create reusable UI components (Button, Input, Card) in frontend/src/components/ui/
- [ ] T050 Add performance optimizations for large task lists in frontend/src/hooks/useTasks.ts
- [ ] T051 [P] Update README.md with full-stack application setup and deployment instructions
- [ ] T052 Create basic manual testing checklist in specs/features/testing-checklist.md
- [ ] T053 [P] Add production environment configuration in .env.production.example

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for authentication
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US2 functionality
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Security enhancement for all stories

### Within Each User Story

- Models before services
- Services before endpoints
- Backend before frontend integration
- Core implementation before enhancement features
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- Frontend and backend components within a story can be developed in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all models and services for User Story 1 together:
Task: "Create authentication service with JWT handling in backend/src/services/auth.py"
Task: "Create user management service in backend/src/services/user.py"
Task: "Set up Better Auth configuration in frontend/src/lib/auth.ts"

# Launch all frontend components for User Story 1 together:
Task: "Create sign-up form component in frontend/src/components/auth/SignUpForm.tsx"
Task: "Create sign-in form component in frontend/src/components/auth/SignInForm.tsx"
Task: "Create sign-out button component in frontend/src/components/auth/SignOutButton.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Task CRUD)
   - Developer C: User Story 3 (Completion Toggle)
   - Developer D: User Story 4 (Data Isolation)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (if tests were requested)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks are sized for one Claude Code session
- Acceptance criteria: Each task should result in working functionality that can be tested immediately