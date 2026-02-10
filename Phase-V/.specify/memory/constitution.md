<!-- SYNC IMPACT REPORT:
Version change: 4.0.0 → 5.0.0
Modified principles:
- V. Persistent Storage with SQLModel → expanded for advanced features (due_at, remind_at, recurring_interval, priority, tags)
- VII. Monorepo Structure and Code Organization → added /dapr-components and new services (notification/recurring/audit)
- IX. Backend Technology Standards → enhanced with Dapr integration, event-driven patterns
- X. Development Workflow → CI/CD with GitHub Actions, cloud deployment workflows
- XIV. Environment Variables and Secrets → Dapr Secrets API, Redpanda/cloud provider credentials
- XVI. Kubernetes Architecture → cloud providers (Oracle OKE, Azure AKS, GKE)
- XVII. Helm Charts Architecture → Dapr annotations and sidecars
Added sections:
- XX. Event-Driven Architecture (Kafka/Redpanda + Dapr)
- XXI. Dapr Building Blocks and Components
- XXII. Advanced Task Features (Recurring, Due Dates, Priorities, Tags, Search/Filter/Sort)
- XXIII. Service Architecture (Backend, Notification, Recurring, Audit)
- XXIV. Kafka Topics and Schemas
- XXV. Dapr Jobs API (Scheduling and Reminders)
- XXVI. Cloud Kubernetes Deployment (Oracle OKE, Azure AKS, GKE)
- XXVII. CI/CD with GitHub Actions
- XXVIII. Monitoring and Observability (Dapr Zipkin, Prometheus, K8s Dashboard)
- XXIX. Migration Path from Phase IV to Phase V
- "Differences from Phase IV" section with Phase V migration guidance
- Phase V comparison column in evolution table
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated (no changes needed - generic enough)
- .specify/templates/spec-template.md ✅ updated (no changes needed - generic enough)
- .specify/templates/tasks-template.md ✅ updated (no changes needed - generic enough)
- CLAUDE.md ✅ requires update (Phase V context with Dapr/Kafka/cloud guidance)
- backend/CLAUDE.md ✅ requires update (Dapr integration patterns, event publishing)
- README.md ✅ requires update (Redpanda Cloud signup, Oracle OKE setup, CI/CD instructions)
Follow-up TODOs:
- Create dapr-components/ directory with component YAML files
- Create notification-service/ and recurring-service/ directories
- Update charts/ with Dapr annotations and configurations
- Create .github/workflows/ CI/CD pipeline
- Create migration scripts for new database fields
- Update API documentation with advanced features
-->

# Todo Application Constitution (Phase V)

> **SINGLE SOURCE OF TRUTH**: This constitution is the authoritative document for ALL Phase IV architectural decisions, technology choices, and implementation constraints. When in doubt, defer to this document. Any conflicting guidance in other files MUST be reconciled with this constitution.

## Project Identity

**Project Name**: hackathon-todo
**Architecture**: Event-Driven Full-Stack Web Application with AI Chatbot, Cloud-Native Deployment (Monorepo)
**Phase**: V - Event-Driven Architecture with Dapr, Kafka, and Cloud Kubernetes Deployment

## Core Principles

### I. Spec-Driven Development
All development MUST follow the Spec-Kit Plus methodology. No manual coding outside of Claude Code agent. Every feature begins with a specification document in `/specs/`. The spec-driven workflow enforces: feature specification → clarification → implementation plan → task breakdown → implementation → validation. This ensures architectural consistency and traceable requirements.

### II. Clean Code and Type Safety
All code MUST follow language-specific style guidelines with mandatory type hints. TypeScript on frontend, Python with type hints on backend. Code MUST be modular, well-documented, and maintainable. Every function MUST have clear purpose, defined inputs/outputs, and be easily testable. No any types or untyped code.

### III. Multi-User Security and Isolation
Every user MUST see and modify only their own tasks. User data isolation is NON-NEGOTIABLE and MUST be enforced at the database query level. All operations MUST be filtered by authenticated user ID. There are no exceptions to user data isolation - any implementation that allows cross-user access is a critical security defect. This applies to BOTH REST API endpoints AND chatbot tool calls.

### IV. Authentication and Authorization
JWT-based authentication bridges Next.js (Better Auth) and FastAPI backend. The BETTER_AUTH_SECRET environment variable MUST be shared between frontend and backend for JWT verification. All API endpoints (including chat endpoint) MUST verify JWT tokens and reject requests without valid authentication. Better Auth handles frontend session management; backend verifies tokens on every request. In Kubernetes, secrets MUST be managed via Kubernetes Secrets or Helm values.

### V. Persistent Storage with SQLModel
All task data MUST be stored in PostgreSQL using SQLModel. PostgreSQL runs via Helm chart (local Minikube or cloud Kubernetes). Database models MUST define proper relationships between users and tasks. Migrations MUST be versioned and applied automatically on startup. Foreign key constraints enforce referential integrity. Conversation and Message tables persist chat history.

**Phase V Schema Additions:**
- Task table MUST include: `due_at` (nullable datetime), `remind_at` (nullable datetime), `recurring_interval` (nullable enum: daily/weekly/monthly/yearly), `priority` (enum: low/medium/high, default medium), `tags` (relationship to Tag entity)
- Tag table: id, name, user_id (multi-user tag isolation)
- TaskTag junction table: task_id, tag_id (many-to-many relationship)
- All datetime fields MUST be timezone-aware (UTC storage, local display)
- Recurring tasks MUST store original task ID for regeneration tracking

### VI. RESTful API Design
All backend endpoints MUST follow RESTful conventions. Proper HTTP methods (GET, POST, PUT, DELETE), status codes, and error responses. API contracts MUST be documented and validated. Request/response validation using Pydantic models. Consistent error handling across all endpoints. The chat endpoint follows POST semantics for message submission.

### VII. Monorepo Structure and Code Organization
The project MUST maintain a clear monorepo structure:
- `/frontend` - Next.js application with ChatKit UI
- `/backend` - FastAPI application (main CRUD + chat endpoint + Cohere integration)
- `/notification-service` - FastAPI microservice (Dapr consumer for reminders topic, sends notifications) (NEW in Phase V)
- `/recurring-service` - FastAPI microservice (Dapr consumer for task-events topic, handles recurring task regeneration) (NEW in Phase V)
- `/audit-service` - Optional FastAPI microservice (Dapr consumer for task-events topic, audit logging) (NEW in Phase V)
- `/charts` - Helm charts for Kubernetes deployment
  - `/charts/todo-frontend` - Frontend Helm chart (with Dapr sidecar annotations)
  - `/charts/todo-backend` - Backend Helm chart (with Dapr sidecar annotations)
  - `/charts/notification-service` - Notification service Helm chart (NEW in Phase V)
  - `/charts/recurring-service` - Recurring service Helm chart (NEW in Phase V)
  - `/charts/postgres` - PostgreSQL Helm chart (or dependency on bitnami/postgresql)
  - `/charts/dapr` - Dapr installation via helm repo add dapr/dapr (optional if using dapr init -k)
- `/dapr-components` - Dapr component YAML definitions (NEW in Phase V)
  - `kafka-pubsub.yaml` - Kafka/Redpanda Pub/Sub component
  - `statestore-postgresql.yaml` - PostgreSQL state store component (for Dapr state API)
  - `dapr-jobs.yaml` - Dapr Jobs API component configuration
  - `kubernetes-secrets.yaml` - Dapr Kubernetes Secrets component
  - `strimzi-kafka-cluster.yaml` - Strimzi KafkaCluster CR for local deployment (optional)
