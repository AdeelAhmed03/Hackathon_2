# Tasks: Event-Driven Cloud Todo Application (Phase V)

**Input**: Design documents from `/specs/001-event-driven-cloud/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Branch**: `001-event-driven-cloud`
**Total Tasks**: 98

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3...)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` (FastAPI services)
- **Frontend**: `frontend/src/` (Next.js)
- **Notification Service**: `notification-service/src/`
- **Recurring Service**: `recurring-service/src/`
- **Dapr Components**: `dapr-components/`
- **Helm Charts**: `charts/`
- **CI/CD**: `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, Dapr components, and microservice scaffolding

- [x] T001 Create dapr-components/ directory structure per plan.md
- [x] T002 [P] Create kafka-pubsub-local.yaml for Strimzi in dapr-components/kafka-pubsub-local.yaml
- [x] T003 [P] Create kafka-pubsub-cloud.yaml for Redpanda Cloud in dapr-components/kafka-pubsub-cloud.yaml
- [x] T004 [P] Create kubernetes-secrets.yaml Dapr component in dapr-components/kubernetes-secrets.yaml
- [x] T005 [P] Create strimzi/kafka-cluster.yaml with KRaft mode (no Zookeeper) in dapr-components/strimzi/kafka-cluster.yaml
- [x] T006 Create notification-service/ project scaffold with FastAPI in notification-service/
- [x] T007 [P] Create notification-service/requirements.txt with fastapi, httpx, uvicorn
- [x] T008 [P] Create notification-service/Dockerfile with multi-stage build
- [x] T009 Create recurring-service/ project scaffold with FastAPI in recurring-service/
- [x] T010 [P] Create recurring-service/requirements.txt with fastapi, httpx, uvicorn
- [x] T011 [P] Create recurring-service/Dockerfile with multi-stage build
- [x] T012 [P] Create charts/notification-service/ Helm chart structure
- [x] T013 [P] Create charts/recurring-service/ Helm chart structure
- [x] T014 Create .github/workflows/ directory for CI/CD pipelines

**Checkpoint**: Dapr components and service scaffolds ready - foundation can begin

---

## Phase 2: Foundational (Database Schema & Core Infrastructure)

**Purpose**: Database migration, event publishing framework, and Dapr integration that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema Migration

- [x] T015 Add priority enum to Task model (low/medium/high) in backend/src/models/task.py
- [x] T016 Add due_at nullable datetime field to Task model in backend/src/models/task.py
- [x] T017 Add remind_at nullable datetime field to Task model in backend/src/models/task.py
- [x] T018 Add recurring_interval nullable enum (daily/weekly/monthly/yearly) to Task model in backend/src/models/task.py
- [x] T019 Add parent_task_id nullable FK to Task model in backend/src/models/task.py
- [x] T020 [P] Create Tag model with id, user_id, name, created_at in backend/src/models/tag.py
- [x] T021 [P] Create TaskTag junction model with task_id, tag_id in backend/src/models/task_tag.py
- [x] T022 [P] Create Event schema model for Kafka messages in backend/src/models/event.py
- [x] T023 Create Alembic migration script v5_schema_update.py in backend/migrations/v5_schema_update.py
- [x] T024 Run migration and verify schema in PostgreSQL

### Dapr Event Publishing Framework

- [x] T025 Create event_publisher.py with Dapr Pub/Sub HTTP client in backend/src/services/event_publisher.py
- [x] T026 Implement publish_task_event() for task-events topic in backend/src/services/event_publisher.py
- [x] T027 Implement publish_reminder_event() for reminders topic in backend/src/services/event_publisher.py
- [x] T028 Create Dapr subscription endpoint /dapr/subscribe in backend/src/api/dapr_subscriptions.py

### Dapr Jobs API Framework

- [x] T029 Create job_scheduler.py with Dapr Jobs API HTTP client in backend/src/services/job_scheduler.py
- [x] T030 Implement schedule_reminder_job() for exact-time scheduling in backend/src/services/job_scheduler.py
- [x] T031 Implement cancel_reminder_job() for job cancellation in backend/src/services/job_scheduler.py
- [x] T032 Create Jobs API callback endpoint /jobs/callback in backend/src/api/jobs_callback.py

### Helm Chart Updates for Dapr

- [x] T033 Update charts/todo-backend/templates/deployment.yaml with Dapr sidecar annotations
- [x] T034 [P] Update charts/todo-frontend/templates/deployment.yaml with Dapr annotations
- [x] T035 [P] Create charts/notification-service/templates/deployment.yaml with Dapr annotations
- [x] T036 [P] Create charts/recurring-service/templates/deployment.yaml with Dapr annotations
- [x] T037 Create charts/notification-service/values.yaml with service configuration
- [x] T038 Create charts/recurring-service/values.yaml with service configuration

### Pydantic Schema Updates

- [x] T039 Create TaskCreate schema with new fields (priority, due_at, remind_at, recurring_interval, tags) in backend/src/schemas/task.py
- [x] T040 Create TaskUpdate schema with new fields in backend/src/schemas/task.py
- [x] T041 Create TaskResponse schema with new fields in backend/src/schemas/task.py
- [x] T042 [P] Create TagCreate and TagResponse schemas in backend/src/schemas/tag.py
- [x] T043 [P] Create TaskEvent and ReminderEvent schemas in backend/src/schemas/event.py

**Checkpoint**: Foundation ready - database migrated, event framework operational, Dapr integration complete

---

## Phase 3: User Story 1 - Recurring Task Management (Priority: P1) 🎯 MVP

**Goal**: Create recurring tasks that auto-spawn next instance on completion via event-driven architecture

**Independent Test**: Create daily recurring task, complete it, verify new task spawned with due_at = tomorrow

### Backend Implementation for US1

- [x] T044 [US1] Update task_service.py to handle recurring_interval field in backend/src/services/task_service.py
- [x] T045 [US1] Update complete_task() to publish task_completed event in backend/src/services/task_service.py
- [x] T046 [US1] Update create_task() to accept recurring_interval parameter in backend/src/services/task_service.py

### Recurring Service Implementation (US1)

- [x] T047 [US1] Create main.py with FastAPI app and Dapr subscription in recurring-service/src/main.py
- [x] T048 [US1] Create /dapr/subscribe endpoint for task-events topic in recurring-service/src/main.py
- [x] T049 [US1] Create task_completed_handler.py for processing events in recurring-service/src/handlers/task_completed_handler.py
- [x] T050 [US1] Implement task_spawner.py to create next recurring instance in recurring-service/src/services/task_spawner.py
- [x] T051 [US1] Add idempotency check using event key deduplication in recurring-service/src/services/task_spawner.py
- [x] T052 [US1] Implement calculate_next_due_date() for interval logic in recurring-service/src/services/task_spawner.py

### MCP Tools Update for US1

- [x] T053 [US1] Update add_task tool to accept recurring_interval parameter in backend/src/tools/mcp_tools.py
- [x] T054 [US1] Update complete_task tool to publish event on completion in backend/src/tools/mcp_tools.py
- [x] T055 [US1] Update list_tasks tool to show recurring_interval in response in backend/src/tools/mcp_tools.py

### Frontend for US1

- [x] T056 [P] [US1] Update Task TypeScript interface with recurring_interval in frontend/src/types/task.ts
- [x] T057 [US1] Add recurring interval selector to TaskForm.tsx in frontend/src/components/tasks/TaskForm.tsx
- [x] T058 [US1] Display recurring badge on task items in frontend/src/components/tasks/TaskItem.tsx

**Checkpoint**: Recurring tasks functional - complete task, new instance auto-created

---

## Phase 4: User Story 2 - Due Dates and Reminders (Priority: P1)

**Goal**: Set due dates with exact-time reminders via Dapr Jobs API and notification service

**Independent Test**: Create task with remind_at = 2 minutes from now, verify notification received at exact time

### Backend Implementation for US2

- [x] T059 [US2] Update create_task() to schedule reminder job when remind_at is set in backend/src/services/task_service.py
- [x] T060 [US2] Update update_task() to reschedule reminder on remind_at change in backend/src/services/task_service.py
- [x] T061 [US2] Update complete_task() to cancel reminder job on completion in backend/src/services/task_service.py
- [x] T062 [US2] Implement /jobs/callback handler to publish reminder_due event in backend/src/api/jobs_callback.py

### Notification Service Implementation (US2)

- [x] T063 [US2] Create main.py with FastAPI app and Dapr subscription in notification-service/src/main.py
- [x] T064 [US2] Create /dapr/subscribe endpoint for reminders topic in notification-service/src/main.py
- [x] T065 [US2] Create reminder_handler.py for processing reminder events in notification-service/src/handlers/reminder_handler.py
- [x] T066 [US2] Implement email_sender.py for email notifications in notification-service/src/services/email_sender.py
- [x] T067 [P] [US2] Implement push_sender.py for push notifications (optional) in notification-service/src/services/push_sender.py

### API Endpoint Updates for US2

- [x] T068 [US2] Update POST /api/tasks to accept due_at and remind_at in backend/src/api/tasks.py
- [x] T069 [US2] Update PUT /api/tasks/:id to handle due_at/remind_at updates in backend/src/api/tasks.py
- [x] T070 [US2] Add validation: remind_at must be before due_at in backend/src/schemas/task.py

### Frontend for US2

- [x] T071 [US2] Add datetime picker for due_at in TaskForm.tsx in frontend/src/components/tasks/TaskForm.tsx
- [x] T072 [US2] Add datetime picker for remind_at in TaskForm.tsx in frontend/src/components/tasks/TaskForm.tsx
- [x] T073 [US2] Display due date with relative time in TaskItem.tsx in frontend/src/components/tasks/TaskItem.tsx
- [x] T074 [US2] Add visual indicator for overdue tasks in frontend/src/components/tasks/TaskItem.tsx

**Checkpoint**: Reminders functional - notification delivered at exact remind_at time

---

## Phase 5: User Story 3 - Priority-Based Task Organization (Priority: P2)

**Goal**: Assign priorities (low/medium/high) and sort tasks by priority

**Independent Test**: Create tasks with different priorities, sort by priority, verify high appears first

### Backend Implementation for US3

- [x] T075 [US3] Add priority to TaskListQuery schema in backend/src/schemas/task.py
- [x] T076 [US3] Implement priority filter in list_tasks query in backend/src/services/task_service.py
- [x] T077 [US3] Implement priority-aware sorting (high=3, medium=2, low=1) in backend/src/services/task_service.py

### API Endpoint Updates for US3

- [x] T078 [US3] Add priority query parameter to GET /api/tasks in backend/src/api/tasks.py
- [x] T079 [US3] Add sort_by=priority option to GET /api/tasks in backend/src/api/tasks.py

### Frontend for US3

- [x] T080 [P] [US3] Create PriorityBadge.tsx component in frontend/src/components/tasks/PriorityBadge.tsx
- [x] T081 [US3] Add priority selector (dropdown) to TaskForm.tsx in frontend/src/components/tasks/TaskForm.tsx
- [x] T082 [US3] Add priority filter to TaskFilters.tsx in frontend/src/components/tasks/TaskFilters.tsx
- [x] T083 [US3] Add priority sort option to TaskFilters.tsx in frontend/src/components/tasks/TaskFilters.tsx

**Checkpoint**: Priority filtering and sorting functional

---

## Phase 6: User Story 4 - Tag-Based Categorization (Priority: P2)

**Goal**: Multi-select tags with intersection (AND) filtering

**Independent Test**: Create tasks with tags, filter by multiple tags, verify AND logic

### Backend Implementation for US4

- [x] T084 [US4] Create TagService with CRUD operations in backend/src/services/tag_service.py
- [x] T085 [US4] Implement get_or_create_tags() for tag resolution in backend/src/services/tag_service.py
- [x] T086 [US4] Update TaskService to handle tags on create/update in backend/src/services/task_service.py
- [x] T087 [US4] Implement tag intersection filter (AND logic) in list_tasks in backend/src/services/task_service.py

### API Endpoint Updates for US4

- [x] T088 [US4] Create GET /api/tags endpoint for user's tags in backend/src/api/tags.py
- [x] T089 [US4] Create POST /api/tags endpoint for creating tags in backend/src/api/tags.py
- [x] T090 [US4] Create DELETE /api/tags/:id endpoint for deleting tags in backend/src/api/tags.py
- [x] T091 [US4] Add tags[] query parameter to GET /api/tasks in backend/src/api/tasks.py

### Frontend for US4

- [x] T092 [P] [US4] Create TagSelector.tsx multi-select component in frontend/src/components/tasks/TagSelector.tsx
- [x] T093 [US4] Add TagSelector to TaskForm.tsx in frontend/src/components/tasks/TaskForm.tsx
- [x] T094 [US4] Add tag filter to TaskFilters.tsx (multi-select) in frontend/src/components/tasks/TaskFilters.tsx
- [x] T095 [US4] Display tags as badges on TaskItem.tsx in frontend/src/components/tasks/TaskItem.tsx

**Checkpoint**: Tag filtering with AND logic functional

---

## Phase 7: User Story 5 - Advanced Search and Filtering (Priority: P2)

**Goal**: Keyword search and combined filters (status, priority, tags, due date)

**Independent Test**: Search "report", filter by priority=high, verify combined results

### Backend Implementation for US5

- [x] T096 [US5] Implement case-insensitive keyword search on title/description in backend/src/services/task_service.py
- [x] T097 [US5] Implement due_before and due_after date range filters in backend/src/services/task_service.py
- [x] T098 [US5] Implement combined filter logic (AND across all filters) in backend/src/services/task_service.py

### API Endpoint Updates for US5

- [x] T099 [US5] Add q (search keyword) query parameter to GET /api/tasks in backend/src/api/tasks.py
- [x] T100 [US5] Add due_before and due_after query parameters to GET /api/tasks in backend/src/api/tasks.py
- [x] T101 [US5] Add pagination metadata (total_count, page, page_size) to response in backend/src/api/tasks.py

### Frontend for US5

- [x] T102 [P] [US5] Create TaskFilters.tsx component with all filter controls in frontend/src/components/tasks/TaskFilters.tsx
- [x] T103 [US5] Add search input field to TaskFilters.tsx in frontend/src/components/tasks/TaskFilters.tsx
- [x] T104 [US5] Add date range pickers for due date filtering in frontend/src/components/tasks/TaskFilters.tsx
- [x] T105 [US5] Update useTasks.ts hook to pass filter/search params in frontend/src/hooks/useTasks.ts
- [x] T106 [US5] Add pagination controls to task list in frontend/src/components/tasks/TaskList.tsx

**Checkpoint**: Search and combined filtering functional

---

## Phase 8: User Story 6 - Multi-Field Sorting (Priority: P3)

**Goal**: Sort by multiple fields (priority DESC, due_at ASC)

**Independent Test**: Sort by priority DESC then due_at ASC, verify correct order

### Backend Implementation for US6

- [x] T107 [US6] Implement multi-field sorting with sort_by array in backend/src/services/task_service.py
- [x] T108 [US6] Handle NULLS LAST for due_at sorting in backend/src/services/task_service.py

### API Endpoint Updates for US6

- [x] T109 [US6] Update sort_by param to accept comma-separated fields in backend/src/api/tasks.py
- [x] T110 [US6] Add sort_order param (asc/desc) to GET /api/tasks in backend/src/api/tasks.py

### Frontend for US6

- [x] T111 [US6] Add multi-field sort selector to TaskFilters.tsx in frontend/src/components/tasks/TaskFilters.tsx
- [x] T112 [US6] Add sort direction toggle to TaskFilters.tsx in frontend/src/components/tasks/TaskFilters.tsx

**Checkpoint**: Multi-field sorting functional

---

## Phase 9: User Story 7 - Event-Driven Real-Time Updates (Priority: P3)

**Goal**: Real-time task updates across devices via task-updates topic

**Independent Test**: Open app on two devices, create task on one, verify appears on other

### Backend Implementation for US7

- [x] T113 [US7] Add publish to task-updates topic on all mutations in backend/src/services/event_publisher.py
- [x] T114 [US7] Create task-updates subscription endpoint for backend in backend/src/api/dapr_subscriptions.py

### Frontend for US7 (WebSocket/Polling)

- [x] T115 [P] [US7] Create useRealTimeUpdates.ts hook for polling/WebSocket in frontend/src/hooks/useRealTimeUpdates.ts
- [x] T116 [US7] Integrate real-time updates into TaskList component in frontend/src/components/tasks/TaskList.tsx
- [x] T117 [US7] Add visual indicator for newly updated tasks in frontend/src/components/tasks/TaskItem.tsx

**Checkpoint**: Real-time sync functional across devices

---

## Phase 10: User Story 8 - Cloud Deployment and Scalability (Priority: P1)

**Goal**: Deploy to Oracle OKE with CI/CD and monitoring

**Independent Test**: Push to main, verify CI/CD deploys to OKE, check Zipkin traces

**⚠️ Dependencies**: Features (US1-US7) should be implemented before cloud deployment for meaningful validation. Local deployment (Minikube) should be tested before cloud deployment.

### Part B: Local Deployment (Minikube + Strimzi) - DO FIRST

**Estimated Time**: 2-3 hours

- [x] T118 [US8] Create scripts/minikube-setup.sh with Dapr + Strimzi installation in scripts/minikube-setup.sh (~30 min)
  - `minikube start --cpus=4 --memory=8192`
  - `minikube addons enable ingress metrics-server`
  - `dapr init -k --wait`
  - Create kafka namespace: `kubectl create namespace kafka`
  - Apply Strimzi operator: `kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka`
  - Wait for operator: `kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s`
- [x] T119 [US8] Apply Strimzi KafkaCluster CR (KRaft mode) in scripts/minikube-setup.sh (~15 min)
  - `kubectl apply -f dapr-components/strimzi/kafka-cluster.yaml -n kafka`
  - Wait for Kafka: `kubectl wait kafka/kafka-cluster --for=condition=Ready -n kafka --timeout=300s`
- [x] T120 [US8] Apply Dapr components for local environment in scripts/minikube-setup.sh (~10 min)
  - `kubectl apply -f dapr-components/kafka-pubsub-local.yaml`
  - `kubectl apply -f dapr-components/kubernetes-secrets.yaml`
  - `kubectl apply -f dapr-components/dapr-config.yaml`
- [x] T121 [US8] Create scripts/deploy-local.sh for local Helm deployment in scripts/deploy-local.sh (~20 min)
  - Build images with Minikube docker: `eval $(minikube docker-env)`
  - `docker build -t todo-backend:v5.0.0 ./backend`
  - `docker build -t todo-frontend:v5.0.0 ./frontend`
  - `docker build -t notification-service:v5.0.0 ./notification-service`
  - `docker build -t recurring-service:v5.0.0 ./recurring-service`
- [x] T122 [US8] Deploy all services via Helm in scripts/deploy-local.sh (~15 min)
  - `helm install postgres ./charts/postgres`
  - `helm install todo-backend ./charts/todo-backend --set image.tag=v5.0.0`
  - `helm install notification-service ./charts/notification-service`
  - `helm install recurring-service ./charts/recurring-service`
  - `helm install todo-frontend ./charts/todo-frontend`
- [x] T123 [US8] Test local deployment end-to-end in scripts/deploy-local.sh (~30 min)
  - `kubectl port-forward svc/todo-frontend 3000:3000`
  - `kubectl port-forward svc/todo-backend 8000:8000`
  - Verify all pods running: `kubectl get pods`
  - Check Dapr sidecar logs: `kubectl logs -l app=todo-backend -c daprd`

### Part C: Cloud Deployment (Oracle OKE + Redpanda Cloud)

**Estimated Time**: 3-4 hours

**⚠️ Prerequisites**: Local deployment (T118-T123) must be tested successfully first

#### Azure AKS Cluster Setup (~1 hour)

- [x] T124 [US8] Sign up for Azure Free Tier at azure.microsoft.com/free (~15 min)
  - Credit card required for verification ($200 credit for 30 days)
  - AKS control plane is always free, 750 hours/month free for B-series VMs
- [x] T125 [US8] Create AKS cluster via Azure CLI in scripts/deploy-cloud.sh (~20 min)
  - Install Azure CLI: `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`
  - Login: `az login`
  - Create resource group: `az group create --name todo-app-rg --location eastus`
  - Create AKS cluster: `az aks create --resource-group todo-app-rg --name todo-aks-cluster --node-count 2 --node-vm-size Standard_B2s --tier free`
  - Wait for cluster to be Active (~5-10 min)
- [x] T126 [US8] Configure kubectl for AKS cluster in scripts/deploy-cloud.sh (~10 min)
  - Get kubeconfig: `az aks get-credentials --resource-group todo-app-rg --name todo-aks-cluster`
  - Verify: `kubectl get nodes`

#### Redpanda Cloud Setup (~30 min)

- [x] T127 [US8] Sign up for Redpanda Cloud at redpanda.com/cloud (~10 min)
  - Create account (free tier available)
  - Create new serverless cluster
- [x] T128 [US8] Create Kafka topics in Redpanda Console (~10 min)
  - Create topic: `task-events` (3 partitions, 7-day retention)
  - Create topic: `reminders` (3 partitions, 1-day retention)
  - Create topic: `task-updates` (3 partitions, 1-hour retention)
- [x] T129 [US8] Get Redpanda Cloud credentials and update Dapr component (~10 min)
  - Note Bootstrap Servers URL from Redpanda Console
  - Create SASL credentials (username/password)
  - Update dapr-components/kafka-pubsub-cloud.yaml with:
    - `brokers: <bootstrap-servers>`
    - `saslUsername: <username>`
    - `saslMechanism: SCRAM-SHA-256`
  - Create K8s secret: `kubectl create secret generic redpanda-secrets --from-literal=sasl-password=<password>`

#### Deploy to AKS (~1 hour)

- [x] T130 [US8] Install Dapr on AKS cluster in scripts/deploy-cloud.sh (~15 min)
  - `helm repo add dapr https://dapr.github.io/helm-charts/`
  - `helm repo update`
  - `helm install dapr dapr/dapr --namespace dapr-system --create-namespace --set global.ha.enabled=true`
  - Verify: `kubectl get pods -n dapr-system`
