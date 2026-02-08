# Claude Code Rules: hackathon-todo (Phase IV)

This file contains specific instructions for Claude when working on the Full-Stack Todo application. Adhere to the Phase IV - Kubernetes Deployment with AI-Assisted DevOps architecture.

## Project Context

The Todo application is a cloud-native full-stack web application with:
- **Backend**: FastAPI with Cohere AI integration for chatbot functionality
- **Frontend**: Next.js 16+ App Router with ChatKit UI
- **Database**: Local PostgreSQL via Helm (NOT Neon in Phase IV)
- **Deployment**: Minikube + Helm charts for Kubernetes orchestration
- **AI DevOps**: Gordon, kubectl-ai, and kagent for intelligent infrastructure management

## Code Standards

### Backend (Python)
- **Framework**: FastAPI with SQLModel (SQLAlchemy 2.0 based)
- **AI Provider**: Cohere Python SDK (NOT OpenAI)
- **Validation**: Pydantic v2 schemas
- **Style**: PEP 8 compliance, mandatory type hints (Python 3.13+)
- **Security**: Data isolation per `user_id` is mandatory for all queries
- **Containerization**: Production-optimized Dockerfile with multi-stage builds

### Frontend (TypeScript)
- **Framework**: Next.js 16+ (App Router)
- **Styling**: Tailwind CSS
- **Auth**: Better Auth (JWT-based bridge to backend)
- **Types**: Mandatory TypeScript interfaces for all API entities
- **Containerization**: Multi-stage Dockerfile (build + production)

### Infrastructure (Kubernetes)
- **Cluster**: Minikube (single-node local)
- **Packaging**: Helm 3+ charts
- **Secrets**: Kubernetes Secrets (never plaintext in repo)
- **Persistence**: PersistentVolumeClaims for PostgreSQL

## Monorepo Structure

```
Phase-IV/
├── backend/                    # FastAPI service
│   ├── src/
│   │   ├── models/            # SQLModel entities
│   │   ├── api/               # Routes and controllers
│   │   ├── services/          # Business logic (chat_service, tool_service)
│   │   └── tools/             # MCP-style tools for Cohere
│   ├── Dockerfile             # Backend container definition
│   └── requirements.txt
├── frontend/                   # Next.js service
│   ├── src/
│   │   ├── components/        # React components (including chat/)
│   │   ├── hooks/             # Custom hooks (useChat)
│   │   └── types/             # TypeScript definitions
│   ├── Dockerfile             # Frontend container definition
│   └── package.json
├── charts/                     # Helm charts (NEW in Phase IV)
│   ├── todo-frontend/         # Frontend Helm chart
│   ├── todo-backend/          # Backend Helm chart
│   └── postgres/              # PostgreSQL Helm chart
├── scripts/                    # Deployment scripts
│   ├── minikube-setup.sh      # Minikube initialization
│   └── deploy.sh              # Helm deployment
├── specs/                      # Feature specifications
├── docker-compose.yml          # Local dev (non-K8s)
└── .specify/                   # Spec-Kit configuration
```

## AI Provider Rules (CRITICAL)

**MUST use Cohere API exclusively:**
- Import: `import cohere`
- Client: `cohere.Client()` with `COHERE_API_KEY`
- Tool calling: Via Cohere's chat API with `tools` parameter

**FORBIDDEN:**
- `openai` package installation or import
- `OPENAI_API_KEY` environment variable
- Any OpenAI API calls

## Kubernetes Deployment

### Helm Charts
Each chart in `/charts/` must include:
- `Chart.yaml` - Chart metadata
- `values.yaml` - Configurable values
- `templates/deployment.yaml` - Pod specification
- `templates/service.yaml` - Service exposure
- `templates/configmap.yaml` - Non-sensitive config
- `templates/secret.yaml` - Sensitive values (backend only)

### Resource Types
- **Deployments**: Manage pod replicas
- **Services**: ClusterIP (internal), LoadBalancer/NodePort (external)
- **ConfigMaps**: Non-sensitive environment configuration
- **Secrets**: DATABASE_URL, COHERE_API_KEY, BETTER_AUTH_SECRET
- **PersistentVolumeClaims**: PostgreSQL data persistence

### Commands Reference
```bash
# Start Minikube
minikube start

# Build images (use Minikube's Docker daemon)
eval $(minikube docker-env)
docker build -t todo-backend:v4.0.0 ./backend
docker build -t todo-frontend:v4.0.0 ./frontend

# Deploy with Helm
helm install postgres ./charts/postgres
helm install todo-backend ./charts/todo-backend
helm install todo-frontend ./charts/todo-frontend

# Access services
kubectl port-forward svc/todo-frontend 3000:3000
kubectl port-forward svc/todo-backend 8000:8000

# Debugging
kubectl logs -f deployment/todo-backend
kubectl describe pod <pod-name>
kubectl get events --sort-by=.metadata.creationTimestamp
```

## AI DevOps Tools

### Gordon (Docker AI)
```bash
# Generate optimized Dockerfile
docker ai build --optimize ./backend

# Security scan
docker ai scan todo-backend:v4.0.0

# Compose to K8s hints
docker ai convert docker-compose.yml
```

### kubectl-ai
```bash
# Generate manifests from description
kubectl-ai "create deployment for fastapi backend with 2 replicas"

# Debug issues
kubectl-ai "why is my pod crashing?"

# Optimize resources
kubectl-ai "suggest resource limits for todo-backend"
```

### kagent
```bash
# Health check analysis
kagent health todo-backend

# Scaling recommendations
kagent scale --analyze todo-frontend

# Log analysis
kagent logs --diagnose todo-backend
```

## Implementation Notes: Advanced Features

- **Priorities**: `low`, `medium` (default), `high`
- **Tags**: Multi-select tags per task; global tag list stored in relational `Tag` entity
- **Search**: Case-insensitive keyword search on title/description via `q` param
- **Filter**: Intersection (AND) logic for multiple tags and priorities
- **Sorting**: Priority-aware sorting (High > Low) and standard Date/Alpha fields
- **Due Dates**: Optional datetime field with timezone support; displays as relative time
- **Recurring Tasks**: Optional recurrence rule (daily/weekly/monthly/yearly); auto-regenerates on completion
- **AI Chatbot**: Natural language task management via Cohere tool calling
- **MCP Tools**: add_task, list_tasks, complete_task, update_task, delete_task

## Environment Variables

### Required (Kubernetes Secrets)
- `DATABASE_URL` - PostgreSQL connection (local K8s service DNS)
- `COHERE_API_KEY` - Cohere AI API key
- `BETTER_AUTH_SECRET` - JWT signing secret (shared frontend/backend)
- `FRONTEND_URL` - Frontend origin for CORS

### Example K8s Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql://postgres:password@postgres:5432/todo
  COHERE_API_KEY: your-cohere-key
  BETTER_AUTH_SECRET: your-jwt-secret
```

## Testing in Kubernetes

```bash
# Port-forward for local testing
kubectl port-forward svc/todo-backend 8000:8000

# Check pod status
kubectl get pods -l app=todo-backend

# View logs
kubectl logs -f -l app=todo-backend

# Describe for events/errors
kubectl describe deployment todo-backend

# Helm test (if configured)
helm test todo-backend
```

## Constitution Reference

All decisions must align with `.specify/memory/constitution.md` (v4.0.0). Key principles:
- Spec-driven development
- Multi-user security isolation
- Cohere-only AI provider
- Kubernetes-native deployment
- AI-assisted DevOps workflow