- `/specs` - Feature specifications and design documents
- `/shared` - Shared types and utilities (if needed)
- `/.github/workflows` - GitHub Actions CI/CD workflows (NEW in Phase V)
- `/scripts` - Deployment and setup scripts (minikube-setup.sh, deploy.sh, cloud-deploy.sh)
- `docker-compose.yml` - Retained for local non-Kubernetes development (Phase IV compatibility)
- Separate CLAUDE.md files at root, `/frontend`, `/backend`, and `/notification-service`, `/recurring-service` for domain-specific guidance.

### VIII. Frontend Technology Standards
Frontend MUST use:
- Next.js 16+ with App Router
- TypeScript throughout
- Tailwind CSS for styling
- Better Auth for authentication
- OpenAI ChatKit (or equivalent) for chat UI component
- React Server Components where appropriate
Client-side MUST handle auth state and provide smooth user experience for both task management and conversational interfaces.

### IX. Backend Technology Standards
Backend MUST use:
- FastAPI with SQLModel
- Python with full type coverage (3.13+)
- PostgreSQL (via Helm, local Minikube or cloud Kubernetes)
- JWT verification middleware
- Proper CORS configuration for frontend communication
- Environment-based configuration for all secrets (via Dapr Secrets API in Phase V, fallback to Kubernetes Secrets)
- **Cohere Python SDK** for AI capabilities (NOT OpenAI)
- Tool calling via Cohere's chat API with tool_use support
- **Dapr HTTP API** for Pub/Sub, State, Jobs, Service Invocation (NEW in Phase V)
- Event publishing via Dapr Pub/Sub API (`POST http://localhost:3500/v1.0/publish/<pubsub-name>/<topic>`)
- State management via Dapr State API (`POST http://localhost:3500/v1.0/state/<statestore-name>`) for conversation persistence (optional alternative to direct DB)
- Job scheduling via Dapr Jobs API (`POST http://localhost:3500/v1.0-alpha1/jobs/<job-name>` with `dueTime`)
- **NO direct kafka-python dependency** unless explicitly required as fallback; prefer Dapr abstraction

### X. Development Workflow
- Follow spec-driven development: **spec → clarify → plan → tasks → agent implementation prompts**
- No manual coding outside of Claude Code agent prompts
- All code MUST pass type checking (mypy/TypeScript compiler) and linting
- Pull requests require code review and passing tests
- Contract tests for API endpoints (backend testing frontend contracts)
- Integration tests for user journeys (including chatbot flows, event-driven flows)
- Docker Compose for local development environment (non-K8s, Phase IV compatibility)
- **AI-Assisted DevOps**: Use Gordon (Docker AI), kubectl-ai, and kagent for intelligent infrastructure management
- **CI/CD Pipeline**: GitHub Actions workflows for automated build, test, and deployment (NEW in Phase V)
  - On push to main: Build Docker images, push to registry (Docker Hub, GitHub Container Registry, or cloud provider registry)
  - Automated Helm deployment to staging/production environments
  - Helm lint and dry-run validation before deployment
  - Rollback capabilities via Helm history
- **Cloud Deployment**: Support Minikube (local) + Oracle OKE (preferred free tier) or Azure AKS/GKE (fallback) (NEW in Phase V)

### XI. AI Chatbot Integration (Cohere-Powered)
The AI chatbot MUST be integrated into the SAME existing FastAPI backend. No separate microservice or new repository.

**Non-Negotiable AI Provider Rules:**
- MUST use Cohere API exclusively (via `cohere` Python SDK)
- MUST NOT use OpenAI API keys or OpenAI models anywhere in the project
- MUST NOT install or import the `openai` Python package
- MUST use `cohere.Client()` with `COHERE_API_KEY` environment variable
- MUST implement agent-like behavior using Cohere's tool calling + multi-turn chat capabilities

**Rationale for Cohere:**
- Native tool calling support in chat API
- Cost-effective for conversational AI
- Excellent multi-turn conversation handling
- No dependency on OpenAI ecosystem

### XII. Conversation Persistence and State Management
The chatbot architecture MUST support stateless server-side operation with optional Dapr State API.

**State Management Rules (Phase V):**
- Conversation state lives in PostgreSQL database (Conversation + Message tables) OR Dapr State Store (optional)
- Each chat request MUST load conversation history from database or Dapr State API
- Each response MUST persist the new messages to database or Dapr State API
- Dapr State API provides transactional state management and TTL support
- No in-memory conversation caching between requests (stateless pods)
- Conversation MUST be scoped to authenticated user (user_id foreign key or state key prefix)

**Database Schema (Retained from Phase IV):**
- `Conversation` table: id, user_id, created_at, updated_at, title (optional)
- `Message` table: id, conversation_id, role (user/assistant/tool), content, tool_calls (JSON), created_at

**Dapr State Alternative (Optional):**
- State key format: `conversations/{user_id}/{conversation_id}`
- State value: JSON with message history
- TTL support for conversation expiration
- Transactional operations for consistency

### XIII. MCP Tools Architecture
Task operations MUST be exposed as MCP-style tools callable by the Cohere chat agent.

**Required Tools (Phase V Enhanced):**
- `add_task` - Create a new task with priority, tags, due_date, recurring_interval (publishes task-created event)
- `list_tasks` - List tasks with filters (priority, tags, status, search keyword, sort by priority/due_date/created_at)
- `complete_task` - Mark task completed (publishes task-completed event; recurring-service handles regeneration)
- `delete_task` - Delete a task (publishes task-deleted event)
- `update_task` - Update task properties (title, description, priority, tags, due_date, recurring_interval) (publishes task-updated event)
- `search_tasks` - Full-text search on title/description with case-insensitive keyword matching
- `filter_tasks_by_tags` - Intersection (AND) logic for multiple tag filters
- `get_task_reminders` - List upcoming reminders for user

**Tool Security Rules:**
- Every tool MUST receive `user_id` from the authenticated JWT (NOT from user input)
- Every database query within tools MUST filter by `user_id`
- Tools MUST NOT allow cross-user access under any circumstances
- Tool responses MUST be sanitized before returning to the chat model

**Event Publishing (NEW in Phase V):**
- All mutating tools (add/update/complete/delete) MUST publish events to `task-events` topic via Dapr Pub/Sub
- Event payload: `{"event_type": "task_created|task_updated|task_completed|task_deleted", "task_id": "...", "task_data": {...}, "user_id": "...", "timestamp": "..."}`
- Events enable audit logging, recurring task regeneration, and real-time sync

### XIV. Environment Variables and Secrets (Phase V)

**Core Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string (local or cloud Kubernetes)
- `COHERE_API_KEY` - API key for Cohere AI services (REQUIRED) (managed via Dapr Secrets)
- `BETTER_AUTH_SECRET` - Shared secret for JWT verification (managed via Dapr Secrets)
- `FRONTEND_URL` - Frontend origin for CORS configuration
- `DAPR_HTTP_PORT` - Dapr sidecar HTTP port (default 3500)
- `DAPR_GRPC_PORT` - Dapr sidecar gRPC port (default 50001)

**Kafka/Redpanda Environment Variables (NEW):**
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka/Redpanda bootstrap servers (Redpanda Cloud or Strimzi local)
- `KAFKA_SASL_USERNAME` - SASL username for Redpanda Cloud (if using cloud)
- `KAFKA_SASL_PASSWORD` - SASL password for Redpanda Cloud (if using cloud)
- `KAFKA_SASL_MECHANISM` - SASL mechanism (SCRAM-SHA-256 or SCRAM-SHA-512 for Redpanda Cloud)

**Cloud Provider Environment Variables (NEW):**
- Oracle OKE: `OCI_TENANCY`, `OCI_USER`, `OCI_REGION`, `OCI_FINGERPRINT` (for kubectl config)
- Azure AKS: `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AKS_CLUSTER_NAME`
- GKE: `GCP_PROJECT_ID`, `GKE_CLUSTER_NAME`, `GKE_ZONE`

