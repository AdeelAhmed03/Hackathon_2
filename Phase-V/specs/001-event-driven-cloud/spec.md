# Feature Specification: Advanced Event-Driven Cloud Todo Application

**Feature Branch**: `001-event-driven-cloud`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Create a new feature specification for Phase V advanced cloud deployment with event-driven architecture, Dapr integration, Kafka messaging, recurring tasks, due dates, reminders, priorities, tags, search/filter/sort, cloud deployment (Oracle OKE/Azure AKS/GKE), and CI/CD with GitHub Actions"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recurring Task Management (Priority: P1)

As a user, I want to create recurring tasks (daily, weekly, monthly, yearly) so that I don't have to manually recreate repetitive tasks. When I complete a recurring task, the system automatically creates the next instance with the updated due date.

**Why this priority**: Core feature that provides significant value by automating repetitive task management. This is the foundation of the event-driven architecture and demonstrates the value of the new system design.

**Independent Test**: Can be fully tested by creating a daily recurring task, marking it complete, and verifying a new task is automatically created with tomorrow's due date. Delivers immediate automation value to users.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I create a task with title "Daily standup" and set recurring_interval to "daily", **Then** the task is created with recurring_interval stored
2. **Given** I have a daily recurring task, **When** I mark it as complete, **Then** a new task with the same title, description, priority, and tags is automatically created with due_at set to tomorrow
3. **Given** I have a weekly recurring task due today, **When** I complete it, **Then** a new instance is created with due_at set to 7 days from now
4. **Given** I have a monthly recurring task, **When** I complete it, **Then** a new instance is created with due_at set to the same day next month
5. **Given** I have a recurring task, **When** I update it to set recurring_interval to null, **Then** future completions do not spawn new instances

---

### User Story 2 - Due Dates and Reminders (Priority: P1)

As a user, I want to set due dates on my tasks and receive timely reminders so that I never miss important deadlines.

**Why this priority**: Critical for task management effectiveness. Reminders demonstrate the Jobs API scheduling capability and provide immediate user value through proactive notifications.

**Independent Test**: Can be fully tested by creating a task with a due date 5 minutes in the future and a reminder 2 minutes before due. Verify notification is received exactly at remind_at time.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set due_at to a specific datetime (e.g., "2026-02-15 14:00 UTC"), **Then** the task stores the timezone-aware due date
2. **Given** I have a task with due_at set, **When** I set remind_at to 1 hour before due_at, **Then** the system schedules a reminder job via Dapr Jobs API
3. **Given** a reminder job is scheduled, **When** the remind_at time is reached, **Then** I receive a notification (email or push) with the task details
4. **Given** I update a task's due_at, **When** the update is saved, **Then** the existing reminder job is cancelled and a new one is scheduled for the new remind_at
5. **Given** I complete a task with a scheduled reminder, **When** the task is marked complete, **Then** the reminder job is cancelled

---

### User Story 3 - Priority-Based Task Organization (Priority: P2)

As a user, I want to assign priorities (low, medium, high) to my tasks and sort by priority so that I can focus on what matters most.

**Why this priority**: Enhances task management effectiveness by enabling prioritization. Builds on basic CRUD functionality and provides clear visual organization.

**Independent Test**: Can be fully tested by creating tasks with different priorities, sorting by priority descending, and verifying high-priority tasks appear first.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set priority to "high", **Then** the task is created with priority "high"
2. **Given** I have tasks with mixed priorities, **When** I request the task list sorted by priority, **Then** tasks are returned in order: high, medium, low
3. **Given** I am viewing my task list, **When** I filter by priority "high", **Then** only high-priority tasks are displayed
4. **Given** I update a task, **When** I change its priority from "low" to "high", **Then** the priority is updated and reflected in sorted views
5. **Given** I create a task without specifying priority, **When** the task is saved, **Then** it defaults to "medium" priority

---

### User Story 4 - Tag-Based Categorization (Priority: P2)

As a user, I want to add multiple tags to my tasks and filter by tags so that I can organize tasks by context (e.g., "work", "personal", "urgent").

**Why this priority**: Provides flexible categorization beyond priorities. Enables users to organize tasks by multiple dimensions (project, context, urgency) which is essential for complex task management.

**Independent Test**: Can be fully tested by creating tasks with various tags, filtering by multiple tags (e.g., "work" AND "urgent"), and verifying only matching tasks are returned.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I add tags ["work", "urgent", "meeting"], **Then** the task is associated with all three tags
2. **Given** I have tasks with various tags, **When** I filter by tag "work", **Then** only tasks tagged with "work" are displayed
3. **Given** I want to find specific tasks, **When** I filter by multiple tags ["work", "urgent"], **Then** only tasks that have BOTH tags are displayed (intersection/AND logic)
4. **Given** I am updating a task, **When** I add a new tag "project-x", **Then** the tag is added without removing existing tags
5. **Given** I am updating a task, **When** I remove a tag "urgent", **Then** the tag is removed but other tags remain
6. **Given** I have multiple tasks, **When** I request all unique tags, **Then** I receive a list of all tags I've used (scoped to my user_id)

---

### User Story 5 - Advanced Search and Filtering (Priority: P2)

As a user, I want to search tasks by keywords and apply multiple filters (status, priority, tags, due date) so that I can quickly find specific tasks.

**Why this priority**: Enhances usability as task lists grow. Combined search and filter enables power users to navigate large task collections efficiently.

**Independent Test**: Can be fully tested by creating 20+ tasks with varied content, searching for a keyword in titles/descriptions, applying filters, and verifying accurate results.

**Acceptance Scenarios**:

1. **Given** I have tasks with various titles, **When** I search for keyword "report", **Then** all tasks with "report" in title or description are returned (case-insensitive)
2. **Given** I want to find specific tasks, **When** I apply filters for priority="high" and status="pending", **Then** only pending high-priority tasks are returned
3. **Given** I have tasks with due dates, **When** I filter by due_at before a specific date, **Then** only tasks due before that date are returned
4. **Given** I am searching tasks, **When** I combine search keyword "meeting" with tag filter "work", **Then** only work-tagged tasks containing "meeting" are returned
5. **Given** I have a large task list, **When** I sort by due_at ascending, **Then** tasks with nearest due dates appear first, followed by tasks without due dates

---

### User Story 6 - Multi-Field Sorting (Priority: P3)

As a user, I want to sort my tasks by multiple fields (priority, due date, created date, title) so that I can view tasks in the most useful order for my workflow.

**Why this priority**: Quality-of-life improvement that enhances user experience. Less critical than core features but improves daily usability.

**Independent Test**: Can be fully tested by creating tasks with various priorities and due dates, sorting by "priority DESC, due_at ASC", and verifying high-priority tasks with nearest due dates appear first.

**Acceptance Scenarios**:

1. **Given** I have tasks with various creation dates, **When** I sort by created_at descending, **Then** newest tasks appear first
2. **Given** I have tasks with due dates, **When** I sort by due_at ascending, **Then** tasks due soonest appear first
3. **Given** I want complex sorting, **When** I sort by priority descending and then due_at ascending, **Then** high-priority tasks appear first, and within each priority level, tasks are sorted by nearest due date
4. **Given** I have tasks with and without due dates, **When** I sort by due_at ascending, **Then** tasks with due dates appear first (sorted), followed by tasks without due dates
5. **Given** I want alphabetical sorting, **When** I sort by title ascending, **Then** tasks are sorted alphabetically by title

---

### User Story 7 - Event-Driven Real-Time Updates (Priority: P3)

As a user, I want my task list to automatically update when I make changes on another device so that I always see the latest information across all my devices.

**Why this priority**: Enhanced multi-device experience. Less critical than core features but provides modern app expectations. Demonstrates the full potential of event-driven architecture.

**Acceptance Scenarios**:

