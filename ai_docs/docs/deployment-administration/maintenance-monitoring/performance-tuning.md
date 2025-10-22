# Performance Tuning

## Overview

This guide covers performance optimization strategies for OpenCHS, including database tuning, application optimization, caching strategies, and load balancing configurations.

---

## Table of Contents

1. [Performance Baseline](#performance-baseline)
2. [Database Optimization](#database-optimization)
3. [Web Server Tuning](#web-server-tuning)
4. [Application Optimization](#application-optimization)
5. [AI Service Performance](#ai-service-performance)
6. [Caching Strategies](#caching-strategies)
7. [Load Balancing](#load-balancing)

---

## Performance Baseline

### Establish Baseline Metrics

```bash
#!/bin/bash
# /usr/local/bin/benchmark-openchs.sh

echo "======================================"
echo "OpenCHS Performance Baseline"
echo "======================================"

# Database performance
echo "Database Query Performance:"
mysql helpline -e "
    SELECT 
        COUNT(*) as total_cases,
        AVG(TIMESTAMPDIFF(SECOND, created_at, updated_at)) as avg_processing_time
    FROM kase
    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);
"

# API response times
echo -e "\nAPI Response Times:"
for i in {1..10}; do
    curl -o /dev/null -s -w "Request $i: %{time_total}s\n" \
        https://helpline.yourdomain.com/helpline/api/health
done

# AI Service performance
echo -e "\nAI Service Status:"
curl -s http://localhost:8123/health/detailed | jq '{
    queue_size: .queue.current_size,
    avg_processing_time: .performance.avg_processing_time,
    models_loaded: .models_loaded
}'

# System resources
echo -e "\nSystem Resources:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk I/O: $(iostat -x 1 2 | tail -1 | awk '{print $4}')"
```

### Performance Targets

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| **API Response Time** | < 200ms | > 1000ms |
| **Database Query Time** | < 100ms | > 500ms |
| **AI Processing Time** | < 30s/min audio | > 60s/min audio |
| **Page Load Time** | < 2s | > 5s |
| **Concurrent Users** | 100+ | N/A |
| **CPU Usage** | < 70% | > 90% |
| **Memory Usage** | < 80% | > 95% |

---

## Database Optimization

### MySQL Configuration Tuning

**Edit: `/etc/mysql/mysql.conf.d/mysqld.cnf`**

```ini
[mysqld]
# Connection Management
max_connections = 200
max_connect_errors = 100
connect_timeout = 10
wait_timeout = 600
interactive_timeout = 600

# InnoDB Optimization
innodb_buffer_pool_size = 4G  # 70-80% of available RAM
innodb_buffer_pool_instances = 4
innodb_log_file_size = 512M
innodb_log_buffer_size = 64M
innodb_flush_log_at_trx_commit = 2  # 0=fastest, 1=safest, 2=balanced
innodb_flush_method = O_DIRECT
innodb_file_per_table = 1
innodb_io_capacity = 2000
innodb_io_capacity_max = 4000
innodb_read_io_threads = 4
innodb_write_io_threads = 4

# Query Cache (MySQL 5.7 only)
# query_cache_type = 1
# query_cache_size = 128M
# query_cache_limit = 2M

# Thread and Table Cache
thread_cache_size = 50
table_open_cache = 4000
table_definition_cache = 2000
open_files_limit = 65535

# Temporary Tables
tmp_table_size = 256M
max_heap_table_size = 256M

# Binary Logging
binlog_cache_size = 32M
max_binlog_size = 100M
expire_logs_days = 7
sync_binlog = 0  # 0=faster, 1=safer

# MyISAM (if used)
key_buffer_size = 256M
myisam_sort_buffer_size = 64M

# Slow Query Log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-query.log
long_query_time = 2
log_queries_not_using_indexes = 1
```

Restart MySQL:
```bash
sudo systemctl restart mysql
```

### Index Optimization

```sql
-- Analyze current indexes
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    SEQ_IN_INDEX,
    COLUMN_NAME,
    CARDINALITY
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'helpline'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- Find missing indexes
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME,
    COUNT_STAR,
    COUNT_READ,
    COUNT_WRITE
FROM performance_schema.table_io_waits_summary_by_table
WHERE OBJECT_SCHEMA = 'helpline'
ORDER BY COUNT_STAR DESC;

-- Add recommended indexes
-- Cases table
CREATE INDEX idx_status_created ON helpline.kase(status, created_at);
CREATE INDEX idx_assigned_to ON helpline.kase(assigned_to);
CREATE INDEX idx_priority ON helpline.kase(priority);

-- Contact table
CREATE INDEX idx_phone ON helpline.contact(phone);
CREATE INDEX idx_email ON helpline.contact(email);
CREATE INDEX idx_channel_created ON helpline.contact(channel_id, created_at);

-- Activity table
CREATE INDEX idx_case_created ON helpline.kase_activity(kase_id, created_at);
CREATE INDEX idx_user_created ON helpline.kase_activity(user_id, created_at);

-- Analyze tables after adding indexes
ANALYZE TABLE helpline.kase, helpline.contact, helpline.kase_activity;
```

### Query Optimization

```sql
-- Enable profiling
SET profiling = 1;

-- Run your query
SELECT * FROM kase WHERE status = 'open' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);

-- Show profile
SHOW PROFILES;
SHOW PROFILE FOR QUERY 1;

-- Explain query execution plan
EXPLAIN SELECT * FROM kase WHERE status = 'open' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);

-- Optimize slow queries example
-- Before (slow)
SELECT * FROM kase k
JOIN contact c ON k.contact_id = c.id
WHERE k.status = 'open';

-- After (optimized)
SELECT k.id, k.status, c.phone, c.email
FROM kase k
JOIN contact c ON k.contact_id = c.id
WHERE k.status = 'open'
AND k.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### Database Maintenance

```bash
#!/bin/bash
# /usr/local/bin/optimize-database.sh

echo "Starting database optimization..."

# Optimize all tables
mysql helpline -e "
    SELECT CONCAT('OPTIMIZE TABLE ', table_schema, '.', table_name, ';')
    FROM information_schema.tables
    WHERE table_schema = 'helpline'
    AND engine = 'InnoDB';
" | grep "OPTIMIZE" | mysql

# Analyze tables
mysql helpline -e "ANALYZE TABLE kase, contact, kase_activity, disposition, activity;"

# Update table statistics
mysql helpline -e "
    FLUSH TABLES;
    FLUSH STATUS;
"

echo "Database optimization completed."
```

Schedule weekly:
```bash
# Add to crontab
0 3 * * 0 /usr/local/bin/optimize-database.sh >> /var/log/openchs/db-optimize.log 2>&1
```

---

## Web Server Tuning

### Nginx Optimization

**Edit: `/etc/nginx/nginx.conf`**

```nginx
user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    access_log /var/log/nginx/access.log main buffer=32k flush=5s;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    reset_timedout_connection on;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 50m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;
    output_buffers 1 32k;
    postpone_output 1460;
    
    # Timeouts
    client_body_timeout 30;
    client_header_timeout 30;
    send_timeout 30;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 1000;
    gzip_disable "msie6";
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/rss+xml
        application/atom+xml
        font/truetype
        font/opentype
        application/vnd.ms-fontobject
        image/svg+xml;
    
    # FastCGI cache
    fastcgi_cache_path /var/cache/nginx/fastcgi 
        levels=1:2 
        keys_zone=PHP_CACHE:100m 
        inactive=60m 
        max_size=1g;
    fastcgi_cache_key "$scheme$request_method$host$request_uri";
    fastcgi_cache_use_stale error timeout invalid_header http_500;
    fastcgi_cache_valid 200 60m;
    fastcgi_cache_valid 404 10m;
    fastcgi_ignore_headers Cache-Control Expires Set-Cookie;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    
    # Connection limiting
    limit_conn addr 10;
    
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

**Enable caching in server block:**

```nginx
server {
    # ... existing configuration ...
    
    location ~ \.php$ {
        # FastCGI cache
        fastcgi_cache PHP_CACHE;
        fastcgi_cache_bypass $http_cache_control;
        add_header X-FastCGI-Cache $upstream_cache_status;
        
        # Existing FastCGI configuration
        fastcgi_pass php-fpm;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        
        # Buffer sizes
        fastcgi_buffer_size 32k;
        fastcgi_buffers 8 16k;
        fastcgi_busy_buffers_size 64k;
        fastcgi_temp_file_write_size 64k;
    }
    
    # Static file caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
```

Create cache directory:
```bash
sudo mkdir -p /var/cache/nginx/fastcgi
sudo chown -R nginx:nginx /var/cache/nginx
```

### PHP-FPM Tuning

**Edit: `/etc/php/8.2/fpm/pool.d/www.conf`**

```ini
[www]
; Process Management
pm = dynamic
pm.max_children = 50         ; Maximum number of child processes
pm.start_servers = 10        ; Number of children at startup
pm.min_spare_servers = 5     ; Minimum idle servers
pm.max_spare_servers = 15    ; Maximum idle servers
pm.max_requests = 500        ; Restart workers after N requests
pm.process_idle_timeout = 10s

; Performance tuning
pm.status_path = /status
ping.path = /ping
ping.response = pong
request_terminate_timeout = 300
request_slowlog_timeout = 10s
slowlog = /var/log/php8.2-fpm-slow.log

; PHP settings
php_admin_value[memory_limit] = 256M
php_admin_value[max_execution_time] = 300
php_admin_value[max_input_time] = 300
php_admin_value[post_max_size] = 50M
php_admin_value[upload_max_filesize] = 50M

; OPcache settings
php_admin_value[opcache.enable] = 1
php_admin_value[opcache.memory_consumption] = 256
php_admin_value[opcache.interned_strings_buffer] = 16
php_admin_value[opcache.max_accelerated_files] = 10000
php_admin_value[opcache.revalidate_freq] = 60
php_admin_value[opcache.validate_timestamps] = 1
php_admin_value[opcache.fast_shutdown] = 1
php_admin_value[opcache.enable_cli] = 0

; Realpath cache
php_admin_value[realpath_cache_size] = 4096k
php_admin_value[realpath_cache_ttl] = 600
```

**Monitoring PHP-FPM:**

```bash
# Enable status page in Nginx
location ~ ^/(status|ping)$ {
    access_log off;
    allow 127.0.0.1;
    deny all;
    include fastcgi_params;
    fastcgi_pass php-fpm;
}

# Check PHP-FPM status
curl http://localhost/status?full
curl http://localhost/status?json

# Monitor slow requests
tail -f /var/log/php8.2-fpm-slow.log
```

---

## Application Optimization

### Code-Level Optimization

**Enable Production Mode:**

```bash
# In .env file
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=warning
```

**Database Connection Pooling:**

```php
// config/database.php
return [
    'connections' => [
        'mysql' => [
            'driver' => 'mysql',
            // ... existing config ...
            'options' => [
                PDO::ATTR_PERSISTENT => true,  // Enable persistent connections
                PDO::ATTR_EMULATE_PREPARES => false,
                PDO::ATTR_STRINGIFY_FETCHES => false,
            ],
        ],
    ],
];
```

**Query Result Caching:**

```php
// Example: Cache frequently accessed data
$cache = new Cache();
$cacheKey = 'active_cases_count';

$count = $cache->remember($cacheKey, 300, function() {
    return DB::table('kase')->where('status', 'open')->count();
});
```

### Asset Optimization

```bash
# Minify CSS and JavaScript
npm install -g clean-css-cli uglify-js

# Minify CSS
cleancss -o style.min.css style.css

# Minify JavaScript
uglifyjs app.js -o app.min.js -c -m

# Optimize images
sudo apt-get install -y optipng jpegoptim
find /var/www/html/helpline/public/images -name "*.png" -exec optipng -o5 {} \;
find /var/www/html/helpline/public/images -name "*.jpg" -exec jpegoptim --strip-all {} \;
```

---

## AI Service Performance

### GPU Optimization

**CUDA Configuration:**

```bash
# In /opt/openchs-ai/.env
CUDA_VISIBLE_DEVICES=0
TORCH_DTYPE=float16
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# For multiple GPUs
CUDA_VISIBLE_DEVICES=0,1

# CPU thread optimization
OMP_NUM_THREADS=8
MKL_NUM_THREADS=8
```

### Model Loading Optimization

```python
# app/models/model_loader.py

import torch
from functools import lru_cache

class ModelLoader:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        
    @lru_cache(maxsize=5)
    def load_model(self, model_name):
        """Cache loaded models in memory"""
        if model_name not in self.models:
            model = self._load_model_from_disk(model_name)
            model.to(self.device)
            model.eval()  # Set to evaluation mode
            
            # Enable optimizations
            if self.device == "cuda":
                model = torch.compile(model)  # PyTorch 2.0+
                
            self.models[model_name] = model
            
        return self.models[model_name]
```

### Batch Processing

```python
# app/services/audio_processor.py

class AudioProcessor:
    def __init__(self, batch_size=4):
        self.batch_size = batch_size
        self.queue = []
        
    async def process_batch(self):
        """Process multiple audio files in a single batch"""
        if len(self.queue) >= self.batch_size:
            batch = self.queue[:self.batch_size]
            self.queue = self.queue[self.batch_size:]
            
            # Process batch together (more efficient than one-by-one)
            results = await self.model.process_batch(batch)
            return results
```

### Celery Worker Optimization

**Edit: `/opt/openchs-ai/.env`**

```bash
# Worker concurrency
CELERY_WORKER_CONCURRENCY=1  # Use 1 for GPU workloads
CELERY_WORKER_PREFETCH_MULTIPLIER=1

# Task time limits
CELERY_TASK_TIME_LIMIT=600
CELERY_TASK_SOFT_TIME_LIMIT=500

# Result backend
CELERY_RESULT_EXPIRES=3600
CELERY_TASK_IGNORE_RESULT=False

# Optimization
CELERY_TASK_ACKS_LATE=True
CELERY_WORKER_DISABLE_RATE_LIMITS=False
```

**Scale Celery Workers:**

```bash
# For CPU-based processing, scale workers
sudo systemctl stop openchs-ai-worker

# Edit systemd service to add more workers
sudo systemctl edit openchs-ai-worker

[Service]
ExecStart=
ExecStart=/opt/openchs-ai/venv/bin/celery -A app.celery_app worker \
    --loglevel=info -E --pool=prefork --concurrency=4

sudo systemctl start openchs-ai-worker
```

### Redis Optimization

**Edit: `/etc/redis/redis.conf`**

```conf
# Memory optimization
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence tuning (for faster performance, trade durability)
save ""  # Disable RDB snapshots
appendonly yes
appendfsync everysec  # Balance between safety and speed
no-appendfsync-on-rewrite yes

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
databases 16
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes

# Threading (Redis 6.0+)
io-threads 4
io-threads-do-reads yes
```

---

## Caching Strategies

### Application-Level Caching

**Redis Cache Implementation:**

```php
<?php
// CacheManager.php

class CacheManager {
    private $redis;
    
    public function __construct() {
        $this->redis = new Redis();
        $this->redis->connect('127.0.0.1', 6379);
    }
    
    public function remember($key, $ttl, $callback) {
        $value = $this->redis->get($key);
        
        if ($value === false) {
            $value = $callback();
            $this->redis->setex($key, $ttl, serialize($value));
        } else {
            $value = unserialize($value);
        }
        
        return $value;
    }
    
    public function forget($key) {
        $this->redis->del($key);
    }
    
    public function flush() {
        $this->redis->flushDB();
    }
}

// Usage example
$cache = new CacheManager();

// Cache user data for 1 hour
$user = $cache->remember('user:123', 3600, function() {
    return DB::table('auth')->find(123);
});

// Cache statistics for 5 minutes
$stats = $cache->remember('dashboard:stats', 300, function() {
    return [
        'total_cases' => DB::table('kase')->count(),
        'open_cases' => DB::table('kase')->where('status', 'open')->count(),
        'active_users' => DB::table('auth')->where('status', 'active')->count(),
    ];
});
```

### HTTP Caching Headers

```php
// Set proper cache headers for API responses
header('Cache-Control: public, max-age=300'); // 5 minutes
header('Expires: ' . gmdate('D, d M Y H:i:s', time() + 300) . ' GMT');
header('ETag: ' . md5(json_encode($data)));

// Check if client has cached version
if (isset($_SERVER['HTTP_IF_NONE_MATCH']) && 
    $_SERVER['HTTP_IF_NONE_MATCH'] === md5(json_encode($data))) {
    http_response_code(304);
    exit;
}
```

### Cache Invalidation Strategy

```php
<?php
// Automatic cache invalidation on data changes

class CaseRepository {
    private $cache;
    
    public function update($id, $data) {
        // Update database
        $result = DB::table('kase')->where('id', $id)->update($data);
        
        // Invalidate related caches
        $this->cache->forget("case:$id");
        $this->cache->forget("cases:user:" . $data['assigned_to']);
        $this->cache->forget("dashboard:stats");
        
        return $result;
    }
}
```

---

## Load Balancing

### Nginx Load Balancer Configuration

**Setup for multiple application servers:**

```nginx
# /etc/nginx/conf.d/upstream.conf

upstream helpline_backend {
    least_conn;  # Use least connections algorithm
    
    server 192.168.1.10:8080 weight=3 max_fails=3 fail_timeout=30s;
    server 192.168.1.11:8080 weight=3 max_fails=3 fail_timeout=30s;
    server 192.168.1.12:8080 weight=2 max_fails=3 fail_timeout=30s backup;
    
    keepalive 32;  # Keep connections alive
}

upstream ai_service_backend {
    ip_hash;  # Sticky sessions for AI processing
    
    server 192.168.1.20:8123 max_fails=2 fail_timeout=30s;
    server 192.168.1.21:8123 max_fails=2 fail_timeout=30s;
    
    keepalive 16;
}

server {
    listen 443 ssl http2;
    server_name helpline.yourdomain.com;
    
    location /helpline/ {
        proxy_pass http://helpline_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    location /ai-service/ {
        proxy_pass http://ai_service_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Longer timeout for AI processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### HAProxy Configuration (Alternative)

```bash
# Install HAProxy
sudo apt-get install -y haproxy

# Edit /etc/haproxy/haproxy.cfg
```

```conf
global
    log /dev/log local0
    log /dev/log local1 notice
    maxconn 4096
    tune.ssl.default-dh-param 2048

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000
    timeout client 50000
    timeout server 50000

frontend http_front
    bind *:80
    redirect scheme https code 301 if !{ ssl_fc }

frontend https_front
    bind *:443 ssl crt /etc/ssl/certs/openchs.pem
    default_backend helpline_backend
    
    acl is_ai_service path_beg /ai-service
    use_backend ai_backend if is_ai_service

backend helpline_backend
    balance leastconn
    option httpchk GET /health
    http-check expect status 200
    
    server web1 192.168.1.10:8080 check inter 5s rise 2 fall 3
    server web2 192.168.1.11:8080 check inter 5s rise 2 fall 3
    server web3 192.168.1.12:8080 check inter 5s rise 2 fall 3 backup

backend ai_backend
    balance source  # Sticky sessions
    option httpchk GET /health
    
    server ai1 192.168.1.20:8123 check inter 10s rise 2 fall 3
    server ai2 192.168.1.21:8123 check inter 10s rise 2 fall 3

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats auth admin:secure_password
```

### Database Read Replicas

**MySQL Replication Setup:**

```sql
-- On Master Server
CREATE USER 'replicator'@'%' IDENTIFIED BY 'strong_password';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
FLUSH PRIVILEGES;
FLUSH TABLES WITH READ LOCK;
SHOW MASTER STATUS;  -- Note File and Position

-- Backup master database
mysqldump -u root -p helpline > helpline_master.sql

-- On Slave Server
mysql -u root -p helpline < helpline_master.sql

CHANGE MASTER TO
    MASTER_HOST='192.168.1.10',
    MASTER_USER='replicator',
    MASTER_PASSWORD='strong_password',
    MASTER_LOG_FILE='mysql-bin.000001',  -- From SHOW MASTER STATUS
    MASTER_LOG_POS=12345;  -- From SHOW MASTER STATUS

START SLAVE;
SHOW SLAVE STATUS\G
```

**Application Configuration for Read/Write Splitting:**

```php
// config/database.php
return [
    'connections' => [
        'mysql_write' => [
            'driver' => 'mysql',
            'host' => '192.168.1.10',  // Master
            // ... other config
        ],
        'mysql_read' => [
            'driver' => 'mysql',
            'host' => ['192.168.1.11', '192.168.1.12'],  // Slaves
            'sticky' => false,
            // ... other config
        ],
    ],
];

// Usage
DB::connection('mysql_write')->table('kase')->insert($data);  // Writes to master
$cases = DB::connection('mysql_read')->table('kase')->get();  // Reads from slave
```

---

## Performance Monitoring

### Continuous Monitoring Script

```bash
#!/bin/bash
# /usr/local/bin/monitor-performance.sh

METRICS_DIR="/var/log/openchs/performance"
mkdir -p "$METRICS_DIR"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

{
    echo "=== Performance Metrics: $TIMESTAMP ==="
    
    # System resources
    echo -e "\n[System Resources]"
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
    
    # Database performance
    echo -e "\n[Database]"
    mysql -N -e "SHOW GLOBAL STATUS LIKE 'Queries';" | awk '{print "Total Queries: " $2}'
    mysql -N -e "SHOW GLOBAL STATUS LIKE 'Slow_queries';" | awk '{print "Slow Queries: " $2}'
    mysql -N -e "SHOW GLOBAL STATUS LIKE 'Threads_connected';" | awk '{print "Connections: " $2}'
    
    # Nginx performance
    echo -e "\n[Nginx]"
    echo "Active Connections: $(ss -tan | grep :443 | wc -l)"
    
    # Redis performance
    echo -e "\n[Redis]"
    redis-cli INFO stats | grep -E "total_connections_received|total_commands_processed"
    
    # AI Service
    echo -e "\n[AI Service]"
    curl -s http://localhost:8123/audio/queue/status | jq '{queue_size, processing}'
    
} | tee "$METRICS_DIR/metrics_$TIMESTAMP.log"

# Keep only last 7 days
find "$METRICS_DIR" -name "metrics_*.log" -mtime +7 -delete
```

### Benchmark Scripts

```bash
#!/bin/bash
# /usr/local/bin/benchmark-api.sh

# Install Apache Bench if not available
# sudo apt-get install apache2-utils

echo "Benchmarking Helpline API..."

# Test 1: Health endpoint
echo -e "\n=== Health Endpoint ==="
ab -n 1000 -c 10 https://helpline.yourdomain.com/helpline/api/health

# Test 2: Case list endpoint (with authentication)
echo -e "\n=== Case List Endpoint ==="
ab -n 100 -c 5 -H "Authorization: Bearer YOUR_TOKEN" \
    https://helpline.yourdomain.com/helpline/api/cases

# AI Service benchmark
echo -e "\n=== AI Service Health ==="
ab -n 100 -c 5 http://localhost:8123/health
```

---

## Next Steps

After performance tuning:

1. **Set Up Logging**: See [Logging & Auditing](logging-auditing.md)
2. **Plan Upgrades**: See [Upgrading OpenCHS](upgrading-openchs.md)
3. **Review Health Checks**: See [System Health Checks](system-health-checks.md)

---

## Quick Reference

### Performance Check Commands

```bash
# Check system resources
htop
iostat -x 1
vmstat 1

# Check MySQL performance
mysql -e "SHOW PROCESSLIST;"
mysql -e "SHOW ENGINE INNODB STATUS\G"
mysqladmin -i 1 status

# Check Nginx status
curl http://localhost/nginx_status

# Check PHP-FPM status
curl http://localhost/status?full

# Check Redis performance
redis-cli INFO stats
redis-cli --latency

# Monitor AI Service
curl http://localhost:8123/health/detailed | jq .

# Test response times
time curl https://helpline.yourdomain.com/helpline/
```

### Troubleshooting Slow Performance

```bash
# Identify slow MySQL queries
mysql -e "SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;"

# Find PHP processes using high CPU
ps aux | grep php | sort -nrk 3 | head -10

# Check disk I/O
iotop -o

# Network performance
iftop

# Clear all caches
# PHP OPcache
systemctl restart php8.2-fpm

# Nginx cache
rm -rf /var/cache/nginx/*
systemctl reload nginx

# Redis cache
redis-cli FLUSHALL
```