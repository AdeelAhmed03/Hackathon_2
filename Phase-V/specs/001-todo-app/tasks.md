---
description: "Task list for basic in-memory todo console app implementation"
---

# Tasks: Basic In-Memory Todo Console App

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan in src/todo_app/
- [ ] T002 [P] Set up UV virtual environment and project configuration
- [ ] T003 [P] Create initial directory structure: src/todo_app/, tests/
- [ ] T004 [P] Generate README.md and CLAUDE.md files

---
## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Task data model in src/todo_app/task.py
- [ ] T006 Create in-memory storage implementation in src/todo_app/task_manager.py
- [ ] T007 [P] Implement error handling utilities in src/todo_app/utils.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and List Tasks (Priority: P1) 🎯 MVP

**Goal**: Allow users to add tasks with title and description, and view all tasks with status indicators and IDs

**Independent Test**: User can run the app, add a task with 'add' command, then list tasks with 'list' command to see the added task with proper ID and status indicator

### Implementation for User Story 1

- [ ] T008 Create CLI interface implementation in src/todo_app/cli.py
- [ ] T009 Implement 'add' command functionality in src/todo_app/cli.py
- [ ] T010 Implement 'list' command functionality in src/todo_app/cli.py
- [ ] T011 Create main entry point in src/todo_app/main.py
- [ ] T012 [P] Add basic manual testing instructions to tests/manual_tests.md

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Update and Delete Tasks (Priority: P2)

**Goal**: Allow users to update task title/description by ID and delete tasks by ID

**Independent Test**: User can add a task, update its details with 'update <id>' command, and verify changes; user can also delete a task with 'delete <id>' command

### Implementation for User Story 2

- [ ] T013 Implement 'update' command functionality in src/todo_app/cli.py
- [ ] T014 Implement 'delete' command functionality in src/todo_app/cli.py
- [ ] T015 Add validation for task ID existence in src/todo_app/task_manager.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Tasks Complete/Incomplete (Priority: P3)

**Goal**: Allow users to toggle completion status of tasks by providing their ID

**Independent Test**: User can add a task, mark it complete with 'complete <id>' command, and verify status changes; can also mark complete tasks as pending again

### Implementation for User Story 3

- [ ] T016 Implement 'complete' command functionality in src/todo_app/cli.py
- [ ] T017 Add status toggle logic in src/todo_app/task_manager.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T018 [P] Add type hints to all modules in src/todo_app/
- [ ] T019 [P] Add docstrings to all functions and classes in src/todo_app/
- [ ] T020 [P] Implement error handling for invalid commands in src/todo_app/cli.py
- [ ] T021 [P] Implement error handling for invalid task IDs in src/todo_app/task_manager.py
- [ ] T022 [P] Add edge case handling (empty list, invalid ID) in src/todo_app/cli.py
- [ ] T023 Update README.md with complete usage instructions
- [ ] T024 Run quickstart validation and update documentation as needed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all components for User Story 1 together:
Task: "Create CLI interface implementation in src/todo_app/cli.py"
Task: "Implement 'add' command functionality in src/todo_app/cli.py"
Task: "Implement 'list' command functionality in src/todo_app/cli.py"
Task: "Create main entry point in src/todo_app/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence