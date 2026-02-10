# Research: Phase V Technology Decisions

**Feature**: 001-event-driven-cloud
**Date**: 2026-02-09
**Status**: Complete

## 1. Dapr v1.16 Kafka Integration

### Decision
Use Dapr Pub/Sub with Kafka component (`pubsub.kafka`) and gzip compression for all event messaging.

### Rationale
- Dapr v1.16+ provides stable Kafka integration with improved reliability
- Abstracts Kafka complexity (no direct kafka-python dependency)
- Consistent API across local (Strimzi) and cloud (Redpanda) environments
- gzip compression balances CPU overhead with bandwidth savings for JSON payloads

### Configuration Details
```yaml
metadata:
  - name: compressionType
    value: "gzip"  # Options: none, gzip, snappy, lz4, zstd
  - name: consumerGroup
    value: "todo-app"
  - name: initialOffset
    value: "oldest"  # Ensures no messages missed on restart
  - name: maxMessageBytes
    value: "1048576"  # 1MB max message size
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Direct kafka-python | Full control, native features | Tight coupling, complex config | Rejected |
| Dapr + snappy | Faster compression | Slightly larger size | Not chosen |
| Dapr + lz4 | Best speed | Less compression ratio | Not chosen |
| Dapr + gzip | Best compression, wide support | Slightly slower | **Selected** |

### Consumer Group Strategy
- Single consumer group `todo-app` for all services
- Each service uses Dapr subscription with routing rules
- Partition by user_id ensures ordering per user
- Dead-letter queue via Dapr component configuration

---

## 2. Dapr Jobs API (Alpha)

### Decision
Use Dapr Jobs API (v1.0-alpha1) for scheduling reminders at exact remind_at times, with cron binding as fallback.

### Rationale
- Jobs API provides exact-time scheduling (vs cron's interval-based approach)
- Alpha status acceptable for non-critical reminder feature
- Callback pattern integrates well with FastAPI endpoints
- Fallback ensures reliability if Jobs API unavailable

### API Pattern
```python
# Schedule a job
POST http://localhost:3500/v1.0-alpha1/jobs/{job-name}
{
    "dueTime": "2026-02-15T14:00:00Z",  # ISO8601 exact time
    "data": {
        "task_id": "uuid",
        "user_id": "uuid",
        "reminder_message": "Task due soon"
    },
    "ttl": "1h"  # Expires 1 hour after dueTime if not executed
}

# Cancel a job
DELETE http://localhost:3500/v1.0-alpha1/jobs/{job-name}

