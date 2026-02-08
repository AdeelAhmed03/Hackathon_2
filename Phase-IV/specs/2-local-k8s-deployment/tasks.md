# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/2-local-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Branch**: `002-local-k8s-deployment`
**Date**: 2026-02-06

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (FastAPI)
- **Frontend**: `frontend/` (Next.js)
- **Charts**: `charts/` (Helm)
- **Scripts**: `scripts/` (Deployment automation)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and base configuration files

- [x] T001 Create charts/ directory structure with todo-backend/, todo-frontend/, postgres/ subdirectories
- [x] T002 Create scripts/ directory with placeholder files for minikube-setup.sh, deploy.sh, build-images.sh, teardown.sh
- [x] T003 [P] Create backend/.dockerignore with exclusions for __pycache__, .env, .git, tests/, *.pyc
- [x] T004 [P] Create frontend/.dockerignore with exclusions for node_modules/, .next/, .env, .git

**Checkpoint**: Directory structure ready for Dockerfile and Helm chart creation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core containerization and Helm scaffolding that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Dockerfiles (Required for all deployments)

- [x] T005 Create backend/Dockerfile with multi-stage build (python:3.13-slim base, non-root user uid 1001, EXPOSE 8000)
- [x] T006 Create frontend/Dockerfile with multi-stage build (node:18-alpine → nginx:alpine, non-root user, EXPOSE 3000)
- [x] T007 [P] Create frontend/nginx.conf with proxy configuration for Next.js static export serving on port 3000

### Helm Chart Scaffolding

- [x] T008 Create charts/postgres/Chart.yaml with name: postgres, version: 0.1.0, appVersion: "16"
- [x] T009 Create charts/postgres/values.yaml with image, service, secrets, persistence, resources, probes configuration
- [x] T010 [P] Create charts/postgres/templates/_helpers.tpl with standard Helm helper functions
- [x] T011 Create charts/todo-backend/Chart.yaml with name: todo-backend, version: 0.1.0
- [x] T012 Create charts/todo-backend/values.yaml with image, service, secrets, config, resources, probes configuration
- [x] T013 [P] Create charts/todo-backend/templates/_helpers.tpl with standard Helm helper functions
- [x] T014 Create charts/todo-frontend/Chart.yaml with name: todo-frontend, version: 0.1.0
- [x] T015 Create charts/todo-frontend/values.yaml with image, service, config, resources, probes configuration
- [x] T016 [P] Create charts/todo-frontend/templates/_helpers.tpl with standard Helm helper functions

### Backend Health Endpoint

- [x] T017 Add /health endpoint to backend/src/main.py returning {"status": "healthy"} for K8s probes (already existed)

**Checkpoint**: Foundation ready - Dockerfiles and Helm scaffolding complete

---

## Phase 3: User Story 2 - Secure Container Images (Priority: P1)

**Goal**: Build secure, production-ready container images with non-root users and minimal base images

**Independent Test**: Build images and verify they run as non-root, check image sizes

### Implementation for User Story 2

- [x] T018 [US2] Update backend/Dockerfile to add RUN useradd -r -u 1001 appuser and USER appuser directives
- [x] T019 [US2] Update frontend/Dockerfile to add RUN adduser -D -u 1001 appuser and USER appuser directives
- [x] T020 [P] [US2] Create scripts/build-images.sh with docker build commands for backend and frontend (tags: v4.0.0)
- [ ] T021 [US2] Test backend Dockerfile builds successfully with `docker build -t todo-backend:v4.0.0 ./backend`
- [ ] T022 [US2] Test frontend Dockerfile builds successfully with `docker build -t todo-frontend:v4.0.0 ./frontend`
- [ ] T023 [US2] Verify backend container runs as non-root with `docker run todo-backend:v4.0.0 id` (should show uid 1001)
- [ ] T024 [US2] Verify frontend container runs as non-root with `docker run todo-frontend:v4.0.0 id` (should show uid 1001)
- [ ] T025 [US2] Verify backend image size is under 300MB with `docker images todo-backend:v4.0.0`
- [ ] T026 [US2] Verify frontend image size is under 500MB with `docker images todo-frontend:v4.0.0`

**Checkpoint**: Secure container images built and verified

---

## Phase 4: User Story 6 - Configuration Management (Priority: P2)

**Goal**: Manage secrets and configuration via Kubernetes Secrets and ConfigMaps

**Independent Test**: Deploy with different configurations and verify secrets are not exposed

### Implementation for User Story 6

- [x] T027 [US6] Create charts/postgres/templates/secret.yaml with POSTGRES_PASSWORD from .Values.secrets.postgresPassword
- [x] T028 [US6] Create charts/todo-backend/templates/secret.yaml with COHERE_API_KEY, BETTER_AUTH_SECRET, DATABASE_URL
- [x] T029 [P] [US6] Create charts/todo-backend/templates/configmap.yaml with PORT, FRONTEND_URL from .Values.config
- [x] T030 [P] [US6] Create charts/todo-frontend/templates/configmap.yaml with NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_BASE_URL
- [x] T031 [US6] Update charts/todo-backend/values.yaml secrets section with placeholder comments (never commit real values)
- [x] T032 [US6] Update charts/postgres/values.yaml secrets section with placeholder comments