**Dapr Secrets Management:**
- MUST use Dapr Secrets API (`GET http://localhost:3500/v1.0/secrets/<secret-store>/<key>`)
- Dapr component: `kubernetes-secrets.yaml` references Kubernetes Secrets
- Backend services retrieve secrets via Dapr HTTP API (never direct K8s API)
- Helm values.yaml MUST support secret references
- NEVER commit plaintext secrets to repository

**Forbidden Environment Variables:**
- `OPENAI_API_KEY` - MUST NOT be used or referenced in Phase V

### XV. Containerization Standards (Docker and Gordon)

**Dockerfile Requirements:**
- MUST create production-optimized Dockerfiles for both frontend and backend
- Frontend Dockerfile: Multi-stage build for Next.js (build + production image)
- Backend Dockerfile: Python base with FastAPI + Cohere SDK dependencies
- Use `.dockerignore` to exclude unnecessary files

**Docker AI Agent (Gordon) Usage:**
- SHOULD use Gordon for intelligent Dockerfile generation when available
- Gordon can assist with: Dockerfile optimization, security scanning, compose-to-k8s hints
- Fallback: Standard Docker best practices if Gordon unavailable

**Image Tagging:**
- Use semantic versioning for image tags
- Tag format: `todo-frontend:v4.x.x`, `todo-backend:v4.x.x`

### XVI. Kubernetes Architecture (Minikube + kubectl)

**Cluster Requirements:**
- MUST use Minikube for local Kubernetes cluster
- Single-node cluster sufficient for development/testing
- kubectl MUST be configured to communicate with Minikube

**Resource Definitions:**
- Deployments: Manage pod replicas for frontend and backend
- Services: ClusterIP for internal communication, LoadBalancer/NodePort for external access
- ConfigMaps: Non-sensitive configuration data
- Secrets: Sensitive environment variables (DATABASE_URL, COHERE_API_KEY, BETTER_AUTH_SECRET)
- PersistentVolumeClaims: PostgreSQL data persistence

**Ingress (Optional):**
- Minikube Ingress addon for unified entry point
- Alternative: Direct service exposure via `minikube service` command

### XVII. Helm Charts Architecture

**Chart Structure:**
```
/charts/
├── todo-frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── ingress.yaml (optional)
│   └── .helmignore
├── todo-backend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── secret.yaml
│   │   └── configmap.yaml
│   └── .helmignore
└── postgres/
    ├── Chart.yaml
    ├── values.yaml (or dependency on bitnami/postgresql)
    └── templates/
```

**Helm Best Practices:**
- Use `values.yaml` for environment-specific overrides
- Template all configurable values
- Document all values in README or values.yaml comments
- Support dry-run and diff before deployment

### XVIII. AI-Assisted DevOps Workflow

**kubectl-ai Usage:**
- Generate Kubernetes manifests from natural language descriptions
- Debug deployment issues with AI-assisted analysis
- Optimize resource requests/limits

**kagent Usage:**
- Automated health checks and scaling recommendations
- Intelligent log analysis and troubleshooting
- Deployment optimization suggestions

**Gordon (Docker AI) Usage:**
- Dockerfile generation and optimization
- Security vulnerability scanning
- Compose to Kubernetes conversion hints

**Workflow Integration:**
1. Use Gordon for Dockerfile creation/optimization
2. Use kubectl-ai for manifest generation and debugging
3. Use kagent for runtime monitoring and optimization
4. Fall back to manual methods if AI tools unavailable

### XIX. Local Development vs Kubernetes Deployment

**Local Development (Docker Compose):**
- Retain `docker-compose.yml` for quick local development (Phase IV compatibility)
- Suitable for rapid iteration without Kubernetes overhead
- Use local PostgreSQL container
- Optional: Local Kafka via Redpanda container for event testing

**Kubernetes Deployment (Minikube + Helm):**
- Production-like environment for testing
- Full Helm chart deployment with Dapr sidecars
- Persistent volumes for data durability
- Service discovery via Kubernetes DNS
- Strimzi Kafka operator for local Kafka cluster (NEW in Phase V)
- Dapr installed via `dapr init -k` or Helm chart

**Cloud Kubernetes Deployment (NEW in Phase V):**
- Oracle OKE (preferred): Always free tier (4500 hours/month, 3000 OCPU hours, 18000 GB hours)
- Azure AKS (fallback): $200 credit for 30 days
- GKE (fallback): $300 credit + 1 free cluster/month
- Redpanda Cloud (free serverless) or managed Kafka alternative
- Dapr deployed via Helm with production configurations
- External LoadBalancers for frontend/backend services

**Testing Approach:**
- `kubectl port-forward` for accessing services
- `kubectl describe` and `kubectl logs` for debugging
- `dapr logs -a <app-id> -k` for Dapr sidecar logs
- `helm test` for chart validation
- Integration tests against Kubernetes-deployed services
- Event flow testing via Kafka topic inspection

### XX. Event-Driven Architecture (Kafka/Redpanda + Dapr)

**Architecture Principles:**
- MUST use Dapr Pub/Sub building block for all event messaging
- Kafka/Redpanda serves as the underlying message broker
- Services MUST NOT directly depend on Kafka client libraries (kafka-python); use Dapr HTTP API
- Events enable loose coupling between services (backend, notification, recurring, audit)
- All events MUST include `user_id` for multi-tenant isolation

**Kafka Topics (NEW in Phase V):**
1. **task-events** - CRUD operations and audit trail
   - Producers: backend service (via Dapr)
   - Consumers: recurring-service (for task_completed events), audit-service (for all events)
   - Partitioning: By user_id for ordering guarantees per user

2. **reminders** - Due date and reminder notifications
   - Producers: backend service (via Dapr Jobs API scheduled jobs)
   - Consumers: notification-service (sends email/push notifications)
   - Partitioning: By user_id

3. **task-updates** - Real-time UI sync (optional, future)
   - Producers: backend service (on any task mutation)
   - Consumers: frontend WebSocket gateway (future enhancement)
   - Partitioning: By user_id

**Event Schema Standard:**
```json
{
  "event_type": "task_created | task_updated | task_completed | task_deleted | reminder_due",
  "task_id": "uuid",
  "task_data": {
    "title": "string",
    "description": "string",
    "priority": "low | medium | high",
    "tags": ["string"],
    "due_at": "ISO8601 datetime",
    "recurring_interval": "daily | weekly | monthly | yearly | null"
  },
  "user_id": "uuid",
  "timestamp": "ISO8601 datetime"
}
```

**Kafka Deployment Options:**
1. **Local (Minikube)**: Strimzi Kafka Operator with KRaft (no Zookeeper)
   - `kubectl create namespace kafka`
   - `kubectl apply -f https://strimzi.io/install/latest?namespace=kafka`
   - Apply custom KafkaCluster CR: 1 replica, ephemeral storage, internal listeners
2. **Cloud**: Redpanda Cloud free serverless tier (preferred)
   - Signup at redpanda.com/cloud
   - Create topics via Redpanda Console
   - Obtain bootstrap servers and SASL credentials
   - Configure in Dapr Kafka component

**Dapr Pub/Sub Component:**
- Component name: `kafka-pubsub`
- Component type: `pubsub.kafka`
- Metadata: brokers, consumerID, authType (sasl_plaintext for Redpanda Cloud)
- Scopes: backend, notification-service, recurring-service, audit-service

### XXI. Dapr Building Blocks and Components

**Dapr Version Requirements:**
- MUST use Dapr v1.16+ for Jobs API support
- Install via `dapr init -k` on Kubernetes or Helm chart (`helm repo add dapr https://dapr.github.io/helm-charts/`)

