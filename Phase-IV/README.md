# Full-Stack Todo Application with AI Chatbot (Phase IV)

A modern, cloud-native full-stack todo application built with FastAPI backend and Next.js 16 frontend, featuring JWT authentication, SQLModel ORM, Better Auth integration, **AI-powered natural language task management**, and **Kubernetes deployment with AI-assisted DevOps**.

## Phase IV: Kubernetes Deployment

This phase adds cloud-native deployment capabilities:
- **Containerization**: Production-optimized Dockerfiles for frontend and backend
- **Kubernetes**: Local Minikube cluster for orchestration
- **Helm Charts**: Production-grade packaging for all services
- **AI DevOps Tools**: Gordon, kubectl-ai, and kagent for intelligent infrastructure management
- **Local PostgreSQL**: Helm-managed database (replaces Neon for local deployment)

## Features

### Core Features
- **User Authentication**: Secure JWT-based authentication with Better Auth
- **Task Management**: Complete CRUD operations for todo tasks
- **Multi-User Support**: Each user has isolated data with proper security
- **Modern Tech Stack**: FastAPI, Next.js 16, SQLModel, PostgreSQL

### AI Chatbot Features (Phase III)
- **Natural Language Processing**: Manage tasks using conversational language
- **Floating Chat Widget**: Always-accessible chat interface on every page
- **Intent Recognition**: Automatically understands user commands
- **Multi-Tool Execution**: Performs complex operations in a single request
- **Conversation History**: Maintains context across chat sessions
- **Real-time Responses**: Instant feedback with loading indicators
- **Tool Result Badges**: Visual confirmation of completed actions

### Advanced Todo Features
- **Priorities**: Low, Medium, High priority levels
- **Tags**: Multi-select tagging system for organization
- **Search**: Case-insensitive keyword search
- **Filtering**: Filter by tags, priorities, and status
- **Due Dates**: Timezone-aware datetime with relative display
- **Recurring Tasks**: Daily, weekly, monthly, yearly recurrence patterns
- **Visual Indicators**: Status badges and due date warnings

### Kubernetes Features (Phase IV)
- **Helm Charts**: Declarative deployment configuration
- **ConfigMaps & Secrets**: Secure configuration management
- **PersistentVolumes**: Data durability for PostgreSQL
- **Health Probes**: Automatic container health monitoring
- **Rolling Updates**: Zero-downtime deployments

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLModel**: SQLAlchemy-based ORM with Pydantic integration
- **Cohere AI**: Large Language Model for natural language processing
- **Better Auth**: Authentication and authorization
- **PostgreSQL**: Local database via Helm (Phase IV)
- **Pydantic v2**: Data validation and settings management

### Frontend
- **Next.js 16**: React framework with App Router
- **TailwindCSS**: Utility-first CSS framework
- **Framer Motion**: Animation library for smooth UI transitions
- **Better Auth**: Client-side authentication
- **React Hook Form**: Form management
- **Zod**: Schema validation
- **Lucide React**: Icon library

### Infrastructure (Phase IV)
- **Docker**: Container runtime
- **Gordon (Docker AI)**: Intelligent Dockerfile generation
- **Minikube**: Local Kubernetes cluster
- **Helm 3+**: Kubernetes package manager
- **kubectl**: Kubernetes CLI
- **kubectl-ai**: AI-assisted Kubernetes operations
- **kagent**: Intelligent monitoring and optimization

### AI Integration
- **Cohere Command R**: LLM for intent extraction and response generation
- **Custom Tool System**: Extensible tool framework for task operations
- **Stateless Chat**: No server-side session storage, database-backed history

## Project Structure

