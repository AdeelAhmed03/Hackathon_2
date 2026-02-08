# Research: Search and Filter Optimization

## Decision: PostgreSQL ILIKE with B-Tree Indexes

We have evaluated two primary methods for implementing search and filtering in this phase:
1.  **Full-Text Search (FTS)** using PostgreSQL GIN indexes and `tsvector`.
2.  **Basic Pattern Matching** using `ILIKE` with B-Tree/Trigram indexes.

### Rationale
For "Intermediate" usage (hundreds to low thousands of tasks per user), **ILIKE** with a Trigram index (`pg_trgm`) provides the best balance of speed and implementation simplicity. It handles case-insensitivity natively and supports partial word matches (e.g., "groc" matching "groceries").

### Multi-Tag Filtering Logic (AND)
To support requirement **FR-004** (Combining filters using AND logic), we will use subqueries or multiple `EXISTS` clauses for tags.
Example Logic:
```sql
SELECT * FROM tasks t
WHERE t.user_id = :user_id
  AND EXISTS (SELECT 1 FROM task_tag_link ttl JOIN tags tg ON tg.id = ttl.tag_id WHERE ttl.task_id = t.id AND tg.name = 'work')
  AND EXISTS (SELECT 1 FROM task_tag_link ttl JOIN tags tg ON tg.id = ttl.tag_id WHERE ttl.task_id = t.id AND tg.name = 'urgent')
```
This ensures tasks must have *all* requested tags.

## Priority Sorting Strategy
To sort by priority (`high` > `medium` > `low`), we have two choices:
1.  **Postgres ENUM**: Native sorting based on defined order.
2.  **Mapping Function**: `CASE` statement in SQL.

**Decision**: Use `CASE` statement in the SQLAlchemy query to ensure portability and clarity without complex enum migrations.
```python
priority_map = case(
    (Task.priority == "high", 3),
    (Task.priority == "medium", 2),
    (Task.priority == "low", 1),
    else_=0
)
```

## Frontend Debouncing
To meet **SC-002** (500ms perceived update), the frontend will debounce keyboard input by 300ms before triggering a refetch. Client-side optimistic filtering will be skipped to maintain a single source of truth from the backend, especially for complex tag/priority combinations.
