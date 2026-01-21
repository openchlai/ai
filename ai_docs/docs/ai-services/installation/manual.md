---
layout: doc
title: Manual Installation
---

# Manual Installation

Install the AI Service directly on a Linux server without Docker.

## Overview

This guide covers installing the AI Service on bare metal or VM:

1. System preparation
2. Python environment setup
3. Redis installation
4. Application setup
5. Service configuration
6. Running as systemd services

---

## System Requirements

### Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 24+ cores |
| RAM | 8GB | 32GB+ |
| Storage | 50GB | 100GB+ |
| GPU | - | NVIDIA 16GB+ VRAM |

### Operating System

- **Ubuntu** 20.04 LTS or later (recommended)
- **Debian** 11+
- **RHEL/CentOS** 8+

---

## Step 1: System Preparation

### Update System

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### Install System Dependencies

```bash
sudo apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    build-essential \
    git \
    curl \
    wget \
    libsndfile1 \
    ffmpeg \
    libffi-dev \
    libssl-dev
```

### Install NVIDIA Drivers (GPU Only)

```bash
# Add NVIDIA repository
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:graphics-drivers/ppa
sudo apt-get update

# Install drivers
sudo apt-get install -y nvidia-driver-535

# Install CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-toolkit-12-2

# Verify installation
nvidia-smi
```

---

## Step 2: Install Redis

### Option A: APT Package

```bash
# Install Redis
sudo apt-get install -y redis-server

# Configure Redis
sudo sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping
# Expected: PONG
```

### Option B: Latest Version

```bash
# Download and compile
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install -y redis

# Start service
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

---

## Step 3: Application Setup

### Create Application User

```bash
# Create dedicated user
sudo useradd -r -m -s /bin/bash aiservice
sudo usermod -aG sudo aiservice

# Switch to user
sudo su - aiservice
```

### Clone Repository

```bash
# Clone the repository
git clone https://github.com/openchlai/ai-service.git
cd ai-service
```

### Create Virtual Environment

```bash
# Create venv
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg
```

### Create Directories

```bash
mkdir -p models logs temp data results
chmod 755 models logs temp data results
```

---

## Step 4: Configuration

### Create Environment File

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

### Minimal Configuration

```bash
# Application
APP_NAME=AI_Pipeline
APP_VERSION=0.1.0
APP_PORT=8125
LOG_LEVEL=INFO

# Redis
REDIS_URL=redis://localhost:6379/0

# Models
ENABLE_MODEL_LOADING=true
WHISPER_DEVICE=cuda  # or 'cpu'
WHISPER_COMPUTE_TYPE=float16
USE_HF_MODELS=true

# Processing
DEFAULT_PROCESSING_MODE=adaptive
ENABLE_STREAMING_PROCESSING=true
ENABLE_POSTCALL_PROCESSING=true
```

### Database Setup (Optional)

For production, use PostgreSQL instead of SQLite:

```bash
# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Create database
sudo -u postgres psql << EOF
CREATE USER aiservice WITH PASSWORD 'your-password';
CREATE DATABASE ai_service OWNER aiservice;
GRANT ALL PRIVILEGES ON DATABASE ai_service TO aiservice;
EOF

# Update .env
DATABASE_URL=postgresql://aiservice:your-password@localhost/ai_service
```

---

## Step 5: Systemd Services

### API Server Service

Create `/etc/systemd/system/ai-service-api.service`:

```ini
[Unit]
Description=AI Service API Server
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple
User=aiservice
Group=aiservice
WorkingDirectory=/home/aiservice/ai-service
Environment="PATH=/home/aiservice/ai-service/venv/bin"
EnvironmentFile=/home/aiservice/ai-service/.env
ExecStart=/home/aiservice/ai-service/venv/bin/python -m app.main
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/home/aiservice/ai-service/logs/api.log
StandardError=append:/home/aiservice/ai-service/logs/api-error.log

# Security
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/aiservice/ai-service/logs /home/aiservice/ai-service/temp

[Install]
WantedBy=multi-user.target
```

### Celery Worker Service

Create `/etc/systemd/system/ai-service-worker.service`:

```ini
[Unit]
Description=AI Service Celery Worker
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple
User=aiservice
Group=aiservice
WorkingDirectory=/home/aiservice/ai-service
Environment="PATH=/home/aiservice/ai-service/venv/bin"
EnvironmentFile=/home/aiservice/ai-service/.env
ExecStart=/home/aiservice/ai-service/venv/bin/celery -A app.celery_app worker --loglevel=info -E --pool=solo -Q model_processing,celery
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/home/aiservice/ai-service/logs/worker.log
StandardError=append:/home/aiservice/ai-service/logs/worker-error.log

# GPU access
Environment="CUDA_VISIBLE_DEVICES=0"

[Install]
WantedBy=multi-user.target
```

### Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable ai-service-api
sudo systemctl enable ai-service-worker

# Start services
sudo systemctl start ai-service-api
sudo systemctl start ai-service-worker

# Check status
sudo systemctl status ai-service-api
sudo systemctl status ai-service-worker
```

---

## Step 6: NGINX Reverse Proxy (Optional)

### Install NGINX

```bash
sudo apt-get install -y nginx
```

### Configure NGINX

Create `/etc/nginx/sites-available/ai-service`:

```nginx
upstream ai_service {
    server 127.0.0.1:8125;
}

server {
    listen 80;
    server_name ai-service.example.com;

    location / {
        proxy_pass http://ai_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Large file uploads
    client_max_body_size 500M;
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/ai-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Enable HTTPS with Certbot

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ai-service.example.com
```

---

## Step 7: Verify Installation

### Check Services

```bash
# Check API
curl http://localhost:8125/health

# Check detailed status
curl http://localhost:8125/health/detailed | jq

# Check models
curl http://localhost:8125/health/models | jq
```

### Check Logs

```bash
# API logs
tail -f /home/aiservice/ai-service/logs/api.log

# Worker logs
tail -f /home/aiservice/ai-service/logs/worker.log

# System logs
journalctl -u ai-service-api -f
journalctl -u ai-service-worker -f
```

---

## Management Commands

### Service Control

```bash
# Start/stop/restart
sudo systemctl start ai-service-api
sudo systemctl stop ai-service-worker
sudo systemctl restart ai-service-api

# View status
sudo systemctl status ai-service-api

# View logs
journalctl -u ai-service-api -n 100
```

### Application Commands

```bash
# Activate environment
cd /home/aiservice/ai-service
source venv/bin/activate

# Run manual commands
python -m app.main  # Run API manually
celery -A app.celery_app inspect active  # Check active tasks
celery -A app.celery_app purge  # Clear task queue
```

### Update Application

```bash
cd /home/aiservice/ai-service
source venv/bin/activate

# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart services
sudo systemctl restart ai-service-api
sudo systemctl restart ai-service-worker
```

---

## Troubleshooting

### Service won't start

```bash
# Check logs
journalctl -u ai-service-api -n 50 --no-pager

# Check permissions
ls -la /home/aiservice/ai-service/

# Check environment
sudo -u aiservice bash -c 'source /home/aiservice/ai-service/venv/bin/activate && python -c "import app"'
```

### GPU not detected

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA
nvcc --version

# Check PyTorch GPU access
source venv/bin/activate
python -c "import torch; print(torch.cuda.is_available())"
```

### Redis connection failed

```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check Redis logs
sudo journalctl -u redis-server
```

---

## Next Steps

- [Docker Compose Deployment](./docker-compose.md) - Container-based deployment
- [Configuration Reference](../configuration/environment-variables.md) - All settings
- [Monitoring](../operations/monitoring.md) - Set up monitoring