1. **Given** I have the app open on two devices, **When** I create a task on device A, **Then** device B receives a real-time update and displays the new task without refreshing
2. **Given** I am viewing tasks on my phone, **When** I complete a task on my desktop, **Then** my phone automatically marks the task as complete
3. **Given** I am collaborating on tasks, **When** another user updates a shared task, **Then** I see the update in real-time (future multi-user enhancement)

---

### User Story 8 - Cloud Deployment and Scalability (Priority: P1)

As a system administrator, I want the application deployed to cloud Kubernetes (Oracle OKE preferred) with automated CI/CD so that the application is production-ready, scalable, and maintainable.

**Why this priority**: Infrastructure foundation that enables all other features to run in production. Critical for Phase V objectives and demonstrates cloud-native architecture.

**Independent Test**: Can be fully tested by deploying to Oracle OKE, creating tasks, verifying event flow through Kafka, checking Dapr sidecars, and monitoring with Zipkin/Prometheus.

**Acceptance Scenarios**:

1. **Given** the codebase is pushed to GitHub main branch, **When** the CI/CD pipeline runs, **Then** Docker images are built, pushed to registry, and Helm charts are deployed to production
2. **Given** the application is deployed to Oracle OKE, **When** I access the frontend URL, **Then** the application loads and I can perform all task operations
3. **Given** the application is running in Kubernetes, **When** I create a task, **Then** the event flows through Kafka (Redpanda Cloud) and is consumed by appropriate services
4. **Given** monitoring is enabled, **When** I perform operations, **Then** I can view distributed traces in Zipkin and metrics in Grafana
5. **Given** the application is deployed, **When** I scale the backend deployment to 3 replicas, **Then** load is distributed across replicas and all features work correctly

---

### Edge Cases

- **Reminder at exact time**: What happens when a reminder is scheduled for a time in the past (e.g., user sets remind_at to yesterday)? System should either reject with validation error or skip scheduling the reminder.

- **Recurring task chain**: What happens if a user completes the same recurring task multiple times rapidly (within seconds)? System should handle idempotency to prevent duplicate task creation.

- **Real-time sync with multiple clients**: What happens when two devices update the same task simultaneously? System should use last-write-wins or version-based conflict resolution.

- **Consumer failover**: What happens if the recurring-service or notification-service crashes while processing an event? Kafka consumer groups should provide automatic failover and reprocessing guarantees.

- **Invalid due_at**: What happens if a user sets due_at to an invalid datetime format or a date far in the past/future? API validation should reject invalid formats and provide reasonable bounds (e.g., max 10 years in future).

- **Jobs API failure**: What happens if the Dapr Jobs API is unavailable when scheduling a reminder? System should fall back to periodic cron-based checks or queue the job for retry.

- **Kafka unavailability**: What happens if Kafka/Redpanda is down when publishing an event? Backend should implement retry logic with exponential backoff or circuit breaker pattern.

- **Tag isolation**: What happens if a user tries to filter by tags from another user? System must ensure user_id scoping for all tag queries to prevent cross-user access.

- **Recurring task without due_at**: What happens if a user creates a recurring task without setting due_at? System should either require due_at for recurring tasks or default to current time + interval.

- **Timezone handling**: What happens when a user in timezone UTC+8 sets a reminder for 9 AM and then travels to UTC-5? System stores all times in UTC; client converts to local timezone for display. Reminder triggers at absolute UTC time regardless of user's current location.

- **Large tag collections**: What happens when a user has 1000+ unique tags? API should paginate tag lists and optimize tag queries with indexes.

- **Bulk operations**: What happens when a user completes 50 recurring tasks at once? Event publishing should handle bulk operations efficiently, possibly batching events or using async processing.

## Requirements *(mandatory)*

### Functional Requirements

#### Advanced Task Features

- **FR-001**: System MUST support recurring tasks with intervals: daily, weekly, monthly, yearly
- **FR-002**: System MUST automatically create a new task instance when a recurring task is completed, with due_at calculated as (original due_at + interval)
- **FR-003**: System MUST store due_at as a nullable, timezone-aware datetime field (UTC storage)
- **FR-004**: System MUST store remind_at as a nullable, timezone-aware datetime field (UTC storage)
- **FR-005**: System MUST support priorities with values: low, medium (default), high
- **FR-006**: System MUST support multi-select tags with user-scoped isolation (each user has their own tag namespace)
- **FR-007**: System MUST validate that recurring_interval is only set when due_at is also provided
- **FR-008**: Users MUST be able to disable recurring behavior by setting recurring_interval to null