**Checkpoint**: Secrets and ConfigMaps templates ready

---

## Phase 5: User Story 3 - Data Persistence Across Restarts (Priority: P2)

**Goal**: Implement PersistentVolumeClaim for PostgreSQL data durability

**Independent Test**: Create data, restart pod, verify data persists

### Implementation for User Story 3

- [x] T033 [US3] Create charts/postgres/templates/pvc.yaml with 1Gi storage, ReadWriteOnce, storageClassName: standard
- [x] T034 [US3] Create charts/postgres/templates/deployment.yaml with volumeMounts for /var/lib/postgresql/data
- [x] T035 [US3] Create charts/postgres/templates/service.yaml with ClusterIP type, port 5432
- [x] T036 [US3] Update charts/postgres/values.yaml persistence section with enabled: true, size: 1Gi

**Checkpoint**: PostgreSQL with persistent storage ready

---

## Phase 6: User Story 4 - Service Health Monitoring (Priority: P2)

**Goal**: Configure liveness and readiness probes for automatic failure detection and recovery

**Independent Test**: Simulate failure and verify automatic restart within 60 seconds

### Implementation for User Story 4

- [x] T037 [US4] Create charts/todo-backend/templates/deployment.yaml with livenessProbe (httpGet /health, initialDelaySeconds: 30)
- [x] T038 [US4] Update charts/todo-backend/templates/deployment.yaml with readinessProbe (httpGet /health, initialDelaySeconds: 5)
- [x] T039 [US4] Create charts/todo-backend/templates/service.yaml with ClusterIP type, port 8000
- [x] T040 [US4] Create charts/todo-frontend/templates/deployment.yaml with livenessProbe (httpGet /, initialDelaySeconds: 15)
- [x] T041 [US4] Update charts/todo-frontend/templates/deployment.yaml with readinessProbe (httpGet /, initialDelaySeconds: 5)
- [x] T042 [US4] Create charts/todo-frontend/templates/service.yaml with ClusterIP type, port 3000
- [x] T043 [US4] Update charts/postgres/templates/deployment.yaml with livenessProbe (exec pg_isready, initialDelaySeconds: 30)
- [x] T044 [US4] Update charts/postgres/templates/deployment.yaml with readinessProbe (exec pg_isready, initialDelaySeconds: 5)

**Checkpoint**: All services have health probes configured

---

## Phase 7: User Story 1 - One-Command Full Stack Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy entire stack with single command, verify chatbot works end-to-end

**Independent Test**: Run deploy script, access frontend, send chat message, verify AI response

### Implementation for User Story 1

- [x] T045 [US1] Create scripts/minikube-setup.sh with minikube start --memory=4096 --cpus=2, addons enable ingress
- [x] T046 [US1] Update scripts/build-images.sh to use eval $(minikube docker-env) before building
- [x] T047 [US1] Create scripts/deploy.sh with kubectl create namespace, helm install postgres, wait, helm install backend, helm install frontend
- [x] T048 [US1] Create scripts/teardown.sh with helm uninstall commands and kubectl delete namespace
- [x] T049 [US1] Add envFrom secretRef and configMapRef to charts/todo-backend/templates/deployment.yaml
- [x] T050 [US1] Add envFrom configMapRef to charts/todo-frontend/templates/deployment.yaml
- [x] T051 [US1] Add securityContext runAsNonRoot: true, runAsUser: 1001 to all deployment templates
- [x] T052 [US1] Add resource requests (256Mi/100m) and limits (512Mi/500m) to backend deployment
- [x] T053 [US1] Add resource requests (128Mi/50m) and limits (256Mi/200m) to frontend deployment
- [x] T054 [US1] Add resource requests (256Mi/100m) and limits (512Mi/500m) to postgres deployment

### End-to-End Verification

- [ ] T055 [US1] Run scripts/minikube-setup.sh and verify cluster starts successfully
- [ ] T056 [US1] Run scripts/build-images.sh and verify images are built in Minikube's Docker
- [ ] T057 [US1] Run scripts/deploy.sh with test secrets and verify all pods reach Running status
- [ ] T058 [US1] Port-forward frontend (kubectl port-forward svc/todo-frontend 3000:3000) and verify login page loads
- [ ] T059 [US1] Create user account, login, send chat message "Add a task to buy milk", verify AI response and task creation

**Checkpoint**: Full stack deployment working end-to-end

---

## Phase 8: User Story 5 - AI-Assisted Troubleshooting (Priority: P3)

