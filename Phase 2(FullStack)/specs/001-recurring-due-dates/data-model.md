# Data Model: Advanced - Recurring Tasks & Due Dates

**Feature**: Advanced - Recurring Tasks & Due Dates
**Created**: 2026-01-15

## Entities

### Task (Extended)
**Description**: Represents a task with optional due date and recurrence properties

**Fields**:
- `id`: INTEGER, PRIMARY KEY, AUTO_INCREMENT
- `title`: VARCHAR(255), NOT NULL, task title
- `description`: TEXT, NULL, optional task description
- `status`: VARCHAR(20), NOT NULL, CHECK (status IN ('pending', 'in_progress', 'completed'))
- `priority`: VARCHAR(10), NOT NULL, CHECK (priority IN ('low', 'medium', 'high')), DEFAULT 'medium'
- `owner_id`: INTEGER, NOT NULL, FOREIGN KEY REFERENCES users(id)
- `created_at`: TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- `completed_at`: TIMESTAMP WITH TIME ZONE, NULL, when task was marked completed
- `due_datetime`: TIMESTAMP WITH TIME ZONE, NULL, when task is due
- `recurrence_rule`: VARCHAR(20), NULL, CHECK (recurrence_rule IN ('daily', 'weekly', 'monthly', 'yearly')), recurrence pattern
- `recurrence_parent_id`: INTEGER, NULL, FOREIGN KEY REFERENCES tasks(id), parent in recurrence chain

**Relationships**:
- Belongs to: User (via owner_id)
- Has many: Child Tasks (via recurrence_parent_id)

**Validation Rules**:
- `due_datetime` must be in the future if provided
- `recurrence_rule` can only be set if `due_datetime` is also set
- `recurrence_parent_id` must reference a valid task owned by the same user
- `recurrence_parent_id` cannot create circular references

**State Transitions**:
- When status changes to 'completed' and `recurrence_rule` is set → create new task with updated due date

### User
**Description**: Represents a user in the system (existing entity, unchanged)

**Fields**:
- `id`: INTEGER, PRIMARY KEY, AUTO_INCREMENT
- `email`: VARCHAR(255), NOT NULL, UNIQUE
- `password_hash`: VARCHAR(255), NOT NULL
- `created_at`: TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP

## Database Schema Changes

### ALTER TABLE tasks
```sql
ALTER TABLE tasks
ADD COLUMN due_datetime TIMESTAMP WITH TIME ZONE NULL,
ADD COLUMN recurrence_rule VARCHAR(20) NULL
    CONSTRAINT chk_recurrence_rule CHECK (recurrence_rule IN ('daily', 'weekly', 'monthly', 'yearly')),
ADD COLUMN recurrence_parent_id INTEGER NULL
    REFERENCES tasks(id) ON DELETE SET NULL;
```

### Additional Indexes
```sql
CREATE INDEX idx_tasks_due_datetime ON tasks(due_datetime);
CREATE INDEX idx_tasks_recurrence_rule ON tasks(recurrence_rule);
CREATE INDEX idx_tasks_recurrence_parent ON tasks(recurrence_parent_id);
CREATE INDEX idx_tasks_owner_due_status ON tasks(owner_id, due_datetime, status);
```

## Calculated Fields (Computed by Application)

### Due Date Status Indicators
- `is_overdue`: BOOLEAN, TRUE if due_datetime is in the past and status is not 'completed'
- `is_due_today`: BOOLEAN, TRUE if due_datetime is today (based on user's timezone)
- `is_due_soon`: BOOLEAN, TRUE if due_datetime is within 48 hours but not overdue