**Required Dapr Building Blocks:**
1. **Pub/Sub** - Event messaging (Kafka/Redpanda)
2. **State Management** - Conversation persistence (optional, PostgreSQL state store)
3. **Jobs API (Alpha)** - Scheduled reminders and recurring tasks
4. **Secrets** - COHERE_API_KEY, BETTER_AUTH_SECRET retrieval
5. **Service Invocation** - Inter-service communication (optional, future)
6. **Bindings** - Cron triggers for scheduled jobs (fallback if Jobs API unavailable)

**Dapr Components (in /dapr-components/):**

1. **kafka-pubsub.yaml**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "<KAFKA_BOOTSTRAP_SERVERS>"
    - name: consumerGroup
      value: "todo-app"
    - name: authType
      value: "sasl_plaintext"  # For Redpanda Cloud
    - name: saslUsername
      value: "<KAFKA_SASL_USERNAME>"
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: sasl-password
  scopes:
    - backend
    - notification-service
    - recurring-service
    - audit-service
```

2. **statestore-postgresql.yaml**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secrets
        key: connection-string
  scopes:
    - backend
```

3. **kubernetes-secrets.yaml**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

4. **dapr-jobs.yaml** (Component configuration)
- Jobs API uses HTTP/gRPC endpoints directly (no separate component file needed)
- Job scheduling endpoint: `POST http://localhost:3500/v1.0-alpha1/jobs/<job-name>`
- Job payload includes `dueTime` (ISO8601), `data`, `repeats` (for recurring)

**Helm Chart Dapr Annotations:**
All service Deployments MUST include Dapr sidecar annotations:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "<service-name>"
  dapr.io/app-port: "<service-port>"
  dapr.io/log-level: "info"
  dapr.io/enable-api-logging: "true"
```

### XXII. Advanced Task Features

**Recurring Tasks:**
- MUST support intervals: daily, weekly, monthly, yearly
- On task completion (via `complete_task` tool), backend publishes `task_completed` event
- Recurring-service consumes event, checks if `recurring_interval` is set
- If recurring, service creates new task with same properties, updated `due_at` (due_at + interval)
- Original task marked completed; new task ID generated (tracks regeneration lineage)
- User can disable recurrence by setting `recurring_interval` to null via `update_task`

**Due Dates and Reminders:**
- `due_at` field: nullable datetime (timezone-aware, stored as UTC)
- `remind_at` field: nullable datetime (when to send reminder, e.g., due_at - 1 hour)
- Backend schedules reminder job via Dapr Jobs API when task created/updated with `remind_at`
- Job payload: `{"task_id": "...", "user_id": "...", "reminder_message": "Task X due soon"}`
- At `remind_at`, Dapr triggers job callback → backend publishes event to `reminders` topic
- Notification-service consumes `reminders` topic, sends notification (email/push/in-app)

**Priorities:**
- Enum: `low`, `medium` (default), `high`
- UI displays priority badges (color-coded)
- Search/filter supports priority filtering
- Sorting: Priority-aware (High > Medium > Low) combined with date/alpha sorting

**Tags:**
- Many-to-many relationship: Task ↔ Tag (via TaskTag junction table)
- Tag entity: id, name, user_id (user-scoped tags for isolation)
- UI: Multi-select tag picker
- Filter: Intersection (AND) logic for multiple selected tags (e.g., "urgent" AND "work")
- Backend query: `SELECT tasks WHERE task_id IN (SELECT task_id FROM task_tags WHERE tag_id IN (...) GROUP BY task_id HAVING COUNT(tag_id) = N)`

**Search and Filter:**
- Search: Case-insensitive keyword match on `title` and `description` (e.g., `WHERE LOWER(title) LIKE '%keyword%' OR LOWER(description) LIKE '%keyword%'`)
- Filter parameters: `priority`, `tags[]`, `status`, `search` (keyword)
- Combine filters with AND logic
- API endpoint: `GET /api/tasks?priority=high&tags=urgent&tags=work&search=report&status=pending`

**Sorting:**
- Supported fields: `created_at`, `due_at`, `priority`, `title`
- Priority sorting: Map `high` → 3, `medium` → 2, `low` → 1, then ORDER BY priority_value DESC
- Combined sorting: e.g., ORDER BY priority DESC, due_at ASC
- API parameter: `?sort=priority,desc&sort=due_at,asc`

### XXIII. Service Architecture

**Service Decomposition (Microservices):**

1. **Backend Service** (FastAPI)
   - Port: 8000
   - Dapr app-id: `backend`
   - Responsibilities:
     - CRUD API for tasks (POST, GET, PUT, DELETE)
     - Chat endpoint + Cohere integration (MCP tools)
     - JWT authentication middleware
     - Publishes events to `task-events` topic on all mutations
     - Schedules reminder jobs via Dapr Jobs API
   - Dapr interactions: Pub/Sub (publish), Secrets (retrieve), Jobs (schedule)

2. **Notification Service** (FastAPI) - NEW
   - Port: 8001
   - Dapr app-id: `notification-service`
   - Responsibilities:
     - Subscribes to `reminders` topic (Dapr Pub/Sub)
     - Sends notifications (email via SMTP, push via Firebase/OneSignal, or in-app)
     - Logs notification delivery status
   - Dapr interactions: Pub/Sub (subscribe), Secrets (retrieve email credentials)
   - Endpoints:
     - `POST /dapr/subscribe` - Dapr subscription endpoint
     - `POST /reminders` - Dapr-invoked handler for reminder events

3. **Recurring Service** (FastAPI) - NEW
   - Port: 8002
   - Dapr app-id: `recurring-service`
   - Responsibilities:
     - Subscribes to `task-events` topic (filters for `task_completed` events)
     - Checks if completed task has `recurring_interval` set
     - Creates new task with updated `due_at` via backend API (Dapr Service Invocation) or direct DB insert
     - Tracks regeneration lineage (optional: parent_task_id field)
   - Dapr interactions: Pub/Sub (subscribe), Service Invocation (call backend API)
   - Endpoints:
     - `POST /dapr/subscribe` - Dapr subscription endpoint
     - `POST /task-events` - Dapr-invoked handler for task events

4. **Audit Service** (FastAPI) - OPTIONAL
   - Port: 8003
   - Dapr app-id: `audit-service`
   - Responsibilities:
     - Subscribes to `task-events` topic (all event types)
     - Logs events to audit table or external logging system (e.g., Elasticsearch)
     - Compliance and analytics
   - Dapr interactions: Pub/Sub (subscribe)

**Inter-Service Communication:**
- Prefer Dapr Pub/Sub for async, event-driven communication
- Use Dapr Service Invocation for synchronous calls (e.g., recurring-service → backend to create task)
- Service Invocation format: `POST http://localhost:3500/v1.0/invoke/<target-app-id>/method/<method-name>`

**Database Access:**
- Backend service: Full CRUD access to all tables
- Recurring service: Read-only access to Task table (or use Service Invocation to backend)
- Notification service: No direct DB access (consumes events only)
- Audit service: Write-only access to AuditLog table (if using DB for audit)

### XXIV. Kafka Topics and Schemas

**Topic: task-events**
- Purpose: CRUD audit trail and recurring task triggers
- Partitions: 3 (partition by user_id for ordering)
- Retention: 7 days (configurable)
- Producers: backend (Dapr Pub/Sub)
- Consumers: recurring-service, audit-service (Dapr Pub/Sub)

**Topic: reminders**
- Purpose: Due date notifications
- Partitions: 3 (partition by user_id)
- Retention: 1 day (short-lived notifications)
- Producers: backend (Dapr Jobs API callback)
- Consumers: notification-service (Dapr Pub/Sub)

