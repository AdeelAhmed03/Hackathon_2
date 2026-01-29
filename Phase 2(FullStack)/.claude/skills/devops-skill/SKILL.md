---
name: devops-skill
description: Automate CI/CD pipelines, manage infrastructure, containerization, and deployment workflows. Use for deployment automation and infrastructure management.
---

# DevOps Skill - CI/CD, Infrastructure & Deployment Automation

## Instructions

1. **CI/CD Pipeline Configuration**
   - Define clear stages: build, test, deploy
   - Use YAML syntax for GitHub Actions, GitLab CI, CircleCI
   - Implement caching for dependencies and build artifacts
   - Set up automatic triggers (push, pull request, tags)
   - Configure environment-specific workflows

2. **Containerization with Docker**
   - Write multi-stage Dockerfiles for optimal image size
   - Use appropriate base images (alpine for smaller size)
   - Implement proper layer caching
   - Set non-root users for security
   - Define health checks and entry points
   - Use .dockerignore to exclude unnecessary files

3. **Infrastructure as Code (IaC)**
   - Use Terraform, CloudFormation, or Pulumi
   - Define resources declaratively
   - Implement modules for reusability
   - Manage state files securely
   - Version control all infrastructure code

4. **Kubernetes Orchestration**
   - Create Deployments, Services, and Ingress resources
   - Define resource limits and requests
   - Implement health checks (liveness, readiness probes)
   - Use ConfigMaps and Secrets for configuration
   - Set up horizontal pod autoscaling
   - Configure persistent volumes for stateful apps

5. **Secrets Management**
   - Never commit secrets to version control
   - Use platform-specific secret stores (GitHub Secrets, AWS Secrets Manager, Vault)
   - Rotate secrets regularly
   - Use environment variables for runtime configuration
   - Implement least-privilege access

6. **Monitoring & Logging**
   - Set up application and infrastructure monitoring
   - Configure log aggregation (CloudWatch, ELK, Datadog)
   - Define alerting thresholds
   - Implement distributed tracing for microservices
   - Monitor deployment success rates

## Best Practices

- **Security First**: Scan images for vulnerabilities, use minimal base images, run as non-root
- **Immutable Infrastructure**: Never modify running containers, always deploy new versions
- **Fail Fast**: Include early validation steps, fail pipeline on test failures
- **Rollback Strategy**: Always have a way to quickly revert to previous version
- **Documentation**: Comment complex pipeline logic, document deployment procedures
- **Cost Optimization**: Clean up unused resources, use spot instances where appropriate
- **Testing**: Test deployment scripts in staging before production
- **Versioning**: Tag all Docker images and infrastructure releases

## Example CI/CD Pipeline

### GitHub Actions - Full Stack Deployment
```yaml
name: Deploy Application

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Run tests
        run: npm test
        env:
          CI: true
      
      - name: Run integration tests
        run: npm run test:integration

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name staging-cluster --region us-east-1
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/app-deployment \
            app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:staging \
            --namespace=staging
          kubectl rollout status deployment/app-deployment --namespace=staging

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name production-cluster --region us-east-1
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/app-deployment \
            app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:main \
            --namespace=production
          kubectl rollout status deployment/app-deployment --namespace=production
      
      - name: Verify deployment
        run: |
          kubectl get pods --namespace=production
          kubectl get services --namespace=production
```

## Example Docker Configuration

### Optimized Multi-Stage Dockerfile
```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Stage 2: Build
FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 3: Production
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nodejs

# Copy necessary files
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=deps --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

USER nodejs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "dist/index.js"]
```

### docker-compose.yml for Development
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

## Example Kubernetes Configuration

### Complete Application Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
  labels:
    app: web-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: app
        image: myregistry/web-app:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - web-app
              topologyKey: kubernetes.io/hostname

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app-service
  namespace: production
spec:
  selector:
    app: web-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP

---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: web-app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-service
            port:
              number: 80
```

## Common Deployment Patterns

### Blue-Green Deployment
```bash
# Deploy new version (green)
kubectl apply -f deployment-green.yaml

# Wait for green to be ready
kubectl wait --for=condition=available --timeout=300s deployment/app-green

# Switch traffic to green
kubectl patch service app-service -p '{"spec":{"selector":{"version":"green"}}}'

# Verify green is working
# If successful, remove blue
kubectl delete deployment app-blue

# If issues, rollback to blue
kubectl patch service app-service -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Canary Deployment with Traffic Split
```yaml
# 90% traffic to stable, 10% to canary
apiVersion: v1
kind: Service
metadata:
  name: app-stable
spec:
  selector:
    app: myapp
    version: stable
  ports:
  - port: 80

---
apiVersion: v1
kind: Service
metadata:
  name: app-canary
spec:
  selector:
    app: myapp
    version: canary
  ports:
  - port: 80

---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-route
spec:
  hosts:
  - app.example.com
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: app-canary
  - route:
    - destination:
        host: app-stable
      weight: 90
    - destination:
        host: app-canary
      weight: 10
```