# Full-Stack Todo Application with AI Chatbot (Phase V)

A modern, cloud-native, event-driven full-stack todo application built with FastAPI backend and Next.js 16 frontend, featuring JWT authentication, SQLModel ORM, Better Auth integration, **AI-powered natural language task management**, **event-driven microservices architecture with Dapr**, and **Azure AKS cloud deployment**.

## Phase V: Event-Driven Cloud Architecture

This phase transforms the application into a cloud-native, event-driven system:

- **Event Streaming**: Kafka via Dapr Pub/Sub (Strimzi local / Redpanda Cloud production)
- **Microservices**: notification-service, recurring-service as event consumers
- **Exact-Time Reminders**: Dapr Jobs API for precise reminder scheduling
- **Cloud Deployment**: Azure AKS Free Tier with GitHub Actions CI/CD
- **Distributed Tracing**: Zipkin integration for observability
- **Advanced Features**: Priorities, tags, search, filter, sort, recurring tasks

## Features

### Core Features
- **User Authentication**: Secure JWT-based authentication with Better Auth
- **Task Management**: Complete CRUD operations for todo tasks
- **Multi-User Support**: Each user has isolated data with proper security
- **Modern Tech Stack**: FastAPI, Next.js 16, SQLModel, PostgreSQL

### AI Chatbot Features
- **Natural Language Processing**: Manage tasks using conversational language
- **Floating Chat Widget**: Always-accessible chat interface on every page
- **Intent Recognition**: Automatically understands user commands
- **Multi-Tool Execution**: Performs complex operations in a single request
- **Conversation History**: Maintains context across chat sessions

### Advanced Todo Features (Phase V)
- **Priorities**: Low, Medium, High priority levels with sorting
- **Tags**: Multi-select tagging with AND intersection filtering
- **Search**: Case-insensitive keyword search on title/description
- **Filtering**: Combined filters (status, priority, tags, due dates)
- **Due Dates**: Timezone-aware datetime with relative display
- **Reminders**: Exact-time notifications via Dapr Jobs API
- **Recurring Tasks**: Daily, weekly, monthly, yearly auto-spawn on completion
- **Pagination**: Server-side pagination with total counts
- **Multi-Field Sorting**: Sort by multiple fields with NULLS LAST

### Event-Driven Features (Phase V)
- **Task Events**: Published to Kafka on create/update/complete/delete
- **Recurring Service**: Consumes task_completed events, spawns next instances
- **Notification Service**: Consumes reminder_due events, sends notifications
- **Real-Time Updates**: Task-updates topic for cross-device sync

### Cloud Deployment Features
- **Azure AKS**: Free tier Kubernetes cluster
- **Dapr Sidecars**: Service mesh for pub/sub, secrets, and jobs
- **Helm Charts**: Declarative deployment for all services
- **GitHub Actions**: CI/CD pipeline with staging/production environments
- **Zipkin Tracing**: Distributed tracing for debugging

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLModel**: SQLAlchemy-based ORM with Pydantic integration
- **Cohere AI**: Large Language Model for natural language processing
- **Better Auth**: Authentication and authorization
- **PostgreSQL**: Database via Helm chart
- **Dapr**: Service mesh for pub/sub, secrets, jobs

### Frontend
- **Next.js 16**: React framework with App Router
- **TailwindCSS**: Utility-first CSS framework
- **TypeScript**: Type-safe development
- **Better Auth**: Client-side authentication

### Microservices
- **notification-service**: FastAPI service consuming reminders topic
- **recurring-service**: FastAPI service consuming task-events topic

### Infrastructure
- **Docker**: Container runtime
- **Minikube**: Local Kubernetes cluster
- **Azure AKS**: Cloud Kubernetes (Free Tier)
- **Helm 3+**: Kubernetes package manager
- **Dapr**: Distributed application runtime
- **Strimzi**: Kafka operator for local development
- **Redpanda Cloud**: Managed Kafka for production
- **GitHub Actions**: CI/CD automation

## Project Structure

