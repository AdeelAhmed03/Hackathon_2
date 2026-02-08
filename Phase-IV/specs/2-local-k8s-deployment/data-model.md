# Infrastructure Model: Local Kubernetes Deployment

**Feature**: 002-local-k8s-deployment
**Date**: 2026-02-06

## Kubernetes Resources

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    app.kubernetes.io/name: todo-app
    app.kubernetes.io/part-of: hackathon-todo
```

---

## PostgreSQL Resources

### Deployment: postgres

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_USER
              value: "postgres"
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secrets
                  key: POSTGRES_PASSWORD
            - name: POSTGRES_DB
              value: "todo"
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
          livenessProbe:
            exec:
              command: ["pg_isready", "-U", "postgres"]
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "postgres"]
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: postgres-data
          persistentVolumeClaim:
            claimName: postgres-data
```

### Service: postgres

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: todo-app
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  type: ClusterIP
```

### PersistentVolumeClaim: postgres-data

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: todo-app
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: standard
```

### Secret: postgres-secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secrets
  namespace: todo-app
type: Opaque
stringData:
  POSTGRES_PASSWORD: "your-secure-password"
```

---

## Backend Resources

### Deployment: todo-backend

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
        - name: todo-backend
          image: todo-backend:v4.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: todo-backend-config
            - secretRef:
                name: todo-backend-secrets
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
```

### Service: todo-backend

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  selector:
    app: todo-backend
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

### ConfigMap: todo-backend-config

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-backend-config
  namespace: todo-app
data:
  PORT: "8000"
  FRONTEND_URL: "http://todo-frontend:3000"
```

### Secret: todo-backend-secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secrets
  namespace: todo-app
type: Opaque
stringData:
  DATABASE_URL: "postgresql://postgres:password@postgres:5432/todo"
  COHERE_API_KEY: "your-cohere-api-key"
  BETTER_AUTH_SECRET: "your-jwt-secret"
```

---

## Frontend Resources

### Deployment: todo-frontend

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
        - name: todo-frontend
          image: todo-frontend:v4.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 3000
          envFrom:
            - configMapRef:
                name: todo-frontend-config
          livenessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 15
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: "128Mi"
              cpu: "50m"
            limits:
              memory: "256Mi"
              cpu: "200m"
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
```

### Service: todo-frontend

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  namespace: todo-app
spec:
  selector:
    app: todo-frontend
  ports:
    - port: 3000
      targetPort: 3000
  type: ClusterIP
```

### ConfigMap: todo-frontend-config

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-frontend-config
  namespace: todo-app
data:
  NEXT_PUBLIC_API_BASE_URL: "http://todo-backend:8000"
  NEXT_PUBLIC_BASE_URL: "http://localhost:3000"
```

---

## Ingress Resource (Optional)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  namespace: todo-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: todo.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: todo-frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: todo-backend
                port:
                  number: 8000
```

---

## Resource Summary

| Resource | Name | Replicas | Port |
|----------|------|----------|------|
| Deployment | postgres | 1 | 5432 |
| Deployment | todo-backend | 2 | 8000 |
| Deployment | todo-frontend | 2 | 3000 |
| Service | postgres | - | 5432 |
| Service | todo-backend | - | 8000 |
| Service | todo-frontend | - | 3000 |
| PVC | postgres-data | - | 1Gi |
| Secret | postgres-secrets | - | - |
| Secret | todo-backend-secrets | - | - |
| ConfigMap | todo-backend-config | - | - |
| ConfigMap | todo-frontend-config | - | - |
| Ingress | todo-app-ingress | - | - |

---

## Health Check Endpoints

| Service | Endpoint | Method | Expected |
|---------|----------|--------|----------|
| Backend | /health | GET | 200 OK |
| Frontend | / | GET | 200 OK |
| Postgres | pg_isready | exec | exit 0 |