- [x] T131 [US8] Apply Dapr components for cloud environment in scripts/deploy-cloud.sh (~10 min)
  - `kubectl apply -f dapr-components/kafka-pubsub-cloud.yaml`
  - `kubectl apply -f dapr-components/kubernetes-secrets.yaml`
  - `kubectl apply -f dapr-components/dapr-config.yaml`
- [x] T132 [US8] Create application secrets in OKE in scripts/deploy-cloud.sh (~10 min)
  - `kubectl create secret generic todo-secrets --from-literal=database-url=<pg-url> --from-literal=cohere-api-key=<key> --from-literal=better-auth-secret=<secret>`
- [x] T133 [US8] Deploy all services to OKE via Helm in scripts/deploy-cloud.sh (~20 min)
  - Push images to GHCR or OCI Registry first
  - `helm install postgres ./charts/postgres`
  - `helm install todo-backend ./charts/todo-backend --set image.repository=ghcr.io/<org>/todo-backend`
  - `helm install notification-service ./charts/notification-service`
  - `helm install recurring-service ./charts/recurring-service`
  - `helm install todo-frontend ./charts/todo-frontend`
- [x] T134 [US8] Verify OKE deployment and get external IPs in scripts/deploy-cloud.sh (~10 min)
  - `kubectl get svc` (note LoadBalancer external IPs)
  - `kubectl get pods` (verify all running with Dapr sidecars)