#### Search, Filter, and Sort

- **FR-009**: System MUST support case-insensitive keyword search on task title and description
- **FR-010**: System MUST support filtering by: status (pending/completed), priority (low/medium/high), tags (array, intersection/AND logic), due_at (before/after date ranges)
- **FR-011**: System MUST support sorting by: priority (high > medium > low), due_at (ascending/descending), created_at (ascending/descending), title (alphabetical)
- **FR-012**: System MUST support multi-field sorting (e.g., sort by priority DESC, then due_at ASC)
- **FR-013**: System MUST combine search, filter, and sort parameters in a single API request

#### Event-Driven Architecture

- **FR-014**: System MUST publish events to Kafka topics on all task mutations (create, update, complete, delete)
- **FR-015**: System MUST define event schema with fields: event_type, task_id, task_data, user_id, timestamp
- **FR-016**: System MUST partition Kafka topics by user_id to ensure ordering guarantees per user
- **FR-017**: Backend service MUST publish to topic "task-events" for CRUD operations
- **FR-018**: Backend service MUST publish to topic "reminders" for due date notifications
- **FR-019**: Backend service MUST publish to topic "task-updates" for real-time sync (optional/future)
- **FR-020**: Recurring-service MUST consume "task-events" topic and filter for "task_completed" events
- **FR-021**: Recurring-service MUST check if completed task has recurring_interval set and create next instance
- **FR-022**: Notification-service MUST consume "reminders" topic and send notifications via email/push
- **FR-023**: Audit-service (optional) MUST consume "task-events" topic and log all events for compliance

#### Dapr Integration

- **FR-024**: System MUST use Dapr Pub/Sub building block for all event publishing and subscription (no direct kafka-python)
- **FR-025**: System MUST define Dapr component "kafka-pubsub" with type pubsub.kafka pointing to Redpanda or Strimzi brokers
- **FR-026**: System MUST use Dapr Secrets building block to retrieve COHERE_API_KEY and BETTER_AUTH_SECRET
- **FR-027**: System MUST define Dapr component "kubernetes-secrets" with type secretstores.kubernetes
- **FR-028**: System MUST use Dapr Jobs API (v1.0-alpha1) to schedule reminder jobs at exact remind_at times
- **FR-029**: System MUST handle Dapr Jobs API callbacks at a designated endpoint (e.g., POST /jobs/callback)
- **FR-030**: System MUST cancel scheduled reminder jobs when task is completed or remind_at is updated
- **FR-031**: System MAY use Dapr State building block as an alternative to direct PostgreSQL access for conversation history
- **FR-032**: System MAY use Dapr Service Invocation for inter-service communication (e.g., recurring-service calling backend API)
- **FR-033**: System MAY use Dapr Bindings (cron) as a fallback if Jobs API is unavailable for periodic reminder checks

#### Local Deployment (Minikube)

- **FR-034**: System MUST support deployment to Minikube with Dapr installed via "dapr init -k"
- **FR-035**: System MUST deploy Strimzi Kafka Operator v0.50+ for local Kafka cluster
- **FR-036**: Strimzi KafkaCluster MUST use KRaft mode (no Zookeeper), 1 replica, ephemeral storage, plain listener on port 9092
- **FR-037**: System MUST apply Dapr components from /dapr-components/ directory (kafka-pubsub.yaml, statestore-postgresql.yaml, kubernetes-secrets.yaml)
- **FR-038**: System MUST deploy new pods: notification-service, recurring-service with Dapr sidecar annotations
- **FR-039**: All Helm charts MUST include Dapr annotations: dapr.io/enabled: "true", dapr.io/app-id, dapr.io/app-port

#### Cloud Deployment

