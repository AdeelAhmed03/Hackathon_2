# Tasks: Intermediate Organization & Usability

**Input**: Design documents from `/specs/001-intermediate-org-usability/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Prioritization follows spec.md requirements.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify backend/frontend build and lint status before feature start
- [x] T002 [P] Register updated CLAUDE.md context for Priority/Tag support
- [x] T003 [P] Ensure `BETTER_AUTH_SECRET` is configured for JWT verification in backend/.env

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model and infrastructure needed for all user stories

**⚠️ CRITICAL**: Task T004 must be completed before any story-specific work.

- [x] T004 Update SQLModel classes for Task, Tag, and TaskTagLink in `backend/src/models/` (Data Model ref)
- [x] T005 [P] Implement Tag schema and ownership in `backend/src/models/tag.py`
- [x] T006 Create and apply database migration for user-specific tags and priorities in `backend/`
- [x] T007 Initialize TaskQueryService class skeleton in `backend/src/services/task_query_service.py`
- [x] T008 [P] Extend TypeScript Task interface with priority and tags in `frontend/src/types/task.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Task Organization with Priorities and Tags (Priority: P1) 🎯 MVP

**Goal**: Assign priority levels and tags to categorise tasks.

**Independent Test**: Create a task with "high" priority and "work" tag via API/UI and verify persistence and badge display.

- [x] T009 [US1] Implement Tag CRUD endpoints (GET /api/tags, POST /api/tags) in `backend/src/api/tags.py`
- [x] T010 [US1] Update Task creation logic to handle priority and tag links in `backend/src/api/tasks.py`
- [x] T011 [P] [US1] Create PriorityBadge component in `frontend/src/components/PriorityBadge.tsx`
- [x] T012 [P] [US1] Create TagPills component in `frontend/src/components/TagPills.tsx`
- [x] T013 [US1] Update TaskCard to display PriorityBadge and TagPills in `frontend/src/components/TaskCard.tsx`
- [x] T014 [US1] Add Priority/Tag selectors to create/edit task forms in `frontend/src/components/TaskForm.tsx`

**Checkpoint**: User Story 1 (Organization) functional and testable.

---

## Phase 4: User Story 2 - Finding Tasks via Search and Filtering (Priority: P2)

**Goal**: Find tasks via keyword search and multi-select filters (Status, Priority, Tags).

**Independent Test**: Use search input to find task by subtitle; apply multiple filters and verify list reflects the subset.

- [x] T015 [US2] Implement case-insensitive ILIKE keyword search logic in `backend/src/services/task_query_service.py`
- [x] T016 [US2] Implement AND-logic multi-filter for priority, status, and tags in `backend/src/services/task_query_service.py`
- [x] T017 [US2] Update GET /api/tasks to accept and process QueryParams using TaskQueryService in `backend/src/api/tasks.py`
- [x] T018 [P] [US2] Create SearchInput component with 300ms debounce in `frontend/src/components/SearchInput.tsx`
- [x] T019 [P] [US2] Create FilterBar with Tag/Priority multi-select in `frontend/src/components/FilterBar.tsx`
- [x] T020 [US2] Refactor useTasks hook to internalize filter state and query params in `frontend/src/hooks/useTasks.ts`

**Checkpoint**: User Story 2 (Search/Filter) functional and testable.

---

## Phase 5: User Story 3 - Ordering Tasks with Sorting (Priority: P3)

**Goal**: Change task order based on date, priority, or title.

**Independent Test**: Select "Sort by Priority" and verify High tasks appear first; select "A-Z" and verify alphabetical order.

- [x] T021 [US3] Implement priority mapping (High=3, Med=2, Low=1) sorting logic in `backend/src/services/task_query_service.py`
- [x] T022 [US3] Add sort_by and order parameters support to TaskQueryService in `backend/src/services/task_query_service.py`
- [x] T023 [P] [US3] Create SortSelector dropdown component in `frontend/src/components/SortSelector.tsx`
- [x] T024 [US3] Integrate sorting state with API fetching and UI controls in `frontend/src/components/Header.tsx`

**Checkpoint**: User Story 3 (Sorting) functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: UX refinements and state persistence.

- [x] T025 [P] Implement URL state persistence for filters/sort using searchParams in `frontend/src/hooks/useTasks.ts`
- [x] T026 [P] Add "No results found" empty state message to TaskList in `frontend/src/components/TaskList.tsx`
- [x] T027 [P] Implement loading skeleton states for filter refetches in `frontend/src/components/TaskListSkeleton.tsx`
- [x] T028 Perform manual verification of mandatory due_date validation in `backend/src/api/tasks.py`

---

## Dependencies & Implementation Strategy

1.  **US1 → US2 → US3**: Stories are implemented sequentially. US2 depends on the data added in US1. US3 refines the presentation of data from US1/US2.
2.  **MVP Scope**: Successful completion of US1 provides the core organization value.
3.  **Parallelism**: UI components (T011, T012, T018, T019, T023) can be built in parallel with backend logic once the Task interface (T008) is updated.

---

## Manual Testing Checklist

- [x] Create Task: Mandatory due_date fails if missing.
- [x] Create Task: Priority defaults to 'medium'.
- [x] Filter: Select 'High' priority AND 'work' tag; verify strict intersection.
- [x] Search: Verify searching for 'WORK' finds 'work' (case-insensitive).
- [x] Security: User A attempts to filter by User B's tag name; verify no leakage.
- [x] URL Sync: Set filter, refresh page; verify filter is preserved.