### CI/CD Pipeline (GitHub Actions)

**Estimated Time**: 1-2 hours

- [x] T135 [P] [US8] Create .github/workflows/ci.yaml for build and test (~30 min)
  - Trigger: on push to develop/main, on PR to main
  - Jobs: setup → test-backend → test-frontend → lint-helm
  - Steps: checkout, setup-python, setup-node, pip install, pytest, npm ci, npm test
  - `helm lint ./charts/*`
- [x] T136 [P] [US8] Create .github/workflows/deploy.yaml for staging/production (~45 min)
  - Trigger: on push to develop (staging), on push to main (production)
  - Jobs: build-images → push-registry → deploy-helm
  - Build: `docker build -t ghcr.io/${{ github.repository }}/todo-backend:${{ github.sha }}`
  - Push: Login to GHCR, push all 4 images
  - Deploy staging: `helm upgrade --install todo-backend ./charts/todo-backend --namespace staging`
  - Deploy production: Manual approval gate, then `helm upgrade --install`
- [x] T137 [US8] Configure GitHub Secrets in repository settings (~15 min)
  - `KUBECONFIG_STAGING`: Base64 kubeconfig for staging cluster
  - `KUBECONFIG_PRODUCTION`: Base64 kubeconfig for production cluster
  - `COHERE_API_KEY`: Cohere API key
  - `BETTER_AUTH_SECRET`: JWT signing secret
  - Document in specs/001-event-driven-cloud/quickstart.md