```
Phase-V/
├── backend/                          # FastAPI main service
│   ├── src/
│   │   ├── models/                  # SQLModel entities
│   │   ├── services/               # Business logic + event publishing
│   │   ├── tools/                  # MCP-style AI tools
│   │   ├── api/                   # API endpoints + Dapr handlers
│   │   └── database/             # Database configuration
│   └── Dockerfile
├── frontend/                        # Next.js frontend
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   ├── components/           # React components
│   │   │   └── tasks/           # TaskFilters, TagSelector
│   │   ├── hooks/               # useTasks, useRealTimeUpdates
│   │   └── types/              # TypeScript definitions
│   └── Dockerfile
├── notification-service/            # Reminder consumer microservice
│   ├── src/
│   │   ├── main.py              # FastAPI + Dapr subscription
│   │   ├── handlers/           # Event handlers
│   │   └── services/          # Email/push senders
│   └── Dockerfile
├── recurring-service/               # Recurring task spawner
│   ├── src/
│   │   ├── main.py              # FastAPI + Dapr subscription
│   │   ├── handlers/           # Task completion handler
│   │   └── services/          # Task spawner with idempotency
│   └── Dockerfile
├── dapr-components/                 # Dapr configuration
│   ├── kafka-pubsub-local.yaml    # Strimzi config
│   ├── kafka-pubsub-cloud.yaml    # Redpanda Cloud config
│   ├── kubernetes-secrets.yaml    # K8s secrets store
│   ├── dapr-config.yaml          # Zipkin tracing
│   └── strimzi/
│       └── kafka-cluster.yaml    # KRaft mode Kafka
├── charts/                          # Helm charts
│   ├── todo-frontend/
│   ├── todo-backend/
│   ├── notification-service/
│   ├── recurring-service/
│   └── postgres/
├── .github/workflows/               # CI/CD pipelines
│   ├── ci.yaml                    # Build and test
│   └── deploy.yaml               # Deploy to AKS
├── scripts/
│   ├── minikube-setup.sh         # Local cluster + Dapr + Strimzi
│   ├── deploy-local.sh          # Local Helm deployment
│   └── deploy-cloud.sh         # Azure AKS deployment
└── specs/                          # Feature specifications
```

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 22+
- Docker Desktop
- Minikube (local) or Azure CLI (cloud)
- Helm 3+
- kubectl
- Dapr CLI
- Cohere API Key ([Get one free](https://dashboard.cohere.com/))

### Option 1: Local Development (Minikube + Dapr + Strimzi)

Full event-driven architecture locally.

#### Step 1: Setup Minikube with Dapr and Kafka

```bash
# Run the setup script (installs Dapr, Strimzi, Kafka)
./scripts/minikube-setup.sh

# This will:
# - Start Minikube with 4 CPUs, 8GB RAM
# - Install Dapr on Kubernetes
# - Install Strimzi Kafka Operator
# - Deploy Kafka cluster (KRaft mode)
# - Apply Dapr components
# - Install Zipkin for tracing
```

#### Step 2: Build and Deploy

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build and deploy all services
./scripts/deploy-local.sh all

# Or step by step:
./scripts/deploy-local.sh build    # Build images
./scripts/deploy-local.sh deploy   # Deploy via Helm
./scripts/deploy-local.sh verify   # Check status
```

#### Step 3: Access Services

```bash
# Frontend
kubectl port-forward svc/todo-frontend 3000:3000

# Backend API
kubectl port-forward svc/todo-backend 8000:8000

# Zipkin Tracing
kubectl port-forward svc/zipkin 9411:9411 -n dapr-system
```

### Option 2: Cloud Deployment (Azure AKS)

Production deployment on Azure Free Tier.

#### Step 1: Setup Azure AKS

```bash
# Set required environment variables
export COHERE_API_KEY=your-cohere-api-key
export REDPANDA_SASL_PASSWORD=your-redpanda-password

# Run full setup (creates AKS cluster, installs Dapr)
./scripts/deploy-cloud.sh setup
```

#### Step 2: Deploy Services

```bash
# Deploy all services
./scripts/deploy-cloud.sh deploy

# Verify deployment
./scripts/deploy-cloud.sh verify
```

#### Step 3: Get External IPs

```bash
kubectl get svc -n production
# Note the LoadBalancer external IPs for frontend and backend
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COHERE_API_KEY` | Cohere API key for AI chatbot | Yes |
| `BETTER_AUTH_SECRET` | JWT signing secret (auto-generated if not set) | No |
| `DATABASE_URL` | PostgreSQL connection URL | No (uses in-cluster) |
| `REDPANDA_SASL_PASSWORD` | Redpanda Cloud SASL password | Yes (cloud only) |
| `AKS_RESOURCE_GROUP` | Azure resource group name | No (default: todo-app-rg) |
| `AKS_CLUSTER_NAME` | Azure AKS cluster name | No (default: todo-aks-cluster) |

## Event-Driven Architecture

### Kafka Topics

| Topic | Publisher | Consumer | Purpose |
|-------|-----------|----------|---------|
| `task-events` | Backend | recurring-service | Task CRUD events |
| `reminders` | Backend (via Jobs API) | notification-service | Reminder notifications |
| `task-updates` | Backend | Frontend (polling) | Real-time sync |

### Event Flow

```
User Action → Backend API → Dapr Pub/Sub → Kafka → Consumer Services

Example: Complete Recurring Task
1. User completes task via API
2. Backend publishes task_completed event to task-events topic
3. recurring-service consumes event
4. recurring-service creates next task instance
5. New task appears in user's list
```

### Reminder Flow

```
1. User creates task with remind_at
2. Backend schedules Dapr Job for remind_at time
3. At remind_at, Dapr triggers /jobs/callback
4. Backend publishes reminder_due to reminders topic
5. notification-service sends email/push notification
```

## CI/CD Pipeline

### Triggers

- **Push to develop**: Deploy to staging namespace
- **Push to main**: Deploy to production namespace (with approval)
- **Pull Request**: Run tests and Helm lint

### GitHub Secrets Required

```
AZURE_CREDENTIALS    # Azure service principal JSON
COHERE_API_KEY       # Cohere API key
```

### Creating Azure Credentials

```bash
# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/todo-app-rg \
  --sdk-auth

# Copy the JSON output to GitHub Secrets as AZURE_CREDENTIALS
```

## API Endpoints

### Tasks API

```
GET    /api/v1/tasks              # List with search, filter, sort, pagination
POST   /api/v1/tasks              # Create task (with tags, reminder)
GET    /api/v1/tasks/:id          # Get single task
PUT    /api/v1/tasks/:id          # Update task
DELETE /api/v1/tasks/:id          # Delete task
PATCH  /api/v1/tasks/:id/complete # Complete task (triggers events)
```

### Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search keyword |
| `status` | enum | pending, in_progress, completed |
| `priority` | enum | low, medium, high |
| `tags` | int[] | Tag IDs (AND filter) |
| `due_before` | datetime | Due date upper bound |
| `due_after` | datetime | Due date lower bound |
| `sort_by` | string | Field(s) to sort by |
| `sort_order` | string | asc or desc |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

### Tags API

```
GET    /api/v1/tags               # List user's tags
POST   /api/v1/tags               # Create tag
DELETE /api/v1/tags/:id           # Delete tag
```

### Dapr Endpoints

```
GET  /dapr/subscribe              # Subscription discovery
POST /events/task-updates         # Task update handler
POST /jobs/callback               # Jobs API callback
```

## Monitoring

### Zipkin Tracing

```bash
kubectl port-forward svc/zipkin 9411:9411 -n dapr-system
# Open http://localhost:9411
```

### View Logs

```bash
# Backend logs
kubectl logs -f -l app.kubernetes.io/name=todo-backend -c todo-backend

# Dapr sidecar logs
kubectl logs -f -l app.kubernetes.io/name=todo-backend -c daprd

# Event consumer logs
kubectl logs -f -l app.kubernetes.io/name=notification-service
kubectl logs -f -l app.kubernetes.io/name=recurring-service
```

### Dapr Dashboard

```bash
dapr dashboard -k
# Open http://localhost:8080
```

## Cleanup

### Local (Minikube)

```bash
./scripts/deploy-local.sh cleanup
minikube delete
```

### Cloud (Azure AKS)

```bash
./scripts/deploy-cloud.sh cleanup
# Or delete entire resource group:
az group delete --name todo-app-rg --yes --no-wait
```

## Azure Free Tier Limits

- **AKS Control Plane**: Always free
- **B-series VMs**: 750 hours/month free
- **Managed Disks**: 64GB free
- **Bandwidth**: 15GB outbound free

The default configuration uses 2x Standard_B2s nodes, which fits within free tier limits for moderate usage.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.
