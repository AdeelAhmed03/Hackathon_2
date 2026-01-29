# Tasks: Advanced - Recurring Tasks & Due Dates

**Input**: Design documents from `/specs/001-recurring-due-dates/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by implementation phase to enable progressive development and testing. Prioritization follows spec.md requirements with database/backend logic prioritized first.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Database & Backend Foundation

**Purpose**: Core data model and backend infrastructure needed for all features

**⚠️ CRITICAL**: All Phase 1 tasks must be completed before frontend work begins.

- [ ] T001 Add due_datetime & recurrence_rule columns to tasks table in `backend/src/models/task.py` (Data Model ref)
- [ ] T002 [P] Update SQLModel Task model with new fields in `backend/src/models/task.py`
- [ ] T003 [P] Update Pydantic schemas (TaskCreate, TaskUpdate, TaskRead) in `backend/src/models/task.py`
- [ ] T004 Create helper function: calculate_next_due_date(current_due, recurrence_rule) in `backend/src/services/task_service.py`
- [ ] T005 Implement complete endpoint special logic for recurring tasks in `backend/src/api/tasks.py`
- [ ] T006 [P] Add due date validation logic in `backend/src/services/task_service.py`
- [ ] T007 [P] Update GET /api/tasks to return new due date fields in `backend/src/api/tasks.py`

**Checkpoint**: Backend foundation ready - frontend implementation can now begin.

---

## Phase 2: Backend Enhancement

**Purpose**: Advanced backend logic for due date calculations and recurrence

- [ ] T008 Add overdue/due-soon/due-today calculation helpers in `backend/src/services/task_service.py`
- [ ] T009 Update task completion endpoint with recurrence creation logic in `backend/src/api/tasks.py`
- [ ] T010 [P] Create recurrence chain validation to prevent circular references in `backend/src/services/task_service.py`
- [ ] T011 Add timezone-aware due date calculations in `backend/src/services/task_service.py`
- [ ] T012 [P] Update API documentation with new fields in `backend/src/api/tasks.py`
- [ ] T013 Add database indexes for performance in `backend/alembic/versions/` (migration file)

**Checkpoint**: Backend logic complete - all due date and recurrence functionality implemented.

---

## Phase 3: Frontend Data Layer

**Purpose**: Update frontend data structures and types to support new features

**⚠️ CRITICAL**: Task T014 must be completed before any UI component work.

- [ ] T014 Update TypeScript Task interface with new fields in `frontend/src/types/task.ts`
- [ ] T015 [P] Update useTasks hook to handle new fields in `frontend/src/hooks/useTasks.ts`
- [ ] T016 [P] Add date/time utility functions in `frontend/src/utils/date.ts`

**Checkpoint**: Frontend data layer ready - UI components can now be developed.

---

## Phase 4: UI Components (Parallelizable)

**Purpose**: Create reusable UI components for due dates and recurrence

- [ ] T017 [P] [US1] Create DateTimePicker component in `frontend/src/components/DateTimePicker.tsx`
- [ ] T018 [P] [US1] Create RecurrenceSelector component in `frontend/src/components/RecurrenceSelector.tsx`
- [ ] T019 [P] [US1] Create DueStatusBadge component (OVERDUE, DUE TODAY, DUE SOON) in `frontend/src/components/DueStatusBadge.tsx`
- [ ] T020 [P] [US2] Create RecurringTaskIndicator component in `frontend/src/components/RecurringTaskIndicator.tsx`
- [ ] T021 [P] [US1] Create RelativeTimeDisplay component in `frontend/src/components/RelativeTimeDisplay.tsx`

**Checkpoint**: All UI components ready - can now integrate into task forms and lists.

---

## Phase 5: User Story 1 - Due Date Assignment (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign due dates and times to tasks with visual indicators.

**Independent Test**: Create a task with a due date and see it displayed in the task list with relative time and status badges.

- [ ] T022 [US1] Update TaskForm to include DateTimePicker in `frontend/src/components/task/TaskForm.tsx`
- [ ] T023 [US1] Update TaskForm to include DueStatusBadge display in `frontend/src/components/task/TaskForm.tsx`
- [ ] T024 [US1] Update TaskItem to display RelativeTimeDisplay in `frontend/src/components/task/TaskItem.tsx`
- [ ] T025 [US1] Update TaskItem to display DueStatusBadge in `frontend/src/components/task/TaskItem.tsx`
- [ ] T026 [US1] Update task list sorting to handle null due dates (put at bottom) in `frontend/src/components/task/TaskList.tsx`

**Checkpoint**: User Story 1 (Due Dates) functional and testable.

---

## Phase 6: User Story 2 - Recurring Task Creation (Priority: P2)

**Goal**: Allow users to create recurring tasks with specified intervals.

**Independent Test**: Users can create a recurring task with a specified interval (daily/weekly/monthly/yearly) and see the recurrence indicator in the UI.

- [ ] T027 [US2] Update TaskForm to include RecurrenceSelector in `frontend/src/components/task/TaskForm.tsx`
- [ ] T028 [US2] Update TaskItem to display RecurringTaskIndicator in `frontend/src/components/task/TaskItem.tsx`
- [ ] T029 [US2] Add recurrence validation in frontend form in `frontend/src/components/task/TaskForm.tsx`

**Checkpoint**: User Story 2 (Recurring Creation) functional and testable.

---

## Phase 7: User Story 3 - Recurring Task Completion (Priority: P3)

**Goal**: Automatically create new task instances when recurring tasks are marked complete.

**Independent Test**: When a user marks a recurring task as complete, a new identical task appears in the list with the due date advanced by the recurrence interval.

- [ ] T030 [US3] Update task completion logic in frontend to handle recurrence in `frontend/src/components/task/TaskItem.tsx`
- [ ] T031 [US3] Add notification for new recurring task creation in `frontend/src/components/task/TaskItem.tsx`
- [ ] T032 [US3] Update task list to show newly created recurring tasks in `frontend/src/components/task/TaskList.tsx`

**Checkpoint**: User Story 3 (Recurring Completion) functional and testable.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: UX refinements and final touches.

- [ ] T033 [P] Improve overdue detection & visual emphasis in `frontend/src/components/DueStatusBadge.tsx`
- [ ] T034 [P] Update empty state / no-tasks message variants in `frontend/src/components/task/TaskList.tsx`
- [ ] T035 [P] Add timezone handling for date display in `frontend/src/utils/date.ts`
- [ ] T036 [P] Update API documentation with new fields in `backend/src/api/tasks.py`
- [ ] T037 [P] Add error handling for recurrence failures in `frontend/src/components/task/TaskItem.tsx`
- [ ] T038 [P] Add loading states for date/time picker in `frontend/src/components/DateTimePicker.tsx`

**Checkpoint**: All features polished and ready for testing.

---

## Phase 9: Documentation & Testing

**Purpose**: Final verification and documentation.

- [ ] T039 Create manual testing checklist for recurrence chain in `specs/001-recurring-due-dates/testing-checklist.md`
- [ ] T040 Create manual testing checklist for overdue cases in `specs/001-recurring-due-dates/testing-checklist.md`
- [ ] T041 Create manual testing checklist for timezone handling in `specs/001-recurring-due-dates/testing-checklist.md`
- [ ] T042 Update API documentation with new behaviors in `backend/src/api/tasks.py`
- [ ] T043 [P] Add unit tests for new backend functionality in `backend/tests/`
- [ ] T044 [P] Add unit tests for new frontend components in `frontend/tests/`

---

## Dependencies & Implementation Strategy

1.  **Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7**: Sequential implementation required as each phase builds on the previous one.
2.  **MVP Scope**: Successful completion of Phase 5 provides the core due date value.
3.  **Parallelism**: UI components in Phase 4 can be built in parallel once the frontend data layer (Phase 3) is established.
4.  **Testing**: Phases 8-9 can run in parallel with user story implementation but should be completed before release.

---