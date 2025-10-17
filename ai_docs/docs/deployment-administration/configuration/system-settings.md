# System Settings

## Overview

This guide covers the configuration of system-wide settings for both the Helpline System and AI Service components of OpenCHS.

---

## Table of Contents

1. [Helpline System Configuration](#helpline-system-configuration)
2. [AI Service Configuration](#ai-service-configuration)
3. [Integration Settings](#integration-settings)
4. [Security Settings](#security-settings)
5. [Performance Settings](#performance-settings)

---

## Helpline System Configuration

### Database Configuration

Location: `/var/www/html/helpline/config/database.php`

```php
<?php
return [
    'default' => 'mysql',
    
    'connections' => [
        'mysql' => [
            'driver' => 'mysql',
            'host' => env('DB_HOST', 'localhost'),
            'port' => env('DB_PORT', '3306'),
            'database' => env('DB_DATABASE', 'helpline'),
            'username' => env('DB_USERNAME', 'nginx'),
            'password' => env('DB_PASSWORD', ''),
            'unix_socket' => '/var/run/mysqld/mysqld.sock',
            'charset' => 'utf8mb4',
            'collation' => 'utf8mb4_unicode_ci',
            'prefix' => '',
            'strict' => true,
            'engine' => 'InnoDB',
        ],
    ],
];
```

### Application Configuration

Location: `/var/www/html/helpline/config/app.php`

```php
<?php
return [
    // Application name
    'name' => env('APP_NAME', 'OpenCHS Helpline'),
    
    // Environment (local, staging, production)
    'env' => env('APP_ENV', 'production'),
    
    // Debug mode
    'debug' => env('APP_DEBUG', false),
    
    // Application URL
    'url' => env('APP_URL', 'https://helpline.yourdomain.com'),
    
    // Timezone
    'timezone' => env('APP_TIMEZONE', 'Africa/Nairobi'),
    
    // Locale
    'locale' => 'en',
    'fallback_locale' => 'en',
    
    // Session configuration
    'session_lifetime' => env('SESSION_LIFETIME', 480), // 8 hours in minutes
    'session_driver' => 'database',
    
    // Logging
    'log_level' => env('LOG_LEVEL', 'warning'),
    'log_channel' => env('LOG_CHANNEL', 'daily'),
    'log_max_files' => 14,
];
```

### API Configuration

Location: `/var/www/html/helpline/config/api.php`

```php
<?php
return [
    // API versioning
    'version' => 'v1',
    
    // Rate limiting
    'rate_limit' => [
        'enabled' => true,
        'max_attempts' => 60,
        'decay_minutes' => 1,
    ],
    
    // CORS settings
    'cors' => [
        'allowed_origins' => explode(',', env('CORS_ALLOWED_ORIGINS', '*')),
        'allowed_methods' => ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        'allowed_headers' => ['Content-Type', 'Authorization', 'X-Requested-With'],
        'exposed_headers' => ['X-Total-Count', 'X-Page-Count'],
        'max_age' => 3600,
    ],
    
    // Pagination
    'pagination' => [
        'default_per_page' => 20,
        'max_per_page' => 100,
    ],
    
    // File uploads
    'uploads' => [
        'max_size' => env('UPLOAD_MAX_SIZE', 10485760), // 10MB in bytes
        'allowed_types' => ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/webm'],
        'storage_path' => env('UPLOAD_STORAGE_PATH', '/var/www/html/helpline/storage/uploads'),
    ],
];
```

### Environment Variables

Location: `/var/www/html/helpline/.env`

```bash
# Application
APP_NAME="OpenCHS Helpline"
APP_ENV=production
APP_DEBUG=false
APP_URL=https://helpline.yourdomain.com
APP_TIMEZONE=Africa/Nairobi

# Database
DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=helpline
DB_USERNAME=nginx
DB_PASSWORD=

# Session
SESSION_LIFETIME=480
SESSION_DRIVER=database

# Logging
LOG_LEVEL=warning
LOG_CHANNEL=daily

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Uploads
UPLOAD_MAX_SIZE=10485760
UPLOAD_STORAGE_PATH=/var/www/html/helpline/storage/uploads

# AI Service Integration
AI_SERVICE_URL=http://localhost:8123
AI_SERVICE_ENABLED=true
AI_SERVICE_TIMEOUT=300
```

---

## AI Service Configuration

### Application Configuration

Location: `/opt/openchs-ai/.env`

```bash
# ===========================
# Application Settings
# ===========================
APP_NAME="OpenCHS AI Service"
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# ===========================
# Server Configuration
# ===========================
HOST=0.0.0.0
PORT=8123
WORKERS=4
RELOAD=false

# ===========================
# Resource Management
# ===========================
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300
MAX_RETRY_ATTEMPTS=3

# ===========================
# Model Configuration
# ===========================
ENABLE_MODEL_LOADING=true
MODEL_CACHE_SIZE=8192
MODEL_PATH=/opt/openchs-ai/models

# Whisper Configuration
WHISPER_MODEL=large-v3-turbo
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16

# Translation Configuration
TRANSLATION_MODEL=custom-sw-en
TRANSLATION_DEVICE=cuda
TRANSLATION_MAX_LENGTH=512

# NER Configuration
NER_MODEL=en_core_web_md
NER_BATCH_SIZE=16

# Classification Configuration
CLASSIFIER_MODEL=distilbert-case-classifier
CLASSIFIER_THRESHOLD=0.7

# Summarization Configuration
SUMMARIZER_MODEL=facebook/bart-large-cnn
SUMMARIZER_MAX_LENGTH=150
SUMMARIZER_MIN_LENGTH=50

# ===========================
# Redis Configuration
# ===========================
REDIS_URL=redis://localhost:6379/0
REDIS_TASK_DB=1
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_ACCEPT_CONTENT=["json"]
CELERY_TIMEZONE=Africa/Nairobi
CELERY_ENABLE_UTC=true

# ===========================
# Security Settings
# ===========================
SITE_ID=production-001
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DATA_RETENTION_HOURS=24
ENABLE_AUTH=false
API_KEY=

# ===========================
# File Processing
# ===========================
MAX_FILE_SIZE_MB=100
ALLOWED_AUDIO_FORMATS=wav,mp3,ogg,webm,m4a
UPLOAD_DIR=/opt/openchs-ai/uploads
TEMP_DIR=/tmp/openchs-ai

# ===========================
# Performance Tuning
# ===========================
# CPU Settings
OMP_NUM_THREADS=8
MKL_NUM_THREADS=8

# GPU Settings (if available)
CUDA_VISIBLE_DEVICES=0
TORCH_DTYPE=float16
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Memory Management
CUDA_LAUNCH_BLOCKING=0
PYTORCH_NO_CUDA_MEMORY_CACHING=0

# ===========================
# Monitoring & Logging
# ===========================
ENABLE_METRICS=true
METRICS_PORT=9090
LOG_FILE=/var/log/openchs/ai-service.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# ===========================
# Feature Flags
# ===========================
ENABLE_TRANSLATION=true
ENABLE_NER=true
ENABLE_CLASSIFICATION=true
ENABLE_SUMMARIZATION=true
ENABLE_INSIGHTS=true
```

### Model Configuration File

Location: `/opt/openchs-ai/config/models.yaml`

```yaml
models:
  whisper:
    name: "Whisper Large V3 Turbo"
    model_id: "openai/whisper-large-v3-turbo"
    device: "cuda"
    compute_type: "float16"
    language_support: "multilingual"
    max_audio_length: 1800  # 30 minutes
    
  translation:
    name: "Swahili-English Translation"
    model_id: "custom-sw-en-v1"
    source_lang: "sw"
    target_lang: "en"
    device: "cuda"
    max_length: 512
    num_beams: 4
    
  ner:
    name: "Named Entity Recognition"
    model_id: "en_core_web_md"
    entities:
      - PERSON
      - ORG
      - GPE
      - LOC
      - DATE
      - TIME
      - MONEY
      - PERCENT
    
  classifier:
    name: "Case Classification"
    model_id: "distilbert-case-classifier-v1"
    labels:
      - child_protection
      - mental_health_crisis
      - domestic_violence
      - substance_abuse
      - educational_support
      - general_inquiry
    threshold: 0.7
    
  summarizer:
    name: "Text Summarization"
    model_id: "facebook/bart-large-cnn"
    max_length: 150
    min_length: 50
    length_penalty: 2.0
    num_beams: 4
```

### Performance Tuning Configuration

Location: `/opt/openchs-ai/config/performance.yaml`

```yaml
# Resource allocation
resources:
  gpu:
    memory_fraction: 0.9
    allow_growth: true
    per_process_memory_fraction: 0.9
    
  cpu:
    num_threads: 8
    inter_op_parallelism: 2
    intra_op_parallelism: 8
    
  memory:
    max_cache_size_gb: 8
    buffer_size_mb: 512

# Batch processing
batch_processing:
  enabled: true
  max_batch_size: 4
  batch_timeout_seconds: 5
  
# Queue management
queue:
  max_size: 20
  timeout_seconds: 300
  priority_levels: 3
  
# Caching
cache:
  enabled: true
  ttl_seconds: 3600
  max_entries: 1000
  
# Connection pooling
connection_pool:
  redis:
    max_connections: 50
    min_idle_connections: 5
    connection_timeout: 5
```

---

## Integration Settings

### Helpline to AI Service Integration

Configure the Helpline system to communicate with the AI Service:

**Location**: `/var/www/html/helpline/config/integrations.php`

```php
<?php
return [
    'ai_service' => [
        'enabled' => env('AI_SERVICE_ENABLED', true),
        'url' => env('AI_SERVICE_URL', 'http://localhost:8123'),
        'timeout' => env('AI_SERVICE_TIMEOUT', 300),
        'retry_attempts' => 3,
        'retry_delay' => 1000, // milliseconds
        
        'endpoints' => [
            'process' => '/audio/process',
            'analyze' => '/audio/analyze',
            'status' => '/audio/task/{task_id}',
            'health' => '/health/detailed',
        ],
        
        'features' => [
            'transcription' => true,
            'translation' => true,
            'ner' => true,
            'classification' => true,
            'summarization' => true,
        ],
        
        'defaults' => [
            'language' => 'sw',
            'include_translation' => true,
            'enable_insights' => true,
        ],
    ],
];
```

### API Authentication

For secure communication between services:

```bash
# Generate API key
php artisan key:generate --api

# Add to .env
AI_SERVICE_API_KEY=generated-api-key-here
```

Update AI Service configuration:

```bash
# In /opt/openchs-ai/.env
ENABLE_AUTH=true
API_KEY=same-generated-api-key-here
```

---

## Security Settings

### SSL/TLS Configuration

**Nginx SSL Configuration** (`/etc/nginx/sites-available/openchs`):

```nginx
# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;

# Security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
```

### Database Security

```bash
# MySQL configuration (/etc/mysql/mysql.conf.d/mysqld.cnf)
[mysqld]
# Network security
bind-address = 127.0.0.1
skip-networking = 0
port = 3306

# Connection limits
max_connections = 200
max_user_connections = 50

# Security options
local-infile = 0
symbolic-links = 0

# Logging
log_error = /var/log/mysql/error.log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-query.log
long_query_time = 2
```

### Firewall Configuration

```bash
# UFW rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw enable
```

---

## Performance Settings

### PHP-FPM Optimization

**Location**: `/etc/php/8.2/fpm/pool.d/www.conf`

```ini
[www]
# Process management
pm = dynamic
pm.max_children = 50
pm.start_servers = 10
pm.min_spare_servers = 5
pm.max_spare_servers = 15
pm.max_requests = 500
pm.process_idle_timeout = 10s

# Performance tuning
php_admin_value[memory_limit] = 256M
php_admin_value[max_execution_time] = 300
php_admin_value[max_input_time] = 300
php_admin_value[post_max_size] = 50M
php_admin_value[upload_max_filesize] = 50M

# OPcache settings
php_admin_value[opcache.enable] = 1
php_admin_value[opcache.memory_consumption] = 128
php_admin_value[opcache.interned_strings_buffer] = 8
php_admin_value[opcache.max_accelerated_files] = 4000
php_admin_value[opcache.revalidate_freq] = 60
php_admin_value[opcache.fast_shutdown] = 1
```

### Nginx Optimization

**Location**: `/etc/nginx/nginx.conf`

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 50m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;
    
    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;
    
    # FastCGI cache
    fastcgi_cache_path /var/cache/nginx levels=1:2 keys_zone=PHP_CACHE:100m inactive=60m;
    fastcgi_cache_key "$scheme$request_method$host$request_uri";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=10r/s;
}
```

### MySQL Performance Tuning

**Location**: `/etc/mysql/mysql.conf.d/mysqld.cnf`

```ini
[mysqld]
# InnoDB settings
innodb_buffer_pool_size = 4G
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
innodb_file_per_table = 1

# Query cache (deprecated in MySQL 8.0)
# For MySQL 5.7:
# query_cache_type = 1
# query_cache_size = 128M
# query_cache_limit = 2M

# Connection settings
max_connections = 200
max_allowed_packet = 64M
thread_cache_size = 50

# Table cache
table_open_cache = 4000
table_definition_cache = 2000

# Temporary tables
tmp_table_size = 256M
max_heap_table_size = 256M

# Logging
slow_query_log = 1
long_query_time = 2
log_queries_not_using_indexes = 1
```

### Redis Optimization

**Location**: `/etc/redis/redis.conf`

```conf
# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
databases 16

# Slow log
slowlog-log-slower-than 10000
slowlog-max-len 128
```

---

## Configuration Management

### Environment-Specific Configurations

Create separate configuration files for different environments:

```bash
# Directory structure
/opt/openchs-ai/config/
├── .env.production
├── .env.staging
├── .env.development
└── .env.local

# Symlink to active environment
ln -sf .env.production .env
```

### Configuration Validation

```bash
# Validate Nginx configuration
sudo nginx -t

# Validate PHP-FPM configuration
sudo php-fpm8.2 -t

# Test MySQL configuration
sudo mysqld --validate-config

# Check AI Service configuration
cd /opt/openchs-ai
source venv/bin/activate
python -m app.config_validator
```

### Configuration Backup

```bash
# Backup all configuration files
#!/bin/bash
BACKUP_DIR="/backup/config/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Helpline configs
cp -r /var/www/html/helpline/config $BACKUP_DIR/helpline-config
cp /var/www/html/helpline/.env $BACKUP_DIR/helpline-env

# AI Service configs
cp -r /opt/openchs-ai/config $BACKUP_DIR/ai-config
cp /opt/openchs-ai/.env $BACKUP_DIR/ai-env

# System configs
cp /etc/nginx/sites-available/openchs $BACKUP_DIR/nginx-config
cp /etc/php/8.2/fpm/pool.d/www.conf $BACKUP_DIR/php-fpm-config
cp /etc/mysql/mysql.conf.d/mysqld.cnf $BACKUP_DIR/mysql-config
cp /etc/redis/redis.conf $BACKUP_DIR/redis-config

echo "Configuration backup completed: $BACKUP_DIR"
```

---

## Next Steps

After configuring system settings:

1. **Set Up Users and Roles**: See [User Role Management](user-role-management.md)
2. **Configure Communication Channels**: See [Configuring Communication Channels](configuring-communication-channels.md)
3. **Set Up Backups**: See [Backup & Recovery](backup-recovery.md)
4. **Configure Monitoring**: See [System Health Checks](../maintenance-monitoring/system-health-checks.md)

---

## Quick Reference

### Restart Services After Configuration Changes

```bash
# Helpline system
sudo systemctl restart nginx
sudo systemctl restart php8.2-fpm
sudo systemctl restart mysql

# AI Service
sudo systemctl restart openchs-ai-api
sudo systemctl restart openchs-ai-worker
sudo systemctl restart redis-server
```

### Verify Configuration

```bash
# Check service status
sudo systemctl status nginx php8.2-fpm mysql openchs-ai-api openchs-ai-worker

# Test connectivity
curl -I https://helpline.yourdomain.com
curl http://localhost:8123/health/detailed
```