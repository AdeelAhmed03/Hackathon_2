<!-- SYNC IMPACT REPORT:
Version change: 3.0.0 → 4.0.0
Modified principles:
- V. Persistent Storage with SQLModel → updated for local PostgreSQL (Helm-managed) instead of Neon
- VII. Monorepo Structure and Code Organization → expanded to include /charts directory
- IX. Backend Technology Standards → updated database reference and Cohere integration preserved
- X. Development Workflow → enhanced with AI-assisted DevOps workflow (Gordon, kubectl-ai, kagent)
- XIV. Environment Variables and Secrets → updated for Phase IV (local PostgreSQL, Minikube context)
Added sections:
- XV. Containerization Standards (Docker and Gordon)
- XVI. Kubernetes Architecture (Minikube + kubectl)
- XVII. Helm Charts Architecture
- XVIII. AI-Assisted DevOps Workflow (Gordon, kubectl-ai, kagent)
- XIX. Local Development vs Kubernetes Deployment
- "Differences from Phase III" section with Phase IV migration guidance:
  - Infrastructure Shift (Neon → Local PostgreSQL via Helm)
  - Deployment Model (Docker Compose → Kubernetes/Helm)
  - AI DevOps Tooling (Gordon, kubectl-ai, kagent)
- Phase I vs Phase II vs Phase III vs Phase IV comparison table
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated (no changes needed - generic enough)
- .specify/templates/spec-template.md ✅ updated (no changes needed - generic enough)
- .specify/templates/tasks-template.md ✅ updated (no changes needed - generic enough)
- CLAUDE.md ✅ updated (Phase IV context with Helm/K8s guidance)
- backend/CLAUDE.md ✅ created (local PostgreSQL + containerization + Cohere guidance)
- README.md ✅ updated (Minikube + Helm deployment instructions, AI DevOps tools, troubleshooting)
Follow-up TODOs: None
-->

# Todo Application Constitution (Phase IV)

> **SINGLE SOURCE OF TRUTH**: This constitution is the authoritative document for ALL Phase IV architectural decisions, technology choices, and implementation constraints. When in doubt, defer to this document. Any conflicting guidance in other files MUST be reconciled with this constitution.

## Project Identity

**Project Name**: hackathon-todo
**Architecture**: Full-Stack Web Application with AI Chatbot, Cloud-Native Local Deployment (Monorepo)
**Phase**: IV - Kubernetes Deployment with AI-Assisted DevOps

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
All task data MUST be stored in PostgreSQL using SQLModel. In Phase IV, PostgreSQL runs locally via Helm chart (bitnami/postgresql or similar) instead of Neon Serverless. Database models MUST define proper relationships between users and tasks. Migrations MUST be versioned and applied automatically on startup. Foreign key constraints enforce referential integrity. Conversation and Message tables persist chat history.

### VI. RESTful API Design
All backend endpoints MUST follow RESTful conventions. Proper HTTP methods (GET, POST, PUT, DELETE), status codes, and error responses. API contracts MUST be documented and validated. Request/response validation using Pydantic models. Consistent error handling across all endpoints. The chat endpoint follows POST semantics for message submission.

### VII. Monorepo Structure and Code Organization
The project MUST maintain a clear monorepo structure:
- `/frontend` - Next.js application with ChatKit UI
- `/backend` - FastAPI application (includes chat endpoint + Cohere integration)
- `/charts` - Helm charts for Kubernetes deployment (NEW in Phase IV)
  - `/charts/todo-frontend` - Frontend Helm chart
  - `/charts/todo-backend` - Backend Helm chart
  - `/charts/postgres` - PostgreSQL Helm chart (or dependency on bitnami/postgresql)
- `/specs` - Feature specifications and design documents
- `/shared` - Shared types and utilities (if needed)
- `docker-compose.yml` - Retained for local non-Kubernetes development
- Separate CLAUDE.md files at root, `/frontend`, and `/backend` for domain-specific guidance.

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
- PostgreSQL (local via Helm in Phase IV, NOT Neon)
- JWT verification middleware
- Proper CORS configuration for frontend communication
- Environment-based configuration for all secrets (via Kubernetes Secrets in K8s context)
- **Cohere Python SDK** for AI capabilities (NOT OpenAI)
- Tool calling via Cohere's chat API with tool_use support

### X. Development Workflow
- Follow spec-driven development: **spec → clarify → plan → tasks → agent implementation prompts**
- No manual coding outside of Claude Code agent prompts
- All code MUST pass type checking (mypy/TypeScript compiler) and linting
- Pull requests require code review and passing tests
- Contract tests for API endpoints (backend testing frontend contracts)
- Integration tests for user journeys (including chatbot flows)
- Docker Compose for local development environment (non-K8s)
- **AI-Assisted DevOps**: Use Gordon (Docker AI), kubectl-ai, and kagent for intelligent infrastructure management

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
The chatbot architecture MUST be fully stateless on the server side.

**State Management Rules:**
- Conversation state lives ONLY in the database (Conversation + Message tables)
- Each chat request MUST load conversation history from database
- Each response MUST persist the new messages to database
- No in-memory conversation caching between requests
- Conversation MUST be scoped to authenticated user (user_id foreign key)

**Database Schema Additions:**
- `Conversation` table: id, user_id, created_at, updated_at, title (optional)
- `Message` table: id, conversation_id, role (user/assistant/tool), content, tool_calls (JSON), created_at

### XIII. MCP Tools Architecture
Task operations MUST be exposed as MCP-style tools callable by the Cohere chat agent.

**Required Tools:**
- `add_task` - Create a new task for the authenticated user
- `list_tasks` - List tasks with optional filters (priority, tags, status, search)
- `complete_task` - Mark a task as completed (handles recurring task regeneration)
- `delete_task` - Delete a task
- `update_task` - Update task properties (title, description, priority, tags, due_date)

