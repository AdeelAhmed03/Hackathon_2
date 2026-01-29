# Quickstart Guide: Advanced - Recurring Tasks & Due Dates

**Feature**: Advanced - Recurring Tasks & Due Dates
**Created**: 2026-01-15

## Overview
This guide provides a rapid introduction to implementing due dates and recurring tasks functionality in the todo application.

## Prerequisites
- Python 3.9+ with pip
- Node.js 18+ with npm
- PostgreSQL (or Neon Serverless)
- Git

## Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Backend Setup
```bash
cd backend
pip install -e .
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## Database Migration
After adding the due date and recurrence fields:

```bash
cd backend
alembic revision --autogenerate -m "Add due_datetime and recurrence fields to tasks"
alembic upgrade head
```

## Key Implementation Areas

### 1. Update Task Model
Location: `backend/src/models/task.py`
- Add `due_datetime` field (TIMESTAMP WITH TIME ZONE, nullable)
- Add `recurrence_rule` field (enum: daily/weekly/monthly/yearly)
- Add `recurrence_parent_id` field (foreign key to tasks)

### 2. Update Pydantic Schemas
Location: `backend/src/models/task.py`
- Update TaskCreate, TaskUpdate, and TaskRead schemas
- Add validation for due date and recurrence rules

### 3. Update API Endpoints
Location: `backend/src/api/tasks.py`
- Update GET /api/tasks to return new fields
- Update POST /api/tasks to accept new fields
- Update PUT /api/tasks/{id} to accept new fields
- Update PATCH /api/tasks/{id}/complete to handle recurrence logic

### 4. Implement Recurrence Logic
Location: `backend/src/services/task_service.py`
- Create helper function for calculating next due date
- Implement logic to create new task instance when recurring task is completed

### 5. Frontend Task Interface
Location: `frontend/src/types/task.ts`
- Add due_datetime, recurrence_rule, recurrence_parent_id fields
- Add is_overdue, is_due_today, is_due_soon computed properties

### 6. Update Components
- Create date/time picker component
- Create recurrence selector component
- Update TaskForm to include new fields
- Update TaskList to display due date status and recurrence indicators

## API Usage Examples

### Create Task with Due Date
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Submit quarterly report",
    "due_datetime": "2026-02-15T10:00:00Z",
    "priority": "high"
  }'
```

### Create Recurring Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team meeting",
    "due_datetime": "2026-01-20T14:00:00Z",
    "recurrence_rule": "weekly",
    "priority": "medium"
  }'
```

### Complete Recurring Task
```bash
curl -X PATCH http://localhost:8000/api/tasks/123/complete \
  -H "Authorization: Bearer <token>"
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/test_tasks.py -k "due_date or recurrence"
```

### Frontend Tests
```bash
cd frontend
npm run test -- --testPathPattern="due-date|recurrence"
```

## Common Issues & Solutions

### Issue: Timezone Conversion Problems
**Solution**: Ensure all datetimes are stored in UTC and converted appropriately for display

### Issue: Recurrence Chain Not Creating New Instance
**Solution**: Verify that recurrence_rule is set and the completion endpoint contains the recurrence logic

### Issue: Due Date Status Not Calculating Correctly
**Solution**: Check that the backend is computing is_overdue/is_due_soon/is_due_today fields correctly

## Next Steps
1. Implement the database schema changes
2. Update backend models and endpoints
3. Add frontend components for date picking and recurrence selection
4. Test the complete workflow of creating and completing recurring tasks