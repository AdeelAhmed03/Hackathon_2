# Implementation Plan: Local Kubernetes Deployment

**Branch**: `002-local-k8s-deployment` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/2-local-k8s-deployment/spec.md`

## Summary

Deploy the Phase III AI-powered Todo chatbot to a local Kubernetes cluster using Minikube. This involves containerizing both frontend (Next.js) and backend (FastAPI + Cohere), creating production-grade Helm charts, implementing persistent storage for PostgreSQL, and integrating AI-assisted DevOps tools (Gordon, kubectl-ai, kagent) for intelligent infrastructure management.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 18+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Cohere SDK, Next.js 16+, Tailwind CSS, Better Auth
**Infrastructure**: Minikube, Helm 3+, kubectl, Docker
**Storage**: PostgreSQL (local via Helm chart with PVC)
**Testing**: pytest (backend), Jest (frontend), manual K8s validation
**Target Platform**: Local Kubernetes (Minikube single-node)
**Project Type**: Web application (monorepo with frontend + backend + charts)
**Performance Goals**: All services running in <5 minutes, chatbot response <5 seconds
**Constraints**: 4GB RAM minimum, local-only (no cloud resources)
**Scale/Scope**: Single developer local deployment, 1-2 pod replicas per service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Following spec → plan → tasks workflow |
| II. Clean Code and Type Safety | ✅ PASS | TypeScript frontend, Python type hints backend |
| III. Multi-User Security Isolation | ✅ PASS | user_id filtering preserved in K8s deployment |
| IV. Authentication and Authorization | ✅ PASS | JWT auth via K8s Secrets |
| V. Persistent Storage with SQLModel | ✅ PASS | PostgreSQL via Helm with PVC |
| VII. Monorepo Structure | ✅ PASS | Adding /charts directory per constitution |
| IX. Backend Technology Standards | ✅ PASS | Cohere SDK (NOT OpenAI) per constitution |
| X. Development Workflow | ✅ PASS | AI-assisted DevOps tools (Gordon, kubectl-ai, kagent) |
| XI. AI Chatbot Integration (Cohere) | ✅ PASS | Cohere-only, no OpenAI |
| XV. Containerization Standards | ✅ PASS | Multi-stage, non-root, minimal images |
| XVI. Kubernetes Architecture | ✅ PASS | Minikube + Helm per constitution |
| XVII. Helm Charts Architecture | ✅ PASS | Separate charts for frontend, backend, postgres |

**All gates pass. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/2-local-k8s-deployment/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (infrastructure model)
├── quickstart.md        # Phase 1 output (deployment guide)
├── contracts/           # Phase 1 output (Helm value schemas)
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
Phase-IV/
├── backend/
│   ├── src/                    # Existing FastAPI application
│   ├── Dockerfile              # NEW: Multi-stage production build
│   ├── .dockerignore           # NEW: Exclude unnecessary files
│   └── requirements.txt
├── frontend/
│   ├── src/                    # Existing Next.js application
│   ├── Dockerfile              # NEW: Multi-stage build (node → nginx)
│   ├── .dockerignore           # NEW: Exclude unnecessary files
│   ├── nginx.conf              # NEW: Production nginx config
│   └── package.json
├── charts/                     # NEW: Helm charts directory
│   ├── todo-backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── configmap.yaml
│   │       ├── secret.yaml
│   │       └── _helpers.tpl
│   ├── todo-frontend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── configmap.yaml
│   │       └── _helpers.tpl
│   └── postgres/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── pvc.yaml
│           ├── secret.yaml
│           └── _helpers.tpl
├── scripts/                    # NEW: Deployment scripts
│   ├── minikube-setup.sh       # Minikube initialization
│   ├── deploy.sh               # Full deployment script
│   ├── build-images.sh         # Docker build script
│   └── teardown.sh             # Cleanup script
├── docker-compose.yml          # EXISTING: Local non-K8s development
└── .specify/                   # Spec-Kit configuration
```

