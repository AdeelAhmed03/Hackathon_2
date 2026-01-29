# Data Model: Priorities, Tags, Search, Filter & Sorting

## Entities

### Task
Updated model with priority and due date.

| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | - |
| `user_id` | `UUID` | Owner ID | Foreign Key (Users) |
| `title` | `String` | Task name | Max 255 chars |
| `description` | `String` | Detailed info | Optional |
| `priority` | `Enum` | Importance level | `low`, `medium`, `high` |
| `status` | `Boolean` | Completion state | Default: `false` |
| `due_date` | `DateTime` | Mandatory deadline | NOT NULL |
| `created_at` | `DateTime` | Auto-timestamp | Default: `now()` |

### Tag
New entity for persistent categorization.

| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | - |
| `user_id` | `UUID` | Owner ID | Foreign Key (Users) |
| `name` | `String` | Tag label | Unique per user |

### TaskTagLink
Join table for Many-to-Many relationship.

| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `task_id` | `UUID` | Task reference | Foreign Key (Tasks) |
| `tag_id` | `UUID` | Tag reference | Foreign Key (Tags) |

## Relationships

- **User → Task**: One-to-Many.
- **User → Tag**: One-to-Many.
- **Task ↔ Tag**: Many-to-Many (via TaskTagLink).

## Validation Rules

1.  **Mandatory Due Date**: Tasks cannot be created or updated without a valid `due_date`.
2.  **Tag Name Uniqueness**: A user cannot create two tags with the same name.
3.  **Ownership Verification**: A user can only link tags that they own to tasks that they own.
4.  **Priority Defaults**: If not specified, priority defaults to `medium`.

## Storage Decision

All entities will be stored in Neon Serverless PostgreSQL. SQLAlchemy (SQLModel) will manage the `user_id` filtering as a global requirement for all queries.
