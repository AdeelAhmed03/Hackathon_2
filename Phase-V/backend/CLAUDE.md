# Claude Code Rules: Backend (Phase IV)

Backend-specific instructions for the FastAPI Todo application with Cohere AI chatbot integration.

## Technology Stack

- **Framework**: FastAPI with SQLModel (SQLAlchemy 2.0)
- **Python**: 3.13+ with mandatory type hints
- **Database**: PostgreSQL (local via Helm in K8s, NOT Neon)
- **AI Provider**: Cohere Python SDK (CRITICAL: NOT OpenAI)
- **Auth**: JWT verification middleware (shared BETTER_AUTH_SECRET)
- **Validation**: Pydantic v2 schemas

## Directory Structure

```
backend/
├── src/
│   ├── api/                    # FastAPI route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── tasks.py           # Task CRUD endpoints
│   │   ├── tags.py            # Tag management endpoints
│   │   └── chat.py            # AI chatbot endpoint
│   ├── models/                 # SQLModel database models
│   │   ├── user.py            # User model
│   │   ├── task.py            # Task model (priority, tags, due_date, recurrence)
│   │   ├── tag.py             # Tag model
│   │   ├── conversation.py    # Chat conversation model
│   │   └── message.py         # Chat message model
│   ├── services/               # Business logic
│   │   ├── task_service.py    # Task operations
│   │   ├── chat_service.py    # Cohere AI integration
│   │   └── tool_service.py    # MCP tool execution
│   ├── tools/                  # MCP-style tools for Cohere
│   │   ├── definitions.py     # Tool schemas
│   │   ├── add_task.py        # Create task tool
│   │   ├── list_tasks.py      # List tasks tool
│   │   ├── complete_task.py   # Complete task tool
│   │   ├── update_task.py     # Update task tool
│   │   └── delete_task.py     # Delete task tool
│   ├── middleware/             # FastAPI middleware
│   │   └── auth.py            # JWT verification
│   ├── database/               # Database configuration
│   │   ├── config.py          # Settings
│   │   ├── engine.py          # SQLAlchemy engine
│   │   └── session.py         # Session management
│   └── main.py                # Application entry point
├── alembic/                    # Database migrations
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
└── pyproject.toml             # Project configuration
```

## AI Provider Rules (CRITICAL)

### MUST Use Cohere

```python
import cohere

# Initialize client
client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

# Chat with tool calling
response = client.chat(
    message=user_message,
    chat_history=history,
    tools=tool_definitions,
    preamble=system_prompt
)
```

### FORBIDDEN

```python
# DO NOT USE - These are forbidden in Phase IV
import openai  # FORBIDDEN
from openai import OpenAI  # FORBIDDEN
os.getenv("OPENAI_API_KEY")  # FORBIDDEN
```

## Database Configuration

### Phase IV: Local PostgreSQL (Kubernetes)

```python
# In Kubernetes, DATABASE_URL points to local PostgreSQL service
DATABASE_URL = "postgresql://postgres:password@postgres:5432/todo"

# Connection via K8s service DNS
# Service name: postgres (from Helm chart)
# Port: 5432 (standard PostgreSQL)
```

### SQLModel Usage

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # ALWAYS filter by user_id
    title: str
    description: Optional[str] = None
    priority: str = Field(default="medium")  # low, medium, high
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None  # daily, weekly, monthly, yearly
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Security Requirements

### User Data Isolation (NON-NEGOTIABLE)

Every database query MUST filter by `user_id`:

```python
# CORRECT - Always filter by user_id
def get_user_tasks(session: Session, user_id: str) -> list[Task]:
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

# WRONG - Never query without user_id filter
def get_all_tasks(session: Session) -> list[Task]:  # FORBIDDEN
    return session.exec(select(Task)).all()
```

### JWT Verification

```python
from src.middleware.auth import verify_jwt

@router.get("/tasks")
async def get_tasks(
    request: Request,
    session: Session = Depends(get_session)
):
    # Extract user_id from verified JWT
    user_id = verify_jwt(request)  # Raises 401 if invalid

    # Use user_id for all queries
    tasks = get_user_tasks(session, user_id)
    return tasks
```

## MCP Tools Architecture

### Tool Definition Pattern

```python
# tools/definitions.py
TOOLS = [
    {
        "name": "add_task",
        "description": "Create a new task for the user",
        "parameter_definitions": {
            "title": {
                "type": "str",
                "description": "Task title",
                "required": True
            },
            "priority": {
                "type": "str",
                "description": "Priority level: low, medium, high",
                "required": False
            }
        }
    }
]
```

### Tool Execution Pattern

```python
# tools/add_task.py
def execute_add_task(
    session: Session,
    user_id: str,  # ALWAYS from JWT, never from tool params
    title: str,
    priority: str = "medium",
    **kwargs
) -> dict:
    task = Task(
        user_id=user_id,  # Security: user_id from auth, not AI
        title=title,
        priority=priority
    )
    session.add(task)
    session.commit()
    return {"success": True, "task_id": task.id}
```

## Chat Service Pattern

```python
# services/chat_service.py
import cohere

async def process_chat(
    user_id: str,
    message: str,
    conversation_id: int,
    session: Session
) -> str:
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

    # Load history from database
    history = load_conversation_history(session, conversation_id)

    # Call Cohere with tools
    response = client.chat(
        message=message,
        chat_history=history,
        tools=TOOLS,
        preamble=SYSTEM_PROMPT
    )

    # Execute tool calls if present
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = execute_tool(
                session=session,
                user_id=user_id,  # Pass user_id from JWT
                tool_name=tool_call.name,
                params=tool_call.parameters
            )
            # Continue conversation with tool result
            response = client.chat(
                message=message,
                chat_history=history,
                tool_results=[{"call": tool_call, "outputs": [result]}]
            )

    # Persist messages
    save_message(session, conversation_id, "user", message)
    save_message(session, conversation_id, "assistant", response.text)

    return response.text
```

## Containerization

### Dockerfile Requirements

```dockerfile
# backend/Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
```

### Environment Variables (K8s Secrets)

```yaml
# Injected via Kubernetes Secret
DATABASE_URL: postgresql://postgres:password@postgres:5432/todo
COHERE_API_KEY: <from-secret>
BETTER_AUTH_SECRET: <from-secret>
FRONTEND_URL: http://todo-frontend:3000
```

## Testing

### Local Testing (Docker Compose)

```bash
cd backend
pip install -r requirements.txt
pytest src/api/test_chat.py -v
```

### K8s Testing

```bash
# Port-forward backend service
kubectl port-forward svc/todo-backend 8000:8000

# Test API
curl http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
```

## Migrations

### Alembic Commands

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### In Kubernetes

Migrations run automatically on container startup via the Dockerfile CMD.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/signup | User registration |
| POST | /api/v1/auth/signin | User login |
| GET | /api/v1/tasks | List user's tasks |
| POST | /api/v1/tasks | Create task |
| PUT | /api/v1/tasks/{id} | Update task |
| DELETE | /api/v1/tasks/{id} | Delete task |
| POST | /api/v1/chat | AI chatbot endpoint |
| GET | /api/v1/conversations | List conversations |

## Constitution Compliance

All code must comply with `.specify/memory/constitution.md` (v4.0.0):
- Cohere-only AI provider (XI)
- User data isolation (III)
- JWT authentication (IV)
- SQLModel with PostgreSQL (V)
- MCP tools architecture (XIII)
