---
id: 002
title: phase-v-implementation-plan
stage: plan
date: 2026-02-09T00:00:00Z
surface: cli
model: claude-sonnet-4-5
feature: 001-event-driven-cloud
branch: 001-event-driven-cloud
user: developer
command: /sp.plan
labels: [plan, architecture, dapr, kafka, kubernetes, oracle-oke, ci-cd]
links:
  spec: specs/001-event-driven-cloud/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - path: specs/001-event-driven-cloud/plan.md
    purpose: Comprehensive technical implementation plan
    lines_added: 850
  - path: specs/001-event-driven-cloud/research.md
    purpose: Technology research and decisions
    lines_added: 550
  - path: specs/001-event-driven-cloud/data-model.md
    purpose: Database schema and entity definitions
    lines_added: 650
  - path: specs/001-event-driven-cloud/quickstart.md
    purpose: Deployment guide for local and cloud
    lines_added: 450
  - path: specs/001-event-driven-cloud/contracts/tasks-api.yaml
    purpose: OpenAPI 3.1 specification for task endpoints
    lines_added: 400
  - path: specs/001-event-driven-cloud/contracts/events.yaml
    purpose: AsyncAPI specification for Kafka events
    lines_added: 300
  - path: specs/001-event-driven-cloud/contracts/dapr-endpoints.yaml
    purpose: Dapr subscription and callback endpoints
    lines_added: 280
tests: []
---

## Prompt

Based on approved spec.md, create technical plan.md for Phase V.

Include:
- Architecture: Kubernetes pods (frontend/backend/notification/recurring/audit with Dapr sidecars); Dapr components (pubsub.kafka with Redpanda/Strimzi, state.postgresql connectionString to Neon, secrets.kubernetes, jobs for scheduling); Kafka consumers via Dapr subscriptions (@app.post("/events") handling task-events/reminders).
- Data Model: Update Task (add due_at, remind_at, recurring_interval str, priority enum, tags list[str]); new tables for audit logs if needed.
- Cohere: Adapter in backend/agents (cohere.Client, prompt for tool decisions: "Output JSON {'action':..., 'params':...}").
- Local: Minikube addons (ingress, metrics-server); dapr init -k; apply Strimzi (ns kafka, apply install/latest, kafka-cluster.yaml: kafka replicas=1, listeners plain:9092 internal, storage ephemeral; zookeeper none via KRaft).
- Cloud: Oracle OKE (console create cluster, kubectl config use-context); Redpanda (signup, create serverless cluster, topics via UI, get bootstrap/sasl creds for Dapr yaml). CI/CD: Workflow steps (docker-build, push to OCI/GCR/ACR, helm upgrade with values-prod.yaml).
- Integration: On task create/update, if due_at, schedule Job via Dapr POST /jobs; on complete, publish to task-events; consumer chains (recurring spawns next task).
- Research: Dapr v1.16 Kafka compression, Jobs API callbacks.

## Response snapshot

Successfully created comprehensive Phase V implementation plan with the following artifacts:

**Plan Documentation** (7 files, ~3500 lines):

1. **plan.md** - Complete technical implementation plan
   - Architecture overview with system diagrams
   - Dapr components configuration (kafka-pubsub, kubernetes-secrets)
   - Event flow diagrams (task creation → Kafka → consumers)
   - Cohere tool calling adapter pattern
   - Local deployment (Minikube + Strimzi)
   - Cloud deployment (Oracle OKE + Redpanda Cloud)
   - CI/CD pipeline (GitHub Actions)
   - Monitoring setup (Zipkin, Prometheus, Grafana)
   - Risk assessment and success metrics

2. **research.md** - Technology decisions
   - Dapr v1.16 Kafka integration (gzip compression)
   - Dapr Jobs API (alpha) with cron fallback
   - Strimzi (local) vs Redpanda Cloud (production)
   - Oracle OKE vs Azure AKS vs GKE (OKE Always Free selected)
   - Cohere command-r-plus adapter pattern
   - Event schema design (CloudEvents-inspired)
   - Consumer idempotency patterns

3. **data-model.md** - Schema and entities
   - Task model enhancements (due_at, remind_at, recurring_interval, priority)
   - Tag entity (user-scoped)
   - TaskTag junction table (many-to-many)
   - ProcessedEvent (idempotency)
   - AuditLog (compliance)
   - SQLModel definitions with relationships
   - Pydantic schemas for API validation
   - Alembic migration script

4. **quickstart.md** - Deployment guide
   - Local: Minikube + Dapr + Strimzi step-by-step
   - Cloud: Oracle OKE + Redpanda Cloud setup
   - CI/CD: GitHub Actions configuration
   - Verification checklist
   - Troubleshooting guide

**API Contracts** (3 files):

5. **contracts/tasks-api.yaml** - OpenAPI 3.1
   - Enhanced task endpoints with query parameters
   - Search, filter, sort capabilities
   - Tag management endpoints
   - Chat endpoint specification

6. **contracts/events.yaml** - AsyncAPI
   - Kafka topics: task-events, reminders, task-updates
   - CloudEvents message format
   - Schema definitions for all event types

7. **contracts/dapr-endpoints.yaml** - Dapr integration
   - /dapr/subscribe discovery endpoint
   - Event handler endpoints
   - Jobs API callback endpoint

**Constitution Check**: All 19 principles verified and PASSED

**Project Structure**: Defined monorepo layout with:
- backend/ (enhanced with Dapr integration)
- frontend/ (enhanced with new UI components)
- notification-service/ (NEW)
- recurring-service/ (NEW)
- dapr-components/ (NEW)
- charts/ (updated with Dapr annotations)
- .github/workflows/ (NEW)

## Outcome

- ✅ Impact: Complete Phase V technical plan created with architecture, research, data model, API contracts, and deployment guides. All constitution principles verified. Ready for task generation.
- 🧪 Tests: No code tests yet (planning phase). Architecture validated against 74 functional requirements from spec.
- 📁 Files: Created 7 files totaling ~3500 lines. Committed to branch 001-event-driven-cloud.
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks from this plan. Then begin implementation with database migration and backend API enhancements.
- 🧠 Reflection: Plan successfully translates spec requirements into concrete technical design. Dapr abstraction simplifies Kafka integration. Oracle OKE Always Free provides genuine zero-cost production hosting. Jobs API alpha status acceptable with cron fallback documented.

## Evaluation notes (flywheel)

- Failure modes observed: None. All plan artifacts generated successfully.
- Graders run and results (PASS/FAIL): Constitution check - 19/19 PASSED. No gate violations.
- Prompt variant (if applicable): Standard /sp.plan workflow with detailed user input for architecture guidance
- Next experiment (smallest change to try): Run /sp.tasks to validate that plan provides sufficient detail for task breakdown

