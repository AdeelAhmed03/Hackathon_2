# Claude Code Rules: hackathon-todo (Phase V)

This file contains specific instructions for Claude when working on the Full-Stack Todo application. Adhere to the Phase V - Event-Driven Architecture with Dapr, Kafka, and Cloud Kubernetes Deployment.

## Project Context

The Todo application is an event-driven, cloud-native full-stack web application with:
- **Backend**: FastAPI with Cohere AI integration for chatbot functionality + Dapr sidecar
- **Frontend**: Next.js 16+ App Router with ChatKit UI
- **Microservices**: notification-service, recurring-service (event consumers)
- **Database**: PostgreSQL via Helm (local or cloud Kubernetes)
- **Event Streaming**: Kafka (Strimzi local / Redpanda Cloud production) via Dapr Pub/Sub
- **Scheduling**: Dapr Jobs API for exact-time reminders
- **Deployment**: Minikube (local) + Azure AKS Free Tier (cloud)
- **CI/CD**: GitHub Actions for automated build, test, and deployment
- **AI DevOps**: Gordon, kubectl-ai, and kagent for intelligent infrastructure management

## Code Standards

### Backend (Python)
- **Framework**: FastAPI with SQLModel (SQLAlchemy 2.0 based)
- **AI Provider**: Cohere Python SDK (NOT OpenAI)
- **Validation**: Pydantic v2 schemas
- **Style**: PEP 8 compliance, mandatory type hints (Python 3.13+)
- **Security**: Data isolation per `user_id` is mandatory for all queries and events
- **Containerization**: Production-optimized Dockerfile with multi-stage builds
- **Dapr Integration**: Use httpx for Dapr HTTP API calls (NOT direct kafka-python)

### Frontend (TypeScript)
- **Framework**: Next.js 16+ (App Router)
- **Styling**: Tailwind CSS
- **Auth**: Better Auth (JWT-based bridge to backend)
- **Types**: Mandatory TypeScript interfaces for all API entities
- **Containerization**: Multi-stage Dockerfile (build + production)

### Infrastructure (Kubernetes + Dapr)
- **Cluster**: Minikube (local) or Azure AKS Free Tier (cloud)
- **Packaging**: Helm 3+ charts with Dapr sidecar annotations
- **Secrets**: Dapr Secrets API (kubernetes-secrets component)
- **Persistence**: PersistentVolumeClaims for PostgreSQL
- **Event Streaming**: Dapr Pub/Sub with Kafka/Redpanda backend

## Monorepo Structure

```
Phase-V/
├── backend/                        # FastAPI main service
│   ├── src/
│   │   ├── models/                # SQLModel entities (Task, Tag, TaskTag)
│   │   ├── api/                   # Routes and controllers
│   │   │   ├── tasks.py          # Enhanced with search/filter/sort
│   │   │   ├── tags.py           # Tag management endpoints
│   │   │   ├── dapr_subscriptions.py  # Dapr Pub/Sub handlers
│   │   │   └── jobs_callback.py  # Dapr Jobs API callback
│   │   ├── services/             # Business logic
│   │   │   ├── event_publisher.py # Dapr Pub/Sub publisher
│   │   │   ├── job_scheduler.py  # Dapr Jobs API scheduler
│   │   │   └── chat_service.py   # Cohere integration
│   │   └── tools/                # MCP-style tools for Cohere
│   ├── migrations/               # Alembic migrations
│   ├── Dockerfile
│   └── requirements.txt
├── notification-service/          # NEW: Reminder consumer
│   ├── src/
│   │   ├── main.py               # FastAPI + Dapr subscription
│   │   └── handlers/             # Event handlers
│   ├── Dockerfile
│   └── requirements.txt
├── recurring-service/             # NEW: Recurring task spawner
│   ├── src/
│   │   ├── main.py               # FastAPI + Dapr subscription
│   │   └── handlers/             # Event handlers
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                      # Next.js service
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── tasks/           # TaskForm, TaskFilters, TagSelector
│   │   │   └── chat/            # Chat UI components
│   │   ├── hooks/               # Custom hooks
│   │   └── types/               # TypeScript definitions
│   ├── Dockerfile
│   └── package.json
├── dapr-components/               # NEW: Dapr component definitions
│   ├── kafka-pubsub.yaml         # Kafka Pub/Sub component
│   ├── kafka-pubsub-local.yaml   # Local Strimzi config
│   ├── kafka-pubsub-cloud.yaml   # Redpanda Cloud config
│   ├── kubernetes-secrets.yaml   # Secrets component
│   └── strimzi/
│       └── kafka-cluster.yaml    # Strimzi KafkaCluster CR
├── charts/                        # Helm charts
│   ├── todo-frontend/            # Updated with Dapr annotations
│   ├── todo-backend/             # Updated with Dapr annotations
│   ├── notification-service/     # NEW
│   ├── recurring-service/        # NEW
│   └── postgres/
├── .github/workflows/             # NEW: CI/CD pipelines
│   ├── ci.yaml                   # Build and test
│   └── deploy.yaml               # Deploy to staging/production
├── scripts/
│   ├── minikube-setup.sh         # Updated with Dapr + Strimzi
│   ├── deploy-local.sh           # Local deployment
│   └── deploy-cloud.sh           # Cloud deployment
├── specs/                         # Feature specifications
├── docker-compose.yml             # Local dev (Phase IV compatibility)
└── .specify/                      # Spec-Kit configuration
```

