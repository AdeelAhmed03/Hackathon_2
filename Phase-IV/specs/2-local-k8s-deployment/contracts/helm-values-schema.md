# Helm Values Schema: Local Kubernetes Deployment

**Feature**: 002-local-k8s-deployment
**Date**: 2026-02-06

This document defines the values.yaml schema for each Helm chart.

---

## charts/todo-backend/values.yaml

```yaml
# Replica configuration
replicaCount: 2

# Container image
image:
  repository: todo-backend
  tag: v4.0.0
  pullPolicy: IfNotPresent

# Service configuration
service:
  type: ClusterIP
  port: 8000

# Secret values (set via --set, never commit to git)
secrets:
  cohereApiKey: ""           # REQUIRED: Cohere API key
  betterAuthSecret: ""       # REQUIRED: JWT signing secret
  databaseUrl: "postgresql://postgres:password@postgres:5432/todo"

# Non-sensitive configuration
config:
  frontendUrl: "http://todo-frontend:3000"
  port: "8000"

# Resource limits
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"

# Health probes
livenessProbe:
  enabled: true
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  enabled: true
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5

# Security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1001

# Ingress (optional)
ingress:
  enabled: false
  className: nginx
  hosts:
    - host: todo.local
      paths:
        - path: /api
          pathType: Prefix
```

---

## charts/todo-frontend/values.yaml

```yaml
# Replica configuration
replicaCount: 2

# Container image
image:
  repository: todo-frontend
  tag: v4.0.0
  pullPolicy: IfNotPresent

# Service configuration
service:
  type: ClusterIP
  port: 3000

# Non-sensitive configuration
config:
  apiBaseUrl: "http://todo-backend:8000"
  baseUrl: "http://localhost:3000"

# Resource limits
resources:
  requests:
    memory: "128Mi"
    cpu: "50m"
  limits:
    memory: "256Mi"
    cpu: "200m"

# Health probes
livenessProbe:
  enabled: true
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 15
  periodSeconds: 10

readinessProbe:
  enabled: true
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5

# Security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1001

# Ingress (optional)
ingress:
  enabled: false
  className: nginx
  hosts:
    - host: todo.local
      paths:
        - path: /
          pathType: Prefix
```

---

## charts/postgres/values.yaml

```yaml
# Replica configuration (always 1 for PostgreSQL)
replicaCount: 1

# Container image
image:
  repository: postgres
  tag: "16-alpine"
  pullPolicy: IfNotPresent

# Service configuration
service:
  type: ClusterIP
  port: 5432

# Secret values
secrets:
  postgresPassword: ""       # REQUIRED: Database password
  postgresUser: "postgres"
  postgresDb: "todo"

# Persistent storage
persistence:
  enabled: true
  storageClass: "standard"   # Minikube default
  size: 1Gi
  accessModes:
    - ReadWriteOnce

# Resource limits
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"

# Health probes
livenessProbe:
  enabled: true
  exec:
    command:
      - pg_isready
      - -U
      - postgres
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  enabled: true
  exec:
    command:
      - pg_isready
      - -U
      - postgres
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## Value Types Reference

| Type | Description | Example |
|------|-------------|---------|
| `replicaCount` | int | Number of pod replicas |
| `image.repository` | string | Docker image name |
| `image.tag` | string | Image version tag |
| `image.pullPolicy` | enum | IfNotPresent, Always, Never |
| `service.type` | enum | ClusterIP, NodePort, LoadBalancer |
| `service.port` | int | Service port number |
| `secrets.*` | string | Sensitive values (base64 encoded in K8s) |
| `config.*` | string | Non-sensitive configuration |
| `resources.requests.*` | string | Minimum resource allocation |
| `resources.limits.*` | string | Maximum resource allocation |
| `persistence.size` | string | Storage size (e.g., "1Gi") |

---

## Required Values

These values MUST be provided via `--set` during deployment:

### todo-backend
- `secrets.cohereApiKey` - Cohere API key for AI chatbot
- `secrets.betterAuthSecret` - JWT signing secret

### postgres
- `secrets.postgresPassword` - Database password

---

## Example Deployment Commands

```bash
# PostgreSQL
helm install postgres ./charts/postgres -n todo-app \
  --set secrets.postgresPassword="secure-password-123"

# Backend
helm install todo-backend ./charts/todo-backend -n todo-app \
  --set secrets.cohereApiKey="co-xxxx" \
  --set secrets.betterAuthSecret="jwt-secret-xxx" \
  --set secrets.databaseUrl="postgresql://postgres:secure-password-123@postgres:5432/todo"

# Frontend
helm install todo-frontend ./charts/todo-frontend -n todo-app
```

---

## Values Override File

For local development, create a `values-local.yaml`:

```yaml
# values-local.yaml (DO NOT COMMIT TO GIT)
secrets:
  cohereApiKey: "your-actual-key"
  betterAuthSecret: "your-actual-secret"
  databaseUrl: "postgresql://postgres:your-password@postgres:5432/todo"
```

Then deploy with:
```bash
helm install todo-backend ./charts/todo-backend -n todo-app -f values-local.yaml
```

Add `values-local.yaml` to `.gitignore`.
