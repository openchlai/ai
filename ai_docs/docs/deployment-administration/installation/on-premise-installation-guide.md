# On-Premise Installation Guide

## Overview

This guide covers manual installation of OpenCHS components on bare metal or virtual machines. For containerized deployment, see [Docker & Kubernetes Setup](docker-kubernetes-setup.md).

---

## Table of Contents

1. [Pre-Installation Checklist](#pre-installation-checklist)
2. [Helpline System Installation](#helpline-system-installation)
3. [AI Service Installation](#ai-service-installation)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [Post-Installation Verification](#post-installation-verification)
6. [Troubleshooting](#troubleshooting)

---

## Pre-Installation Checklist

### System Preparation

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install basic utilities
sudo apt-get install -y curl wget git vim htop net-tools

# Create deployment user (optional but recommended)
sudo useradd -m -s /bin/bash openchs
sudo usermod -aG sudo openchs
```

### Directory Structure

```bash
# Create application directories
sudo mkdir -p /usr/src/OpenChs
sudo mkdir -p /var/www/html/helpline
sudo mkdir -p /etc/pki/openchs/private
sudo mkdir -p /var/log/openchs

# Set permissions
sudo chown -R openchs:openchs /usr/src/OpenChs
sudo chown -R nginx:nginx /var/www/html
```

---

## Helpline System Installation

### Step 1: Install MySQL Database

```bash
# Install MySQL 8.0
sudo apt-get install -y mysql-server

# Secure MySQL installation
sudo mysql_secure_installation

# Start and enable MySQL
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Step 2: Configure Database

```bash
# Create database user with unix_socket authentication
sudo mysql -e "CREATE USER 'nginx'@'localhost' IDENTIFIED VIA unix_socket;"

# Create helpline database
sudo mysql -e "CREATE DATABASE helpline CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Import database schema
# First, obtain the uchl.sql file and place it in /usr/src/OpenChs/rest_api/
sudo mysql helpline < /usr/src/OpenChs/rest_api/uchl.sql

# Grant permissions to nginx user
sudo mysql -e "
GRANT SELECT, INSERT ON helpline.* TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.auth TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.contact TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.kase TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.kase_activity TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.activity TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.disposition TO 'nginx'@'localhost';
GRANT DELETE ON helpline.session TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.chan TO 'nginx'@'localhost';
FLUSH PRIVILEGES;"

# Verify database creation
sudo mysql -e "SHOW DATABASES;" | grep helpline
```

### Step 3: Install PHP and Extensions

```bash
# Add PHP repository (for Ubuntu 20.04)
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:ondrej/php -y
sudo apt-get update

# Install PHP 8.2 and required extensions
sudo apt-get install -y \
    php8.2 \
    php8.2-fpm \
    php8.2-mysql \
    php8.2-curl \
    php8.2-json \
    php8.2-mbstring \
    php8.2-xml \
    php8.2-zip \
    php8.2-gd

# Verify PHP installation
php -v
```

### Step 4: Configure PHP-FPM

```bash
# Configure PHP-FPM main settings
sudo tee /etc/php/8.2/fpm/php-fpm.conf > /dev/null <<EOF
[global]
error_log = /var/log/php8.2-fpm.log
log_level = warning
emergency_restart_threshold = 10
emergency_restart_interval = 1m
process_control_timeout = 10s
daemonize = yes
EOF

# Configure PHP-FPM pool
sudo tee /etc/php/8.2/fpm/pool.d/www.conf > /dev/null <<EOF
[www]
user = nginx
group = nginx
listen = /run/php/php8.2-fpm.sock
listen.owner = nginx
listen.group = nginx
listen.mode = 0660

pm = dynamic
pm.max_children = 20
pm.start_servers = 5
pm.min_spare_servers = 5
pm.max_spare_servers = 10
pm.max_requests = 500

php_admin_value[error_log] = /var/log/fpm-php.www.log
php_admin_flag[log_errors] = on
php_admin_value[upload_max_filesize] = 50M
php_admin_value[post_max_size] = 50M
php_admin_value[max_execution_time] = 300
EOF

# Start and enable PHP-FPM
sudo systemctl start php8.2-fpm
sudo systemctl enable php8.2-fpm
```

### Step 5: Install and Configure Nginx

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create PHP-FPM upstream configuration
sudo tee /etc/nginx/conf.d/php-fpm.conf > /dev/null <<EOF
upstream php-fpm {
    server unix:/run/php/php8.2-fpm.sock;
}
EOF

# Create PHP configuration
sudo tee /etc/nginx/default.d/php.conf > /dev/null <<EOF
index index.php index.html index.htm;

location ~ \.(php|phar)(/.*)?$ {
    fastcgi_split_path_info ^(.+\.(?:php|phar))(/.*)$;
    fastcgi_intercept_errors on;
    fastcgi_index index.php;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
    fastcgi_param PATH_INFO \$fastcgi_path_info;
    fastcgi_pass php-fpm;
}
EOF

# Note: Create /etc/nginx/default.d directory if it doesn't exist
sudo mkdir -p /etc/nginx/default.d
```

### Step 6: Configure Nginx Server Block

```bash
# Backup default config
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Create OpenCHS server configuration
sudo tee /etc/nginx/sites-available/openchs > /dev/null <<'EOF'
server {
    listen 443 ssl http2;
    server_name helpline.yourdomain.com;
    root /var/www/html;

    # SSL Configuration
    ssl_certificate /etc/pki/openchs/openchs.crt;
    ssl_certificate_key /etc/pki/openchs/private/openchs.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/openchs-access.log;
    error_log /var/log/nginx/openchs-error.log;

    # Helpline API endpoint
    location /helpline/ {
        index index.php index.html index.htm;
        try_files $uri $uri/ /helpline/api/index.php?$args;
    }

    # PHP processing
    include /etc/nginx/default.d/php.conf;

    # Proxy to AI service (if deployed on same server)
    location /ai-service/ {
        proxy_pass http://127.0.0.1:8123/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name helpline.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/openchs /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 7: Deploy Helpline Application Files

```bash
# Clone or copy application files
# If using git:
cd /usr/src/OpenChs
git clone <repository-url> .

# Or copy from archive:
# tar -xzf openchs-helpline.tar.gz -C /usr/src/OpenChs/

# Copy web files to Nginx root
sudo cp -r /usr/src/OpenChs/rest_api/* /var/www/html/helpline/

# Set correct permissions
sudo chown -R nginx:nginx /var/www/html/helpline
sudo chmod -R 755 /var/www/html/helpline
sudo chmod -R 775 /var/www/html/helpline/uploads # if uploads directory exists

# Configure application settings
sudo nano /var/www/html/helpline/config.php
# Update database credentials and other settings
```

---

## AI Service Installation

### Step 1: Install Python and Dependencies

```bash
# Install Python 3.11
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Verify Python installation
python3.11 --version

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Install system dependencies
sudo apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    libsm6 \
    libxext6
```

### Step 2: Install NVIDIA Drivers and CUDA (GPU Only)

```bash
# Check if NVIDIA GPU is available
lspci | grep -i nvidia

# Install NVIDIA driver
sudo apt-get install -y nvidia-driver-535

# Add NVIDIA package repositories
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"

# Install CUDA Toolkit
sudo apt-get update
sudo apt-get install -y cuda-toolkit-12-1

# Reboot to load drivers
sudo reboot

# After reboot, verify CUDA installation
nvidia-smi
```

### Step 3: Install Redis

```bash
# Install Redis
sudo apt-get install -y redis-server

# Configure Redis
sudo tee /etc/redis/redis.conf > /dev/null <<EOF
bind 127.0.0.1
port 6379
daemonize yes
supervised systemd
dir /var/lib/redis
maxmemory 2gb
maxmemory-policy allkeys-lru
EOF

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping # Should return "PONG"
```

### Step 4: Deploy AI Service Application

```bash
# Create application directory
sudo mkdir -p /opt/openchs-ai
cd /opt/openchs-ai

# Clone or copy AI service files
git clone <ai-service-repository-url> .

# Or copy from archive:
# tar -xzf openchs-ai-service.tar.gz -C /opt/openchs-ai/

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md

# Create directories for models and logs
mkdir -p models logs uploads
```

### Step 5: Configure AI Service

```bash
# Create environment configuration
cat > /opt/openchs-ai/.env <<EOF
# Application Settings
APP_NAME="OpenCHS AI Service"
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=127.0.0.1
PORT=8123

# Resource Management
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_TASK_DB=1

# Model Configuration
ENABLE_MODEL_LOADING=true
MODEL_CACHE_SIZE=8192

# Security
SITE_ID=production-001
DATA_RETENTION_HOURS=24
MAX_FILE_SIZE_MB=100

# GPU Configuration (if available)
CUDA_VISIBLE_DEVICES=0
TORCH_DTYPE=float16
EOF

# Set correct permissions
sudo chown -R openchs:openchs /opt/openchs-ai
```

### Step 6: Create Systemd Services

#### FastAPI Service

```bash
# Create FastAPI systemd service
sudo tee /etc/systemd/system/openchs-ai-api.service > /dev/null <<EOF
[Unit]
Description=OpenCHS AI Service API
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=simple
User=openchs
Group=openchs
WorkingDirectory=/opt/openchs-ai
Environment="PATH=/opt/openchs-ai/venv/bin"
EnvironmentFile=/opt/openchs-ai/.env
ExecStart=/opt/openchs-ai/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8123
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Logging
StandardOutput=append:/var/log/openchs/ai-api.log
StandardError=append:/var/log/openchs/ai-api-error.log

[Install]
WantedBy=multi-user.target
EOF
```

#### Celery Worker Service

```bash
# Create Celery worker systemd service
sudo tee /etc/systemd/system/openchs-ai-worker.service > /dev/null <<EOF
[Unit]
Description=OpenCHS AI Service Celery Worker
After=network.target redis-server.service openchs-ai-api.service
Requires=redis-server.service

[Service]
Type=simple
User=openchs
Group=openchs
WorkingDirectory=/opt/openchs-ai
Environment="PATH=/opt/openchs-ai/venv/bin"
EnvironmentFile=/opt/openchs-ai/.env
ExecStart=/opt/openchs-ai/venv/bin/celery -A app.celery_app worker --loglevel=info -E --pool=solo
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Logging
StandardOutput=append:/var/log/openchs/ai-worker.log
StandardError=append:/var/log/openchs/ai-worker-error.log

[Install]
WantedBy=multi-user.target
EOF
```

### Step 7: Start AI Services

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Start and enable services
sudo systemctl start openchs-ai-api
sudo systemctl enable openchs-ai-api

sudo systemctl start openchs-ai-worker
sudo systemctl enable openchs-ai-worker

# Check service status
sudo systemctl status openchs-ai-api
sudo systemctl status openchs-ai-worker
```

---

## SSL Certificate Setup

### Option 1: Let's Encrypt (Recommended for Production)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d helpline.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Certificates will be automatically placed in:
# /etc/letsencrypt/live/helpline.yourdomain.com/
```

### Option 2: Self-Signed Certificate (Development/Testing)

```bash
# Create certificate directory
sudo mkdir -p /etc/pki/openchs/private

# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/pki/openchs/private/openchs.key \
    -out /etc/pki/openchs/openchs.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=helpline.yourdomain.com"

# Set permissions
sudo chmod 600 /etc/pki/openchs/private/openchs.key
sudo chmod 644 /etc/pki/openchs/openchs.crt
```

### Update Nginx Configuration

```bash
# If using Let's Encrypt, update Nginx config:
sudo sed -i 's|/etc/pki/openchs/openchs.crt|/etc/letsencrypt/live/helpline.yourdomain.com/fullchain.pem|g' /etc/nginx/sites-available/openchs
sudo sed -i 's|/etc/pki/openchs/private/openchs.key|/etc/letsencrypt/live/helpline.yourdomain.com/privkey.pem|g' /etc/nginx/sites-available/openchs

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

## Post-Installation Verification

### Verify Helpline System

```bash
# Check MySQL
sudo systemctl status mysql
sudo mysql -e "SELECT VERSION();"

# Check PHP-FPM
sudo systemctl status php8.2-fpm
php -v

# Check Nginx
sudo systemctl status nginx
curl -I https://helpline.yourdomain.com/helpline/

# Check database connectivity
sudo mysql helpline -e "SHOW TABLES;"
```

### Verify AI Service

```bash
# Check Redis
sudo systemctl status redis-server
redis-cli ping

# Check API service
sudo systemctl status openchs-ai-api
curl http://localhost:8123/health/detailed

# Check Celery worker
sudo systemctl status openchs-ai-worker

# Test AI service
curl -X POST http://localhost:8123/audio/workers/status
```

### Access Applications

```bash
# Helpline system
https://helpline.yourdomain.com/helpline/

# AI Service API documentation
http://localhost:8123/docs

# Or via Nginx proxy
https://helpline.yourdomain.com/ai-service/docs
```

---

## Troubleshooting

### Helpline System Issues

#### PHP-FPM not starting
```bash
# Check logs
sudo tail -f /var/log/php8.2-fpm.log
sudo tail -f /var/log/fpm-php.www.log

# Check socket permissions
ls -la /run/php/php8.2-fpm.sock

# Restart service
sudo systemctl restart php8.2-fpm
```

#### Database connection errors
```bash
# Verify MySQL is running
sudo systemctl status mysql

# Check user permissions
sudo mysql -e "SELECT user, host FROM mysql.user WHERE user='nginx';"

# Test connection
sudo mysql -u nginx helpline -e "SELECT 1;"
```

#### Nginx 502 errors
```bash
# Check if PHP-FPM is running
sudo systemctl status php8.2-fpm

# Check Nginx error log
sudo tail -f /var/log/nginx/openchs-error.log

# Verify PHP-FPM socket
sudo netstat -tlnp | grep 9000
```

### AI Service Issues

#### Models not loading
```bash
# Check logs
sudo journalctl -u openchs-ai-api -f
tail -f /var/log/openchs/ai-api.log

# Verify model files exist
ls -lh /opt/openchs-ai/models/

# Check disk space
df -h

# Manually download models if needed
cd /opt/openchs-ai
source venv/bin/activate
python -m spacy download en_core_web_md
```

#### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA installation
nvcc --version

# Verify PyTorch CUDA support
python3 -c "import torch; print(torch.cuda.is_available())"

# Check environment variables
echo $CUDA_VISIBLE_DEVICES
```

#### Celery worker issues
```bash
# Check worker status
sudo systemctl status openchs-ai-worker

# View worker logs
sudo journalctl -u openchs-ai-worker -f

# Check Redis connection
redis-cli ping

# Restart worker
sudo systemctl restart openchs-ai-worker
```

#### High memory usage
```bash
# Check memory usage
free -h
htop

# Adjust worker configuration in .env
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=10

# Restart services
sudo systemctl restart openchs-ai-worker
```

---

## Next Steps

After successful installation:

1. **Configure System Settings**: See [System Settings](../configuration/system-settings.md)
2. **Set Up Users and Roles**: See [User Role Management](../configuration/user-role-management.md)
3. **Configure Backups**: See [Backup & Recovery](../configuration/backup-recovery.md)
4. **Set Up Monitoring**: See [System Health Checks](../maintenance-monitoring/system-health-checks.md)

---

## Quick Command Reference

### Service Management
```bash
# Restart all services
sudo systemctl restart nginx php8.2-fpm mysql redis-server openchs-ai-api openchs-ai-worker

# Check all service status
sudo systemctl status nginx php8.2-fpm mysql redis-server openchs-ai-api openchs-ai-worker

# View logs
sudo tail -f /var/log/nginx/openchs-error.log
sudo journalctl -u openchs-ai-api -f
```

### Maintenance
```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Restart services after updates
sudo systemctl restart openchs-ai-api openchs-ai-worker nginx php8.2-fpm

# Clean old logs
sudo find /var/log/openchs -type f -name "*.log" -mtime +30 -delete
```