**Goal**: Document AI DevOps tools usage for debugging and optimization

**Independent Test**: Use kubectl-ai to diagnose issue, use kagent for health analysis

### Implementation for User Story 5

- [x] T060 [P] [US5] Add Gordon usage examples to README.md (docker ai build, docker ai scan commands)
- [x] T061 [P] [US5] Add kubectl-ai usage examples to README.md (manifest generation, debugging commands)
- [x] T062 [P] [US5] Add kagent usage examples to README.md (health analysis, scaling recommendations)
- [x] T063 [US5] Create troubleshooting section in README.md with common issues and AI tool diagnosis commands
- [x] T064 [US5] Document fallback commands (standard kubectl) for when AI tools are unavailable

**Checkpoint**: AI DevOps documentation complete

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, cleanup, and validation

- [x] T065 Update README.md with Phase IV deployment section (prerequisites, quick start, Helm commands)
- [x] T066 Add .helmignore files to each chart directory (exclude .git, *.md, tests/)
- [x] T067 [P] Verify all Helm charts pass `helm lint ./charts/<chart-name>` (fixed .helmignore files)
- [x] T068 [P] Verify all Helm charts render correctly with `helm template <name> ./charts/<chart-name>`
- [x] T069 Update CLAUDE.md with Phase IV Kubernetes deployment guidance
- [ ] T070 Run full end-to-end test: fresh minikube → deploy → chatbot test → teardown
- [x] T071 Update specs/2-local-k8s-deployment/quickstart.md with any discovered corrections

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────┐
                                 │
Phase 2 (Foundational) ◄─────────┘
         │
         ├──► Phase 3 (US2: Secure Images) ──┐
         │                                    │
         ├──► Phase 4 (US6: Config Mgmt) ────┼──► Phase 7 (US1: Deployment) 🎯
         │                                    │
         ├──► Phase 5 (US3: Persistence) ────┤
         │                                    │
         └──► Phase 6 (US4: Health) ─────────┘
                                              │
Phase 8 (US5: AI Tools) ◄─────────────────────┘
         │
Phase 9 (Polish) ◄────────────────────────────┘
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US2 (Secure Images) | Phase 2 | T017 complete |
| US6 (Config Mgmt) | Phase 2 | T017 complete |
| US3 (Persistence) | Phase 2 | T017 complete |
| US4 (Health) | Phase 2, US3 | T036 complete |
| US1 (Deployment) | US2, US3, US4, US6 | T044 complete |
| US5 (AI Tools) | US1 | T059 complete |

### Parallel Opportunities

**Within Phase 2:**
```bash
# These can run in parallel:
T003 & T004  # .dockerignore files
T010 & T013 & T016  # _helpers.tpl files
```

**Within Phase 3 (US2):**
```bash
# These can run in parallel:
T018 & T019  # Dockerfile user additions
```

**Within Phase 4 (US6):**
```bash
# These can run in parallel:
T029 & T030  # ConfigMap templates
```

**Within Phase 8 (US5):**
```bash
# These can run in parallel:
T060 & T061 & T062  # README documentation sections
```

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**User Story 1 (Full Stack Deployment)** is the MVP, but requires:
1. ✅ Secure container images (US2)
2. ✅ Configuration management (US6)
3. ✅ Data persistence (US3)
4. ✅ Health monitoring (US4)

**Recommended Order**: US2 → US6 → US3 → US4 → US1

### Incremental Delivery

| Increment | Stories | Deliverable |
|-----------|---------|-------------|
| 1 | US2 | Buildable, secure Docker images |
| 2 | US6 | Secrets and ConfigMaps templates |
| 3 | US3 | PostgreSQL with persistent storage |
| 4 | US4 | All services with health probes |
| 5 | US1 | Complete deployable stack (MVP) |
| 6 | US5 | AI DevOps documentation |

---

## Task Summary

| Phase | Task Count | Parallel Tasks |
|-------|------------|----------------|
| Phase 1 (Setup) | 4 | 2 |
| Phase 2 (Foundational) | 13 | 4 |
| Phase 3 (US2) | 9 | 1 |
| Phase 4 (US6) | 6 | 2 |
| Phase 5 (US3) | 4 | 0 |
| Phase 6 (US4) | 8 | 0 |
| Phase 7 (US1) | 15 | 0 |
| Phase 8 (US5) | 5 | 3 |
| Phase 9 (Polish) | 7 | 2 |
| **Total** | **71** | **14** |

### Tasks by User Story

| User Story | Task Count | Task Range |
|------------|------------|------------|
| US1 (Deployment) | 15 | T045-T059 |
| US2 (Secure Images) | 9 | T018-T026 |
| US3 (Persistence) | 4 | T033-T036 |
| US4 (Health) | 8 | T037-T044 |
| US5 (AI Tools) | 5 | T060-T064 |
| US6 (Config Mgmt) | 6 | T027-T032 |