**Topic: task-updates** (FUTURE)
- Purpose: Real-time UI sync
- Partitions: 3 (partition by user_id)
- Retention: 1 hour (ephemeral)
- Producers: backend (on any mutation)
- Consumers: frontend WebSocket gateway (future)

**Schema Registry (Optional):**
- Consider Redpanda Schema Registry or Confluent Schema Registry for schema validation
- Enforce JSON schema for all events
- Versioning for backward compatibility

### XXV. Dapr Jobs API (Scheduling and Reminders)

**Jobs API Overview:**
- Alpha feature in Dapr v1.16+ (enable via `--enable-api-logging` and alpha API endpoints)
- Allows scheduling one-time or recurring jobs with exact `dueTime`
- Replaces cron-based scheduling for precision (e.g., reminders at specific datetimes)
- Jobs stored in Dapr state store (PostgreSQL) for durability

**Scheduling a Reminder Job:**
When task created/updated with `due_at` and `remind_at`:
```python
import httpx
from datetime import datetime

async def schedule_reminder(task_id: str, user_id: str, remind_at: datetime):
    job_name = f"reminder-{task_id}"
    dapr_url = f"http://localhost:3500/v1.0-alpha1/jobs/{job_name}"
    payload = {
        "dueTime": remind_at.isoformat(),
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "reminder_message": f"Task due soon"
        },
        "ttl": "1h"  # Job expires 1 hour after dueTime if not executed
    }
    async with httpx.AsyncClient() as client:
        await client.post(dapr_url, json=payload)
```

**Job Callback Handler (Backend):**
Dapr invokes callback endpoint when job executes:
```python
@app.post("/jobs/callback")
async def job_callback(job_data: dict):
    task_id = job_data["data"]["task_id"]
    user_id = job_data["data"]["user_id"]
    # Publish reminder event
    dapr_pubsub_url = "http://localhost:3500/v1.0/publish/kafka-pubsub/reminders"
    event = {
        "event_type": "reminder_due",
        "task_id": task_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    async with httpx.AsyncClient() as client:
        await client.post(dapr_pubsub_url, json=event)
```

**Recurring Jobs (for Recurring Tasks):**
- Use `repeats` field in job payload: `"repeats": {"interval": "24h"}` for daily tasks
- Alternative: On task completion, recurring-service schedules next instance as one-time job

**Fallback: Dapr Bindings (Cron):**
If Jobs API unavailable or unstable:
- Use Dapr Cron binding for periodic checks (e.g., every 5 minutes)
- Backend queries tasks with `remind_at <= NOW()` and sends reminders
- Less precise than Jobs API (5-minute granularity vs exact time)

### XXVI. Cloud Kubernetes Deployment

**Preferred: Oracle Cloud Infrastructure (OCI) Kubernetes Engine (OKE)**

**Why Oracle OKE:**
- Always Free Tier: 4500 compute hours/month, 3000 OCPU hours/month, 18000 GB-hours/month
- Sufficient for small-scale production deployment
- No credit card charges (requires verification but no billing)
- Managed Kubernetes (no control plane costs)

**OKE Setup Steps:**
1. **Signup**: oracle.com/cloud/free (requires credit card for verification)
2. **Create Cluster**:
   - OCI Console → Developer Services → Kubernetes Clusters → Create Cluster
   - Quick Create (default settings)
   - Node pool: VM.Standard.E2.1.Micro (Always Free eligible)
   - Nodes: 2-3 (within free tier limits)
3. **Configure kubectl**:
   ```bash
   oci ce cluster create-kubeconfig --cluster-id <cluster-ocid> --file ~/.kube/config-oke
   export KUBECONFIG=~/.kube/config-oke
   kubectl get nodes
   ```
4. **Install Dapr**:
   ```bash
   helm repo add dapr https://dapr.github.io/helm-charts/
   helm repo update
   helm install dapr dapr/dapr --namespace dapr-system --create-namespace
   ```
5. **Deploy Helm Charts**:
   ```bash
   helm install postgres ./charts/postgres
   helm install todo-backend ./charts/todo-backend
   helm install notification-service ./charts/notification-service
   helm install recurring-service ./charts/recurring-service
   helm install todo-frontend ./charts/todo-frontend
   ```
6. **Expose Services**:
   - Use LoadBalancer service type (OCI Load Balancer)
   - Alternative: Ingress controller (nginx-ingress or OCI native)

**Fallback: Azure AKS**

**Why Azure AKS:**
- $200 credit for 30 days (new accounts)
- Free cluster management (pay only for nodes)
- Excellent Dapr integration

**AKS Setup Steps:**
1. **Signup**: azure.com/free (credit card required)
2. **Create Cluster**:
   ```bash
   az aks create --resource-group todo-rg --name todo-aks --node-count 2 --enable-managed-identity --generate-ssh-keys
   az aks get-credentials --resource-group todo-rg --name todo-aks
   ```
3. **Install Dapr**: Same as OKE (Helm install)
4. **Deploy Helm Charts**: Same as OKE

**Fallback: Google GKE**

**Why GKE:**
- $300 credit for 90 days
- 1 free Autopilot cluster/month (regional)
- Advanced Kubernetes features

**GKE Setup Steps:**
1. **Signup**: cloud.google.com/free
2. **Create Cluster**:
   ```bash
   gcloud container clusters create todo-gke --num-nodes=2 --machine-type=e2-medium --zone=us-central1-a
   gcloud container clusters get-credentials todo-gke --zone=us-central1-a
   ```
3. **Install Dapr**: Same as OKE (Helm install)
4. **Deploy Helm Charts**: Same as OKE

**Redpanda Cloud (Kafka):**
- Signup: redpanda.com/cloud (free serverless tier)
- Create topics: task-events, reminders, task-updates
- Obtain bootstrap servers and SASL credentials
- Update `/dapr-components/kafka-pubsub.yaml` with credentials
- Deploy as Kubernetes Secret

**Secrets Management (Cloud):**
- Store sensitive values in Kubernetes Secrets
- Dapr Kubernetes Secrets component retrieves from K8s API
- Cloud-specific alternatives:
  - OKE: OCI Vault (optional, advanced)
  - AKS: Azure Key Vault (optional, requires Dapr Azure Key Vault component)
  - GKE: Google Secret Manager (optional, requires Dapr GCP Secret Manager component)

### XXVII. CI/CD with GitHub Actions

**Pipeline Requirements:**
- MUST automate build, test, and deployment on push to main branch
- MUST build Docker images for all services
- MUST push images to container registry (Docker Hub, GitHub Container Registry, or cloud provider registry)
- MUST run Helm lint and dry-run before deployment
- MUST support staging and production environments
- MUST provide rollback capabilities via Helm history

