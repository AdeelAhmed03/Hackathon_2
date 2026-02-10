---
id: 001
title: phase-v-event-driven-spec
stage: spec
date: 2026-02-09T00:00:00Z
surface: cli
model: claude-sonnet-4-5
feature: 001-event-driven-cloud
branch: 001-event-driven-cloud
user: developer
command: /sp.specify
labels: [specification, phase-v, event-driven, dapr, kafka, cloud-deployment, recurring-tasks, reminders]
links:
  spec: specs/001-event-driven-cloud/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - path: specs/001-event-driven-cloud/spec.md
    purpose: Feature specification for Phase V event-driven cloud deployment
    lines_added: 410
  - path: specs/001-event-driven-cloud/checklists/requirements.md
    purpose: Specification quality validation checklist
    lines_added: 85
tests: []
---

## Prompt

Create a new feature specification for Phase V advanced cloud deployment.

Feature name: advanced-event-driven-cloud-todo

Requirements (Part A):
- Advanced: Recurring Tasks (interval: daily/weekly, auto-create next on complete via consumer), Due Dates (due_at datetime), Reminders (remind_at, send via notification service push/email).
- Intermediate: Priorities (low/medium/high), Tags (array strings), Search (full-text on title/desc), Filter (by status/priority/tag/due), Sort (by due/priority/created/title).
- Event-Driven: Publish to Kafka topics on operations (task-events for audit/recurring, reminders for notifications, task-updates for WebSocket real-time sync); consumers (recurring service spawns next, notification sends, audit logs).
- Dapr: Pub/Sub (kafka-pubsub with Redpanda/Strimzi brokers, consumerGroup); State (postgresql for conv history alternative); Jobs API (schedule reminders at exact remind_at with POST /v1.0-alpha1/jobs, handle callback); Secrets (kubernetes-secrets for keys); Service Invocation (frontend→backend with retries); Bindings (cron fallback for periodic checks if Jobs unavailable).

Requirements (Part B/C):
- Local: Extend Minikube; dapr init -k; apply dapr-components YAML; deploy new pods (notification/recurring); Strimzi for Kafka (simple yaml: replicas=1, plain listener port 9092, ephemeral).
- Cloud: Oracle OKE (free tier signup, create cluster with Arm compute); alt AKS/GKE. Redpanda Cloud (free serverless, create topics, sasl/scram-sha-256 auth). GitHub Actions: .github/workflows/deploy.yaml (docker build/push, helm upgrade --install). Monitoring: Enable metrics-server, Dapr Zipkin; logging via kubectl logs.
- Edge cases: Reminder at exact time, recurring chain, real-time sync multi-client, failover (consumer retry), invalid due_at.

Include user stories (e.g., As a user, I can set recurring daily task and it auto-spawns on complete), acceptance criteria (e.g., Jobs API triggers notification exactly at remind_at), API updates (add fields to tasks, new endpoints for search/filter/sort), Dapr component YAML examples, Kafka schemas, review checklist, monorepo notes.

## Response snapshot

Successfully created comprehensive Phase V specification with:

**Branch & Files**:
- Created branch: `001-event-driven-cloud`
- Specification: `specs/001-event-driven-cloud/spec.md` (410 lines)
- Quality checklist: `specs/001-event-driven-cloud/checklists/requirements.md` (85 lines)

**User Stories (8 prioritized)**:
1. **P1** - Recurring Task Management: Daily/weekly/monthly/yearly tasks with auto-spawn on completion
2. **P1** - Due Dates and Reminders: Exact-time notifications via Dapr Jobs API
3. **P2** - Priority-Based Organization: Low/medium/high priorities with sorting
4. **P2** - Tag-Based Categorization: Multi-select tags with intersection filtering
5. **P2** - Advanced Search and Filtering: Keyword search + multi-filter combinations
6. **P3** - Multi-Field Sorting: Complex sorting (priority DESC, due_at ASC)
7. **P3** - Event-Driven Real-Time Updates: Cross-device synchronization
8. **P1** - Cloud Deployment and Scalability: Oracle OKE/AKS/GKE with CI/CD

