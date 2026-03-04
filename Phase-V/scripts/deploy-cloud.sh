#!/bin/bash
# Cloud Deployment Script for Azure AKS Free Tier
# Phase V: Event-Driven Cloud Todo Application
# Usage: ./scripts/deploy-cloud.sh [setup|deploy|verify|all]

set -e

echo "======================================"
echo "Phase V: Azure AKS Cloud Deployment"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
REGISTRY="${REGISTRY:-ghcr.io}"
NAMESPACE="${NAMESPACE:-production}"
VERSION="${VERSION:-v5.0.0}"

# Azure Configuration (Free Tier)
AKS_RESOURCE_GROUP="${AKS_RESOURCE_GROUP:-todo-app-rg}"
AKS_CLUSTER_NAME="${AKS_CLUSTER_NAME:-todo-aks-cluster}"
AKS_LOCATION="${AKS_LOCATION:-eastus}"
AKS_NODE_COUNT="${AKS_NODE_COUNT:-2}"
AKS_NODE_VM_SIZE="${AKS_NODE_VM_SIZE:-Standard_B2s}"  # Free tier eligible

# Check Azure CLI prerequisites
check_azure_cli() {
    log_info "Checking Azure CLI..."
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI not installed. Install it:"
        echo "  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        echo "  or: brew install azure-cli"
        exit 1
    fi

    # Check if logged in
    if ! az account show &> /dev/null; then
        log_warn "Not logged into Azure. Running az login..."
        az login
    fi

    log_info "Azure CLI ready. Account: $(az account show --query name -o tsv)"
}

# Create Azure Resource Group
create_resource_group() {
    log_info "Creating Resource Group: $AKS_RESOURCE_GROUP in $AKS_LOCATION..."

    if az group show --name "$AKS_RESOURCE_GROUP" &> /dev/null; then
        log_warn "Resource group already exists"
    else
        az group create \
            --name "$AKS_RESOURCE_GROUP" \
            --location "$AKS_LOCATION"
        log_info "Resource group created"
    fi
}

# Create AKS Cluster (Free Tier)
create_aks_cluster() {
    log_info "Creating AKS Cluster: $AKS_CLUSTER_NAME..."
    log_info "This may take 5-10 minutes..."

    if az aks show --resource-group "$AKS_RESOURCE_GROUP" --name "$AKS_CLUSTER_NAME" &> /dev/null; then
        log_warn "AKS cluster already exists"
    else
        # Create AKS cluster with free tier settings
        az aks create \
            --resource-group "$AKS_RESOURCE_GROUP" \
            --name "$AKS_CLUSTER_NAME" \
            --node-count "$AKS_NODE_COUNT" \
            --node-vm-size "$AKS_NODE_VM_SIZE" \
            --tier free \
            --generate-ssh-keys \
            --enable-managed-identity \
            --network-plugin azure \
            --network-policy azure \
            --enable-addons monitoring \
            --no-wait

        log_info "AKS cluster creation initiated. Waiting for completion..."
        az aks wait \
            --resource-group "$AKS_RESOURCE_GROUP" \
            --name "$AKS_CLUSTER_NAME" \
            --created \
            --timeout 1800

        log_info "AKS cluster created successfully"
    fi
}

# Configure kubectl for AKS
configure_kubectl() {
    log_info "Configuring kubectl for AKS..."

    az aks get-credentials \
        --resource-group "$AKS_RESOURCE_GROUP" \
        --name "$AKS_CLUSTER_NAME" \
        --overwrite-existing

    kubectl cluster-info
    kubectl get nodes
    log_info "kubectl configured successfully"
}

# Install Dapr on AKS
install_dapr() {
    log_info "Installing Dapr on AKS..."

    # Add Dapr Helm repo
    helm repo add dapr https://dapr.github.io/helm-charts/ || true
    helm repo update

    # Check if Dapr is already installed
    if helm list -n dapr-system | grep -q dapr; then
        log_warn "Dapr already installed, upgrading..."
    fi

    # Install/upgrade Dapr (without HA for free tier resource constraints)
    helm upgrade --install dapr dapr/dapr \
        --namespace dapr-system \
        --create-namespace \
        --set global.ha.enabled=false \
        --set global.mtls.enabled=true \
        --wait --timeout 5m

    kubectl get pods -n dapr-system
    log_info "Dapr installed"
}

# Create Redpanda Cloud secrets
create_redpanda_secrets() {
    log_info "Creating Redpanda Cloud secrets..."

    if [ -z "$REDPANDA_SASL_PASSWORD" ]; then
        log_warn "REDPANDA_SASL_PASSWORD not set, skipping Redpanda secrets"
        log_warn "Kafka/Redpanda event streaming will not be available"
        log_warn "Set REDPANDA_SASL_PASSWORD to enable event-driven features"
        return 0
    fi

    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

    kubectl create secret generic redpanda-secrets \
        --namespace $NAMESPACE \
        --from-literal=sasl-password="$REDPANDA_SASL_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_info "Redpanda secrets created"
}