**GitHub Actions Workflow (.github/workflows/ci-cd.yml):**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE: ${{ github.repository }}/todo-backend
  FRONTEND_IMAGE: ${{ github.repository }}/todo-frontend
  NOTIFICATION_IMAGE: ${{ github.repository }}/notification-service
  RECURRING_IMAGE: ${{ github.repository }}/recurring-service

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest

      - name: Run frontend tests
        run: |
          cd frontend
          npm ci
          npm test

      - name: Lint Helm charts
        run: |
          helm lint ./charts/todo-backend
          helm lint ./charts/todo-frontend
          helm lint ./charts/notification-service
          helm lint ./charts/recurring-service

  build-images:
    needs: build-and-test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:${{ github.sha }},${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:latest

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:${{ github.sha }},${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:latest

      - name: Build and push notification service
        uses: docker/build-push-action@v5
        with:
          context: ./notification-service
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.NOTIFICATION_IMAGE }}:${{ github.sha }},${{ env.REGISTRY }}/${{ env.NOTIFICATION_IMAGE }}:latest

      - name: Build and push recurring service
        uses: docker/build-push-action@v5
        with:
          context: ./recurring-service
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.RECURRING_IMAGE }}:${{ github.sha }},${{ env.REGISTRY }}/${{ env.RECURRING_IMAGE }}:latest

  deploy-staging:
    needs: build-images
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4

      - name: Install kubectl
        uses: azure/setup-kubectl@v4

      - name: Install Helm
        uses: azure/setup-helm@v4

      - name: Configure kubectl (OKE example)
        run: |
          echo "${{ secrets.KUBECONFIG_STAGING }}" > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy with Helm
        run: |
          helm upgrade --install postgres ./charts/postgres --namespace staging --create-namespace
          helm upgrade --install todo-backend ./charts/todo-backend \
            --set image.tag=${{ github.sha }} \
            --namespace staging
          helm upgrade --install notification-service ./charts/notification-service \
            --set image.tag=${{ github.sha }} \
            --namespace staging
          helm upgrade --install recurring-service ./charts/recurring-service \
            --set image.tag=${{ github.sha }} \
            --namespace staging
          helm upgrade --install todo-frontend ./charts/todo-frontend \
            --set image.tag=${{ github.sha }} \
            --namespace staging

  deploy-production:
    needs: build-images
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://todo.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Install kubectl
        uses: azure/setup-kubectl@v4

      - name: Install Helm
        uses: azure/setup-helm@v4

      - name: Configure kubectl (OKE example)
        run: |
          echo "${{ secrets.KUBECONFIG_PRODUCTION }}" > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy with Helm
        run: |
          helm upgrade --install postgres ./charts/postgres --namespace production --create-namespace
          helm upgrade --install todo-backend ./charts/todo-backend \
            --set image.tag=${{ github.sha }} \
            --namespace production
          helm upgrade --install notification-service ./charts/notification-service \
            --set image.tag=${{ github.sha }} \
            --namespace production
          helm upgrade --install recurring-service ./charts/recurring-service \
            --set image.tag=${{ github.sha }} \
            --namespace production
          helm upgrade --install todo-frontend ./charts/todo-frontend \
            --set image.tag=${{ github.sha }} \
            --namespace production

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/todo-backend -n production
          kubectl rollout status deployment/todo-frontend -n production
```

**GitHub Secrets Configuration:**
- `KUBECONFIG_STAGING` - Base64-encoded kubeconfig for staging cluster
- `KUBECONFIG_PRODUCTION` - Base64-encoded kubeconfig for production cluster
- Cloud provider credentials (if using cloud registries instead of GHCR)
- Optional: Slack/email notification webhooks for deployment alerts

**Rollback Strategy:**
```bash
# List Helm releases
helm history todo-backend -n production

# Rollback to previous revision
helm rollback todo-backend <revision> -n production
```

### XXVIII. Monitoring and Observability

**Kubernetes Metrics and Dashboard:**
- **metrics-server**: `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`
- **Kubernetes Dashboard**: `kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml`
- Access via `kubectl proxy` or port-forward
- View pod CPU/memory usage, deployment status, events

**Dapr Observability:**
- **Zipkin (Distributed Tracing)**:
  - Dapr auto-instruments HTTP/gRPC calls
  - Install Zipkin: `kubectl apply -f https://raw.githubusercontent.com/dapr/dapr/master/deploy/zipkin.yaml`
  - Configure Dapr tracing: Update Dapr configuration with Zipkin endpoint
  - Access Zipkin UI: `kubectl port-forward svc/zipkin 9411:9411 -n dapr-system`
  - View traces for request flow: frontend → backend → recurring-service

- **Prometheus (Metrics)**:
  - Dapr exposes Prometheus metrics on `:9090/metrics` (sidecar)
  - Install Prometheus: `helm install prometheus prometheus-community/prometheus`
  - Configure Prometheus to scrape Dapr sidecars (ServiceMonitor CRDs)
  - Metrics: dapr_http_server_request_count, dapr_pubsub_messages_sent, dapr_jobs_scheduled

- **Grafana (Dashboards)**:
  - Install Grafana: `helm install grafana grafana/grafana`
  - Import Dapr dashboards from grafana.com/grafana/dashboards
  - Visualize request rates, error rates, latency, Pub/Sub throughput

**Logging:**
- **kubectl logs**: `kubectl logs -f deployment/todo-backend -n production`
- **Dapr logs**: `dapr logs -a backend -k`
- **Centralized Logging (Optional)**:
  - EFK Stack: Elasticsearch, Fluentd, Kibana
  - Loki + Promtail (lightweight alternative)
  - Cloud-native: OCI Logging, Azure Monitor, GCP Cloud Logging

**Alerting:**
- Prometheus Alertmanager for threshold-based alerts (e.g., high error rate, pod restarts)
- Slack/email integration for alert notifications
- Example alert: "Backend 5xx error rate > 5% for 5 minutes"

### XXIX. Migration Path from Phase IV to Phase V

**Phase IV → Phase V Migration Checklist:**

1. **Database Schema Updates**:
   - Add columns: `due_at`, `remind_at`, `recurring_interval`, `priority` to Task table
   - Create Tag and TaskTag tables
   - Run migration scripts (Alembic/SQLAlchemy migrations)

2. **Install Dapr**:
   - Minikube: `dapr init -k`
   - Cloud: `helm install dapr dapr/dapr --namespace dapr-system --create-namespace`
   - Verify: `dapr status -k`

3. **Deploy Kafka**:
   - Local: Apply Strimzi operator and KafkaCluster CR
   - Cloud: Sign up for Redpanda Cloud, create topics, obtain credentials

4. **Create Dapr Components**:
   - Write YAML files in `/dapr-components/` (kafka-pubsub, statestore-postgresql, kubernetes-secrets)
   - Apply: `kubectl apply -f dapr-components/`

5. **Develop New Services**:
   - Create `/notification-service` with Dapr Pub/Sub subscription
   - Create `/recurring-service` with Dapr Pub/Sub subscription
   - Update `/backend` to publish events via Dapr

6. **Update Helm Charts**:
   - Add Dapr annotations to all Deployment templates
   - Create new charts for notification-service and recurring-service
   - Update values.yaml with Dapr-specific configurations

7. **Implement Advanced Features**:
   - Update API endpoints for priorities, tags, search, filter, sort
   - Add `complete_task` logic to check recurring_interval and publish event
   - Implement Dapr Jobs API integration for reminders

8. **Set Up CI/CD**:
   - Create `.github/workflows/ci-cd.yml`
   - Configure GitHub Secrets (kubeconfig, registry credentials)
   - Test pipeline with push to develop branch

9. **Deploy to Cloud**:
   - Choose provider (Oracle OKE preferred)
   - Create cluster and configure kubectl
   - Update Helm values for cloud environment (LoadBalancer, external DB if needed)
   - Deploy via CI/CD or manual `helm install`

10. **Configure Monitoring**:
    - Install metrics-server, Prometheus, Grafana
    - Configure Dapr observability (Zipkin, Prometheus scraping)
    - Set up alerting rules

11. **Test End-to-End**:
    - Create task with recurring_interval, verify regeneration on completion
    - Create task with due_at and remind_at, verify notification delivery
    - Test priority/tag filtering and search
    - Verify event flow via Kafka topic inspection or Zipkin traces

12. **Documentation**:
    - Update README.md with Phase V setup instructions
    - Document Redpanda Cloud signup, Oracle OKE signup, CI/CD setup
    - Add troubleshooting section for Dapr and Kafka issues

## Deliverables Structure