# Callback endpoint (Dapr invokes this at dueTime)
POST /jobs/callback
{
    "name": "reminder-{task-id}",
    "data": { ... },
    "schedule": "@once"
}
```

### Callback Handler Design
```python
@app.post("/jobs/callback")
async def handle_job_callback(request: Request):
    job_data = await request.json()
    task_id = job_data["data"]["task_id"]
    user_id = job_data["data"]["user_id"]

    # Publish reminder event to Kafka
    await publish_event("reminders", {
        "event_type": "reminder_due",
        "task_id": task_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"status": "OK"}
```

### Fallback: Cron Binding
If Jobs API proves unstable:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/5 * * * *"  # Every 5 minutes
```

Backend periodically queries tasks with `remind_at <= NOW()` and sends reminders.

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Dapr Jobs API | Exact time, clean API | Alpha status | **Selected** |
| Dapr Cron Binding | Stable, proven | 5-min granularity | Fallback |
| External scheduler (Celery) | Battle-tested | Extra dependency | Rejected |
| PostgreSQL pg_cron | Native to DB | Vendor lock-in | Rejected |

---

## 3. Strimzi vs Redpanda

### Decision
- **Local (Minikube)**: Strimzi Kafka Operator v0.50+ with KRaft mode
- **Cloud**: Redpanda Cloud free serverless tier

### Rationale

**Strimzi (Local)**:
- Native Kubernetes operator pattern
- KRaft mode eliminates Zookeeper complexity
- Single-replica ephemeral storage sufficient for dev
- Free and open source

**Redpanda Cloud (Production)**:
- Free serverless tier (no infrastructure management)
- Kafka-compatible API (same Dapr component config)
- Built-in schema registry
- SASL/SCRAM authentication

### Strimzi KRaft Configuration
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
    storage:
      type: ephemeral
  # KRaft mode - no Zookeeper
  zookeeper:
    replicas: 0
```

### Redpanda Cloud Setup
1. Sign up at redpanda.com/cloud
2. Create serverless cluster (free tier: 10GB storage, 10MB/s throughput)
3. Create topics via Console: task-events, reminders, task-updates
4. Generate SASL credentials
5. Configure Dapr component with SCRAM-SHA-256 authentication

### Migration Path
- Same Dapr component type (`pubsub.kafka`) for both
- Only metadata changes between local/cloud configs
- Helm values can switch configurations:
  ```bash
  helm install backend ./charts/todo-backend \
    --set dapr.pubsub.config=local  # or 'cloud'
  ```

### Alternatives Considered
| Option | Environment | Pros | Cons | Decision |
|--------|-------------|------|------|----------|
| Strimzi | Local | K8s native, KRaft | More setup | **Selected (local)** |
| Redpanda (self-hosted) | Local | Simple, fast | Extra container | Not chosen |
| Confluent Cloud | Cloud | Enterprise features | Cost | Rejected |
| Redpanda Cloud | Cloud | Free tier, managed | Vendor lock-in | **Selected (cloud)** |
| Amazon MSK | Cloud | AWS integration | Cost, complexity | Rejected |

---

## 4. Oracle OKE vs Azure AKS vs GKE

### Decision
Oracle OKE as primary target (Always Free tier), with Azure AKS and GKE as documented fallbacks.

### Rationale

**Oracle OKE Always Free Tier**:
- 4500 compute hours/month (sufficient for 2 nodes 24/7)
- 3000 OCPU hours/month
- 18000 GB-hours/month
- No credit card charges (verification only)
- Managed Kubernetes control plane (free)

### Comparison
| Provider | Free Tier | Duration | Control Plane | Best For |
|----------|-----------|----------|---------------|----------|
| Oracle OKE | Always Free | Unlimited | Free | **Production (selected)** |
| Azure AKS | $200 credit | 30 days | Free | Short-term testing |
| GKE | $300 credit + 1 free cluster | 90 days | Free (Autopilot) | GCP ecosystem |

### OKE Setup Commands
```bash
# Prerequisites: OCI CLI installed, configured

# Create cluster (via Console or Terraform)
# Quick Create: VM.Standard.E2.1.Micro shape, 2 nodes

# Configure kubectl
oci ce cluster create-kubeconfig \
  --cluster-id ocid1.cluster.oc1... \
  --file ~/.kube/config-oke \
  --region us-ashburn-1

export KUBECONFIG=~/.kube/config-oke
kubectl get nodes
```

### Resource Planning (OKE Always Free)
| Service | CPU | Memory | Replicas |
|---------|-----|--------|----------|
| Frontend | 0.25 | 512Mi | 1 |
| Backend | 0.5 | 1Gi | 1 |
| Notification | 0.25 | 512Mi | 1 |
| Recurring | 0.25 | 512Mi | 1 |
| PostgreSQL | 0.5 | 1Gi | 1 |
| **Total** | **1.75** | **3.5Gi** | - |

Fits within Always Free: 2 OCPU (4 cores), 12GB RAM per node, 2 nodes.

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Oracle OKE | Always Free, no limit | Less popular | **Selected** |
| Azure AKS | Popular, good docs | 30-day credit | Fallback |
| GKE | Best K8s features | Credit expires | Fallback |
| DigitalOcean | Simple | No free tier | Rejected |
| Linode LKE | Affordable | No free tier | Rejected |

---

## 5. Cohere Tool Calling Adapter

### Decision
Implement structured prompt adapter using Cohere's `command-r-plus` model with JSON output format.

### Rationale
- Constitution mandates Cohere-only (NO OpenAI)
- `command-r-plus` has excellent instruction following
- Structured JSON output enables reliable tool parsing
- Temperature 0.1 ensures deterministic responses

### Implementation Pattern
```python
import cohere
import json
from typing import Any

SYSTEM_PROMPT = """You are a task management assistant. Based on the user's message, determine which action to take.

Output ONLY valid JSON in this format:
{"action": "<action_name>", "params": {<parameters>}}

Available actions:
- add_task: Create task. Params: title (required), description, priority (low/medium/high), tags (array), due_at (ISO8601), remind_at (ISO8601), recurring_interval (daily/weekly/monthly/yearly)
- list_tasks: List tasks. Params: priority, tags (array), status (pending/completed), search (keyword), sort_by (priority/due_at/created_at/title), sort_order (asc/desc)
- complete_task: Complete task. Params: task_id (required)
- update_task: Update task. Params: task_id (required), plus any fields to update
- delete_task: Delete task. Params: task_id (required)
- search_tasks: Search by keyword. Params: keyword (required), priority, tags

Do not include any explanation, only the JSON object."""

class CohereToolAdapter:
    def __init__(self, api_key: str):
        self.client = cohere.Client(api_key)

    async def decide_action(self, user_message: str, conversation_history: list = None) -> dict[str, Any]:
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat(
            message=user_message,
            preamble=SYSTEM_PROMPT,
            model="command-r-plus",
            temperature=0.1,
            chat_history=[
                {"role": m["role"], "message": m["content"]}
                for m in messages[:-1]
            ]
        )

        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback: extract JSON from response
            import re
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Could not parse action from: {response.text}")

    async def execute_tool(self, action: str, params: dict, user_id: str) -> dict:
        """Execute the determined action with user context."""
        # Import tools dynamically to avoid circular imports
        from tools.mcp_tools import (
            add_task, list_tasks, complete_task,
            update_task, delete_task, search_tasks
        )

        tool_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task,
            "search_tasks": search_tasks,
        }

        if action not in tool_map:
            return {"error": f"Unknown action: {action}"}

        # Inject user_id for security
        params["user_id"] = user_id

        return await tool_map[action](**params)
