# Research: Local Kubernetes Deployment

**Feature**: 002-local-k8s-deployment
**Date**: 2026-02-06
**Status**: Complete

## R1: Cohere Tool Calling Support

### Question
Does Cohere API support tool calling similar to OpenAI function calling?

### Decision
**Yes** - Use Cohere Python SDK with native tool calling support

### Research Findings

Cohere's Chat API supports tool calling via the `tools` parameter:

```python
import cohere

client = cohere.Client(api_key="...")

tools = [
    {
        "name": "add_task",
        "description": "Create a new task for the user",
        "parameter_definitions": {
            "title": {"type": "str", "description": "Task title", "required": True},
            "priority": {"type": "str", "description": "low/medium/high", "required": False}
        }
    }
]

response = client.chat(
    message="Add a task to buy milk",
    tools=tools,
    preamble="You are a task management assistant..."
)

# Check for tool calls
if response.tool_calls:
    for call in response.tool_calls:
        print(f"Tool: {call.name}, Params: {call.parameters}")
```

### Rationale
- Native support eliminates need for custom wrapper
- API structure similar to existing MCP tool definitions
- `chat_history` parameter supports multi-turn conversations
- `preamble` replaces system prompt

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| OpenAI SDK | Violates constitution XI (Cohere-only) |
| Custom HTTP client | Unnecessary complexity, SDK handles auth/retry |
| LangChain abstraction | Over-engineered for direct API usage |

---

## R2: Multi-Stage Dockerfile Patterns

### Question
What is the optimal Dockerfile pattern for Next.js frontend and FastAPI backend?

### Decision
- **Frontend**: Node.js build stage → nginx serve stage
- **Backend**: Python slim base with pip dependencies

### Research Findings

**Frontend (Next.js Static Export)**:
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM nginx:1.25-alpine
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 3000
```

**Backend (FastAPI)**:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Requirements
- Non-root user (UID 1001)
- Minimal base images (alpine/slim)
- No build tools in production image
- `.dockerignore` excludes sensitive files

### Image Size Targets
| Image | Target | Achieved By |
|-------|--------|-------------|
| Frontend | <500MB | nginx-alpine, static export |
| Backend | <300MB | python-slim, no dev deps |

---

## R3: Helm Chart Structure

### Question
Should we use an umbrella chart or separate charts for each service?

### Decision
**Separate charts** for frontend, backend, and postgres

### Research Findings

**Umbrella Chart Pros**:
- Single `helm install` command
- Coordinated values across services
- Simpler for initial deployment

**Separate Charts Pros**:
- Independent versioning
- Selective upgrades (upgrade backend only)
- Easier debugging (isolate issues)
- Better for CI/CD (deploy changed service only)

### Chart Structure

```
charts/
├── todo-backend/
│   ├── Chart.yaml          # name: todo-backend, version: 0.1.0
│   ├── values.yaml         # Default values
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       ├── secret.yaml
│       └── _helpers.tpl
├── todo-frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       └── _helpers.tpl
└── postgres/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── deployment.yaml
        ├── service.yaml
        ├── pvc.yaml
        ├── secret.yaml
        └── _helpers.tpl
```

### Deployment Order
1. `postgres` - Database must be ready first
2. `todo-backend` - Needs DATABASE_URL
3. `todo-frontend` - Needs backend API URL

---

## R4: Kubernetes Secret Management

### Question
How should sensitive configuration be managed in Kubernetes?

### Decision
- **Secrets**: API keys, passwords, JWT secrets
- **ConfigMaps**: URLs, ports, feature flags

### Configuration Matrix

| Variable | Type | Chart | Source |
|----------|------|-------|--------|
| COHERE_API_KEY | Secret | todo-backend | Helm --set |
| BETTER_AUTH_SECRET | Secret | todo-backend, todo-frontend | Helm --set |
| DATABASE_URL | Secret | todo-backend | Helm --set or values.yaml |
| POSTGRES_PASSWORD | Secret | postgres | Helm --set |
| FRONTEND_URL | ConfigMap | todo-backend | values.yaml |
| BACKEND_URL | ConfigMap | todo-frontend | values.yaml |

### Secret Creation Pattern

```yaml
# templates/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-backend.fullname" . }}-secrets
type: Opaque
stringData:
  COHERE_API_KEY: {{ .Values.secrets.cohereApiKey | quote }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | quote }}
  DATABASE_URL: {{ .Values.secrets.databaseUrl | quote }}
```

### Security Best Practices
1. Never commit secrets to git
2. Use `--set` for sensitive values
3. Consider external secrets operator for production
4. Rotate secrets regularly

---

## R5: AI DevOps Tools Integration

### Question
How do Gordon, kubectl-ai, and kagent integrate into the deployment workflow?

### Decision
Use AI tools for generation, debugging, and optimization (not required, but recommended)

### Tool Usage Patterns

**Gordon (Docker AI)**:
```bash
# Dockerfile optimization suggestions
docker ai build --suggest ./backend

# Security scanning
docker ai scan todo-backend:v4.0.0

# docker-compose to K8s conversion hints
docker ai convert docker-compose.yml
```

**kubectl-ai**:
```bash
# Manifest generation
kubectl-ai "create deployment for fastapi with health checks"

# Debugging
kubectl-ai "why is my pod in ImagePullBackOff"

# Resource optimization
kubectl-ai "suggest memory limits for todo-backend"
```

**kagent**:
```bash
# Cluster health
kagent health --namespace todo-app

# Scaling analysis
kagent scale --analyze todo-backend

# Log analysis
kagent logs --diagnose todo-backend
```

### Workflow Integration

1. **Build Phase**: Gordon for Dockerfile optimization
2. **Deploy Phase**: kubectl-ai for manifest generation
3. **Debug Phase**: kubectl-ai + kagent for troubleshooting
4. **Optimize Phase**: kagent for resource recommendations

### Fallback
All AI tools are optional. Manual alternatives:
- Gordon → Standard Docker best practices
- kubectl-ai → kubectl + manual YAML writing
- kagent → kubectl describe/logs/top

---

## R6: PersistentVolumeClaim Strategy

### Question
How should PostgreSQL data be persisted across pod restarts?

### Decision
Use PersistentVolumeClaim with Minikube's default StorageClass

### Implementation

```yaml
# postgres/templates/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: standard  # Minikube default
```

### Volume Mount

```yaml
# postgres/templates/deployment.yaml
volumes:
  - name: postgres-data
    persistentVolumeClaim:
      claimName: postgres-data
volumeMounts:
  - name: postgres-data
    mountPath: /var/lib/postgresql/data
```

### Data Durability
- PVC survives pod restarts
- PVC survives `helm upgrade`
- PVC deleted only with `helm uninstall` (configurable)

---

## Summary

All research questions resolved. No blockers for Phase 1 design.

| Topic | Decision | Confidence |
|-------|----------|------------|
| Cohere SDK | Native tool calling | High |
| Dockerfiles | Multi-stage, non-root | High |
| Helm structure | Separate charts | High |
| Secrets | K8s Secrets + Helm --set | High |
| AI DevOps | Optional, documented | Medium |
| Storage | PVC with default StorageClass | High |
