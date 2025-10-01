# Logging & Auditing

## Overview

This guide covers comprehensive logging and audit trail implementation for OpenCHS, including log management, security auditing, compliance tracking, and log analysis tools.

---

## Table of Contents

1. [Logging Strategy](#logging-strategy)
2. [Application Logging](#application-logging)
3. [System Logging](#system-logging)
4. [Audit Trail Implementation](#audit-trail-implementation)
5. [Log Management](#log-management)
6. [Log Analysis](#log-analysis)
7. [Compliance & Retention](#compliance--retention)

---

## Logging Strategy

### Log Levels

| Level | Use Case | Examples |
|-------|----------|----------|
| **DEBUG** | Development debugging | Variable values, function calls |
| **INFO** | General information | User login, case created |
| **WARNING** | Warning conditions | Deprecated API use, high resource usage |
| **ERROR** | Error conditions | Failed database query, file not found |
| **CRITICAL** | Critical conditions | System failure, security breach |

### Log Categories

1. **Application Logs**: User actions, business logic
2. **Security Logs**: Authentication, authorization, access control
3. **Audit Logs**: Data changes, administrative actions
4. **Performance Logs**: Response times, resource usage
5. **Error Logs**: Exceptions, failures
6. **Access Logs**: HTTP requests, API calls

---

## Application Logging

### Helpline System Logging

**Configuration: `/var/www/html/helpline/config/logging.php`**

```php
<?php
return [
    'default' => env('LOG_CHANNEL', 'daily'),
    
    'channels' => [
        'daily' => [
            'driver' => 'daily',
            'path' => '/var/log/openchs/helpline/application.log',
            'level' => env('LOG_LEVEL', 'info'),
            'days' => 14,
        ],
        
        'security' => [
            'driver' => 'daily',
            'path' => '/var/log/openchs/helpline/security.log',
            'level' => 'info',
            'days' => 90,
        ],
        
        'audit' => [
            'driver' => 'daily',
            'path' => '/var/log/openchs/helpline/audit.log',
            'level' => 'info',
            'days' => 365,
        ],
        
        'error' => [
            'driver' => 'daily',
            'path' => '/var/log/openchs/helpline/error.log',
            'level' => 'error',
            'days' => 30,
        ],
    ],
];
```

**Usage in Application:**

```php
<?php
// Logger.php

class Logger {
    public static function info($message, array $context = []) {
        self::log('info', $message, $context);
    }
    
    public static function error($message, array $context = []) {
        self::log('error', $message, $context);
    }
    
    public static function security($message, array $context = []) {
        self::log('security', $message, $context);
    }
    
    public static function audit($action, $userId, $resourceType, $resourceId, $changes = []) {
        $entry = [
            'timestamp' => date('Y-m-d H:i:s'),
            'user_id' => $userId,
            'action' => $action,
            'resource_type' => $resourceType,
            'resource_id' => $resourceId,
            'changes' => $changes,
            'ip_address' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
        ];
        
        self::log('audit', json_encode($entry));
        
        // Also store in database
        DB::table('audit_log')->insert($entry);
    }
    
    private static function log($level, $message, array $context = []) {
        $channel = getLogChannel($level);
        $logFile = getLogFile($channel);
        
        $entry = sprintf(
            "[%s] %s: %s %s\n",
            date('Y-m-d H:i:s'),
            strtoupper($level),
            $message,
            !empty($context) ? json_encode($context) : ''
        );
        
        file_put_contents($logFile, $entry, FILE_APPEND | LOCK_EX);
    }
}

// Usage examples
Logger::info('User logged in', ['user_id' => 123, 'username' => 'jdoe']);
Logger::error('Database connection failed', ['error' => $exception->getMessage()]);
Logger::security('Failed login attempt', ['username' => 'admin', 'ip' => '192.168.1.100']);
Logger::audit('update', $userId, 'case', $caseId, ['status' => ['open' => 'closed']]);
```

### AI Service Logging

**Configuration: `/opt/openchs-ai/app/config/logging.py`**

```python
import logging
import logging.handlers
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def setup_logging():
    # Main application log
    app_handler = logging.handlers.RotatingFileHandler(
        '/var/log/openchs/ai-service/application.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    app_handler.setFormatter(JSONFormatter())
    app_handler.setLevel(logging.INFO)
    
    # Error log
    error_handler = logging.handlers.RotatingFileHandler(
        '/var/log/openchs/ai-service/error.log',
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setFormatter(JSONFormatter())
    error_handler.setLevel(logging.ERROR)
    
    # Performance log
    perf_handler = logging.handlers.RotatingFileHandler(
        '/var/log/openchs/ai-service/performance.log',
        maxBytes=10485760,
        backupCount=5
    )
    perf_handler.setFormatter(JSONFormatter())
    perf_handler.setLevel(logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # Performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    
    return root_logger

# Usage in application
logger = logging.getLogger(__name__)

logger.info("Audio processing started", extra={'request_id': task_id, 'file_size': file_size})
logger.error("Model loading failed", extra={'model': 'whisper', 'error': str(e)})

# Performance logging
perf_logger = logging.getLogger('performance')
perf_logger.info("Processing completed", extra={
    'request_id': task_id,
    'processing_time': elapsed_time,
    'audio_duration': audio_duration,
    'models_used': ['whisper', 'translation', 'ner']
})
```

---

## System Logging

### Nginx Access Logs

**Custom Log Format: `/etc/nginx/nginx.conf`**

```nginx
log_format detailed '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    'rt=$request_time '
                    'uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" '
                    'urt="$upstream_response_time" '
                    'cs=$upstream_cache_status '
                    'request_id=$request_id';

access_log /var/log/nginx/openchs-access.log detailed;
error_log /var/log/nginx/openchs-error.log warn;
```

### MySQL Query Logging

**Enable Slow Query Log:**

```sql
-- Enable slow query logging
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- Enable general query log (use sparingly in production)
-- SET GLOBAL general_log = 'ON';
-- SET GLOBAL general_log_file = '/var/log/mysql/general.log';
```

**Analyze Slow Queries:**

```bash
# Install pt-query-digest
sudo apt-get install percona-toolkit

# Analyze slow query log
pt-query-digest /var/log/mysql/slow-query.log > /tmp/slow-query-analysis.txt

# Top 10 slowest queries
pt-query-digest /var/log/mysql/slow-query.log --limit 10
```

### Redis Logging

**Configuration: `/etc/redis/redis.conf`**

```conf
# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Slow log
slowlog-log-slower-than 10000  # microseconds (10ms)
slowlog-max-len 128
```

**View Slow Log:**

```bash
# View slow commands
redis-cli SLOWLOG GET 10

# Reset slow log
redis-cli SLOWLOG RESET
```

### System Logs (Systemd)

```bash
# View service logs
sudo journalctl -u nginx -f
sudo journalctl -u php8.2-fpm -f
sudo journalctl -u mysql -f
sudo journalctl -u openchs-ai-api -f
sudo journalctl -u openchs-ai-worker -f

# View logs for specific time range
sudo journalctl -u openchs-ai-api --since "2024-01-15 10:00:00" --until "2024-01-15 11:00:00"

# Export logs to file
sudo journalctl -u openchs-ai-api --since today > /tmp/ai-service-today.log
```

---

## Audit Trail Implementation

### Database Audit Log Table

```sql
-- Create comprehensive audit log table
CREATE TABLE IF NOT EXISTS helpline.audit_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT UNSIGNED,
    username VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INT UNSIGNED,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_action (action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_request_id (request_id)
) ENGINE=InnoDB;

-- Trigger for case updates
DELIMITER //
CREATE TRIGGER audit_case_update
AFTER UPDATE ON helpline.kase
FOR EACH ROW
BEGIN
    INSERT INTO helpline.audit_log (
        user_id,
        action,
        resource_type,
        resource_id,
        old_values,
        new_values,
        ip_address
    ) VALUES (
        @current_user_id,
        'update',
        'case',
        NEW.id,
        JSON_OBJECT(
            'status', OLD.status,
            'priority', OLD.priority,
            'assigned_to', OLD.assigned_to
        ),
        JSON_OBJECT(
            'status', NEW.status,
            'priority', NEW.priority,
            'assigned_to', NEW.assigned_to
        ),
        @client_ip
    );
END//
DELIMITER ;
```

### Audit Log Queries

```sql
-- View all actions by user
SELECT 
    timestamp,
    action,
    resource_type,
    resource_id,
    old_values,
    new_values
FROM helpline.audit_log
WHERE user_id = 123
ORDER BY timestamp DESC
LIMIT 50;

-- View all changes to a specific case
SELECT 
    al.timestamp,
    u.username,
    al.action,
    al.old_values,
    al.new_values,
    al.ip_address
FROM helpline.audit_log al
LEFT JOIN helpline.auth u ON al.user_id = u.id
WHERE al.resource_type = 'case'
AND al.resource_id = 456
ORDER BY al.timestamp DESC;

-- Security audit: Failed login attempts
SELECT 
    timestamp,
    username,
    ip_address,
    error_message,
    COUNT(*) OVER (PARTITION BY ip_address) as attempts_from_ip
FROM helpline.audit_log
WHERE action = 'login'
AND status = 'failed'
AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC;

-- Data export audit
SELECT 
    al.timestamp,
    u.username,
    u.email,
    al.resource_type,
    COUNT(*) as export_count
FROM helpline.audit_log al
JOIN helpline.auth u ON al.user_id = u.id
WHERE al.action = 'export'
AND al.timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY al.user_id, al.resource_type
ORDER BY export_count DESC;
```

---

## Log Management

### Log Rotation Configuration

**Logrotate Configuration: `/etc/logrotate.d/openchs`**

```conf
/var/log/openchs/*/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 nginx nginx
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
        systemctl reload php8.2-fpm > /dev/null 2>&1 || true
    endscript
}

/var/log/openchs/helpline/audit.log {
    daily
    missingok
    rotate 365
    compress
    delaycompress
    notifempty
    create 0640 nginx nginx
}

/var/log/openchs/ai-service/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 openchs openchs
    sharedscripts
    postrotate
        systemctl reload openchs-ai-api > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/openchs-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 nginx nginx
    sharedscripts
    postrotate
        nginx -s reopen > /dev/null 2>&1 || true
    endscript
}
```

Test logrotate:
```bash
# Test configuration
sudo logrotate -d /etc/logrotate.d/openchs

# Force rotation
sudo logrotate -f /etc/logrotate.d/openchs
```

### Centralized Logging (Optional)

**Rsyslog Configuration for Remote Logging:**

```conf
# /etc/rsyslog.d/30-openchs.conf

# Send OpenCHS logs to remote syslog server
if $programname == 'openchs' then @@remote-syslog-server.com:514
& stop
```

### Log Archival Script

```bash
#!/bin/bash
# /usr/local/bin/archive-logs.sh

ARCHIVE_DIR="/backup/openchs/logs"
LOG_DIR="/var/log/openchs"
RETENTION_DAYS=90

mkdir -p "$ARCHIVE_DIR"

# Archive logs older than 30 days
find "$LOG_DIR" -name "*.log.gz" -mtime +30 -exec mv {} "$ARCHIVE_DIR/" \;

# Clean up archives older than retention period
find "$ARCHIVE_DIR" -name "*.log.gz" -mtime +$RETENTION_DAYS -delete

echo "Log archival completed: $(date)" >> /var/log/openchs/archive.log
```

Schedule monthly:
```bash
# Add to crontab
0 2 1 * * /usr/local/bin/archive-logs.sh
```

---

## Log Analysis

### Log Analysis Scripts

**Parse Nginx Logs:**

```bash
#!/bin/bash
# /usr/local/bin/analyze-nginx-logs.sh

LOG_FILE="/var/log/nginx/openchs-access.log"

echo "=== Nginx Log Analysis ==="
echo ""

echo "Top 10 IP Addresses:"
awk '{print $1}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -10

echo -e "\nTop 10 Requested URLs:"
awk '{print $7}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -10

echo -e "\nHTTP Status Code Distribution:"
awk '{print $9}' "$LOG_FILE" | sort | uniq -c | sort -rn

echo -e "\nSlowest Requests (top 10):"
awk '{print $NF, $7}' "$LOG_FILE" | sed 's/rt=//' | sort -rn | head -10

echo -e "\nRequests per Hour:"
awk '{print $4}' "$LOG_FILE" | cut -d: -f2 | sort | uniq -c
```

**Analyze Application Logs:**

```bash
#!/bin/bash
# /usr/local/bin/analyze-app-logs.sh

LOG_FILE="/var/log/openchs/helpline/application.log"

echo "=== Application Log Analysis ==="
echo ""

echo "Error Count by Type:"
grep -E "ERROR|CRITICAL" "$LOG_FILE" | awk '{print $3}' | sort | uniq -c | sort -rn

echo -e "\nMost Active Users:"
grep "user_id" "$LOG_FILE" | grep -oP 'user_id":\K[0-9]+' | sort | uniq -c | sort -rn | head -10

echo -e "\nRecent Errors:"
grep -E "ERROR|CRITICAL" "$LOG_FILE" | tail -20
```

### Real-time Log Monitoring

```bash
#!/bin/bash
# /usr/local/bin/monitor-logs.sh

# Monitor for errors across all logs
echo "Monitoring for errors (Ctrl+C to stop)..."

tail -f /var/log/openchs/*/*.log \
    /var/log/nginx/openchs-error.log \
    /var/log/mysql/error.log \
| grep --line-buffered -E "ERROR|CRITICAL|ALERT" \
| while read line; do
    echo "[$(date)] $line"
    # Send alert if critical
    if echo "$line" | grep -q "CRITICAL"; then
        echo "$line" | mail -s "CRITICAL Error Detected" admin@yourdomain.com
    fi
done
```

### GoAccess for Web Log Analysis

```bash
# Install GoAccess
sudo apt-get install -y goaccess

# Real-time HTML report
goaccess /var/log/nginx/openchs-access.log \
    --log-format=COMBINED \
    -o /var/www/html/stats/report.html \
    --real-time-html \
    --ws-url=wss://helpline.yourdomain.com:7890

# Terminal-based analysis
goaccess /var/log/nginx/openchs-access.log --log-format=COMBINED
```

---

## Compliance & Retention

### GDPR Compliance

**Data Retention Policy:**

```sql
-- Anonymize old audit logs
UPDATE helpline.audit_log
SET 
    ip_address = 'ANONYMIZED',
    user_agent = 'ANONYMIZED'
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 2 YEAR);

-- Delete very old audit logs
DELETE FROM helpline.audit_log
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 7 YEAR);
```

**Data Subject Access Request (DSAR):**

```sql
-- Export all logs related to a user
SELECT * FROM helpline.audit_log
WHERE user_id = 123
OR username = 'jdoe'
OR JSON_SEARCH(old_values, 'one', 'jdoe') IS NOT NULL
OR JSON_SEARCH(new_values, 'one', 'jdoe') IS NOT NULL
ORDER BY timestamp DESC;
```

### Retention Automation

```bash
#!/bin/bash
# /usr/local/bin/enforce-retention-policy.sh

# Application logs: 90 days
find /var/log/openchs/helpline -name "*.log.gz" -mtime +90 -delete

# Security logs: 1 year
find /var/log/openchs/helpline -name "security*.log.gz" -mtime +365 -delete

# Audit logs: 7 years (in database)
mysql helpline -e "
    DELETE FROM audit_log 
    WHERE timestamp < DATE_SUB(NOW(), INTERVAL 7 YEAR);
"

# Nginx logs: 30 days
find /var/log/nginx -name "*.log.gz" -mtime +30 -delete

echo "Retention policy enforced: $(date)" >> /var/log/openchs/retention.log
```

Schedule monthly:
```bash
# Add to crontab
0 3 1 * * /usr/local/bin/enforce-retention-policy.sh
```

---

## Next Steps

After setting up logging and auditing:

1. **Plan System Upgrades**: See [Upgrading OpenCHS](upgrading-openchs.md)
2. **Review Health Checks**: See [System Health Checks](system-health-checks.md)
3. **Optimize Performance**: See [Performance Tuning](performance-tuning.md)

---

## Quick Reference

### Common Log Locations

```bash
# Application Logs
/var/log/openchs/helpline/application.log
/var/log/openchs/helpline/security.log
/var/log/openchs/helpline/audit.log
/var/log/openchs/ai-service/application.log
/var/log/openchs/ai-service/error.log

# System Logs
/var/log/nginx/openchs-access.log
/var/log/nginx/openchs-error.log
/var/log/mysql/error.log
/var/log/mysql/slow-query.log
/var/log/redis/redis-server.log

# Service Logs (systemd)
journalctl -u nginx
journalctl -u php8.2-fpm
journalctl -u mysql
journalctl -u openchs-ai-api
journalctl -u openchs-ai-worker
```

### Log Commands

```bash
# Tail multiple logs
tail -f /var/log/openchs/*/*.log

# Search for errors
grep -r "ERROR" /var/log/openchs/

# Count errors by type
grep "ERROR" /var/log/openchs/helpline/application.log | awk '{print $3}' | sort | uniq -c

# View recent audit entries
mysql helpline -e "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 20;"

# Export logs for analysis
tar -czf openchs-logs-$(date +%Y%m%d).tar.gz /var/log/openchs/
```