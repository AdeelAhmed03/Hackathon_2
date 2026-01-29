---
name: backend-deployment-skill
description: Deploy APIs, servers, databases, and containerized applications to cloud infrastructure. Use for backend service deployment.
---

# Backend Deployment Skill – APIs, Servers & Infrastructure

## Instructions

1. **Containerization with Docker**
   - Write multi-stage Dockerfiles for optimized images
   - Use appropriate base images (alpine for size, debian for compatibility)
   - Implement proper layer caching
   - Set non-root users for security
   - Define health checks
   - Keep images under 500MB when possible
   - Tag images with version numbers and commit SHAs

2. **Container Orchestration**
   - **Kubernetes**: Create Deployments, Services, ConfigMaps, Secrets
   - **Docker Compose**: Define multi-container applications for local dev
   - **AWS ECS**: Configure task definitions and services
   - **Google Cloud Run**: Deploy stateless containers with auto-scaling
   - Set resource limits (CPU, memory)
   - Configure horizontal pod autoscaling
   - Implement rolling updates with zero downtime

3. **Cloud Platform Deployment**
   - **AWS**: EC2, ECS, EKS, Lambda, Elastic Beanstalk
   - **Google Cloud**: GCE, GKE, Cloud Run, App Engine
   - **Azure**: VM, AKS, Container Instances, App Service
   - **DigitalOcean**: Droplets, Kubernetes, App Platform
   - Use infrastructure as code (Terraform, CloudFormation)
   - Configure auto-scaling policies
   - Set up load balancers

4. **Database Deployment & Migrations**
   - Run migrations before deploying new application code
   - Use transaction-based migrations for safety
   - Test migrations on staging with production-like data
   - Implement automatic backup before migrations
   - Never run destructive migrations without backups
   - Use migration tools (Prisma, TypeORM, Flyway, Liquibase)
   - Configure connection pooling appropriately

5. **Environment Configuration**
   - Separate configs for dev, staging, production
   - Use secret management (AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets)
   - Never commit secrets to version control
   - Use .env files for local development only
   - Inject environment variables at runtime
   - Validate required environment variables on startup

6. **Monitoring & Logging**
   - Set up centralized logging (CloudWatch, Datadog, ELK)
   - Configure application performance monitoring (APM)
   - Create health check endpoints (`/health`, `/ready`)
   - Set up alerts for errors, high latency, resource usage
   - Monitor database connection pools
   - Track deployment success/failure rates
   - Implement distributed tracing for microservices

7. **Security Configuration**
   - Use HTTPS/TLS for all connections
   - Configure firewalls and security groups
   - Implement rate limiting
   - Set up WAF (Web Application Firewall) for APIs
   - Enable DDoS protection
   - Scan images for vulnerabilities
   - Use principle of least privilege for IAM roles
   - Rotate credentials regularly

8. **CI/CD Pipeline Setup**
   - Automate build, test, and deployment
   - Run tests before deployment
   - Implement staged rollouts (canary, blue-green)
   - Configure automatic rollback on failures
   - Use feature flags for gradual rollouts
   - Deploy to staging before production
   - Require manual approval for production deploys

## Best Practices

- **Immutable Infrastructure**: Never modify running servers, deploy new versions
- **Graceful Shutdown**: Handle SIGTERM signals properly
- **Health Checks**: Implement liveness and readiness probes
- **Idempotent Deployments**: Safe to run multiple times
- **Database Backups**: Always backup before migrations
- **Secrets Rotation**: Rotate credentials and keys regularly
- **Monitoring First**: Set up monitoring before going to production
- **Rollback Plan**: Always have a way to quickly rollback
- **Load Testing**: Test production-like load before launch
- **Documentation**: Document deployment procedures and architecture

## Example Configurations

### Multi-Stage Dockerfile (Node.js API)
```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Stage 2: Build
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev)
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build && \
    npm prune --production

# Stage 3: Production
FROM node:18-alpine AS runner
WORKDIR /app

# Set environment
ENV NODE_ENV=production \
    PORT=3000

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nodejs

# Copy necessary files from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=deps --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["node", "dist/server.js"]
```

### Kubernetes Deployment Configuration
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
  namespace: production