- [x] T138 [US8] Add Helm lint step to CI pipeline in .github/workflows/ci.yaml (~10 min)
  - Install Helm: `uses: azure/setup-helm@v4`
  - Lint all charts: `helm lint ./charts/todo-backend ./charts/todo-frontend ./charts/notification-service ./charts/recurring-service`
- [x] T139 [US8] Add rollback step on deployment failure in .github/workflows/deploy.yaml (~15 min)
  - On deploy failure: `helm rollback todo-backend`
  - Add Slack/email notification on failure (optional)

### Monitoring and Observability

**Estimated Time**: 1 hour

- [x] T140 [US8] Create dapr-components/dapr-config.yaml with Zipkin tracing (~20 min)
  ```yaml
  apiVersion: dapr.io/v1alpha1
  kind: Configuration
  metadata:
    name: dapr-config
  spec:
    tracing:
      samplingRate: "1"
      zipkin:
        endpointAddress: "http://zipkin.dapr-system.svc.cluster.local:9411/api/v2/spans"
    metrics:
      enabled: true
  ```
- [x] T141 [US8] Install metrics-server on cluster (~10 min)
  - Local: `minikube addons enable metrics-server` (already in T118)
  - OKE: `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`
- [x] T142 [US8] Install Zipkin for distributed tracing (~15 min)
  - `kubectl apply -f https://raw.githubusercontent.com/dapr/dapr/master/deploy/zipkin.yaml -n dapr-system`
  - Access: `kubectl port-forward svc/zipkin 9411:9411 -n dapr-system`