- **FR-040**: System MUST support deployment to Oracle OKE (preferred), Azure AKS, or GKE
- **FR-041**: System MUST use Redpanda Cloud free serverless tier for Kafka in cloud deployments (preferred)
- **FR-042**: Dapr kafka-pubsub component MUST support SASL authentication (SCRAM-SHA-256 or SCRAM-SHA-512) for Redpanda Cloud
- **FR-043**: System MUST provide deployment guides for Oracle OKE Always Free tier (4500 compute hours/month)
- **FR-044**: System MUST support alternative cloud providers (Azure AKS with $200 credit, GKE with $300 credit)

#### CI/CD

- **FR-045**: System MUST provide GitHub Actions workflow at .github/workflows/deploy.yaml
- **FR-046**: CI/CD pipeline MUST build Docker images for: backend, frontend, notification-service, recurring-service
- **FR-047**: CI/CD pipeline MUST push images to Docker Hub, GitHub Container Registry, or cloud provider registry
- **FR-048**: CI/CD pipeline MUST run tests (backend pytest, frontend jest) before building images
- **FR-049**: CI/CD pipeline MUST run "helm lint" for all charts before deployment
- **FR-050**: CI/CD pipeline MUST deploy to staging environment on push to develop branch
- **FR-051**: CI/CD pipeline MUST deploy to production environment on push to main branch (with manual approval gate)
- **FR-052**: CI/CD pipeline MUST support rollback via "helm rollback" on deployment failure

#### Monitoring and Logging

- **FR-053**: System MUST enable Kubernetes metrics-server for pod/node resource metrics
- **FR-054**: System MUST enable Dapr Zipkin integration for distributed tracing
- **FR-055**: System MUST configure Prometheus to scrape Dapr sidecar metrics
- **FR-056**: System MUST provide Grafana dashboards for: request rates, error rates, latency, Pub/Sub throughput
- **FR-057**: System MUST support log aggregation via "kubectl logs" (minimum) or optional EFK/Loki stack
- **FR-058**: System MUST configure Prometheus alerts for: high error rates, pod restarts, Kafka consumer lag

#### Database Schema

- **FR-059**: Task table MUST add columns: due_at (nullable timestamptz), remind_at (nullable timestamptz), recurring_interval (nullable enum), priority (enum: low/medium/high, default medium)
- **FR-060**: System MUST create Tag table with columns: id, name, user_id (for user-scoped tags)
- **FR-061**: System MUST create TaskTag junction table with columns: task_id, tag_id (for many-to-many relationship)
- **FR-062**: System MUST provide Alembic/SQLAlchemy migration script to add new columns and tables
- **FR-063**: System MUST add indexes: (user_id, due_at), (user_id, priority), (task_id, tag_id)

#### API Updates

- **FR-064**: POST /api/tasks MUST accept new fields: due_at, remind_at, recurring_interval, priority, tags (array of strings)
- **FR-065**: PUT /api/tasks/:id MUST support updating: due_at, remind_at, recurring_interval, priority, tags
- **FR-066**: GET /api/tasks MUST accept query parameters: q (search keyword), priority, tags[], status, due_before, due_after, sort (comma-separated fields), sort_order (asc/desc)
- **FR-067**: GET /api/tasks MUST return pagination metadata: total_count, page, page_size
- **FR-068**: GET /api/tags MUST return list of unique tags for authenticated user
- **FR-069**: AI chatbot tools (add_task, update_task, list_tasks) MUST support all new fields and query parameters

#### Security and Isolation

- **FR-070**: All database queries MUST filter by user_id (authenticated from JWT token)
- **FR-071**: Tag queries MUST be scoped to authenticated user (prevent cross-user tag access)
- **FR-072**: Event payloads MUST include user_id for multi-tenant isolation in consumers
- **FR-073**: Dapr components MUST retrieve secrets from Kubernetes Secrets (never plaintext in YAML)
- **FR-074**: Dapr mTLS MUST be enabled for secure inter-service communication

### Key Entities