data:
  NODE_ENV: "production"
  LOG_LEVEL: "info"
  PORT: "3000"

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: production
type: Opaque
stringData:
  database-url: "postgresql://user:pass@db.example.com:5432/myapp"
  redis-url: "redis://:password@redis.example.com:6379"
  jwt-secret: "your-secret-key"
  api-key: "your-api-key"

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: production
  labels:
    app: api-server
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "3000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: api-server
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      
      containers:
      - name: api-server
        image: myregistry.io/api-server:v1.2.3
        imagePullPolicy: Always
        
        ports:
        - name: http
          containerPort: 3000
          protocol: TCP
        
        env:
        - name: NODE_ENV
          valueFrom:
            configMapKeyRef:
              name: api-config
              key: NODE_ENV
        - name: PORT
          valueFrom:
            configMapKeyRef:
              name: api-config
              key: PORT
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: redis-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: jwt-secret
        
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
        
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
      
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
                  - api-server
              topologyKey: kubernetes.io/hostname
      
      terminationGracePeriodSeconds: 30

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-server
  namespace: production
  labels:
    app: api-server
spec:
  type: ClusterIP
  selector:
    app: api-server
  ports:
  - name: http
    port: 80
    targetPort: 3000
    protocol: TCP
  sessionAffinity: None

---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-server
            port:
              number: 80
```

### GitHub Actions CI/CD Pipeline
```yaml
name: Deploy Backend API

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  AWS_REGION: us-east-1

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "
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
  
  - name: Run unit tests
    run: npm test
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      REDIS_URL: redis://localhost:6379
  
  - name: Run integration tests
    run: npm run test:integration
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      REDIS_URL: redis://localhost:6379
  
  - name: Upload coverage
    uses: codecov/codecov-action@v3
    with:
      files: ./coverage/lcov.info

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
        type=semver,pattern={{version}}
        type=sha,prefix={{branch}}-
        type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}
  
  - name: Build and push Docker image
    uses: docker/build-push-action@v4
    with:
      context: .
      push: true
      tags: ${{ steps.meta.outputs.tags }}
      labels: ${{ steps.meta.outputs.labels }}
      cache-from: type=gha
      cache-to: type=gha,mode=max
      build-args: |
        NODE_ENV=production
  
  - name: Scan image for vulnerabilities
    uses: aquasecurity/trivy-action@master
    with:
      image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
      format: 'sarif'
      output: 'trivy-results.sarif'
  
  - name: Upload Trivy results to GitHub Security
    uses: github/codeql-action/upload-sarif@v2
    with:
      sarif_file: 'trivy-results.sarif'

