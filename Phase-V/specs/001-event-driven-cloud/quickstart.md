# Quickstart Guide: Phase V Deployment

**Feature**: 001-event-driven-cloud
**Date**: 2026-02-09

This guide covers deploying the Phase V Todo application with event-driven architecture locally (Minikube) and to cloud Kubernetes (Oracle OKE).

## Prerequisites

### Required Tools
- Docker Desktop (or Docker Engine)
- kubectl v1.28+
- Helm 3.12+
- Dapr CLI v1.16+
- Git

### Optional Tools
- Oracle Cloud CLI (OCI) - for Oracle OKE deployment
- Azure CLI - for AKS deployment
- Google Cloud SDK - for GKE deployment

## Option 1: Local Deployment (Minikube + Strimzi)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster is running
kubectl get nodes
```

### Step 2: Install Dapr

```bash
# Install Dapr CLI (if not installed)
# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize Dapr on Kubernetes
dapr init -k --wait

# Verify Dapr is running
dapr status -k
kubectl get pods -n dapr-system
```

### Step 3: Deploy Strimzi Kafka

```bash
# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka

# Wait for operator to be ready
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Apply Kafka cluster (KRaft mode - no Zookeeper)
kubectl apply -f dapr-components/strimzi/kafka-cluster.yaml -n kafka

# Wait for Kafka to be ready (may take 2-3 minutes)
kubectl wait kafka/kafka-cluster --for=condition=Ready -n kafka --timeout=300s

# Verify Kafka pods
kubectl get pods -n kafka
```

### Step 4: Apply Dapr Components

```bash
# Apply Dapr components for local environment
kubectl apply -f dapr-components/kafka-pubsub-local.yaml
kubectl apply -f dapr-components/kubernetes-secrets.yaml

# Verify components
kubectl get components
```

### Step 5: Create Secrets

```bash
# Create secrets for the backend
kubectl create secret generic todo-secrets \
  --from-literal=database-url="postgresql://postgres:password@postgres:5432/todo" \
  --from-literal=cohere-api-key="your-cohere-api-key" \
  --from-literal=better-auth-secret="your-jwt-secret-at-least-32-chars"
```

### Step 6: Deploy Application

```bash
# Build images (use Minikube's Docker daemon)
eval $(minikube docker-env)

# Build all service images
docker build -t todo-backend:v5.0.0 ./backend
docker build -t todo-frontend:v5.0.0 ./frontend
docker build -t notification-service:v5.0.0 ./notification-service
docker build -t recurring-service:v5.0.0 ./recurring-service

# Deploy with Helm
helm install postgres ./charts/postgres
helm install todo-backend ./charts/todo-backend --set image.tag=v5.0.0
helm install notification-service ./charts/notification-service --set image.tag=v5.0.0
helm install recurring-service ./charts/recurring-service --set image.tag=v5.0.0
helm install todo-frontend ./charts/todo-frontend --set image.tag=v5.0.0

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=120s
```

### Step 7: Access the Application

```bash
# Port-forward frontend
kubectl port-forward svc/todo-frontend 3000:3000 &

# Port-forward backend (for API testing)
kubectl port-forward svc/todo-backend 8000:8000 &

# Open in browser
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000/docs"
```

### Step 8: Verify Event Flow

```bash
# Check Dapr sidecar logs
kubectl logs -l app=todo-backend -c daprd

# Check Kafka topics (exec into Kafka pod)
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Watch notification service logs
kubectl logs -f -l app=notification-service
```

---

## Option 2: Cloud Deployment (Oracle OKE + Redpanda Cloud)

### Step 1: Oracle Cloud Setup

1. **Sign up for Oracle Cloud** (oracle.com/cloud/free)
   - Credit card required for verification (no charges for Always Free)
   - Choose a region with Always Free availability (e.g., us-ashburn-1)

2. **Install OCI CLI**
   ```bash
   # macOS/Linux
   bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

   # Windows
   powershell -Command "iwr -useb https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.ps1 | iex"

   # Configure CLI
   oci setup config
   ```

3. **Create OKE Cluster** (via OCI Console)
   - Navigate: Developer Services → Kubernetes Clusters → Create Cluster
   - Select: Quick Create
   - Name: `todo-oke-cluster`
   - Kubernetes Version: 1.28+
   - Shape: `VM.Standard.E2.1.Micro` (Always Free)
   - Number of nodes: 2
   - Click: Create Cluster

4. **Configure kubectl**
   ```bash
   # Get cluster OCID from OCI Console
   oci ce cluster create-kubeconfig \
     --cluster-id ocid1.cluster.oc1... \
     --file ~/.kube/config-oke \
     --region us-ashburn-1

   export KUBECONFIG=~/.kube/config-oke
   kubectl get nodes
   ```

### Step 2: Redpanda Cloud Setup

1. **Sign up for Redpanda Cloud** (redpanda.com/cloud)
   - Create account (free tier available)
   - Create a new serverless cluster

2. **Create Topics**
   - Navigate to Topics in Redpanda Console
   - Create topics: `task-events`, `reminders`, `task-updates`
   - Default settings (3 partitions, 7-day retention)

3. **Get Connection Details**
   - Note Bootstrap Servers URL
   - Create SASL credentials (username/password)
   - Security: SASL/SCRAM-SHA-256

### Step 3: Install Dapr on OKE

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true

# Verify Dapr
kubectl get pods -n dapr-system
```

### Step 4: Create Cloud Secrets

