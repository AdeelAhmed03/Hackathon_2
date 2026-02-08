# Quickstart: Local Kubernetes Deployment

**Feature**: 002-local-k8s-deployment
**Date**: 2026-02-06

This guide walks you through deploying the Todo AI Chatbot to a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

Ensure you have the following installed:

- [ ] **Docker Desktop** - Container runtime
- [ ] **Minikube** - Local Kubernetes cluster
- [ ] **Helm 3+** - Kubernetes package manager
- [ ] **kubectl** - Kubernetes CLI
- [ ] **Cohere API Key** - Get one at [dashboard.cohere.com](https://dashboard.cohere.com/)

### Verify Prerequisites

```bash
# Check versions
docker --version      # Docker version 24.0+
minikube version      # minikube version: v1.32+
helm version          # version.BuildInfo{Version:"v3.14+"}
kubectl version       # Client Version: v1.29+
```

---

## Step 1: Start Minikube

```bash
# Start cluster with recommended resources
minikube start --memory=4096 --cpus=2

# Verify cluster is running
kubectl cluster-info

# Enable ingress addon (optional but recommended)
minikube addons enable ingress
```

**Expected Output**:
```
😄  minikube v1.32.0 on Darwin 14.0
✨  Automatically selected the docker driver
📌  Using Docker Desktop driver with root privileges
🧯  Starting control plane node minikube in cluster minikube
🚜  Pulling base image ...
🔥  Creating docker container (CPUs=2, Memory=4096MB) ...
🐳  Preparing Kubernetes v1.29.0 on Docker 24.0.7 ...
🔎  Verifying Kubernetes components...
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster
```

---

## Step 2: Build Container Images

```bash
# Use Minikube's Docker daemon (IMPORTANT!)
eval $(minikube docker-env)

# Verify you're using Minikube's Docker
docker images | head -5  # Should show Minikube's images

# Build backend image
cd backend
docker build -t todo-backend:v4.0.0 .

# Build frontend image
cd ../frontend
docker build -t todo-frontend:v4.0.0 .

# Verify images are built
docker images | grep todo
```

**Expected Output**:
```
todo-backend    v4.0.0    abc123def456    10 seconds ago    285MB
todo-frontend   v4.0.0    789ghi012jkl    5 seconds ago     145MB
```

---

## Step 3: Create Namespace

```bash
kubectl create namespace todo-app

# Verify namespace
kubectl get namespaces | grep todo-app
```

---

## Step 4: Deploy PostgreSQL

```bash
# Deploy PostgreSQL
helm install postgres ./charts/postgres -n todo-app \
  --set secrets.postgresPassword="your-db-password"

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n todo-app --timeout=120s

# Verify PostgreSQL is running
kubectl get pods -n todo-app -l app=postgres
```

**Expected Output**:
```
NAME                        READY   STATUS    RESTARTS   AGE
postgres-7b9c5d6f4-x2k9m    1/1     Running   0          45s
```

---

## Step 5: Deploy Backend

Set your Cohere API key and Better Auth secret:

```bash
# Export secrets (replace with your actual values)
export COHERE_API_KEY="your-cohere-api-key-here"
export BETTER_AUTH_SECRET="your-jwt-secret-here"

# Deploy backend
helm install todo-backend ./charts/todo-backend -n todo-app \
  --set secrets.cohereApiKey="$COHERE_API_KEY" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.databaseUrl="postgresql://postgres:your-db-password@postgres:5432/todo"

# Wait for backend to be ready
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=120s
```

---

## Step 6: Deploy Frontend

```bash
# Deploy frontend
helm install todo-frontend ./charts/todo-frontend -n todo-app

# Wait for frontend to be ready
kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-app --timeout=120s
```

---

## Step 7: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check events for any issues
kubectl get events -n todo-app --sort-by=.metadata.creationTimestamp | tail -10
```

**Expected Output**:
```
NAME                             READY   STATUS    RESTARTS   AGE
postgres-7b9c5d6f4-x2k9m         1/1     Running   0          3m
todo-backend-5f8d7b6c4-abc12     1/1     Running   0          2m
todo-backend-5f8d7b6c4-def34     1/1     Running   0          2m
todo-frontend-3a4b5c6d7-ghi56    1/1     Running   0          1m
todo-frontend-3a4b5c6d7-jkl78    1/1     Running   0          1m
```

---

## Step 8: Access the Application

### Option A: Port Forwarding (Recommended)

```bash
# Forward frontend port
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app &

# Forward backend port (for API testing)
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app &

# Access the application
open http://localhost:3000
```

### Option B: Minikube Service

```bash
# Open frontend in browser
minikube service todo-frontend -n todo-app
```

### Option C: Ingress (if enabled)

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Access via browser
open http://todo.local
```

---

## Step 9: Test the Chatbot

1. Open http://localhost:3000 in your browser
2. Sign up for a new account or sign in
3. Click the chat button in the bottom-right corner
4. Try these commands:
   - "Add a task to buy groceries"
   - "Show my tasks"
   - "Mark the groceries task as complete"

**Expected**: AI responds with task confirmations and the tasks appear in your list.

---

## Cleanup

```bash
# Uninstall all Helm releases
helm uninstall todo-frontend -n todo-app
helm uninstall todo-backend -n todo-app
helm uninstall postgres -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Stop Minikube
minikube stop

# (Optional) Delete Minikube cluster entirely
minikube delete
```

---

## Troubleshooting

### Pod not starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app
```

### Database connection refused

```bash
# Verify PostgreSQL is running
kubectl get pods -l app=postgres -n todo-app

# Check PostgreSQL logs
kubectl logs -l app=postgres -n todo-app

# Test connection from backend pod
kubectl exec -it <backend-pod> -n todo-app -- nc -zv postgres 5432
```

### Frontend can't reach backend

```bash
# Check service endpoints
kubectl get endpoints -n todo-app

# Test backend health from within cluster
kubectl run test --rm -it --image=busybox -n todo-app -- wget -qO- http://todo-backend:8000/health
```

### AI DevOps Tools (Optional)

```bash
# Use kubectl-ai for diagnosis
kubectl-ai "why is my todo-backend pod crashing?"

# Use kagent for health check
kagent health -n todo-app

# Use Gordon for Dockerfile optimization
docker ai scan todo-backend:v4.0.0
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `minikube start` | Start cluster |
| `eval $(minikube docker-env)` | Use Minikube's Docker |
| `kubectl get pods -n todo-app` | List pods |
| `kubectl logs <pod> -n todo-app` | View logs |
| `kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app` | Access frontend |
| `helm list -n todo-app` | List Helm releases |
| `helm upgrade <release> ./charts/<chart> -n todo-app` | Upgrade release |