steps:
  - uses: actions/checkout@v3
  
  - name: Configure AWS credentials
    uses: aws-actions/configure-aws-credentials@v2
    with:
      aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      aws-region: ${{ env.AWS_REGION }}
  
  - name: Update kubeconfig
    run: aws eks update-kubeconfig --name staging-cluster --region ${{ env.AWS_REGION }}
  
  - name: Run database migrations
    run: |
      kubectl run migration-${{ github.sha }} \
        --image=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:staging \
        --restart=Never \
        --namespace=staging \
        --env="DATABASE_URL=${{ secrets.STAGING_DATABASE_URL }}" \
        --command -- npm run migrate
      
      kubectl wait --for=condition=complete --timeout=300s \
        job/migration-${{ github.sha }} \
        --namespace=staging
  
  - name: Deploy to Kubernetes
    run: |
      kubectl set image deployment/api-server \
        api-server=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:staging \
        --namespace=staging
      
      kubectl rollout status deployment/api-server \
        --namespace=staging \
        --timeout=5m
  
  - name: Verify deployment
    run: |
      kubectl get pods --namespace=staging
      kubectl get services --namespace=staging
  
  - name: Run smoke tests
    run: |
      API_URL=$(kubectl get service api-server -n staging -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
      curl -f http://$API_URL/health || exit 1

steps:
  - uses: actions/checkout@v3
  
  - name: Configure AWS credentials
    uses: aws-actions/configure-aws-credentials@v2
    with:
      aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      aws-region: ${{ env.AWS_REGION }}
  
  - name: Update kubeconfig
    run: aws eks update-kubeconfig --name production-cluster --region ${{ env.AWS_REGION }}
  
  - name: Backup database
    run: |
      kubectl create job backup-$(date +%Y%m%d-%H%M%S) \
        --from=cronjob/database-backup \
        --namespace=production
  
  - name: Run database migrations
    run: |
      kubectl run migration-${{ github.sha }} \
        --image=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest \
        --restart=Never \
        --namespace=production \
        --env="DATABASE_URL=${{ secrets.PROD_DATABASE_URL }}" \
        --command -- npm run migrate
      
      kubectl wait --for=condition=complete --timeout=300s \
        job/migration-${{ github.sha }} \
        --namespace=production
  
  - name: Deploy to Kubernetes (Canary)
    run: |
      # Deploy canary with 10% traffic
      kubectl apply -f k8s/canary-deployment.yaml
      kubectl rollout status deployment/api-server-canary --namespace=production
  
  - name: Wait and monitor canary
    run: |
      echo "Monitoring canary for 5 minutes..."
      sleep 300
  
  - name: Check canary metrics
    id: canary-check
    run: |
      # Check error rate, latency, etc.
      ERROR_RATE=$(kubectl exec -n production deployment/api-server-canary -- \
        curl -s http://localhost:3000/metrics | grep error_rate | awk '{print $2}')
      
      if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
        echo "Canary error rate too high: $ERROR_RATE"
        exit 1
      fi
  
  - name: Promote canary to production
    if: success()
    run: |
      kubectl set image deployment/api-server \
        api-server=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest \
        --namespace=production
      
      kubectl rollout status deployment/api-server \
        --namespace=production \
        --timeout=10m
      
      # Remove canary
      kubectl delete deployment api-server-canary --namespace=production
  
  - name: Rollback on failure
    if: failure()
    run: |
      echo "Canary failed, rolling back..."
      kubectl delete deployment api-server-canary --namespace=production
      # Previous version remains active
  
  - name: Verify production deployment
    run: |
      kubectl get pods --namespace=production
      kubectl get services --namespace=production
  
  - name: Run smoke tests
    run: |
      curl -f https://api.example.com/health || exit 1
      curl -f https://api.example.com/ready || exit 1
  
  - name: Notify deployment success
    uses: 8398a7/action-slack@v3
    with:
      status: ${{ job.status }}
      text: 'Production deployment successful! :rocket:'
      webhook_url: ${{ secrets.SLACK_WEBHOOK }}

### Terraform Infrastructure as Code
```hcl
# main.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }
  
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  name = "${var.project_name}-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  cluster_name    = "${var.project_name}-${var.environment}"
  cluster_version = "1.27"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  cluster_endpoint_public_access = true
  
  eks_managed_node_groups = {
    general = {
      desired_size = 3
      min_size     = 2
      max_size     = 10
      
      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"
      
      labels = {
        role = "general"
      }
      
      tags = {
        Environment = var.environment
      }
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# RDS Database
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"
  
  identifier = "${var.project_name}-${var.environment}-db"
  
  engine               = "postgres"
  engine_version       = "15.3"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = "db.t3.medium"
  
  allocated_storage     = 50
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = var.db_name
  username = var.db_username
  port     = 5432
  
  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [aws_security_group.rds.id]
  
  backup_retention_period = 7
  backup_window          = "03:00-06:00"
  maintenance_window     = "Mon:00:00-Mon:03:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.project_name}-${var.environment}-final-snapshot"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project_name}-${var.environment}-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  
  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]
  
  snapshot_retention_limit = 5
  snapshot_window         = "00:00-05:00"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Application Load Balancer
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 8.0"
  
  name = "${var.project_name}-${var.environment}-alb"
  
  load_balancer_type = "application"
  
  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.alb.id]
  
  target_groups = [
    {
      name             = "${var.project_name}-tg"
      backend_protocol = "HTTP"
      backend_port     = 80
      target_type      = "ip"
      health_check = {
        enabled             = true
        interval            = 30
        path                = "/health"
        port                = "traffic-port"
        healthy_threshold   = 3
        unhealthy_threshold = 3
        timeout             = 6
        protocol            = "HTTP"
        matcher             = "200-299"
      }
    }
  ]
  
  https_listeners = [
    {
      port               = 443
      protocol           = "HTTPS"
      certificate_arn    = aws_acm_certificate.main.arn
      target_group_index = 0
    }
  ]
  
  http_tcp_listeners = [
    {
      port        = 80
      protocol    = "HTTP"
      action_type = "redirect"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  ]
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "db_endpoint" {
  description = "RDS instance endpoint"
  value       = module.db.db_instance_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
  sensitive   = true
}

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = module.alb.lb_dns_name
}
```

## Deployment Checklist

**Pre-Deployment:**
- [ ] Run all tests (unit, integration, e2e)
- [ ] Build Docker image successfully
- [ ] Scan image for vulnerabilities
- [ ] Backup database
- [ ] Review infrastructure changes
- [ ] Verify environment variables are set
- [ ] Check resource limits and quotas

**During Deployment:**
- [ ] Run database migrations
- [ ] Deploy with rolling update strategy
- [ ] Monitor deployment progress
- [ ] Check health endpoints
- [ ] Verify logs for errors
- [ ] Monitor resource usage

**Post-Deployment:**
- [ ] Run smoke tests
- [ ] Verify all services are healthy
- [ ] Check application logs
- [ ] Monitor error rates and latency
- [ ] Verify database connections
- [ ] Test critical user flows
- [ ] Update documentation

**Rollback Plan:**
- [ ] Document rollback procedure
- [ ] Keep previous version available
- [ ] Test rollback in staging
- [ ] Monitor metrics after rollback

