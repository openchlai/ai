---
layout: doc
title: Kubernetes Deployment
---

# Kubernetes Deployment

Deploy the AI Service on Kubernetes for high availability and scalability.

## Overview

This guide covers deploying the AI Service on Kubernetes with:

- **API Deployment** - Scalable FastAPI pods
- **Worker Deployment** - GPU-enabled Celery workers
- **Redis** - StatefulSet with persistence
- **Ingress** - External access with TLS
- **ConfigMaps & Secrets** - Configuration management
- **Horizontal Pod Autoscaler** - Auto-scaling based on load

---

## Prerequisites

- Kubernetes cluster 1.24+
- `kubectl` configured
- NVIDIA GPU Operator (for GPU support)
- Helm 3.x (optional, for Redis)
- Container registry access
- Persistent volume provisioner

### Verify Prerequisites

```bash
# Check Kubernetes version
kubectl version

# Check GPU nodes
kubectl get nodes -l accelerator=nvidia-gpu

# Check NVIDIA GPU Operator
kubectl get pods -n gpu-operator
```

---

## Namespace Setup

```bash
# Create namespace
kubectl create namespace ai-service

# Set default namespace
kubectl config set-context --current --namespace=ai-service
```

---

## ConfigMap

Create `configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-service-config
  namespace: ai-service
data:
  APP_NAME: "AI_Pipeline"
  APP_VERSION: "0.1.0"
  APP_PORT: "8125"
  LOG_LEVEL: "INFO"
  REDIS_URL: "redis://redis-service:6379/0"
  ENABLE_STREAMING_PROCESSING: "true"
  ENABLE_POSTCALL_PROCESSING: "true"
  DEFAULT_PROCESSING_MODE: "adaptive"
  STREAMING_PORT: "8301"
  WHISPER_DEVICE: "cuda"
  WHISPER_COMPUTE_TYPE: "float16"
  USE_HF_MODELS: "true"
  HF_ASR_MODEL: "openai/whisper-large-v3"
  HF_CLASSIFIER_MODEL: "openchs/multitask-classifier"
  HF_NER_MODEL: "openchs/ner-model"
  HF_TRANSLATOR_MODEL: "openchs/translation-model"
  HF_SUMMARIZER_MODEL: "openchs/summarization-model"
  HF_QA_MODEL: "openchs/qa-model"
```

```bash
kubectl apply -f configmap.yaml
```

---

## Secrets

Create `secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-service-secrets
  namespace: ai-service
type: Opaque
stringData:
  REDIS_PASSWORD: "your-redis-password"
  JWT_SECRET_KEY: "your-jwt-secret"
  DATABASE_URL: "postgresql://user:password@postgres:5432/ai_service"
```

```bash
kubectl apply -f secrets.yaml
```

---

## Redis Deployment

### Option A: Simple Redis

Create `redis.yaml`:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
  namespace: ai-service
spec:
  serviceName: redis
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command:
          - redis-server
          - --appendonly
          - "yes"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        volumeMounts:
        - name: redis-data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: ai-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  clusterIP: None
```

### Option B: Helm (Recommended for Production)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis \
  --namespace ai-service \
  --set auth.enabled=true \
  --set auth.password=your-redis-password \
  --set replica.replicaCount=3
```

---

## API Deployment

Create `api-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-service-api
  namespace: ai-service
  labels:
    app: ai-service
    component: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-service
      component: api
  template:
    metadata:
      labels:
        app: ai-service
        component: api
    spec:
      containers:
      - name: api
        image: your-registry/ai-service:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8125
          name: http
        - containerPort: 8301
          name: streaming
        envFrom:
        - configMapRef:
            name: ai-service-config
        - secretRef:
            name: ai-service-secrets
        env:
        - name: ENABLE_MODEL_LOADING
          value: "false"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8125
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8125
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: ai-service-api
  namespace: ai-service
spec:
  selector:
    app: ai-service
    component: api
  ports:
  - name: http
    port: 8125
    targetPort: 8125
  - name: streaming
    port: 8301
    targetPort: 8301
  type: ClusterIP
```

---

## Worker Deployment (GPU)

Create `worker-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-service-worker
  namespace: ai-service
  labels:
    app: ai-service
    component: worker
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-service
      component: worker
  template:
    metadata:
      labels:
        app: ai-service
        component: worker
    spec:
      containers:
      - name: worker
        image: your-registry/ai-service:latest
        imagePullPolicy: Always
        command:
          - celery
          - -A
          - app.celery_app
          - worker
          - --loglevel=info
          - -E
          - --pool=solo
          - -Q
          - model_processing,celery
        envFrom:
        - configMapRef:
            name: ai-service-config
        - secretRef:
            name: ai-service-secrets
        env:
        - name: ENABLE_MODEL_LOADING
          value: "true"
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: 1
        volumeMounts:
        - name: models
          mountPath: /app/models
        - name: logs
          mountPath: /app/logs
        - name: shm
          mountPath: /dev/shm
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: ai-models-pvc
      - name: logs
        emptyDir: {}
      - name: shm
        emptyDir:
          medium: Memory
          sizeLimit: 8Gi
      nodeSelector:
        accelerator: nvidia-gpu
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
```

---

## Persistent Volume Claim

Create `pvc.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ai-models-pvc
  namespace: ai-service
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  storageClassName: standard  # Adjust for your cluster
```

---

## Ingress

Create `ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-service-ingress
  namespace: ai-service
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "500m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  tls:
  - hosts:
    - ai-service.example.com
    secretName: ai-service-tls
  rules:
  - host: ai-service.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-service-api
            port:
              number: 8125
```

---

## Horizontal Pod Autoscaler

Create `hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-service-api-hpa
  namespace: ai-service
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-service-api
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

---

## Deployment Commands

### Apply All Resources

```bash
# Apply in order
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f pvc.yaml
kubectl apply -f redis.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f worker-deployment.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n ai-service

# Check services
kubectl get svc -n ai-service

# Check ingress
kubectl get ingress -n ai-service

# View logs
kubectl logs -f deployment/ai-service-api -n ai-service
kubectl logs -f deployment/ai-service-worker -n ai-service
```

### Scale Workers

```bash
# Manual scaling
kubectl scale deployment ai-service-worker --replicas=4 -n ai-service

# Check HPA status
kubectl get hpa -n ai-service
```

---

## Monitoring

### Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ai-service-monitor
  namespace: ai-service
spec:
  selector:
    matchLabels:
      app: ai-service
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ai-service-pdb
  namespace: ai-service
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: ai-service
      component: api
```

---

## Troubleshooting

### Pod stuck in Pending

```bash
# Check events
kubectl describe pod <pod-name> -n ai-service

# Check node resources
kubectl describe nodes | grep -A 5 "Allocated resources"
```

### GPU not available

```bash
# Check GPU operator
kubectl get pods -n gpu-operator

# Check node labels
kubectl get nodes --show-labels | grep gpu

# Check GPU allocation
kubectl describe node <node-name> | grep nvidia
```

### Models not loading

```bash
# Check worker logs
kubectl logs deployment/ai-service-worker -n ai-service

# Check PVC
kubectl get pvc -n ai-service
kubectl describe pvc ai-models-pvc -n ai-service
```

---

## Next Steps

- [Manual Installation](./manual.md) - Install without containers
- [Configuration Reference](../configuration/environment-variables.md) - All environment variables
- [Monitoring Setup](../operations/monitoring.md) - Prometheus and Grafana