**Functional Requirements (74 total)**:
- FR-001 to FR-008: Advanced task features (recurring, due dates, reminders, priorities, tags)
- FR-009 to FR-013: Search, filter, and sort capabilities
- FR-014 to FR-023: Event-driven architecture (Kafka topics, consumers)
- FR-024 to FR-033: Dapr integration (Pub/Sub, Secrets, Jobs API, State, Service Invocation)
- FR-034 to FR-039: Local deployment (Minikube + Strimzi)
- FR-040 to FR-044: Cloud deployment (Oracle OKE, Redpanda Cloud)
- FR-045 to FR-052: CI/CD pipeline (GitHub Actions, Helm)
- FR-053 to FR-058: Monitoring and logging (Zipkin, Prometheus, Grafana)
- FR-059 to FR-063: Database schema (new columns and tables)
- FR-064 to FR-069: API updates (new endpoints and query parameters)
- FR-070 to FR-074: Security and isolation (user_id scoping, Dapr mTLS)

**Success Criteria (20 measurable outcomes)**:
- Event-driven latency: <5 seconds for recurring task creation
- Notification precision: <10 seconds variance from scheduled time
- Query performance: <500ms for filtered/sorted lists up to 1000 tasks
- Search performance: <500ms for keyword search
- Concurrent users: 100 users without event loss
- CI/CD speed: <10 minutes for full pipeline
- Cloud deployment: Operates within Oracle OKE Always Free limits
- Observability: Complete distributed traces in Zipkin
- Reliability: 99% notification delivery rate
- Stability: 7 days continuous operation without restarts

**Edge Cases (12 identified)**:
- Reminder scheduling for past times
- Rapid recurring task completion (idempotency)
- Simultaneous updates from multiple clients
- Consumer failover and retry logic
- Invalid datetime formats
- Dapr Jobs API unavailability (cron fallback)
- Kafka unavailability (retry/circuit breaker)
- Tag isolation enforcement
- Recurring tasks without due_at
- Timezone handling across user travel
- Large tag collections (1000+)
- Bulk operations (50+ recurring tasks)

**Key Entities**:
- Task (enhanced): Added due_at, remind_at, recurring_interval, priority fields
- Tag: User-scoped labels for categorization
- TaskTag: Many-to-many junction table
- Event: Kafka message schema (event_type, task_id, task_data, user_id, timestamp)
- ReminderJob: Dapr Jobs API scheduled job
- DaprComponent: Infrastructure configuration (kafka-pubsub, statestore, secrets)

**Quality Validation**:
- ✅ All checklist items passed
- Zero [NEEDS CLARIFICATION] markers
- All requirements testable and unambiguous
- Success criteria measurable and technology-agnostic
- Comprehensive acceptance scenarios
- Scope clearly bounded to Phase V features
- Ready for planning phase (/sp.plan)

## Outcome

- ✅ Impact: Complete Phase V specification created with 8 user stories, 74 functional requirements, 20 success criteria, and 12 edge cases. Establishes foundation for event-driven cloud-native architecture.
- 🧪 Tests: No code tests yet (specification phase). Quality validated via requirements checklist (all items passed).
- 📁 Files: Created `specs/001-event-driven-cloud/spec.md` (410 lines) and `checklists/requirements.md` (85 lines). Branch `001-event-driven-cloud` created and committed.
- 🔁 Next prompts: `/sp.plan` to create implementation plan; `/sp.clarify` if any requirements need refinement (none currently needed based on checklist).
- 🧠 Reflection: Specification successfully balances comprehensiveness (74 requirements) with clarity (zero ambiguity markers). Prioritization (P1/P2/P3) enables phased implementation. Success criteria provide clear measurable goals for validation.

## Evaluation notes (flywheel)

- Failure modes observed: None. PowerShell script had parameter parsing issue but fallback manual branch creation succeeded.
- Graders run and results (PASS/FAIL): Specification quality checklist - ALL PASSED (14/14 criteria met)
- Prompt variant (if applicable): Standard /sp.specify workflow with comprehensive requirements input
- Next experiment (smallest change to try): Test specification clarity by running /sp.plan without additional clarifications to validate completeness