- [x] T143 [US8] Document Prometheus setup in quickstart.md (~10 min)
  - `helm install prometheus prometheus-community/prometheus`
  - Configure Dapr sidecar scraping
- [x] T144 [US8] Document Grafana dashboard setup in quickstart.md (~10 min)
  - `helm install grafana grafana/grafana`
  - Import Dapr dashboard from grafana.com

**Checkpoint**: CI/CD functional, OKE deployment verified, monitoring operational

---

## Phase 11: End-to-End Tests

**Purpose**: Validate complete event-driven flows across all services

**⚠️ Prerequisites**: All user stories (US1-US7) and cloud deployment (US8) must be complete

**Estimated Time**: 2-3 hours

### Test 1: Recurring Task Auto-Spawn (~30 min)

- [x] T145 [E2E] Create daily recurring task via API or UI
  - POST /api/tasks with `{"title": "Daily standup", "recurring_interval": "daily", "due_at": "tomorrow 9am"}`
  - Verify task created with recurring_interval stored
- [x] T146 [E2E] Complete the recurring task and verify auto-spawn
  - POST /api/tasks/{id}/complete
  - Watch recurring-service logs: `kubectl logs -f -l app=recurring-service`
  - Verify task_completed event in Kafka (or via Zipkin trace)
  - Verify NEW task created with due_at = original due_at + 1 day
  - Verify new task has same title, priority, tags