## AI Provider Rules (CRITICAL)

**MUST use Cohere API exclusively:**
- Import: `import cohere`
- Client: `cohere.Client()` with `COHERE_API_KEY` (via Dapr Secrets)
- Tool calling: Structured JSON prompt with command-r-plus model

**FORBIDDEN:**
- `openai` package installation or import
- `OPENAI_API_KEY` environment variable
- Any OpenAI API calls

## Dapr Integration Patterns

### Publishing Events
```python
import httpx

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

async def publish_event(topic: str, event: dict):
    """Publish event to Kafka via Dapr Pub/Sub."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=event)
        response.raise_for_status()
```

### Subscribing to Events
```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription discovery endpoint."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        }
    ]

@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """Handle task events from Kafka."""
    event = await request.json()
    # Process event
    return {"status": "SUCCESS"}
```

### Scheduling Jobs (Reminders)
```python
async def schedule_reminder(task_id: str, user_id: str, remind_at: datetime):
    """Schedule reminder via Dapr Jobs API."""
    job_name = f"reminder-{task_id}"
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}"
    payload = {
        "dueTime": remind_at.isoformat(),
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "reminder_message": "Task due soon"
        }
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
```

### Retrieving Secrets
```python
async def get_secret(secret_name: str, key: str) -> str:
    """Retrieve secret via Dapr Secrets API."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/secrets/kubernetes-secrets/{secret_name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return data[key]
```

## Kafka Topics and Events

### Topics
- **task-events**: CRUD operations (task_created, task_updated, task_completed, task_deleted)
- **reminders**: Due date notifications (reminder_due)
- **task-updates**: Real-time sync (future)

### Event Schema
```json
{
  "event_type": "task_created | task_updated | task_completed | task_deleted",
  "task_id": "uuid",
  "task_data": {
    "title": "string",
    "priority": "low | medium | high",
    "tags": ["string"],
    "due_at": "ISO8601",
    "recurring_interval": "daily | weekly | monthly | yearly | null"
  },
  "user_id": "uuid",
  "timestamp": "ISO8601"
}
```

## Kubernetes Deployment

### Helm Charts with Dapr
Each chart must include Dapr sidecar annotations:
```yaml
# templates/deployment.yaml
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
```

### Local Deployment (Minikube + Strimzi)
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Install Dapr
dapr init -k --wait

# Install Strimzi Kafka
kubectl create namespace kafka
kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka
kubectl apply -f dapr-components/strimzi/kafka-cluster.yaml -n kafka

# Apply Dapr components
kubectl apply -f dapr-components/kafka-pubsub-local.yaml
kubectl apply -f dapr-components/kubernetes-secrets.yaml

# Deploy services
helm install postgres ./charts/postgres
helm install todo-backend ./charts/todo-backend
helm install notification-service ./charts/notification-service
helm install recurring-service ./charts/recurring-service
helm install todo-frontend ./charts/todo-frontend
```

### Cloud Deployment (Oracle OKE + Redpanda Cloud)
```bash
# Configure kubectl for OKE
oci ce cluster create-kubeconfig --cluster-id <ocid> --file ~/.kube/config-oke
export KUBECONFIG=~/.kube/config-oke