**Structure Decision**: Web application with separate Helm charts for each service. Charts are kept separate (not umbrella) for independent versioning and deployment flexibility.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MINIKUBE CLUSTER                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                         INGRESS CONTROLLER                          │ │
│  │                    (minikube ingress addon)                         │ │
│  └────────────────────────────┬───────────────────────────────────────┘ │
│                               │                                          │
│         ┌─────────────────────┴─────────────────────┐                   │
│         ▼                                           ▼                    │
│  ┌─────────────────┐                      ┌─────────────────┐           │
│  │   todo-frontend │                      │   todo-backend  │           │
│  │   (Next.js)     │                      │   (FastAPI)     │           │
│  │   Service:3000  │                      │   Service:8000  │           │
│  └────────┬────────┘                      └────────┬────────┘           │
│           │                                        │                     │
│           │                  ┌─────────────────────┘                     │
│           │                  │                                           │
│           │                  ▼                                           │
│           │         ┌─────────────────┐                                  │
│           │         │    postgres     │                                  │
│           │         │  Service:5432   │                                  │
│           │         └────────┬────────┘                                  │
│           │                  │                                           │
│           │                  ▼                                           │
│           │         ┌─────────────────┐                                  │
│           │         │      PVC        │                                  │
│           │         │  (postgres-data)│                                  │
│           │         └─────────────────┘                                  │
│           │                                                              │
│           │         ┌─────────────────┐                                  │
│           └────────►│  ConfigMaps     │◄────────────────────────────────┤
│                     │  + Secrets      │                                  │
│                     └─────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │   Cohere API    │
                    │   (External)    │
                    └─────────────────┘
```

---

## Phase 0: Research

### R1: Cohere Tool Calling Support

**Decision**: Use Cohere Python SDK (`cohere`) with native tool calling support

**Rationale**:
- Cohere's Chat API supports `tools` parameter for function definitions
- Response includes `tool_calls` array when tools should be invoked
- Compatible with existing MCP-style tool pattern from Phase III

**Implementation Pattern**:
```python
import cohere

client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

response = client.chat(
    message=user_message,
    chat_history=history,
    tools=MCP_TOOL_DEFINITIONS,
    preamble=SYSTEM_PROMPT
)

if response.tool_calls:
    # Execute tools and continue conversation
    for tool_call in response.tool_calls:
        result = execute_mcp_tool(tool_call.name, tool_call.parameters, user_id)
```

**Alternatives Considered**:
- OpenAI SDK wrapper → Rejected (violates constitution XI)
- Custom HTTP client → Rejected (unnecessary complexity)

### R2: Multi-Stage Dockerfile Patterns

**Decision**: Use Node.js build stage → nginx serve for frontend, Python slim base for backend

**Frontend Dockerfile Pattern**:
```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
RUN adduser -D -u 1001 appuser && chown -R appuser:appuser /usr/share/nginx/html
USER appuser
EXPOSE 3000
```

**Backend Dockerfile Pattern**:
```dockerfile
# Stage 1: Dependencies
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY src/ ./src/
RUN useradd -r -u 1001 appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Rationale**:
- Multi-stage reduces image size (no build tools in production)
- Non-root user (uid 1001) for security
- Alpine/slim bases for minimal attack surface

### R3: Helm Chart Structure

**Decision**: Separate charts (not umbrella) for frontend, backend, postgres

**Rationale**:
- Independent versioning per service
- Simpler upgrades (can upgrade backend without touching frontend)
- Easier debugging (isolate issues to specific chart)
- Aligns with constitution XVII

**Chart Dependency**:
- `todo-backend` depends on `postgres` (DATABASE_URL)
- `todo-frontend` depends on `todo-backend` (API endpoint)
- Deploy order: postgres → backend → frontend

### R4: Kubernetes Secret Management

**Decision**: Use Kubernetes Secrets for sensitive values, ConfigMaps for non-sensitive

| Value | Resource Type | Notes |
|-------|---------------|-------|
| COHERE_API_KEY | Secret | API key for AI |
| BETTER_AUTH_SECRET | Secret | JWT signing key |
| DATABASE_URL | Secret | Contains password |
| POSTGRES_PASSWORD | Secret | Database password |
| FRONTEND_URL | ConfigMap | CORS origin |
| PORT | ConfigMap | Service ports |