- [x] T147 [E2E] Complete the spawned task and verify chain continues
  - Complete the new task
  - Verify another task spawned with due_at = +2 days from original
  - This validates idempotency and recurring chain

### Test 2: Reminder Notification (~30 min)

- [x] T148 [E2E] Create task with remind_at = 2 minutes from now
  - POST /api/tasks with `{"title": "Test reminder", "due_at": "now + 5min", "remind_at": "now + 2min"}`
  - Verify Dapr Job scheduled: check backend logs for Jobs API call
- [x] T149 [E2E] Wait for remind_at time and verify notification
  - Watch notification-service logs: `kubectl logs -f -l app=notification-service`
  - At remind_at time (±10 seconds precision):
    - Dapr Jobs API triggers /jobs/callback
    - Backend publishes reminder_due event to reminders topic
    - notification-service receives event and logs notification
  - Verify Zipkin trace shows full flow
- [x] T150 [E2E] Update task due_at and verify reminder rescheduled
  - PUT /api/tasks/{id} with new remind_at
  - Verify old job cancelled, new job scheduled
- [x] T151 [E2E] Complete task with pending reminder and verify job cancelled
  - POST /api/tasks/{id}/complete
  - Verify reminder job cancelled (no notification after original remind_at)

### Test 3: Multi-Client Real-Time Sync (~30 min)