- Monorepo root with `.spec-kit/config.yaml` (if using Spec-Kit)
- Organized `/specs` folder: overview, features, api, database, ui, events, dapr
- Separate CLAUDE.md files at root, `/frontend`, `/backend`, `/notification-service`, `/recurring-service`
- `/charts` directory with Helm charts for all services (with Dapr annotations)
- `/dapr-components` directory with Dapr component YAML files
- Dockerfiles in `/frontend`, `/backend`, `/notification-service`, `/recurring-service` directories
- `docker-compose.yml` for local development (non-K8s, Phase IV compatibility)
- `/.github/workflows/ci-cd.yml` for GitHub Actions CI/CD pipeline
- `/scripts` directory with setup and deployment scripts:
  - `minikube-setup.sh` - Minikube + Dapr + Strimzi initialization
  - `deploy.sh` - Local Helm deployment
  - `cloud-deploy.sh` - Cloud Kubernetes deployment (OKE/AKS/GKE)
  - `migration-v5.py` - Database migration script for Phase V schema
- Final `README.md` with:
  - Architecture overview (event-driven diagram with Dapr + Kafka)
  - Docker Compose run instructions (Phase IV compatibility)
  - Minikube + Dapr + Helm deployment instructions
  - Strimzi Kafka setup OR Redpanda Cloud signup instructions
  - Oracle OKE/Azure AKS/GKE cloud deployment instructions
  - CI/CD setup with GitHub Actions
  - Monitoring and observability (Zipkin, Prometheus, Grafana)
  - kubectl-ai and kagent usage examples
  - Gordon commands (or fallback)
  - Troubleshooting section (Dapr sidecar issues, Kafka connectivity, Jobs API)

## Technology Stack (Non-Negotiable)

### Frontend
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth
- OpenAI ChatKit (or equivalent chat UI library)
- Dapr sidecar (optional, for future client-side state management)

### Backend Services
- FastAPI for all services (backend, notification-service, recurring-service, audit-service)
- SQLModel
- PostgreSQL (via Helm, local or cloud Kubernetes)
- **Cohere Python SDK** (NOT OpenAI)
- Dapr Python SDK or HTTP client (`httpx`) for Dapr API calls

### Shared
- JWT authentication (Better Auth ↔ FastAPI)
- BETTER_AUTH_SECRET environment variable
- Event schemas (JSON) for Kafka messages

### AI Integration
- Cohere API for chat and tool calling
- COHERE_API_KEY environment variable (via Dapr Secrets)
- Agent patterns inspired by OpenAI Agents SDK (implemented via Cohere)
- Cohere-powered MCP tools with event publishing

### Event-Driven Architecture (NEW in Phase V)
- **Kafka/Redpanda** - Message broker
  - Local: Strimzi Kafka Operator v0.50+ (KRaft mode, no Zookeeper)
  - Cloud: Redpanda Cloud free serverless tier (preferred)
- **Dapr v1.16+** - Distributed application runtime
  - Pub/Sub building block (Kafka component)
  - State Management building block (PostgreSQL component)
  - Jobs API (Alpha) for scheduled reminders
  - Secrets building block (Kubernetes Secrets)
  - Service Invocation building block (optional)
  - Bindings building block (cron fallback)

### Infrastructure (Phase V)
- Docker for containerization
- Docker AI Agent (Gordon) for intelligent Dockerfile management
- **Minikube** for local Kubernetes cluster (with Dapr + Strimzi)
- **Cloud Kubernetes** (NEW):
  - **Oracle OKE** (preferred): Always Free Tier
  - **Azure AKS** (fallback): $200 credit
  - **GKE** (fallback): $300 credit + 1 free cluster/month
- Helm 3+ for Kubernetes package management
- kubectl for cluster interaction
- kubectl-ai for AI-assisted Kubernetes operations
- kagent for intelligent monitoring and optimization
- Dapr CLI for Dapr management

### CI/CD (NEW in Phase V)
- GitHub Actions for automated pipelines
- Docker Hub / GitHub Container Registry / Cloud registry for image storage
- Helm for deployment automation
- GitHub Secrets for credential management

### Monitoring and Observability (NEW in Phase V)
- Kubernetes metrics-server and Dashboard
- Dapr Zipkin (distributed tracing)
- Prometheus (metrics collection)
- Grafana (visualization)
- Alertmanager (alerting)
- Optional: EFK/Loki for centralized logging

## Governance

This constitution governs all development decisions for the Todo application. All code MUST comply with these principles. Amendments require documentation and team approval. All pull requests MUST verify compliance with these principles before merging.

**Version**: 5.0.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-09

---

## Differences from Phase IV (Key Phase V Changes)

This section highlights the critical architectural and technology decisions that differentiate Phase V from Phase IV. **This constitution is the single source of truth for all Phase V decisions.**

### 1. Architecture Shift: Monolithic → Event-Driven Microservices

| Aspect | Phase IV | Phase V |
|--------|----------|---------|
| **Architecture** | Monolithic backend | Event-driven microservices |
| **Services** | Single backend (FastAPI) | Backend + notification + recurring + audit services |
| **Communication** | Synchronous (REST only) | Asynchronous (events) + Synchronous (REST) |
| **Messaging** | None | Kafka/Redpanda + Dapr Pub/Sub |
| **Rationale** | Simplicity | Scalability, loose coupling, advanced features |

**Why Event-Driven?**
- Recurring tasks require async regeneration on completion
- Reminders need scheduled notifications without blocking API
- Audit logging decoupled from main application
- Real-time sync (future) requires event streams

### 2. Dapr Integration (Distributed Application Runtime)

| Aspect | Phase IV | Phase V |
|--------|----------|---------|
| **Service Communication** | Direct HTTP/gRPC | Dapr Service Invocation |
| **Messaging** | None | Dapr Pub/Sub (Kafka) |
| **State Management** | Direct database access | Dapr State API (optional) |
| **Secrets** | Kubernetes Secrets (direct) | Dapr Secrets API |
| **Scheduling** | None | Dapr Jobs API (Alpha) |
| **Observability** | Manual instrumentation | Auto-instrumented (Zipkin traces) |

**Why Dapr?**
- Abstracts infrastructure complexity (Kafka, state stores, secrets)
- Portable across cloud providers and message brokers
- Built-in observability (Zipkin, Prometheus)
- Simplifies microservices patterns (Pub/Sub, Service Invocation)

### 3. Advanced Task Features (Recurring, Due Dates, Priorities, Tags)

| Feature | Phase IV | Phase V |
|---------|----------|---------|
| **Recurring Tasks** | Not supported | Daily/weekly/monthly/yearly with auto-regeneration |
| **Due Dates** | Not supported | Timezone-aware datetime with reminders |
| **Reminders** | Not supported | Scheduled notifications via Dapr Jobs API |
| **Priorities** | Not supported | Low/Medium/High with priority-aware sorting |
| **Tags** | Not supported | Multi-select tags with intersection filtering |
| **Search** | Not supported | Case-insensitive keyword search on title/description |
| **Filtering** | Basic (status only) | Priority + tags + status + search with AND logic |
| **Sorting** | Basic (created_at) | Priority, due_at, created_at, title with multi-field |

### 4. Cloud Deployment Support

| Aspect | Phase IV | Phase V |
|--------|----------|---------|
| **Deployment Target** | Minikube only (local) | Minikube + Cloud Kubernetes |
| **Cloud Providers** | None | Oracle OKE (preferred), Azure AKS, GKE |
| **Kafka** | None | Redpanda Cloud (serverless) or Strimzi (local) |
| **Cost** | Zero (local only) | Zero with free tiers (OKE Always Free, Redpanda Cloud free) |
| **Scalability** | Single-node | Multi-node cloud clusters with auto-scaling |

**Why Cloud?**
- Production-ready deployment beyond local development
- Oracle OKE Always Free tier provides genuine free hosting
- Redpanda Cloud free tier eliminates local Kafka management
- Learning path to enterprise Kubernetes deployments

### 5. CI/CD Automation