# Apply Dapr components
apply_dapr_components() {
    log_info "Applying Dapr components..."

    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

    # Apply Kafka pubsub only if Redpanda is configured
    if [ -n "$REDPANDA_SASL_PASSWORD" ]; then
        kubectl apply -f dapr-components/kafka-pubsub-cloud.yaml -n $NAMESPACE
    else
        log_warn "Skipping Kafka pubsub component (Redpanda not configured)"
    fi

    kubectl apply -f dapr-components/kubernetes-secrets.yaml -n $NAMESPACE
    kubectl apply -f dapr-components/dapr-config.yaml -n $NAMESPACE

    kubectl get component -n $NAMESPACE 2>/dev/null || true
    log_info "Dapr components applied"
}

# Create application secrets
create_app_secrets() {
    log_info "Creating application secrets..."

    if [ -z "$COHERE_API_KEY" ]; then
        log_error "COHERE_API_KEY not set"
        echo "  export COHERE_API_KEY=<your-cohere-api-key>"
        exit 1
    fi

    if [ -z "$BETTER_AUTH_SECRET" ]; then
        log_warn "BETTER_AUTH_SECRET not set, generating random secret..."
        BETTER_AUTH_SECRET=$(openssl rand -base64 32)
    fi

    if [ -z "$DATABASE_URL" ]; then
        log_warn "DATABASE_URL not set, using default PostgreSQL URL..."
        DATABASE_URL="postgresql://postgres:postgres@postgres:5432/todo"
    fi

    kubectl create secret generic todo-secrets \
        --namespace $NAMESPACE \
        --from-literal=cohere-api-key="$COHERE_API_KEY" \
        --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
        --from-literal=database-url="$DATABASE_URL" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_info "Application secrets created"
}