```

### Error Handling
- JSON parse failure: Regex extraction fallback
- Unknown action: Return error response
- Tool execution failure: Wrap in try/except, return error
- Rate limiting: Exponential backoff with max 3 retries

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Cohere command-r-plus | Best instruction following | Cost | **Selected** |
| Cohere command-r | Cheaper | Less reliable JSON | Fallback |
| Cohere embed + search | Semantic matching | Not conversational | Rejected |
| Fine-tuned model | Best accuracy | Training overhead | Future |

---

## 6. Event Schema Design

### Decision
Use JSON schema with CloudEvents-inspired structure for all Kafka messages.

### Rationale
- JSON is human-readable and widely supported
- CloudEvents provides proven event structure patterns
- Schema validation ensures data integrity
- user_id in all events enables multi-tenant isolation

### Event Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TaskEvent",
  "type": "object",
  "required": ["event_type", "task_id", "user_id", "timestamp"],
  "properties": {
    "event_type": {
      "type": "string",
      "enum": ["task_created", "task_updated", "task_completed", "task_deleted", "reminder_due"]
    },
    "task_id": {
      "type": "string",
      "format": "uuid"
    },
    "task_data": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "due_at": {"type": "string", "format": "date-time"},
        "remind_at": {"type": "string", "format": "date-time"},
        "recurring_interval": {"type": "string", "enum": ["daily", "weekly", "monthly", "yearly"]},
        "status": {"type": "string", "enum": ["pending", "completed"]}
      }
    },
    "user_id": {
      "type": "string",
      "format": "uuid"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "source": {"type": "string"},
        "correlation_id": {"type": "string"},
        "version": {"type": "string"}
      }
    }
  }
}
```

### Topic Partitioning
- Partition key: `user_id`
- Ensures ordering of events per user
- Enables consumer parallelism across users
- Recommended: 3 partitions per topic (balances parallelism and overhead)

---

## 7. Consumer Idempotency

### Decision
Implement idempotent consumers using event deduplication with task_id + event_type + timestamp.

### Rationale
- Kafka guarantees at-least-once delivery
- Consumers may process same event multiple times
- Idempotency prevents duplicate recurring tasks
- Database constraints enforce uniqueness

### Implementation Pattern
```python
from datetime import datetime, timedelta

class IdempotentConsumer:
    def __init__(self, db_session):
        self.db = db_session
        self.processed_events = set()  # In-memory cache
        self.cache_ttl = timedelta(hours=1)

    async def process_event(self, event: dict) -> bool:
        """Returns True if event was processed, False if duplicate."""
        event_key = f"{event['task_id']}:{event['event_type']}:{event['timestamp']}"

        # Check in-memory cache first
        if event_key in self.processed_events:
            return False

        # Check database for processed event
        existing = await self.db.query(ProcessedEvent).filter(
            ProcessedEvent.event_key == event_key
        ).first()

        if existing:
            self.processed_events.add(event_key)
            return False

        # Process event
        try:
            await self._handle_event(event)

            # Record processed event
            await self.db.add(ProcessedEvent(
                event_key=event_key,
                processed_at=datetime.utcnow()
            ))
            await self.db.commit()

            self.processed_events.add(event_key)
            return True

        except Exception as e:
            await self.db.rollback()
            raise
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Event key deduplication | Simple, reliable | DB storage overhead | **Selected** |
| Kafka exactly-once | Native support | Complex config | Future enhancement |
| Optimistic locking | No extra table | Race conditions | Rejected |
| Redis dedup cache | Fast | Extra dependency | Not chosen |

---

## Summary of Decisions

| Topic | Decision | Confidence |
|-------|----------|------------|
| Dapr Kafka Integration | pubsub.kafka with gzip compression | High |
| Reminder Scheduling | Dapr Jobs API (alpha) + cron fallback | Medium |
| Local Kafka | Strimzi v0.50+ with KRaft | High |
| Cloud Kafka | Redpanda Cloud free serverless | High |
| Cloud Kubernetes | Oracle OKE Always Free | High |
| AI Integration | Cohere command-r-plus with JSON prompt | High |
| Event Schema | JSON with CloudEvents structure | High |
| Consumer Pattern | Idempotent with event key dedup | High |

All research items resolved. Ready for Phase 1: Design & Contracts.