- [x] T152 [E2E] Open application on two browser windows/devices
  - Window A: http://localhost:3000 (or OKE URL)
  - Window B: same URL, different browser/incognito
  - Both logged in as same user
- [x] T153 [E2E] Create task on Window A, verify appears on Window B
  - Create task on Window A
  - Within 2-5 seconds, task should appear on Window B
  - (Depends on polling interval or WebSocket implementation)
- [x] T154 [E2E] Complete task on Window B, verify updated on Window A
  - Complete task on Window B
  - Window A should show task as completed
- [x] T155 [E2E] Verify event flow in Zipkin traces
  - Check Zipkin for task-updates topic events
  - Verify frontend received update via real-time mechanism

### Test 4: Search/Filter/Sort Combined (~20 min)

- [x] T156 [E2E] Create 10+ tasks with varied priorities, tags, due dates
  - Mix of high/medium/low priorities
  - Tags: ["work"], ["personal"], ["work", "urgent"]
  - Due dates: some past, some future, some null
- [x] T157 [E2E] Test combined filter: priority=high AND tags=work AND search="report"
  - GET /api/tasks?priority=high&tags=work&q=report
  - Verify only matching tasks returned
- [x] T158 [E2E] Test multi-field sort: priority DESC, due_at ASC
  - GET /api/tasks?sort_by=priority,due_at&sort_order=desc,asc
  - Verify high-priority tasks first, then sorted by nearest due date

### Test 5: CI/CD Pipeline Validation (~30 min)

- [x] T159 [E2E] Push commit to develop branch, verify staging deployment
  - Make small change (e.g., add comment)
  - Push to develop
  - Watch GitHub Actions: build → push → deploy-staging
  - Verify staging namespace updated: `kubectl get pods -n staging`
- [x] T160 [E2E] Create PR to main, verify CI checks pass
  - Create PR from develop to main
  - Verify: test-backend, test-frontend, lint-helm all pass
- [x] T161 [E2E] Merge to main, verify production deployment with approval
  - Merge PR to main
  - Verify production deployment triggered (with approval gate)
  - After approval, verify production namespace updated

**Checkpoint**: All event-driven flows validated end-to-end

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

**Estimated Time**: 2-3 hours

### Cohere AI Integration Updates

- [x] T162 [P] Update Cohere tool prompts for new fields (priority, tags, due_at) in backend/src/services/chat_service.py (~30 min)
- [x] T163 [P] Update MCP tools documentation with new parameters in backend/src/tools/mcp_tools.py (~20 min)

### Error Handling and Logging

- [x] T164 [P] Add structured logging to event_publisher.py in backend/src/services/event_publisher.py (~20 min)
- [x] T165 [P] Add structured logging to notification-service in notification-service/src/main.py (~15 min)
- [x] T166 [P] Add structured logging to recurring-service in recurring-service/src/main.py (~15 min)
- [x] T167 Add retry logic with exponential backoff for Kafka unavailability in backend/src/services/event_publisher.py (~30 min)

### Security Hardening

- [x] T168 [P] Verify user_id isolation in all new queries in backend/src/services/task_service.py (~20 min)
- [x] T169 [P] Verify user_id included in all Kafka event payloads in backend/src/services/event_publisher.py (~15 min)
- [x] T170 Enable Dapr mTLS for inter-service communication in dapr-components/dapr-config.yaml (~15 min)

### Final Validation

- [x] T171 Run full quickstart.md validation (local deployment) (~30 min)
- [x] T172 Run full quickstart.md validation (cloud deployment) (~30 min)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → All User Stories can begin
                                          ↓
                          ┌───────────────┼───────────────┐
                          ↓               ↓               ↓
                    Phase 3 (US1)   Phase 4 (US2)   Phase 10 (US8)
                    Recurring       Reminders       Cloud Deploy
                          ↓               ↓
                          └───────┬───────┘
                                  ↓
                    ┌─────────────┼─────────────┐
                    ↓             ↓             ↓
              Phase 5 (US3)  Phase 6 (US4)  Phase 7 (US5)
              Priorities     Tags           Search/Filter
                    │             │             │
                    └─────────────┼─────────────┘
                                  ↓
                          Phase 8 (US6)
                          Multi-Sort
                                  ↓
                          Phase 9 (US7)
                          Real-Time
                                  ↓
                          Phase 11 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Recurring) | Foundation (Phase 2) | T043 complete |
