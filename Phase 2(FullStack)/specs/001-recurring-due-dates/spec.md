# Feature Specification: Advanced - Recurring Tasks & Due Dates

**Feature Branch**: `001-recurring-due-dates`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "Advanced - Recurring Tasks & Due Dates - Builds directly on existing multi-user CRUD + priorities/tags/filter/sort. Main new capabilities: 1. Due Dates & Times - Optional due datetime field (date + optional time), Input via proper date/time picker in frontend (use shadcn/ui or similar), Display in task list: Relative time ('in 2 days', 'tomorrow', '3 hours ago'), Status badges: OVERDUE (red), DUE TODAY (orange), DUE SOON (yellow, ≤48h), Sorting by due date should put tasks without due date at the bottom. 2. Recurring Tasks - Optional recurrence rule per task: daily / weekly / monthly / yearly, When a recurring task is marked complete: Create new future instance automatically, Shift due date forward by appropriate interval, New instance starts as pending, inherits title/description/priority/tags/recurrence, Original task remains completed (history preserved), Show recurrence indicator in UI (e.g. repeating arrows icon + frequency label)"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Due Date Assignment (Priority: P1)

Users need to assign due dates and times to their tasks to track deadlines and commitments. This allows them to visualize when tasks are due and prioritize accordingly.

**Why this priority**: Basic due date functionality is essential for any task management system and provides immediate value to users.

**Independent Test**: Users can create a task with a due date and see it displayed in the task list with relative time and status badges.

**Acceptance Scenarios**:

1. **Given** a user is on the task creation screen, **When** they select a due date and time, **Then** the task is saved with that due date and appears in the list with appropriate relative time display
2. **Given** a task with a due date, **When** the user views the task list, **Then** they see relative time indicators like "tomorrow" or "in 3 days" and status badges based on urgency
3. **Given** a task without a due date, **When** the user sorts by due date, **Then** it appears at the bottom of the list

---

### User Story 2 - Recurring Task Creation (Priority: P2)

Users need to create recurring tasks that automatically generate new instances when completed, eliminating the need to manually recreate routine tasks.

**Why this priority**: Recurring tasks provide significant productivity benefits for routine activities, building upon the due date functionality.

**Independent Test**: Users can create a recurring task with a specified interval (daily/weekly/monthly/yearly) and see the recurrence indicator in the UI.

**Acceptance Scenarios**:

1. **Given** a user is creating a task, **When** they select recurrence options (daily/weekly/monthly/yearly), **Then** the task is saved with recurrence metadata and shows a recurrence indicator
2. **Given** a recurring task exists, **When** the user views the task list, **Then** they see a visual indicator showing the recurrence pattern

---

### User Story 3 - Recurring Task Completion (Priority: P3)

When users complete a recurring task, the system should automatically create a new instance with the due date shifted by the recurrence interval, preserving all other properties.

**Why this priority**: This is the core behavior that makes recurring tasks valuable - automating the creation of future instances.

**Independent Test**: When a user marks a recurring task as complete, a new identical task appears in the list with the due date advanced by the recurrence interval.

**Acceptance Scenarios**:

1. **Given** a recurring task exists, **When** the user marks it as complete, **Then** a new instance is automatically created with the due date shifted forward by the recurrence interval and the original task remains completed
2. **Given** a recurring task with specific properties (title, description, priority, tags), **When** it's completed, **Then** the new instance inherits all these properties

---

### Edge Cases

- What happens when a recurring task is completed but the next occurrence would be in the past?
- How does the system handle timezone differences for due date calculations?
- What occurs when a user tries to create a recurring task with invalid recurrence intervals?
- How does the system handle deletion of recurring tasks - does it delete all future instances?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST allow users to assign optional due datetime fields to tasks (date + optional time)
- **FR-002**: System MUST display relative time indicators for due dates ("in 2 days", "tomorrow", "3 hours ago")
- **FR-003**: System MUST show status badges for due dates: OVERDUE (red), DUE TODAY (orange), DUE SOON (yellow, ≤48h)
- **FR-004**: System MUST sort tasks by due date with tasks without due dates appearing at the bottom
- **FR-005**: Users MUST be able to create recurring tasks with intervals: daily, weekly, monthly, yearly
- **FR-006**: System MUST automatically create new task instances when recurring tasks are marked complete
- **FR-007**: New task instances MUST inherit all properties from the original: title, description, priority, tags, recurrence settings
- **FR-008**: System MUST preserve the completed status of the original task when creating new instances
- **FR-009**: System MUST display recurrence indicators in the UI (icon + frequency label)
- **FR-010**: System MUST validate that recurrence intervals are valid (daily/weekly/monthly/yearly only)
- **FR-011**: System MUST handle timezone-aware due date calculations using TIMESTAMP WITH TIME ZONE
- **FR-012**: System MUST prevent creating recurring tasks with due dates in the past for future occurrences

### Key Entities *(include if feature involves data)*

- **Task**: Extended to include due_datetime (TIMESTAMP WITH TIME ZONE) and recurrence_pattern (string enum: daily/weekly/monthly/yearly)
- **RecurrenceRule**: Defines the recurrence pattern and interval for recurring tasks

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Users can create tasks with due dates in under 30 seconds
- **SC-002**: 95% of users successfully identify due date status (overdue/due soon/due today) through visual indicators
- **SC-003**: Users can create recurring tasks with specified intervals (daily/weekly/monthly/yearly) in a single form submission
- **SC-004**: When a recurring task is completed, 100% of the time a new instance is created with the correct due date shift
- **SC-005**: Users can distinguish recurring tasks from regular tasks through clear visual indicators in the UI
- **SC-006**: The system correctly sorts tasks by due date with 99% accuracy, placing tasks without due dates at the bottom
- **SC-007**: Users report a 30% reduction in time spent recreating routine tasks after recurring task functionality is implemented