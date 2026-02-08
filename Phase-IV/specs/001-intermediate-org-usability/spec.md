# Feature Specification: Priorities, Tags, Search, Filter & Sorting

**Feature Branch**: `001-intermediate-org-usability`
**Created**: 2026-01-14
**Status**: Draft
**Input**: User description: "Create a new feature specification file for the intermediate organization & usability improvements. ... Intermediate - Priorities, Tags, Search, Filter & Sorting ... Technical requirements: • All new fields must be added to database schema (tasks table) • Backend must support filtering, searching and sorting via query parameters • API should remain RESTful and respect user ownership • Frontend should update task list in real-time after filter/sort/search changes (client-side if reasonable, or refetch)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Organization with Priorities and Tags (Priority: P1)

As a user, I want to assign priority levels and descriptive tags to my tasks so that I can categorize and identify the importance of my work at a glance.

**Why this priority**: Priorities and tags are the foundational data elements required for all search, filter, and sort capabilities.

**Independent Test**: Can be fully tested by creating or updating a task with a specific priority (High/Medium/Low) and multiple tags (e.g., "work", "urgent"), and verifying they are stored and displayed correctly in the UI.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I select "High" priority and add tags "work" and "urgent", **Then** the task should be saved with these attributes.
2. **Given** I am viewing my task list, **When** I look at a high-priority task, **Then** I should see a red badge or clear visual indicator for "High".
3. **Given** I am viewing my task list, **When** I look at a task with tags, **Then** I should see the tags displayed as distinct pills or badges.

---

### User Story 2 - Finding Tasks via Search and Filtering (Priority: P2)

As a user with many tasks, I want to search for specific keywords and filter my list by status, priority, or tags so that I can quickly find the subset of information I need.

**Why this priority**: Focuses on usability and "finding" information, which is critical as the number of tasks grows.

**Independent Test**: Can be tested by entering a keyword in the search box or selecting a filter toggle and observing that only matching tasks are visible.

**Acceptance Scenarios**:

1. **Given** I have a task titled "Buy groceries", **When** I enter "groceries" in the search field, **Then** only that task (and any other matching tasks) should remain visible.
2. **Given** I have a mix of pending and completed tasks, **When** I filter by "Completed", **Then** only completed tasks should be displayed.
3. **Given** multiple filters are applied (e.g., Priority: High AND Tag: work), **When** I view the list, **Then** only tasks matching **all** selected filters should be shown.

---

### User Story 3 - Ordering Tasks with Sorting (Priority: P3)

As a user, I want to change the order of my tasks based on date, priority, or title so that I can focus on what is due soonest or most important.

**Why this priority**: Refines the list presentation but is less critical for basic task retrieval than search/filter.

**Independent Test**: Can be tested by selecting a sort option from a dropdown and verifying the list order updates according to the logic (e.g., alphabetically A-Z).

**Acceptance Scenarios**:

1. **Given** multiple tasks created at different times, **When** I select "Oldest First", **Then** the task created earliest should appear at the top.
2. **Given** tasks with different priorities, **When** I select "Sort by Priority", **Then** High priority tasks should appear above Medium, and Medium above Low.

---

### Edge Cases

- **Search No Results**: What happens when a user searches for a term that matches no tasks? (System should show a "No results found" message).
- **Empty Tags**: How does the system handle a task with zero tags? (Should display normally without tag Pills).
- **Case Sensitivity**: How does search handle "WORK" vs "work"? (Search should be case-insensitive).
- **Deleted Tags**: The system maintains a global list of all tags ever used by the user. Tags persist in filter options even if no current tasks are using them.
- **Sorting with Ties**: How are tasks sorted if they have the same priority/date? (Default to created date descending for ties).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support three task priority levels: `low`, `medium` (default), and `high`.
- **FR-002**: System MUST allow users to assign zero or more tags to a task.
- **FR-003**: System MUST provide a keyword search that matches against task titles and descriptions.
- **FR-004**: System MUST allow combining filters for status, priority, and tags using AND logic.
- **FR-005**: System MUST allow sorting tasks by: `created_at` (asc/desc), `due_date` (asc/desc), `priority` (high-to-low), and `title` (alphabetical).
- **FR-006**: Backend API MUST accept query parameters for search (`q`), filter (`status`, `priority`, `tags`), and sort (`sort_by`, `order`).
- **FR-007**: API MUST only return tasks belonging to the authenticated user, regardless of filters applied.
- **FR-008**: System MUST support a mandatory `due_date` field for all tasks.

### Key Entities *(include if feature involves data)*

- **Task**:
  - `priority`: String enum (low, medium, high)
  - `tags`: Array of strings
  - `due_date`: Date/Time (optional)
  - `title/description`: Existing fields used for full-text search

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can find any specific task by keyword in under 3 seconds.
- **SC-002**: Filtering and sorting updates the visible task list in under 500ms (perceived instant update).
- **SC-003**: 100% of tasks returned by search/filter belong to the requesting user.
- **SC-004**: Users report improved organization efficiency (qualitative survey target).