**Tool Security Rules:**
- Every tool MUST receive `user_id` from the authenticated JWT (NOT from user input)
- Every database query within tools MUST filter by `user_id`
- Tools MUST NOT allow cross-user access under any circumstances
- Tool responses MUST be sanitized before returning to the chat model

### XIV. Environment Variables and Secrets (Phase IV)

**New/Updated Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string (local PostgreSQL in Kubernetes, NOT Neon)
- `COHERE_API_KEY` - API key for Cohere AI services (REQUIRED)
- `BETTER_AUTH_SECRET` - Shared secret for JWT verification
- `FRONTEND_URL` - Frontend origin for CORS configuration

**Kubernetes Secrets Management:**
- Sensitive values MUST be stored in Kubernetes Secrets
- Helm values.yaml MUST support secret references
- NEVER commit plaintext secrets to repository

**Forbidden Environment Variables:**
- `OPENAI_API_KEY` - MUST NOT be used or referenced in Phase IV

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
- Retain `docker-compose.yml` for quick local development
- Suitable for rapid iteration without Kubernetes overhead
- Use local PostgreSQL container or SQLite for simplicity

**Kubernetes Deployment (Minikube + Helm):**
- Production-like environment for testing
- Full Helm chart deployment
- Persistent volumes for data durability
- Service discovery via Kubernetes DNS

**Testing Approach:**
- `kubectl port-forward` for accessing services
- `kubectl describe` and `kubectl logs` for debugging
- `helm test` for chart validation
- Integration tests against Kubernetes-deployed services

## Deliverables Structure

- Monorepo root with `.spec-kit/config.yaml` (if using Spec-Kit)
- Organized `/specs` folder: overview, features, api, database, ui
- Separate CLAUDE.md files at root, `/frontend`, and `/backend`
- `/charts` directory with Helm charts for all services
- Dockerfiles in `/frontend` and `/backend` directories
- `docker-compose.yml` for local development (non-K8s)
- Minikube setup scripts (e.g., `scripts/minikube-setup.sh`)
- Final `README.md` with:
  - Architecture overview
  - Docker Compose run instructions
  - Minikube + Helm deployment instructions
  - kubectl-ai and kagent usage examples
  - Gordon commands (or fallback)
  - Troubleshooting section

## Technology Stack (Non-Negotiable)

### Frontend
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth
- OpenAI ChatKit (or equivalent chat UI library)

### Backend
- FastAPI (SAME existing application)
- SQLModel
- PostgreSQL (local via Helm, NOT Neon in Phase IV)
- **Cohere Python SDK** (NOT OpenAI)

### Shared
- JWT authentication (Better Auth ↔ FastAPI)
- BETTER_AUTH_SECRET environment variable

### AI Integration
- Cohere API for chat and tool calling
- COHERE_API_KEY environment variable
- Agent patterns inspired by OpenAI Agents SDK (implemented via Cohere)

### Infrastructure (Phase IV)
- Docker for containerization
- Docker AI Agent (Gordon) for intelligent Dockerfile management
- Minikube for local Kubernetes cluster
- Helm 3+ for Kubernetes package management
- kubectl for cluster interaction
- kubectl-ai for AI-assisted Kubernetes operations
- kagent for intelligent monitoring and optimization

## Governance

This constitution governs all development decisions for the Todo application. All code MUST comply with these principles. Amendments require documentation and team approval. All pull requests MUST verify compliance with these principles before merging.

**Version**: 4.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2026-02-06

---

## Differences from Phase III (Key Phase IV Changes)

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

| Aspect | Phase I (Console) | Phase II (Web) | Phase III (AI Chatbot) | Phase IV (K8s Deploy) |
|--------|-------------------|----------------|------------------------|------------------------|
| **Architecture** | Single-process CLI | Full-stack web (monorepo) | Full-stack + AI chatbot | Cloud-native local K8s |
| **Frontend** | None (console only) | Next.js 16+ with App Router | Next.js + ChatKit UI | SAME (containerized) |
| **Backend** | In-process Python | FastAPI REST API | SAME + chat endpoint | SAME (containerized) |
| **Database** | In-memory Python dict | Neon Serverless PostgreSQL | SAME Neon + chat tables | Local PostgreSQL (Helm) |
| **Authentication** | None (single-user) | JWT + Better Auth | SAME | SAME (K8s Secrets) |
| **User Isolation** | N/A | Mandatory per-user | SAME + tool enforcement | SAME |
| **UI** | Text-based argparse | Tailwind CSS web | Web UI + chat | SAME |
| **AI Provider** | N/A | N/A | Cohere API | SAME (Cohere) |
| **Deployment** | Local run | Docker Compose | SAME | Minikube + Helm |
| **Orchestration** | N/A | Docker Compose | Docker Compose | Kubernetes |
| **Packaging** | pip install | docker-compose.yml | docker-compose.yml | Helm Charts |
| **Infrastructure Tools** | N/A | Docker | Docker | Docker + Gordon + kubectl-ai + kagent |
| **Config Management** | CLI args | .env files | .env files | ConfigMaps + Secrets |
| **Service Discovery** | N/A | Docker network | Docker network | Kubernetes DNS |
| **Scaling** | N/A | Manual | Manual | K8s replicas |
| **Health Checks** | N/A | Manual | Manual | K8s probes |
| **Type Safety** | Python type hints | TypeScript + Python | SAME | SAME |
| **Testing** | Unit tests only | Contract + integration | + chatbot tests | + K8s integration |
| **Dependencies** | Standard library | Full npm/pip | + cohere SDK | + Helm charts |
