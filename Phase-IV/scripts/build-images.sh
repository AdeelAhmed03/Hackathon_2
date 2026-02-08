#!/bin/bash
# Build Docker images for Phase IV Kubernetes deployment
# Usage: ./scripts/build-images.sh

set -e

VERSION="v4.0.0"

echo "=== Phase IV: Building Docker Images ==="

# Check if using Minikube's Docker daemon
if [ -z "$MINIKUBE_ACTIVE_DOCKERD" ]; then
    echo "WARNING: Not using Minikube's Docker daemon"
    echo "Run: eval \$(minikube docker-env)"
    echo "Then re-run this script"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build backend image
echo "Building backend image: todo-backend:$VERSION"
docker build -t todo-backend:$VERSION ./backend

# Build frontend image
echo "Building frontend image: todo-frontend:$VERSION"
docker build -t todo-frontend:$VERSION ./frontend

echo ""
echo "=== Build complete! ==="
echo ""
echo "Images built:"
docker images | grep -E "todo-backend|todo-frontend" | head -4
echo ""
echo "Next: Run ./scripts/deploy.sh"