# Deploy services to AKS
deploy_services() {
    log_info "Deploying services to AKS..."

    local image_prefix="${REGISTRY}/${GITHUB_REPOSITORY:-todo-app}"

    # Deploy PostgreSQL
    log_info "Deploying PostgreSQL..."
    helm upgrade --install postgres ./charts/postgres \
        --namespace $NAMESPACE \
        --set persistence.enabled=true \
        --set persistence.storageClass=managed-csi \
        --set resources.requests.memory=256Mi \
        --set resources.requests.cpu=100m \
        --wait --timeout 10m || log_warn "PostgreSQL deployment issue"

    # Wait for PostgreSQL
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgres -n $NAMESPACE --timeout=120s || true

    # Deploy Backend
    log_info "Deploying todo-backend..."
    helm upgrade --install todo-backend ./charts/todo-backend \
        --namespace $NAMESPACE \
        --set image.repository="$image_prefix/todo-backend" \
        --set image.tag=$VERSION \
        --set secrets.cohereApiKey="$COHERE_API_KEY" \
        --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
        --set secrets.databaseUrl="$DATABASE_URL" \
        --set service.type=LoadBalancer \
        --set replicaCount=1 \
        --set resources.requests.memory=128Mi \
        --set resources.requests.cpu=50m \
        --wait --timeout 5m

    # Deploy Notification Service
    log_info "Deploying notification-service..."
    helm upgrade --install notification-service ./charts/notification-service \
        --namespace $NAMESPACE \
        --set image.repository="$image_prefix/notification-service" \
        --set image.tag=$VERSION \
        --set replicaCount=1 \
        --set resources.requests.memory=64Mi \
        --set resources.requests.cpu=25m \
        --wait --timeout 5m

    # Deploy Recurring Service
    log_info "Deploying recurring-service..."
    helm upgrade --install recurring-service ./charts/recurring-service \
        --namespace $NAMESPACE \
        --set image.repository="$image_prefix/recurring-service" \
        --set image.tag=$VERSION \
        --set replicaCount=1 \
        --set resources.requests.memory=64Mi \
        --set resources.requests.cpu=25m \
        --wait --timeout 5m

    # Deploy Frontend
    log_info "Deploying todo-frontend..."
    helm upgrade --install todo-frontend ./charts/todo-frontend \
        --namespace $NAMESPACE \
        --set image.repository="$image_prefix/todo-frontend" \
        --set image.tag=$VERSION \
        --set secrets.databaseUrl="$DATABASE_URL" \
        --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
        --set config.backendApiUrl="http://todo-backend:8000" \
        --set service.type=LoadBalancer \
        --set replicaCount=1 \
        --set resources.requests.memory=128Mi \
        --set resources.requests.cpu=50m \
        --wait --timeout 5m

    log_info "All services deployed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying AKS deployment..."

    echo ""
    echo "=== Nodes ==="
    kubectl get nodes

    echo ""
    echo "=== Pods ==="
    kubectl get pods -n $NAMESPACE

    echo ""
    echo "=== Services ==="
    kubectl get svc -n $NAMESPACE

    echo ""
    echo "=== Dapr Components ==="
    kubectl get component -n $NAMESPACE

    echo ""
    echo "=== External Endpoints ==="
    FRONTEND_IP=$(kubectl get svc todo-frontend -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    BACKEND_IP=$(kubectl get svc todo-backend -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

    echo "Frontend: http://$FRONTEND_IP:3000"
    echo "Backend API: http://$BACKEND_IP:8000"
    echo ""
    echo "If IPs show 'pending', wait a minute and run: ./scripts/deploy-cloud.sh verify"

    log_info "Deployment verified"
}

# Install Zipkin for tracing
install_zipkin() {
    log_info "Installing Zipkin for distributed tracing..."

    kubectl apply -f https://raw.githubusercontent.com/dapr/dapr/master/deploy/zipkin.yaml -n dapr-system || true

    log_info "Zipkin installed. Access via:"
    echo "  kubectl port-forward svc/zipkin 9411:9411 -n dapr-system"
}

# Cleanup / Delete cluster
cleanup() {
    log_warn "This will delete the AKS cluster and all resources!"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" = "yes" ]; then
        log_info "Deleting AKS cluster..."
        az aks delete \
            --resource-group "$AKS_RESOURCE_GROUP" \
            --name "$AKS_CLUSTER_NAME" \
            --yes --no-wait

        log_info "Cluster deletion initiated"
        echo "To delete the resource group entirely:"
        echo "  az group delete --name $AKS_RESOURCE_GROUP --yes --no-wait"
    else
        log_info "Cleanup cancelled"
    fi
}

# Get cluster info
get_info() {
    echo "=== Azure AKS Configuration ==="
    echo "Resource Group: $AKS_RESOURCE_GROUP"
    echo "Cluster Name: $AKS_CLUSTER_NAME"
    echo "Location: $AKS_LOCATION"
    echo "Node Count: $AKS_NODE_COUNT"
    echo "Node VM Size: $AKS_NODE_VM_SIZE"
    echo ""
    echo "=== Required Environment Variables ==="
    echo "COHERE_API_KEY: ${COHERE_API_KEY:+set}"
    echo "BETTER_AUTH_SECRET: ${BETTER_AUTH_SECRET:+set}"
    echo "DATABASE_URL: ${DATABASE_URL:+set}"
    echo "REDPANDA_SASL_PASSWORD: ${REDPANDA_SASL_PASSWORD:+set}"
    echo "GITHUB_REPOSITORY: ${GITHUB_REPOSITORY:-not set (will use 'todo-app')}"
}

# Full setup
setup() {
    check_azure_cli
    create_resource_group
    create_aks_cluster
    configure_kubectl
    install_dapr
    install_zipkin
    create_redpanda_secrets
    apply_dapr_components
    create_app_secrets
}

# Main
case "${1:-help}" in
    setup)
        setup
        ;;
    deploy)
        deploy_services
        verify_deployment
        ;;
    verify)
        verify_deployment
        ;;
    configure)
        check_azure_cli
        configure_kubectl
        ;;
    dapr)
        install_dapr
        ;;
    secrets)
        create_redpanda_secrets
        create_app_secrets
        ;;
    components)
        apply_dapr_components
        ;;
    zipkin)
        install_zipkin
        ;;
    cleanup)
        cleanup
        ;;
    info)
        get_info
        ;;
    all)
        setup
        deploy_services
        verify_deployment
        ;;
    help|*)
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  setup      - Create AKS cluster and install Dapr (first time)"
        echo "  deploy     - Deploy all services to AKS"
        echo "  verify     - Check deployment status and get endpoints"
        echo "  configure  - Configure kubectl for existing cluster"
        echo "  dapr       - Install/upgrade Dapr only"
        echo "  secrets    - Create/update secrets only"
        echo "  components - Apply Dapr components only"
        echo "  zipkin     - Install Zipkin tracing"
        echo "  cleanup    - Delete AKS cluster (WARNING: destructive)"
        echo "  info       - Show configuration and environment variables"
        echo "  all        - Full setup + deploy + verify"
        echo ""
        echo "Azure Free Tier Configuration:"
        echo "  - 2 nodes with Standard_B2s VMs"
        echo "  - 750 hours/month free for B1s/B2s VMs"
        echo "  - AKS control plane is always free"
        echo ""
        echo "Required environment variables:"
        echo "  COHERE_API_KEY         - Cohere API key"
        echo "  REDPANDA_SASL_PASSWORD - Redpanda Cloud SASL password"
        echo ""
        echo "Optional environment variables:"
        echo "  AKS_RESOURCE_GROUP     - Resource group name (default: todo-app-rg)"
        echo "  AKS_CLUSTER_NAME       - Cluster name (default: todo-aks-cluster)"
        echo "  AKS_LOCATION           - Azure region (default: eastus)"
        echo "  BETTER_AUTH_SECRET     - Auth secret (auto-generated if not set)"
        echo "  DATABASE_URL           - PostgreSQL URL (uses in-cluster if not set)"
        echo "  GITHUB_REPOSITORY      - For image registry (default: todo-app)"
        ;;
esac