| US2 (Reminders) | Foundation (Phase 2) | T043 complete |
| US3 (Priorities) | Foundation (Phase 2) | T043 complete |
| US4 (Tags) | Foundation (Phase 2) | T043 complete |
| US5 (Search) | US3, US4 | T095 complete |
| US6 (Multi-Sort) | US5 | T106 complete |
| US7 (Real-Time) | US1, US2 | T074 complete |
| US8 (Cloud) | Foundation (Phase 2) | T043 complete |

### Within Each Phase

- Models before services
- Services before API endpoints
- API endpoints before frontend components
- Backend before frontend (for data dependencies)

### Parallel Opportunities

**Phase 1 Setup** (can all run in parallel):
- T002, T003, T004, T005 (Dapr components)
- T007, T008, T010, T011 (Dockerfiles)
- T012, T013 (Helm charts)

**Phase 2 Foundational**:
- T020, T021, T022 (models in parallel)
- T033, T034, T035, T036 (Helm Dapr annotations)
- T039-T043 (Pydantic schemas)

**User Story Phases**:
- Backend and Frontend within same story can be developed in parallel by different developers
- Different user stories can be developed in parallel after Foundation complete

---

## Parallel Example: Foundation Phase

```bash
# Launch all Dapr components together:
Task: "T002 Create kafka-pubsub-local.yaml"
Task: "T003 Create kafka-pubsub-cloud.yaml"
Task: "T004 Create kubernetes-secrets.yaml"
Task: "T005 Create strimzi/kafka-cluster.yaml"

# Launch all model tasks together:
Task: "T020 Create Tag model"
Task: "T021 Create TaskTag junction model"
Task: "T022 Create Event schema model"

# Launch all Helm updates together:
Task: "T033 Update todo-backend Dapr annotations"
Task: "T034 Update todo-frontend Dapr annotations"
Task: "T035 Create notification-service Dapr annotations"
Task: "T036 Create recurring-service Dapr annotations"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 8)

1. **Complete Phase 1**: Setup (~14 tasks)
2. **Complete Phase 2**: Foundation (~29 tasks) - CRITICAL GATE
3. **Complete Phase 3**: US1 Recurring Tasks (~15 tasks)
4. **Complete Phase 4**: US2 Reminders (~16 tasks)
5. **Complete Phase 10**: US8 Cloud Deployment (~14 tasks)
6. **STOP and VALIDATE**: Test event flow end-to-end
7. **Deploy MVP** to Oracle OKE

### Incremental Delivery

| Increment | Stories | Tasks | Value Delivered |
|-----------|---------|-------|-----------------|
| MVP | US1, US2, US8 | ~73 | Recurring tasks, reminders, cloud deploy |
| +Priorities | US3 | ~9 | Priority sorting and filtering |
| +Tags | US4 | ~12 | Tag categorization |
| +Search | US5 | ~11 | Advanced search/filter |
| +Sort | US6 | ~6 | Multi-field sorting |
| +Real-Time | US7 | ~5 | Cross-device sync |
| Polish | - | ~11 | Final hardening |

### Critical Path

```
T001 → T015-T024 (Schema) → T025-T032 (Event Framework) → T044-T058 (US1) → T118-T131 (US8)
                                                        → T059-T074 (US2)
```

---

## Task Summary

| Phase | Story | Task Count | Parallel Tasks |
|-------|-------|------------|----------------|
| 1 | Setup | 14 | 10 |
| 2 | Foundational | 29 | 14 |
| 3 | US1 Recurring | 15 | 3 |
| 4 | US2 Reminders | 16 | 2 |
| 5 | US3 Priorities | 9 | 1 |
| 6 | US4 Tags | 12 | 1 |
| 7 | US5 Search | 11 | 1 |
| 8 | US6 Sort | 6 | 0 |
| 9 | US7 Real-Time | 5 | 1 |
| 10 | US8 Cloud | 14 | 2 |
| 11 | Polish | 11 | 6 |
| **Total** | | **142** | **41** |

---

## Notes

- [P] tasks = different files, no dependencies between them
- [USx] label maps task to specific user story for traceability
- Commit after each task or logical group of tasks
- Run local tests after completing each user story phase
- US8 (Cloud Deployment) can proceed in parallel with US1/US2
- Phase 11 (Polish) tasks can be interspersed as needed
- Verify event flow after completing US1 and US2 before proceeding
