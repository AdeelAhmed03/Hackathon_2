#!/bin/bash
# Deployment script for Phase IV Kubernetes deployment
# Usage: ./scripts/deploy.sh [COHERE_API_KEY] [BETTER_AUTH_SECRET]

set -e

NAMESPACE="todo-app"
COHERE_API_KEY="${1:-$COHERE_API_KEY}"
BETTER_AUTH_SECRET="${2:-$BETTER_AUTH_SECRET}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-todopassword123}"

if [ -z "$COHERE_API_KEY" ]; then
    echo "ERROR: COHERE_API_KEY is required"
    echo "Usage: ./scripts/deploy.sh <COHERE_API_KEY> <BETTER_AUTH_SECRET>"
    echo "Or set environment variables: export COHERE_API_KEY=... BETTER_AUTH_SECRET=..."
    exit 1
fi

if [ -z "$BETTER_AUTH_SECRET" ]; then
    echo "ERROR: BETTER_AUTH_SECRET is required"
    exit 1
fi

echo "=== Phase IV: Deploying Todo App to Kubernetes ==="

# Create namespace
echo "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy PostgreSQL
echo "Deploying PostgreSQL..."
helm upgrade --install postgres ./charts/postgres -n $NAMESPACE \
    --set secrets.postgresPassword="$POSTGRES_PASSWORD"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=120s

# Deploy Backend
echo "Deploying Backend..."
helm upgrade --install todo-backend ./charts/todo-backend -n $NAMESPACE \
    --set secrets.cohereApiKey="$COHERE_API_KEY" \
    --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
    --set secrets.databaseUrl="postgresql://postgres:$POSTGRES_PASSWORD@postgres:5432/todo"

# Deploy Frontend
echo "Deploying Frontend..."
helm upgrade --install todo-frontend ./charts/todo-frontend -n $NAMESPACE

# Wait for all pods to be ready
echo "Waiting for all services to be ready..."
kubectl wait --for=condition=ready pod -l app=todo-backend -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-frontend -n $NAMESPACE --timeout=120s

echo ""
echo "=== Deployment complete! ==="
echo ""
echo "To access the application:"
echo "  kubectl port-forward svc/todo-frontend 3000:3000 -n $NAMESPACE &"
echo "  kubectl port-forward svc/todo-backend 8000:8000 -n $NAMESPACE &"
echo "  open http://localhost:3000"
echo ""
echo "Or use minikube service:"
echo "  minikube service todo-frontend -n $NAMESPACE"