```bash
# Create Redpanda credentials secret
kubectl create secret generic redpanda-secrets \
  --from-literal=sasl-password="your-redpanda-password"

# Create application secrets
kubectl create secret generic todo-secrets \
  --from-literal=database-url="postgresql://postgres:password@postgres:5432/todo" \
  --from-literal=cohere-api-key="your-cohere-api-key" \
  --from-literal=better-auth-secret="your-jwt-secret-at-least-32-chars"
```

### Step 5: Apply Cloud Dapr Components

```bash
# Edit kafka-pubsub-cloud.yaml with your Redpanda details
# - Update brokers with your Redpanda bootstrap servers
# - Update saslUsername with your SASL username

kubectl apply -f dapr-components/kafka-pubsub-cloud.yaml
kubectl apply -f dapr-components/kubernetes-secrets.yaml
```

### Step 6: Deploy Application to OKE

```bash
# Option A: Use pre-built images from GitHub Container Registry
helm install postgres ./charts/postgres
helm install todo-backend ./charts/todo-backend \
  --set image.repository=ghcr.io/your-org/todo-backend \
  --set image.tag=v5.0.0
helm install notification-service ./charts/notification-service \
  --set image.repository=ghcr.io/your-org/notification-service \
  --set image.tag=v5.0.0
helm install recurring-service ./charts/recurring-service \
  --set image.repository=ghcr.io/your-org/recurring-service \
  --set image.tag=v5.0.0
helm install todo-frontend ./charts/todo-frontend \
  --set image.repository=ghcr.io/your-org/todo-frontend \
  --set image.tag=v5.0.0

# Option B: Build and push to OCI Container Registry
# (Requires OCI Container Registry setup)
```

### Step 7: Expose Services

```bash
# Get external IP for frontend
kubectl get svc todo-frontend

# If using LoadBalancer type, note the EXTERNAL-IP
# If pending, use port-forward for testing:
kubectl port-forward svc/todo-frontend 3000:3000
```

---

## CI/CD Setup (GitHub Actions)

### Step 1: Configure GitHub Secrets

In your GitHub repository, add these secrets:
- `KUBECONFIG_STAGING`: Base64-encoded kubeconfig for staging cluster
- `KUBECONFIG_PRODUCTION`: Base64-encoded kubeconfig for production cluster
- `COHERE_API_KEY`: Your Cohere API key
- `BETTER_AUTH_SECRET`: Your JWT signing secret

```bash
# Encode kubeconfig
cat ~/.kube/config-oke | base64 -w 0
# Add output as KUBECONFIG_PRODUCTION secret
```

### Step 2: Create Workflow File

The workflow file is at `.github/workflows/deploy.yaml`. It will:
1. Run tests on PR
2. Build Docker images on push to main/develop
3. Push to GitHub Container Registry
4. Deploy to staging (develop branch) or production (main branch)

### Step 3: Trigger Deployment

```bash
# Push to develop for staging deployment
git push origin develop

# Push to main for production deployment
git push origin main
```

---

## Verification Checklist

### Local Deployment
- [ ] Minikube cluster running
- [ ] Dapr pods healthy in `dapr-system` namespace
- [ ] Kafka cluster ready in `kafka` namespace
- [ ] All application pods running
- [ ] Frontend accessible at localhost:3000
- [ ] Can create task and see in list
- [ ] Can complete recurring task and new task spawns

### Cloud Deployment
- [ ] OKE cluster nodes ready
- [ ] Dapr installed and healthy
- [ ] Redpanda Cloud topics created
- [ ] Application pods running with Dapr sidecars
- [ ] External LoadBalancer IP assigned
- [ ] End-to-end task creation works
- [ ] Reminders trigger notifications

### Event Flow Verification
```bash
# 1. Create a recurring task with reminder
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test recurring task",
    "priority": "high",
    "due_at": "2026-02-10T10:00:00Z",
    "remind_at": "2026-02-10T09:00:00Z",
    "recurring_interval": "daily"
  }'

# 2. Check task-events topic received message
kubectl logs -l app=recurring-service

# 3. Complete the task
curl -X POST http://localhost:8000/api/tasks/<task-id>/complete \
  -H "Authorization: Bearer <token>"

# 4. Verify new task was created (check recurring-service logs)
kubectl logs -l app=recurring-service
```

---

## Troubleshooting

### Dapr Issues

```bash
# Check Dapr sidecar status
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].name}{"\n"}{end}'

# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Check Dapr component status
kubectl get components -o yaml
```

### Kafka Issues

```bash
# Check Kafka cluster status
kubectl get kafka -n kafka

# View Kafka operator logs
kubectl logs -l name=strimzi-cluster-operator -n kafka

# List topics
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Application Issues

```bash
# Check pod events
kubectl describe pod <pod-name>

# View application logs
kubectl logs -f <pod-name> -c <container-name>

# Check service endpoints
kubectl get endpoints
```

---

## Environment Variables Reference

| Variable | Service | Description |
|----------|---------|-------------|
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `COHERE_API_KEY` | Backend | Cohere AI API key |
| `BETTER_AUTH_SECRET` | Backend, Frontend | JWT signing secret |
| `DAPR_HTTP_PORT` | All | Dapr sidecar port (default: 3500) |
| `KAFKA_BOOTSTRAP_SERVERS` | Dapr | Kafka/Redpanda brokers |
| `KAFKA_SASL_USERNAME` | Dapr | SASL username (cloud only) |
| `KAFKA_SASL_PASSWORD` | Dapr | SASL password (cloud only) |

