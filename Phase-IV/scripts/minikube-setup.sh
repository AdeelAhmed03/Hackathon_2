#!/bin/bash
# Minikube setup script for Phase IV Kubernetes deployment
# Usage: ./scripts/minikube-setup.sh

set -e

echo "=== Phase IV: Minikube Setup ==="

# Start Minikube with recommended resources
echo "Starting Minikube cluster..."
minikube start --memory=4096 --cpus=2

# Enable ingress addon
echo "Enabling ingress addon..."
minikube addons enable ingress

# Verify cluster is running
echo "Verifying cluster status..."
kubectl cluster-info

echo ""
echo "=== Minikube setup complete! ==="
echo "Next steps:"
echo "  1. Run: eval \$(minikube docker-env)"
echo "  2. Run: ./scripts/build-images.sh"
echo "  3. Run: ./scripts/deploy.sh"