```
Phase-IV/
├── backend/                          # FastAPI backend
│   ├── src/
│   │   ├── models/                  # SQLModel database models
│   │   ├── services/               # Business logic
│   │   ├── tools/                  # MCP-style AI tools
│   │   ├── api/                   # API endpoints
│   │   ├── middleware/            # Authentication middleware
│   │   └── database/             # Database configuration
│   ├── Dockerfile                  # Backend container
│   └── requirements.txt
├── frontend/                        # Next.js frontend
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   ├── components/           # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── types/              # TypeScript definitions
│   │   └── lib/               # Shared utilities
│   ├── Dockerfile              # Frontend container
│   └── package.json
├── charts/                         # Helm charts (Phase IV)
│   ├── todo-frontend/            # Frontend Helm chart
│   ├── todo-backend/             # Backend Helm chart
│   └── postgres/                 # PostgreSQL Helm chart
├── scripts/                        # Deployment scripts
│   ├── minikube-setup.sh        # Minikube initialization
│   └── deploy.sh                # Helm deployment
├── specs/                          # Feature specifications
├── docker-compose.yml              # Local development (non-K8s)
└── .specify/                       # Spec-Kit configuration
```

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+
- Docker Desktop
- Minikube
- Helm 3+
- kubectl
- Cohere API Key ([Get one free](https://dashboard.cohere.com/))

### Option 1: Local Development (Docker Compose)

Quick start for development without Kubernetes overhead.

#### Environment Setup

**Backend (.env)**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/todo
BETTER_AUTH_SECRET=your-secret-key-here
COHERE_API_KEY=your-cohere-api-key-here
FRONTEND_URL=http://localhost:3000
PORT=8000
```

**Frontend (.env)**
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
BACKEND_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
DATABASE_URL=postgresql://postgres:password@localhost:5432/todo
BETTER_AUTH_SECRET=your-secret-key-here
```

#### Quick Start

```bash
# Clone and enter directory
git clone <repository-url>
cd Phase-IV

# Generate Better Auth Secret
openssl rand -base64 32

# Start with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Kubernetes Deployment (Minikube + Helm)

Production-like deployment for testing and staging.

#### Step 1: Start Minikube

```bash
# Start Minikube cluster
minikube start --memory=4096 --cpus=2

# Enable ingress addon (optional)
minikube addons enable ingress

# Verify cluster is running
kubectl cluster-info
```

#### Step 2: Build Docker Images

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
docker build -t todo-backend:v4.0.0 ./backend

# Build frontend image
docker build -t todo-frontend:v4.0.0 ./frontend

# Verify images
docker images | grep todo
```

#### Step 3: Deploy with Helm

```bash
# Create namespace
kubectl create namespace todo-app

# Deploy PostgreSQL
helm install postgres ./charts/postgres -n todo-app

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n todo-app --timeout=120s

# Deploy backend (with secrets)
helm install todo-backend ./charts/todo-backend -n todo-app \
  --set secrets.cohereApiKey="your-cohere-key" \
  --set secrets.betterAuthSecret="your-jwt-secret"

# Deploy frontend
helm install todo-frontend ./charts/todo-frontend -n todo-app
```

#### Step 4: Access Services

```bash
# Option A: Port forwarding
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app &
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app &

# Option B: Minikube service (opens browser)
minikube service todo-frontend -n todo-app

# Option C: Get NodePort URLs
minikube service list -n todo-app
```

## AI DevOps Tools

### Gordon (Docker AI Agent)

Use Gordon for intelligent container management:

```bash
# Generate optimized Dockerfile
docker ai build --optimize ./backend

# Security vulnerability scan
docker ai scan todo-backend:v4.0.0

# Convert docker-compose to Kubernetes hints
docker ai convert docker-compose.yml

# Get Dockerfile best practices
docker ai suggest ./backend/Dockerfile
```

### kubectl-ai

AI-assisted Kubernetes operations:

```bash
# Generate manifests from natural language
kubectl-ai "create a deployment for fastapi with 2 replicas and 256Mi memory"

# Debug pod issues
kubectl-ai "why is my todo-backend pod in CrashLoopBackOff?"

# Optimize resources
kubectl-ai "suggest resource limits for todo-backend based on usage"

# Generate network policy
kubectl-ai "create network policy to allow only frontend to access backend"
```

### kagent

Intelligent Kubernetes monitoring:

```bash
# Health check analysis
kagent health todo-backend -n todo-app

# Scaling recommendations
kagent scale --analyze todo-frontend -n todo-app

# Log analysis and troubleshooting
kagent logs --diagnose todo-backend -n todo-app

# Performance optimization
kagent optimize -n todo-app
```

## Helm Charts Reference

### todo-backend values.yaml

```yaml
replicaCount: 2

image:
  repository: todo-backend
  tag: v4.0.0
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000

secrets:
  databaseUrl: "postgresql://postgres:password@postgres:5432/todo"
  cohereApiKey: ""  # Set via --set
  betterAuthSecret: ""  # Set via --set

config:
  frontendUrl: "http://todo-frontend:3000"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
```

### Helm Commands

```bash
# Install chart
helm install <release-name> ./charts/<chart-name> -n <namespace>

# Upgrade release
helm upgrade <release-name> ./charts/<chart-name> -n <namespace>

# View release status
helm status <release-name> -n <namespace>

# List releases
helm list -n <namespace>

# Uninstall release
helm uninstall <release-name> -n <namespace>

# Dry-run (preview changes)
helm install --dry-run --debug <release-name> ./charts/<chart-name>

# Template rendering
helm template <release-name> ./charts/<chart-name>
```

## Troubleshooting

### Common Issues

#### Pod stuck in Pending

```bash
# Check events
kubectl describe pod <pod-name> -n todo-app

# Common causes:
# - Insufficient resources: increase Minikube memory/CPU
# - PVC not bound: check storage class
kubectl get pvc -n todo-app
kubectl get events -n todo-app --sort-by=.metadata.creationTimestamp
```

#### Pod in CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> -n todo-app --previous

# Check container status
kubectl describe pod <pod-name> -n todo-app

# Common causes:
# - Missing environment variables
# - Database connection failed
# - Invalid secrets
```

#### Cannot connect to services

```bash
# Verify services are running
kubectl get svc -n todo-app

# Check endpoints
kubectl get endpoints -n todo-app

# Test connectivity from another pod
kubectl run test --rm -it --image=busybox -- wget -qO- http://todo-backend:8000/health
```

#### Database connection issues

```bash
# Check PostgreSQL pod
kubectl logs -l app=postgres -n todo-app

# Verify secret is correct
kubectl get secret todo-backend-secrets -n todo-app -o yaml

# Test connection manually
kubectl exec -it <postgres-pod> -n todo-app -- psql -U postgres -d todo
```

### Debugging Commands

```bash
# Get all resources in namespace
kubectl get all -n todo-app

# Describe deployment
kubectl describe deployment todo-backend -n todo-app

# View logs (follow)
kubectl logs -f -l app=todo-backend -n todo-app

# Execute shell in pod
kubectl exec -it <pod-name> -n todo-app -- /bin/sh

# Port forward for local testing
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app

# View events
kubectl get events -n todo-app --sort-by=.metadata.creationTimestamp

# Resource usage
kubectl top pods -n todo-app
kubectl top nodes
```

### Minikube-Specific Issues

```bash
# Restart Minikube if unresponsive
minikube stop && minikube start

# Clear Minikube cache
minikube delete && minikube start

# Check Minikube status
minikube status

# SSH into Minikube VM
minikube ssh

# View Minikube dashboard
minikube dashboard
```

## AI Chatbot Usage

### Natural Language Commands

The AI chatbot understands natural language and can perform various task operations:

#### Creating Tasks
- "Add a task to buy groceries"
- "Create a new task: Call dentist tomorrow"
- "Remind me to submit the report by Friday"
- "Add buy milk with high priority"

#### Listing Tasks
- "Show my tasks"
- "What's on my list?"
- "List all my high priority tasks"
- "Show me tasks due today"

#### Completing Tasks
- "Mark buy milk as done"
- "Complete the groceries task"
- "I finished the report task"

#### Updating Tasks
- "Change the title of task 5 to 'Buy vegetables'"
- "Update task priority to high"
- "Set due date for task 3 to tomorrow"

#### Deleting Tasks
- "Delete the buy milk task"
- "Remove task 7"

## Security

- **JWT Token Authentication**: All requests require valid tokens
- **User Data Isolation**: Users can only access their own data
- **Kubernetes Secrets**: Sensitive data stored securely in K8s
- **Input Validation**: Pydantic schemas for all requests
- **SQL Injection Protection**: SQLModel ORM with parameterized queries
- **CORS Configuration**: Controlled frontend-backend communication

## Database Schema

### Core Tables
- **users**: User accounts with email and hashed passwords
- **tasks**: Todo items with priorities, tags, due dates, recurrence
- **tags**: Global tag definitions
- **tasktaglink**: Many-to-many relationship for task tags

### Chat Tables (Phase III)
- **conversations**: Chat sessions per user
- **messages**: Individual messages with role (user/assistant) and tool calls

## API Documentation

### Chat Endpoints

#### POST /api/v1/chat
Send a message to the AI chatbot.

**Request:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": null
}
```

**Response:**
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I've created a task for you to buy groceries."
  },
  "tool_executed": true,
  "tool_results": [
    {
      "tool_name": "add_task",
      "success": true,
      "result": "Task created successfully"
    }
  ]
}
```

### Task Endpoints
- `GET /api/v1/tasks/`: List all tasks
- `POST /api/v1/tasks/`: Create a task
- `GET /api/v1/tasks/{id}`: Get task details
- `PUT /api/v1/tasks/{id}`: Update a task
- `DELETE /api/v1/tasks/{id}`: Delete a task
- `PATCH /api/v1/tasks/{id}/complete`: Mark as complete

Full API documentation: http://localhost:8000/docs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- **Cohere AI**: Natural language processing
- **PostgreSQL**: Relational database
- **Better Auth**: Authentication system
- **FastAPI**: Backend framework
- **Next.js**: Frontend framework
- **Kubernetes**: Container orchestration
- **Helm**: Kubernetes package manager
- **Minikube**: Local Kubernetes cluster

## Roadmap

### Phase IV (Current) - Kubernetes Deployment
- [x] Containerization with Docker
- [x] Helm charts for all services
- [x] Minikube local deployment
- [x] AI DevOps tooling (Gordon, kubectl-ai, kagent)
- [ ] CI/CD pipeline integration

### Phase V - Cloud Deployment
- Cloud Kubernetes (EKS/GKE/AKS)
- Managed PostgreSQL
- CDN integration
- Auto-scaling

### Phase VI - Advanced Features
- Voice input for chat
- Task suggestions based on patterns
- Smart scheduling
- Team collaboration

---

**Built with love using AI-Assisted Development**

Star this repository if you find it helpful!
