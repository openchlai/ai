# Docker & Kubernetes Setup

## Overview

This guide covers containerized deployment of OpenCHS using Docker and Kubernetes. This is the recommended approach for production deployments due to simplified management, scalability, and consistency across environments.

---

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Docker Compose Setup](#docker-compose-setup)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Production Best Practices](#production-best-practices)

---

## Docker Deployment

### Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### Install NVIDIA Container Runtime (For GPU Support)

```bash
# Add NVIDIA Container Toolkit repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install NVIDIA Container Toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

---

## Docker Compose Setup

### AI Service Deployment

#### Directory Structure

```bash
openchs-ai/
├── docker-compose.yml
├── docker-compose.prod.yml
├── docker-compose.gpu.yml
├── Dockerfile
├── .env
├── app/
│   ├── main.py
│   ├── celery_app.py
│   └── ...
├── models/
├── logs/
└── requirements.txt
```

#### Dockerfile

```dockerfile
# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_md

# Copy application code
COPY ./app /app/app

# Create necessary directories
RUN mkdir -p /app/models /app/logs /app/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8123

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8123/health || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8123"]
```

#### docker-compose.yml (Development)

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: openchs-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  ai-pipeline:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: openchs-ai-api
    restart: unless-stopped
    depends_on:
      redis:
        condition: service_healthy
    environment:
      - DEBUG=${DEBUG:-true}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - REDIS_URL=redis://redis:6379/0
      - MAX_CONCURRENT_GPU_REQUESTS=${MAX_CONCURRENT_GPU_REQUESTS:-1}
      - ENABLE_MODEL_LOADING=${ENABLE_MODEL_LOADING:-true}
    ports:
      - "8123:8123"
    volumes:
      - ./app:/app/app:ro
      - ./models:/app/models
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8123/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: openchs-celery-worker
    restart: unless-stopped
    depends_on:
      redis:
        condition: service_healthy
      ai-pipeline:
        condition: service_healthy
    command: celery -A app.celery_app worker --loglevel=info -E --pool=solo
    environment:
      - DEBUG=${DEBUG:-true}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - REDIS_URL=redis://redis:6379/0
      - ENABLE_MODEL_LOADING=${ENABLE_MODEL_LOADING:-true}
    volumes:
      - ./app:/app/app:ro
      - ./models:/app/models
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    healthcheck:
      test: ["CMD", "celery", "-A", "app.celery_app", "inspect", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  redis_data:

networks:
  default:
    name: openchs-network
```

#### docker-compose.prod.yml (Production Override)

```yaml
version: '3.8'

services:
  redis:
    command: >
      redis-server
      --appendonly yes
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  ai-pipeline:
    environment:
      - DEBUG=false
      - LOG_LEVEL=WARNING
    deploy:
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G
    volumes:
      - ./models:/app/models:ro
      - ./logs:/app/logs
      - ./uploads:/app/uploads

  celery-worker:
    environment:
      - DEBUG=false
      - LOG_LEVEL=WARNING
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G
    volumes:
      - ./models:/app/models:ro
      - ./logs:/app/logs
      - ./uploads:/app/uploads
```

#### docker-compose.gpu.yml (GPU Support)

```yaml
version: '3.8'

services:
  celery-worker:
    deploy:
      resources:
        limits:
          memory: 32G
        reservations:
          memory: 16G
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - TORCH_DTYPE=float16
```

#### Environment Configuration (.env)

```bash
# Application Settings
APP_NAME="OpenCHS AI Service"
DEBUG=false
LOG_LEVEL=INFO

# Resource Management
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300

# Model Configuration
ENABLE_MODEL_LOADING=true
MODEL_CACHE_SIZE=8192

# Security
SITE_ID=production-001
DATA_RETENTION_HOURS=24
MAX_FILE_SIZE_MB=100
```

### Deployment Commands

```bash
# Development deployment
docker compose up -d

# Production deployment (CPU)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Production deployment (GPU)
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.gpu.yml up -d

# Scale workers
docker compose up -d --scale celery-worker=3

# View logs
docker compose logs -f ai-pipeline
docker compose logs -f celery-worker

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Helpline System with Docker Compose

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: openchs-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: helpline
      MYSQL_USER: helpline_user
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./uchl.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  php-fpm:
    build:
      context: .
      dockerfile: Dockerfile.php
    container_name: openchs-php-fpm
    restart: unless-stopped
    depends_on:
      mysql:
        condition: service_healthy
    volumes:
      - ./rest_api:/var/www/html/helpline
    environment:
      - DB_HOST=mysql
      - DB_NAME=helpline
      - DB_USER=helpline_user
      - DB_PASSWORD=${MYSQL_PASSWORD}

  nginx:
    image: nginx:alpine
    container_name: openchs-nginx
    restart: unless-stopped
    depends_on:
      - php-fpm
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./rest_api:/var/www/html/helpline:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  mysql_data:

networks:
  default:
    name: openchs-helpline-network
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client

# Install Helm (optional but recommended)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### AI Service Kubernetes Manifests

#### Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openchs
  labels:
    name: openchs
```

#### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openchs-ai-config
  namespace: openchs
data:
  APP_NAME: "OpenCHS AI Service"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  MAX_CONCURRENT_GPU_REQUESTS: "1"
  MAX_QUEUE_SIZE: "20"
  REQUEST_TIMEOUT: "300"
  ENABLE_MODEL_LOADING: "true"
  MODEL_CACHE_SIZE: "8192"
  SITE_ID: "production-k8s"
  DATA_RETENTION_HOURS: "24"
  MAX_FILE_SIZE_MB: "100"
  REDIS_URL: "redis://openchs-redis:6379/0"
```

#### Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: openchs-ai-secrets
  namespace: openchs
type: Opaque
stringData:
  REDIS_PASSWORD: "your-redis-password"
  # Add other sensitive data here
```

#### Redis Deployment

```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openchs-redis
  namespace: openchs
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openchs-redis
  template:
    metadata:
      labels:
        app: openchs-redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
          name: redis
        command:
        - redis-server
        - --appendonly
        - "yes"
        - --maxmemory
        - "2gb"
        - --maxmemory-policy
        - allkeys-lru
        volumeMounts:
        - name: redis-data
          mountPath: /data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: openchs-redis
  namespace: openchs
spec:
  selector:
    app: openchs-redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: openchs
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

#### AI API Deployment

```yaml
# ai-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openchs-ai-api
  namespace: openchs
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openchs-ai-api
  template:
    metadata:
      labels:
        app: openchs-ai-api
    spec:
      containers:
      - name: ai-api
        image: openchs/ai-service:latest
        ports:
        - containerPort: 8123
          name: http
        envFrom:
        - configMapRef:
            name: openchs-ai-config
        - secretRef:
            name: openchs-ai-secrets
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        - name: logs
          mountPath: /app/logs
        - name: uploads
          mountPath: /app/uploads
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        livenessProbe:
          httpGet:
            path: /health
            port: 8123
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8123
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
      - name: uploads
        persistentVolumeClaim:
          claimName: uploads-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: openchs-ai-api
  namespace: openchs
spec:
  selector:
    app: openchs-ai-api
  ports:
  - port: 8123
    targetPort: 8123
  type: ClusterIP
```

#### Celery Worker Deployment (GPU)

```yaml
# celery-worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openchs-celery-worker
  namespace: openchs
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openchs-celery-worker
  template:
    metadata:
      labels:
        app: openchs-celery-worker
    spec:
      containers:
      - name: celery-worker
        image: openchs/ai-service:latest
        command:
        - celery
        - -A
        - app.celery_app
        - worker
        - --loglevel=info
        - -E
        - --pool=solo
        envFrom:
        - configMapRef:
            name: openchs-ai-config
        - secretRef:
            name: openchs-ai-secrets
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        - name: logs
          mountPath: /app/logs
        - name: uploads
          mountPath: /app/uploads
        resources:
          requests:
            memory: "16Gi"
            cpu: "8"
            nvidia.com/gpu: 1
          limits:
            memory: "32Gi"
            cpu: "16"
            nvidia.com/gpu: 1
        livenessProbe:
          exec:
            command:
            - celery
            - -A
            - app.celery_app
            - inspect
            - ping
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
      nodeSelector:
        nvidia.com/gpu: "true"
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
      - name: uploads
        persistentVolumeClaim:
          claimName: uploads-pvc
```

#### Persistent Volume Claims

```yaml
# pvcs.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: models-pvc
  namespace: openchs
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 50Gi
  storageClassName: nfs
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: logs-pvc
  namespace: openchs
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 20Gi
  storageClassName: nfs
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: uploads-pvc
  namespace: openchs
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  storageClassName: nfs
```

#### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openchs-ingress
  namespace: openchs
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
spec:
  tls:
  - hosts:
    - ai.openchs.yourdomain.com
    secretName: openchs-ai-tls
  rules:
  - host: ai.openchs.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: openchs-ai-api
            port:
              number: 8123
```

#### Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openchs-ai-api-hpa
  namespace: openchs
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openchs-ai-api
  minReplicas: 2
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
```

### Deployment Commands

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Deploy configuration
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml

# Deploy storage
kubectl apply -f pvcs.yaml

# Deploy services
kubectl apply -f redis-deployment.yaml
kubectl apply -f ai-api-deployment.yaml
kubectl apply -f celery-worker-deployment.yaml

# Deploy ingress
kubectl apply -f ingress.yaml

# Deploy autoscaler
kubectl apply -f hpa.yaml

# Verify deployment
kubectl get pods -n openchs
kubectl get services -n openchs
kubectl get ingress -n openchs

# View logs
kubectl logs -f -n openchs deployment/openchs-ai-api
kubectl logs -f -n openchs deployment/openchs-celery-worker

# Scale deployment
kubectl scale deployment openchs-ai-api -n openchs --replicas=5

# Update deployment
kubectl set image deployment/openchs-ai-api -n openchs ai-api=openchs/ai-service:v2.0

# Delete deployment
kubectl delete namespace openchs
```

### Helm Chart (Optional)

Create a Helm chart for easier management:

```bash
# Create Helm chart structure
helm create openchs-ai

# Directory structure
openchs-ai/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── secrets.yaml
```

**values.yaml** example:

```yaml
replicaCount: 2

image:
  repository: openchs/ai-service
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8123

ingress:
  enabled: true
  className: nginx
  host: ai.openchs.yourdomain.com
  tls:
    enabled: true

resources:
  limits:
    memory: 16Gi
    cpu: 8
  requests:
    memory: 8Gi
    cpu: 4

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

redis:
  enabled: true
  persistence:
    size: 10Gi

celeryWorker:
  enabled: true
  replicas: 1
  gpu:
    enabled: true
    count: 1
  resources:
    limits:
      memory: 32Gi
      cpu: 16
      nvidia.com/gpu: 1
```

Deploy with Helm:

```bash
# Install chart
helm install openchs-ai ./openchs-ai -n openchs --create-namespace

# Upgrade chart
helm upgrade openchs-ai ./openchs-ai -n openchs

# Uninstall chart
helm uninstall openchs-ai -n openchs
```

---

## Production Best Practices

### Security

#### 1. Use Private Container Registry

```bash
# Create Docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email \
  -n openchs

# Reference in deployment
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
```

#### 2. Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: openchs-network-policy
  namespace: openchs
spec:
  podSelector:
    matchLabels:
      app: openchs-ai-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8123
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: openchs-redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

#### 3. Pod Security Standards

```yaml
# pod-security.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openchs
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### High Availability

#### 1. Pod Disruption Budget

```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: openchs-ai-api-pdb
  namespace: openchs
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: openchs-ai-api
```

#### 2. Multi-Zone Deployment

```yaml
# Add to deployment spec
spec:
  template:
    spec:
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
                  - openchs-ai-api
              topologyKey: topology.kubernetes.io/zone
```

### Monitoring

#### 1. Prometheus ServiceMonitor

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: openchs-ai-api
  namespace: openchs
spec:
  selector:
    matchLabels:
      app: openchs-ai-api
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

#### 2. Grafana Dashboard

Create custom dashboards for:
- Request rate and latency
- GPU utilization
- Memory usage
- Queue length
- Error rates

### Backup and Disaster Recovery

#### 1. Velero Backup

```bash
# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket openchs-backups \
  --backup-location-config region=us-east-1

# Create backup schedule
velero schedule create openchs-daily \
  --schedule="0 2 * * *" \
  --include-namespaces openchs

# Restore from backup
velero restore create --from-backup openchs-daily-20240101
```

#### 2. PVC Snapshots

```yaml
# volumesnapshot.yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: models-snapshot
  namespace: openchs
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: models-pvc
```

### Resource Optimization

#### 1. Vertical Pod Autoscaler

```yaml
# vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: openchs-ai-api-vpa
  namespace: openchs
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openchs-ai-api
  updatePolicy:
    updateMode: "Auto"
```

#### 2. Resource Quotas

```yaml
# resourcequota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: openchs-quota
  namespace: openchs
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    requests.nvidia.com/gpu: "4"
    persistentvolumeclaims: "10"
```

### Logging

#### 1. Centralized Logging with Fluentd

```yaml
# fluentd-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: openchs
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*openchs*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
      </parse>
    </source>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      logstash_format true
      logstash_prefix openchs
    </match>
```

### CI/CD Integration

#### 1. GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t openchs/ai-service:${{ github.sha }} .
        docker tag openchs/ai-service:${{ github.sha }} openchs/ai-service:latest
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push openchs/ai-service:${{ github.sha }}
        docker push openchs/ai-service:latest
    
    - name: Deploy to Kubernetes
      uses: azure/k8s-deploy@v4
      with:
        manifests: |
          k8s/deployment.yaml
          k8s/service.yaml
        images: openchs/ai-service:${{ github.sha }}
        kubectl-version: 'latest'
```

### Performance Tuning

#### 1. GPU Node Pool Configuration

```yaml
# For GPU workloads, use dedicated node pools
nodeSelector:
  workload-type: gpu
tolerations:
- key: nvidia.com/gpu
  operator: Exists
  effect: NoSchedule
```

#### 2. Resource Limits

```yaml
# Optimize based on actual usage
resources:
  requests:
    memory: "8Gi"
    cpu: "4"
    ephemeral-storage: "10Gi"
  limits:
    memory: "16Gi"
    cpu: "8"
    ephemeral-storage: "20Gi"
```

---

## Troubleshooting

### Common Issues

#### Pods not starting

```bash
# Check pod status
kubectl get pods -n openchs

# Describe pod for events
kubectl describe pod <pod-name> -n openchs

# Check logs
kubectl logs <pod-name> -n openchs

# Check resource availability
kubectl top nodes
kubectl top pods -n openchs
```

#### GPU not accessible

```bash
# Verify GPU node
kubectl get nodes -l nvidia.com/gpu=true

# Check GPU resources
kubectl describe node <gpu-node-name>

# Verify NVIDIA device plugin
kubectl get pods -n kube-system | grep nvidia
```

#### Persistent volume issues

```bash
# Check PVC status
kubectl get pvc -n openchs

# Check PV status
kubectl get pv

# Describe PVC for details
kubectl describe pvc <pvc-name> -n openchs
```

---

## Next Steps

After successful deployment:

1. **Configure System Settings**: See [System Settings](../configuration/system-settings.md)
2. **Set Up Monitoring**: See [System Health Checks](../maintenance-monitoring/system-health-checks.md)
3. **Configure Backups**: See [Backup & Recovery](../configuration/backup-recovery.md)
4. **Performance Tuning**: See [Performance Tuning](../maintenance-monitoring/performance-tuning.md)

---

## Quick Reference

### Docker Commands

```bash
# Build image
docker build -t openchs/ai-service:latest .

# Run container
docker run -d -p 8123:8123 openchs/ai-service:latest

# View logs
docker logs -f <container-id>

# Execute command in container
docker exec -it <container-id> bash

# Cleanup
docker system prune -a
```

### Kubernetes Commands

```bash
# Get resources
kubectl get all -n openchs

# Scale deployment
kubectl scale deployment openchs-ai-api -n openchs --replicas=3

# Update image
kubectl set image deployment/openchs-ai-api ai-api=openchs/ai-service:v2 -n openchs

# Rollback deployment
kubectl rollout undo deployment/openchs-ai-api -n openchs

# Port forward for testing
kubectl port-forward -n openchs svc/openchs-ai-api 8123:8123
```