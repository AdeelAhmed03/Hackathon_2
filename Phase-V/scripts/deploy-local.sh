#!/bin/bash
# T121-T123: Local Deployment Script for Minikube
# Phase V: Event-Driven Cloud Todo Application
# Usage: ./scripts/deploy-local.sh [build|deploy|all]

set -e

echo "======================================"
echo "Phase V: Local Deployment"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

VERSION="${VERSION:-v5.0.0}"

# T121: Build Docker images using Minikube's Docker daemon
build_images() {
    log_info "Building Docker images (version: $VERSION)..."

    # Use Minikube's Docker daemon
    eval $(minikube docker-env)

    log_info "Building todo-backend..."
    docker build -t todo-backend:$VERSION ./backend

    log_info "Building todo-frontend..."
    docker build -t todo-frontend:$VERSION ./frontend

    log_info "Building notification-service..."
    docker build -t notification-service:$VERSION ./notification-service

    log_info "Building recurring-service..."
    docker build -t recurring-service:$VERSION ./recurring-service

    log_info "All images built successfully"
    docker images | grep -E "(todo-backend|todo-frontend|notification-service|recurring-service)"
}

# T122: Deploy all services via Helm
deploy_services() {
    log_info "Deploying services via Helm..."

    # Deploy PostgreSQL
    log_info "Deploying PostgreSQL..."
    helm upgrade --install postgres ./charts/postgres \
        --set persistence.enabled=true \
        --wait --timeout 5m || log_warn "PostgreSQL deployment issue"

    # Wait for PostgreSQL to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgres --timeout=120s || true

    # Deploy Backend
    log_info "Deploying todo-backend..."
    helm upgrade --install todo-backend ./charts/todo-backend \
        --set image.repository=todo-backend \
        --set image.tag=$VERSION \
        --set image.pullPolicy=Never \
        --wait --timeout 5m

    # Deploy Notification Service
    log_info "Deploying notification-service..."
    helm upgrade --install notification-service ./charts/notification-service \
        --set image.repository=notification-service \
        --set image.tag=$VERSION \
        --set image.pullPolicy=Never \
        --wait --timeout 5m

    # Deploy Recurring Service
    log_info "Deploying recurring-service..."
    helm upgrade --install recurring-service ./charts/recurring-service \
        --set image.repository=recurring-service \
        --set image.tag=$VERSION \
        --set image.pullPolicy=Never \
        --wait --timeout 5m

    # Deploy Frontend
    log_info "Deploying todo-frontend..."
    helm upgrade --install todo-frontend ./charts/todo-frontend \
        --set image.repository=todo-frontend \
        --set image.tag=$VERSION \
        --set image.pullPolicy=Never \
        --wait --timeout 5m

    log_info "All services deployed"
}

# T123: Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    echo ""
    echo "=== Pods ==="
    kubectl get pods

    echo ""
    echo "=== Services ==="
    kubectl get svc

    echo ""
    echo "=== Dapr Components ==="
    kubectl get component

    echo ""
    echo "=== Dapr Sidecars ==="
    kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.name}{" "}{end}{"\n"}{end}'

    log_info "Deployment verified"
}

# Port forward for testing
port_forward() {
    log_info "Setting up port forwarding..."
    echo "Run these commands in separate terminals:"
    echo "  kubectl port-forward svc/todo-frontend 3000:3000"
    echo "  kubectl port-forward svc/todo-backend 8000:8000"
    echo "  kubectl port-forward svc/zipkin 9411:9411 -n dapr-system"
}

# View logs
view_logs() {
    local service=$1
    if [ -z "$service" ]; then
        echo "Usage: ./scripts/deploy-local.sh logs <service>"
        echo "Services: backend, frontend, notification, recurring"
        exit 1
    fi

    case $service in
        backend)
            kubectl logs -f -l app.kubernetes.io/name=todo-backend -c todo-backend
            ;;
        frontend)
            kubectl logs -f -l app.kubernetes.io/name=todo-frontend -c todo-frontend
            ;;
        notification)
            kubectl logs -f -l app.kubernetes.io/name=notification-service -c notification-service
            ;;
        recurring)
            kubectl logs -f -l app.kubernetes.io/name=recurring-service -c recurring-service
            ;;
        dapr-backend)
            kubectl logs -f -l app.kubernetes.io/name=todo-backend -c daprd
            ;;
        *)
            echo "Unknown service: $service"
            exit 1
            ;;
    esac
}

# Cleanup
cleanup() {
    log_info "Cleaning up deployments..."
    helm uninstall todo-frontend 2>/dev/null || true
    helm uninstall todo-backend 2>/dev/null || true
    helm uninstall notification-service 2>/dev/null || true
    helm uninstall recurring-service 2>/dev/null || true
    helm uninstall postgres 2>/dev/null || true
    log_info "Cleanup complete"
}

# Main
case "${1:-all}" in
    build)
        build_images
        ;;
    deploy)
        deploy_services
        verify_deployment
        ;;
    verify)
        verify_deployment
        ;;
    forward)
        port_forward
        ;;
    logs)
        view_logs "$2"
        ;;
    cleanup)
        cleanup
        ;;
    all)
        build_images
        deploy_services
        verify_deployment
        port_forward
        ;;
    *)
        echo "Usage: $0 {build|deploy|verify|forward|logs|cleanup|all}"
        exit 1
        ;;
esac
