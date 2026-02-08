#!/bin/bash
# Teardown script for Phase IV Kubernetes deployment
# Usage: ./scripts/teardown.sh

set -e

NAMESPACE="todo-app"

echo "=== Phase IV: Tearing Down Todo App ==="

# Uninstall Helm releases
echo "Uninstalling Helm releases..."
helm uninstall todo-frontend -n $NAMESPACE 2>/dev/null || echo "todo-frontend not found"
helm uninstall todo-backend -n $NAMESPACE 2>/dev/null || echo "todo-backend not found"
helm uninstall postgres -n $NAMESPACE 2>/dev/null || echo "postgres not found"

# Delete namespace (this will also delete PVCs)
echo "Deleting namespace: $NAMESPACE"
kubectl delete namespace $NAMESPACE --ignore-not-found=true

echo ""
echo "=== Teardown complete! ==="
echo ""
echo "Note: To completely remove Minikube cluster:"
echo "  minikube stop"
echo "  minikube delete"
