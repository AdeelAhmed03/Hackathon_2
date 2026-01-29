---
name: backend-skill
description: Generate FastAPI backend routes, handle request/response validation, and connect to a database. Use for backend API development.
---

# Backend Skill – FastAPI & Database Integration

## Instructions

1. **API Route Generation**
   - Create RESTful routes using FastAPI
   - Follow HTTP method conventions (GET, POST, PUT, PATCH, DELETE)
   - Namespace all endpoints under `/api/`
   - Match routes exactly to the API specifications

2. **Request & Response Handling**
   - Define Pydantic models for request validation
   - Define response schemas for consistent JSON output
   - Validate input data and handle edge cases
   - Return appropriate HTTP status codes

3. **Authentication & Authorization**
   - Extract JWT from `Authorization: Bearer <token>` header
   - Verify JWT signature using shared secret
   - Decode token to identify authenticated user
   - Enforce user-level data isolation on every request

4. **Database Connectivity**
   - Use SQLModel for ORM operations
   - Connect to Neon PostgreSQL using `DATABASE_URL`
   - Implement CRUD queries scoped to authenticated user
   - Use transactions where necessary
   - Apply indexes and constraints defined in specs

5. **Error Handling**
   - Use `HTTPException` for predictable API errors
   - Return structured error responses
   - Prevent information leakage in error messages

---

## Best Practices
- Keep route handlers small and focused
- Separate models, routes, and database logic
- Never trust client-provided user identifiers
- Always filter database queries by authenticated user ID
- Use dependency injection for DB sessions and auth
- Write code that aligns with Spec-Driven Development

---

## Example Structure

```python
@router.post("/api/tasks", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    db_task = Task.from_orm(task)
    db_task.user_id = user.id
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