- **Task** (enhanced): Represents a user's todo item with fields: id, user_id, title, description, status (pending/completed), due_at (nullable datetime), remind_at (nullable datetime), recurring_interval (nullable enum: daily/weekly/monthly/yearly), priority (enum: low/medium/high, default medium), created_at, updated_at. Relationships: many-to-many with Tag via TaskTag.

- **Tag**: Represents a user-defined category label with fields: id, name (string), user_id (for isolation). Relationships: many-to-many with Task via TaskTag. Each user has their own tag namespace.

- **TaskTag**: Junction table for many-to-many relationship between Task and Tag with fields: task_id (FK to Task), tag_id (FK to Tag). Enables a task to have multiple tags and a tag to be used on multiple tasks.

- **Event**: Represents a published Kafka message with schema: event_type (string: task_created/task_updated/task_completed/task_deleted/reminder_due), task_id (uuid), task_data (JSON object with task fields), user_id (uuid), timestamp (ISO8601 datetime). Events flow through Kafka topics and are consumed by services.

- **ReminderJob**: Represents a scheduled job via Dapr Jobs API with fields: job_name (string: "reminder-{task_id}"), dueTime (ISO8601 datetime = remind_at), data (JSON: task_id, user_id, reminder_message), ttl (time-to-live after dueTime). Jobs are stored in Dapr state store and triggered at exact dueTime.

- **DaprComponent**: Configuration entity for Dapr building blocks with fields: name (string: kafka-pubsub, statestore, kubernetes-secrets), type (string: pubsub.kafka, state.postgresql, secretstores.kubernetes), metadata (key-value pairs for connection strings, credentials), scopes (list of service app-ids that can access this component). Components are defined in YAML and applied to Kubernetes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a daily recurring task and verify that completing it automatically creates the next instance within 5 seconds (event-driven latency)

- **SC-002**: Users receive reminder notifications exactly at the scheduled remind_at time with less than 10 seconds variance (Dapr Jobs API precision)

- **SC-003**: Users can filter tasks by multiple tags using AND logic and receive accurate results in under 1 second for task lists up to 1000 items

- **SC-004**: Users can search for keywords across title and description and receive case-insensitive matches in under 500ms

- **SC-005**: Users can sort tasks by priority and due date (multi-field sort) and see high-priority tasks with nearest due dates first

- **SC-006**: System handles 100 concurrent users creating/completing tasks without event loss or duplicate recurring task creation

- **SC-007**: CI/CD pipeline completes build, test, and deployment to staging within 10 minutes of code push

- **SC-008**: Application successfully deploys to Oracle OKE Always Free tier and operates within free tier resource limits (2 OCPU, 12 GB RAM)

- **SC-009**: Distributed traces are viewable in Zipkin for end-to-end request flows (frontend → backend → Kafka → recurring-service) with complete span data

- **SC-010**: Prometheus metrics show Pub/Sub message throughput, consumer lag, and error rates with 1-minute granularity

- **SC-011**: System handles Kafka consumer failures gracefully with automatic failover and message reprocessing (no lost events)

- **SC-012**: Notification service successfully sends email or push notifications with 99% delivery rate (measured over 1000 reminders)

- **SC-013**: API response time for filtered/sorted task lists remains under 500ms even with complex queries (priority + tags + search + sort)

- **SC-014**: Database migration completes successfully on existing Phase IV deployments without data loss (verified via backup/restore test)

- **SC-015**: Real-time updates (via task-updates topic) propagate to connected clients within 2 seconds of the originating event (WebSocket or polling)

- **SC-016**: System scales horizontally to 3 backend replicas and maintains consistent behavior (no duplicate events, proper load distribution)

- **SC-017**: Rollback via "helm rollback" completes within 2 minutes and restores previous working version without downtime

- **SC-018**: 95% of users successfully set up recurring tasks on first attempt without referring to documentation (usability goal)

- **SC-019**: Tag filtering performance remains under 1 second even when users have 100+ unique tags

- **SC-020**: System operates continuously for 7 days without manual intervention or service restarts (stability goal)

