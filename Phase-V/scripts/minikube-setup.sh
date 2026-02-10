#!/bin/bash
# T118-T120: Minikube Setup Script with Dapr and Strimzi
# Phase V: Event-Driven Cloud Todo Application
# Usage: ./scripts/minikube-setup.sh

set -e

echo "======================================"
echo "Phase V: Minikube + Dapr + Strimzi Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    command -v minikube &> /dev/null || { log_error "minikube not installed"; exit 1; }
    command -v kubectl &> /dev/null || { log_error "kubectl not installed"; exit 1; }
    command -v helm &> /dev/null || { log_error "helm not installed"; exit 1; }
    if ! command -v dapr &> /dev/null; then
        log_warn "Dapr CLI not installed. Installing..."
        curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
    fi
    log_info "Prerequisites OK"
}

# T118: Start Minikube with increased resources
start_minikube() {
    log_info "Starting Minikube cluster..."
    if minikube status 2>/dev/null | grep -q "Running"; then
        log_warn "Minikube already running"
    else
        minikube start --cpus=4 --memory=8192 --driver=docker
    fi
    minikube addons enable ingress
    minikube addons enable metrics-server
    log_info "Minikube ready"
}

# T118: Install Dapr on Kubernetes
install_dapr() {
    log_info "Installing Dapr..."
    if kubectl get namespace dapr-system &> /dev/null; then
        log_warn "Dapr already installed"
    else
        dapr init -k --wait
    fi
    kubectl get pods -n dapr-system
    log_info "Dapr ready"
}

# T118-T119: Install Strimzi Kafka Operator
install_strimzi() {
    log_info "Installing Strimzi Kafka Operator..."
    kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
    kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka
    log_info "Waiting for Strimzi operator..."
    kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
    log_info "Strimzi ready"
}

# T119: Deploy Kafka cluster (KRaft mode)
deploy_kafka() {
    log_info "Deploying Kafka cluster (KRaft mode)..."
    kubectl apply -f dapr-components/strimzi/kafka-cluster.yaml -n kafka
    log_info "Waiting for Kafka (this may take several minutes)..."
    kubectl wait kafka/kafka-cluster --for=condition=Ready -n kafka --timeout=600s || {
        log_warn "Kafka not ready yet. Check: kubectl get kafka -n kafka"
    }
    kubectl get pods -n kafka
    log_info "Kafka deployed"
}

# T120: Apply Dapr components
apply_dapr_components() {
    log_info "Applying Dapr components..."
    kubectl apply -f dapr-components/kafka-pubsub-local.yaml
    kubectl apply -f dapr-components/kubernetes-secrets.yaml
    kubectl apply -f dapr-components/dapr-config.yaml
    kubectl get component
    log_info "Dapr components applied"
}

# Create secrets
create_secrets() {
    log_info "Creating application secrets..."
    if kubectl get secret todo-secrets &> /dev/null; then
        log_warn "Secrets exist, skipping"
        return
    fi
    kubectl create secret generic todo-secrets \
        --from-literal=cohere-api-key="${COHERE_API_KEY:-your-cohere-api-key}" \
        --from-literal=better-auth-secret="${BETTER_AUTH_SECRET:-your-auth-secret-32chars}" \
        --from-literal=database-url="${DATABASE_URL:-postgresql://postgres:postgres@postgres:5432/todo}"
    log_info "Secrets created"
}

# T142: Install Zipkin
install_zipkin() {
    log_info "Installing Zipkin..."
    kubectl apply -f https://raw.githubusercontent.com/dapr/dapr/master/deploy/zipkin.yaml -n dapr-system || true
    log_info "Zipkin ready: kubectl port-forward svc/zipkin 9411:9411 -n dapr-system"
}

# Main
main() {
    check_prerequisites
    start_minikube
    install_dapr
    install_strimzi
    deploy_kafka
    apply_dapr_components
    create_secrets
    install_zipkin

    echo ""
    echo "======================================"
    echo "Setup Complete!"
    echo "======================================"
    echo "Next steps:"
    echo "  1. eval \$(minikube docker-env)"
    echo "  2. ./scripts/build-images.sh"
    echo "  3. ./scripts/deploy-local.sh"
    echo ""
    echo "Access:"
    echo "  kubectl port-forward svc/todo-frontend 3000:3000"
    echo "  kubectl port-forward svc/todo-backend 8000:8000"
    echo "  kubectl port-forward svc/zipkin 9411:9411 -n dapr-system"
}

main "$@"