**Helm Values Pattern**:
```yaml
# values.yaml
secrets:
  cohereApiKey: ""      # Set via --set or values override
  betterAuthSecret: ""  # Set via --set or values override
  databaseUrl: "postgresql://postgres:password@postgres:5432/todo"

config:
  frontendUrl: "http://todo-frontend:3000"
  port: 8000
```

### R5: AI DevOps Tools Integration

**Gordon (Docker AI)**:
```bash
# Generate optimized Dockerfile
docker ai build --suggest ./backend

# Security scan
docker ai scan todo-backend:v4.0.0

# Compose to K8s hints
docker ai convert docker-compose.yml --output k8s-hints.yaml
```

**kubectl-ai**:
```bash
# Generate deployment manifest
kubectl-ai "create deployment for fastapi backend with 2 replicas, 256Mi memory, health checks on /health"

# Debug pod issues
kubectl-ai "why is todo-backend-xxx in CrashLoopBackOff"

# Resource optimization
kubectl-ai "suggest resource limits for todo-app namespace based on current usage"
```

**kagent**:
```bash
# Health analysis
kagent health --namespace todo-app

# Scaling recommendations
kagent scale --analyze todo-backend

# Log diagnosis
kagent logs --diagnose todo-backend --last 1h
```

---

## Phase 1: Design & Contracts

### Infrastructure Model (data-model.md)

See [data-model.md](./data-model.md) for full Kubernetes resource specifications.

### Helm Values Schema (contracts/)

See [contracts/](./contracts/) for Helm values.yaml schemas for each chart.

### Deployment Guide (quickstart.md)

See [quickstart.md](./quickstart.md) for step-by-step deployment instructions.

---

## Deployment Sequence

```bash
# 1. Start Minikube
minikube start --memory=4096 --cpus=2

# 2. Enable Ingress
minikube addons enable ingress

# 3. Use Minikube's Docker daemon
eval $(minikube docker-env)

# 4. Build images
docker build -t todo-backend:v4.0.0 ./backend
docker build -t todo-frontend:v4.0.0 ./frontend

# 5. Create namespace
kubectl create namespace todo-app

# 6. Deploy PostgreSQL
helm install postgres ./charts/postgres -n todo-app

# 7. Wait for PostgreSQL
kubectl wait --for=condition=ready pod -l app=postgres -n todo-app --timeout=120s

# 8. Deploy Backend
helm install todo-backend ./charts/todo-backend -n todo-app \
  --set secrets.cohereApiKey="$COHERE_API_KEY" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET"

# 9. Deploy Frontend
helm install todo-frontend ./charts/todo-frontend -n todo-app

# 10. Verify deployment
kubectl get pods -n todo-app

# 11. Access via port-forward or ingress
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app
```

---

## Troubleshooting Guide

### Common Issues

| Symptom | Likely Cause | Diagnosis | Resolution |
|---------|--------------|-----------|------------|
| Pod in `Pending` | Insufficient resources | `kubectl describe pod <name>` | Increase Minikube memory/CPU |
| Pod in `CrashLoopBackOff` | App startup failure | `kubectl logs <pod> --previous` | Check env vars, DB connection |
| Service unreachable | Endpoint not ready | `kubectl get endpoints` | Wait for readiness probe |
| Ingress 404 | Path mismatch | `kubectl describe ingress` | Check ingress rules |
| Database connection refused | Postgres not ready | `kubectl logs -l app=postgres` | Wait for postgres pod ready |

### AI-Assisted Debugging

```bash
# Use kubectl-ai for diagnosis
kubectl-ai "why is my todo-backend pod crashing?"

# Use kagent for health check
kagent health todo-backend -n todo-app

# View resource usage
kubectl top pods -n todo-app
```

---

## Complexity Tracking

No constitution violations. All design decisions align with Phase IV constitution principles.

---

## Next Steps

1. Run `/sp.tasks` to generate task breakdown
2. Implement Dockerfiles (backend, frontend)
3. Create Helm charts (postgres, backend, frontend)
4. Write deployment scripts
5. Update documentation with AI tool examples