| Aspect | Phase IV | Phase V |
|--------|----------|---------|
| **CI/CD** | Manual deployment | GitHub Actions automated pipelines |
| **Build** | Manual `docker build` | Automated multi-arch builds |
| **Registry** | Local Minikube registry | Docker Hub / GHCR / cloud registry |
| **Deployment** | Manual `helm install` | Automated `helm upgrade` on push |
| **Testing** | Manual | Automated tests + Helm lint in CI |
| **Rollback** | Manual | Automated Helm rollback on failure |

### 6. Monitoring and Observability

| Aspect | Phase IV | Phase V |
|--------|----------|---------|
| **Metrics** | Manual kubectl logs | metrics-server + Prometheus + Grafana |
| **Tracing** | None | Dapr Zipkin (distributed tracing) |
| **Dashboards** | None | Kubernetes Dashboard + Grafana |
| **Alerting** | None | Prometheus Alertmanager |
| **Logging** | kubectl logs | kubectl logs + optional EFK/Loki |

### 7. Database Schema Evolution

**New Phase V Schema Additions:**
- Task table: `due_at`, `remind_at`, `recurring_interval`, `priority` columns
- Tag table: id, name, user_id
- TaskTag junction table: task_id, tag_id (many-to-many)
- Migration scripts: Alembic/SQLAlchemy migrations for schema updates

---

## Differences from Phase III (Key Phase IV Changes - RETAINED FOR REFERENCE)

This section highlights the critical architectural and technology decisions that differentiate Phase IV from Phase III. **This constitution is the single source of truth for all Phase IV decisions.**

### 1. Infrastructure Shift: Neon → Local PostgreSQL (Helm)

| Aspect | Phase III | Phase IV |
|--------|-----------|----------|
| **Database** | Neon Serverless PostgreSQL | Local PostgreSQL via Helm |
| **Connection** | Cloud-hosted, connection string | Kubernetes Service DNS |
| **Persistence** | Managed by Neon | PersistentVolumeClaim in K8s |
| **Rationale** | Cloud convenience | Local-only, no cloud dependencies |

**Why Local PostgreSQL?**
- Phase IV is purely local deployment (Minikube)
- No cloud resources or external dependencies
- Full control over database configuration
- Simpler secrets management in Kubernetes context

### 2. Deployment Model: Docker Compose → Kubernetes/Helm

| Aspect | Phase III | Phase IV |
|--------|-----------|----------|
| **Orchestration** | Docker Compose | Kubernetes (Minikube) |
| **Packaging** | docker-compose.yml | Helm Charts |
| **Scaling** | Manual container count | K8s Deployment replicas |
| **Service Discovery** | Docker network | Kubernetes DNS |
| **Configuration** | .env files | ConfigMaps + Secrets |

**Why Kubernetes/Helm?**
- Production-grade deployment patterns
- Declarative infrastructure as code
- Built-in health checks and rolling updates
- Better secrets management
- Learning path to cloud-native deployment

### 3. AI DevOps Tooling (NEW)

| Tool | Purpose | Usage |
|------|---------|-------|
| **Gordon (Docker AI)** | Intelligent Dockerfile generation | `docker ai build`, security scanning |
| **kubectl-ai** | AI-assisted K8s operations | Manifest generation, debugging |
| **kagent** | Intelligent K8s monitoring | Health checks, optimization |

**Integration Pattern:**
```
Developer Intent → AI Tool → Generated Manifest/Dockerfile → Review → Apply
```

### 4. Containerization Requirements (Enhanced)

| Aspect | Phase III | Phase IV |
|--------|-----------|----------|
| **Dockerfiles** | Basic (if any) | Production-optimized, multi-stage |
| **Image Registry** | Local only | Local Minikube registry |
| **Build Tool** | docker build | Gordon-assisted or docker build |
| **Security** | Basic | Gordon security scanning |

### 5. Directory Structure Changes

**New in Phase IV:**
```
/charts/
├── todo-frontend/     # Frontend Helm chart
├── todo-backend/      # Backend Helm chart
└── postgres/          # PostgreSQL Helm chart

/scripts/
├── minikube-setup.sh  # Minikube initialization
└── deploy.sh          # Helm deployment script

/frontend/Dockerfile   # Frontend container definition
/backend/Dockerfile    # Backend container definition
```

---

## Phase Evolution Summary

| Aspect | Phase I (Console) | Phase II (Web) | Phase III (AI Chatbot) | Phase IV (K8s Deploy) | Phase V (Event-Driven Cloud) |
|--------|-------------------|----------------|------------------------|------------------------|------------------------------|
| **Architecture** | Single-process CLI | Full-stack web (monorepo) | Full-stack + AI chatbot | Cloud-native local K8s | Event-driven microservices |
| **Frontend** | None (console only) | Next.js 16+ with App Router | Next.js + ChatKit UI | SAME (containerized) | SAME (with Dapr sidecar) |
| **Backend** | In-process Python | FastAPI REST API | SAME + chat endpoint | SAME (containerized) | Backend + notification + recurring services |
| **Database** | In-memory Python dict | Neon Serverless PostgreSQL | SAME Neon + chat tables | Local PostgreSQL (Helm) | PostgreSQL (local or cloud) + advanced schema |
| **Authentication** | None (single-user) | JWT + Better Auth | SAME | SAME (K8s Secrets) | SAME (Dapr Secrets) |
| **User Isolation** | N/A | Mandatory per-user | SAME + tool enforcement | SAME | SAME + event-level isolation |
| **UI** | Text-based argparse | Tailwind CSS web | Web UI + chat | SAME | SAME + advanced features (tags, priorities) |
| **AI Provider** | N/A | N/A | Cohere API | SAME (Cohere) | SAME (Cohere + event publishing) |
| **Deployment** | Local run | Docker Compose | SAME | Minikube + Helm | Minikube + Cloud K8s (OKE/AKS/GKE) |
| **Orchestration** | N/A | Docker Compose | Docker Compose | Kubernetes | Kubernetes + Dapr |
| **Packaging** | pip install | docker-compose.yml | docker-compose.yml | Helm Charts | Helm Charts + Dapr components |
| **Infrastructure Tools** | N/A | Docker | Docker | Docker + Gordon + kubectl-ai + kagent | SAME + Dapr CLI |
| **Config Management** | CLI args | .env files | .env files | ConfigMaps + Secrets | Dapr Secrets + ConfigMaps |
| **Service Discovery** | N/A | Docker network | Docker network | Kubernetes DNS | Kubernetes DNS + Dapr Service Invocation |
| **Messaging** | N/A | None | None | None | Kafka/Redpanda + Dapr Pub/Sub |
| **Event Bus** | N/A | None | None | None | Kafka topics (task-events, reminders) |
| **Scaling** | N/A | Manual | Manual | K8s replicas | K8s replicas + event-driven horizontal scaling |
| **Health Checks** | N/A | Manual | Manual | K8s probes | K8s probes + Dapr health endpoints |
| **Observability** | N/A | None | None | kubectl logs | Zipkin + Prometheus + Grafana |
| **CI/CD** | N/A | None | None | None | GitHub Actions (build + test + deploy) |
| **Type Safety** | Python type hints | TypeScript + Python | SAME | SAME | SAME |
| **Testing** | Unit tests only | Contract + integration | + chatbot tests | + K8s integration | + event-driven tests + E2E cloud tests |
| **Dependencies** | Standard library | Full npm/pip | + cohere SDK | + Helm charts | + Dapr + Kafka/Redpanda |
| **Advanced Features** | Basic CRUD | Basic CRUD + multi-user | + AI chatbot | SAME | + recurring tasks + due dates + priorities + tags + search/filter/sort |
| **Scheduling** | N/A | None | None | None | Dapr Jobs API (reminders) |