# Install Dapr
helm repo add dapr https://dapr.github.io/helm-charts/
helm install dapr dapr/dapr --namespace dapr-system --create-namespace

# Create secrets for Redpanda Cloud
kubectl create secret generic redpanda-secrets \
  --from-literal=sasl-password="your-password"

# Apply Dapr components (cloud config)
kubectl apply -f dapr-components/kafka-pubsub-cloud.yaml
kubectl apply -f dapr-components/kubernetes-secrets.yaml

# Deploy services
helm install postgres ./charts/postgres
helm install todo-backend ./charts/todo-backend
helm install notification-service ./charts/notification-service
helm install recurring-service ./charts/recurring-service
helm install todo-frontend ./charts/todo-frontend
```

## CI/CD with GitHub Actions

### Workflow Triggers
- **Push to develop**: Deploy to staging
- **Push to main**: Deploy to production (with approval gate)
- **Pull request**: Run tests and Helm lint

### Required GitHub Secrets
- `KUBECONFIG_STAGING`: Base64-encoded kubeconfig for staging
- `KUBECONFIG_PRODUCTION`: Base64-encoded kubeconfig for production
- `COHERE_API_KEY`: Cohere API key
- `BETTER_AUTH_SECRET`: JWT signing secret

## Implementation Notes: Advanced Features

### Task Model Enhancements
- **priority**: `low`, `medium` (default), `high`
- **tags**: Multi-select via Tag entity and TaskTag junction table
- **due_at**: Nullable datetime (UTC), displays as relative time
- **remind_at**: Nullable datetime (UTC), triggers Dapr Jobs API
- **recurring_interval**: `daily`, `weekly`, `monthly`, `yearly` (nullable)

### Search, Filter, Sort
- **Search**: Case-insensitive keyword search on title/description via `q` param
- **Filter**: Intersection (AND) logic for tags; single-value for priority/status
- **Sort**: `sort_by` (created_at, due_at, priority, title) + `sort_order` (asc, desc)

### Recurring Tasks
- On completion, backend publishes `task_completed` event
- recurring-service consumes event, checks `recurring_interval`
- If recurring, creates new task with `due_at += interval`

### Reminders
- On task create/update with `remind_at`, schedule Dapr Job
- At `remind_at`, Dapr triggers `/jobs/callback`
- Backend publishes `reminder_due` event to `reminders` topic
- notification-service sends email/push notification

## Environment Variables

### Required (via Dapr Secrets)
- `DATABASE_URL` - PostgreSQL connection string
- `COHERE_API_KEY` - Cohere AI API key
- `BETTER_AUTH_SECRET` - JWT signing secret
- `FRONTEND_URL` - Frontend origin for CORS

### Kafka/Redpanda (in Dapr component)
- `KAFKA_BOOTSTRAP_SERVERS` - Broker addresses
- `KAFKA_SASL_USERNAME` - SASL username (cloud only)
- `KAFKA_SASL_PASSWORD` - SASL password (cloud only)

### Dapr (automatic)
- `DAPR_HTTP_PORT` - Sidecar HTTP port (default: 3500)
- `DAPR_GRPC_PORT` - Sidecar gRPC port (default: 50001)

## Monitoring and Observability

### Dapr Tracing (Zipkin)
```bash
# View traces
kubectl port-forward svc/zipkin 9411:9411 -n dapr-system
# Open http://localhost:9411
```

### Dapr Metrics (Prometheus)
```bash
# Metrics endpoint
curl http://localhost:9090/metrics
```

### Application Logs
```bash
# Backend logs
kubectl logs -f -l app=todo-backend -c todo-backend

# Dapr sidecar logs
kubectl logs -f -l app=todo-backend -c daprd

# Event consumer logs
kubectl logs -f -l app=notification-service
kubectl logs -f -l app=recurring-service
```

## Constitution Reference

All decisions must align with `.specify/memory/constitution.md` (v5.0.0). Key principles:
- Spec-driven development
- Multi-user security isolation (user_id in all queries AND events)
- Cohere-only AI provider
- Event-driven architecture with Dapr abstraction
- Kubernetes-native deployment (local + cloud)
- CI/CD automation with GitHub Actions
