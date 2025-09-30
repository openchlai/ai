# System Health Checks

## Overview

This guide covers comprehensive health monitoring for OpenCHS, including automated checks, monitoring tools, alerting systems, and troubleshooting procedures.

---

## Table of Contents

1. [Health Check Strategy](#health-check-strategy)
2. [Automated Health Checks](#automated-health-checks)
3. [Service Monitoring](#service-monitoring)
4. [Performance Metrics](#performance-metrics)
5. [Alerting Configuration](#alerting-configuration)
6. [Dashboard Setup](#dashboard-setup)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Health Check Strategy

### Monitoring Levels

| Level | Check Frequency | Response Time | Examples |
|-------|----------------|---------------|----------|
| **Critical** | Every 1 minute | Immediate | Service down, database unavailable |
| **Warning** | Every 5 minutes | 15 minutes | High CPU, disk space low |
| **Info** | Every 15 minutes | 1 hour | Queue buildup, slow queries |

### Key Metrics to Monitor

- **System Resources**: CPU, RAM, Disk, Network
- **Services**: Nginx, PHP-FPM, MySQL, Redis, AI Service
- **Application**: Response time, error rates, queue length
- **Database**: Connection count, slow queries, replication lag
- **AI Service**: GPU utilization, model status, processing queue

---

## Automated Health Checks

### Master Health Check Script

```bash
#!/bin/bash
# /usr/local/bin/openchs-health-check.sh

set -e

LOG_FILE="/var/log/openchs/health-check.log"
STATUS_FILE="/var/run/openchs-health-status.json"
ALERT_EMAIL="admin@yourdomain.com"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Status tracking
OVERALL_STATUS="OK"
ISSUES=()

# Initialize status JSON
echo "{\"timestamp\": \"$(date -Iseconds)\", \"checks\": {" > "$STATUS_FILE"

##############################################
# SYSTEM RESOURCE CHECKS
##############################################

log "Starting system health checks..."

# Check CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo -e "${RED}✗ CPU usage critical: ${CPU_USAGE}%${NC}"
    ISSUES+=("CPU usage high: ${CPU_USAGE}%")
    OVERALL_STATUS="WARNING"
else
    echo -e "${GREEN}✓ CPU usage normal: ${CPU_USAGE}%${NC}"
fi
echo "\"cpu\": {\"status\": \"$([[ ${#ISSUES[@]} -eq 0 ]] && echo OK || echo WARNING)\", \"usage\": $CPU_USAGE}," >> "$STATUS_FILE"

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
    echo -e "${RED}✗ Memory usage critical: ${MEM_USAGE}%${NC}"
    ISSUES+=("Memory usage high: ${MEM_USAGE}%")
    OVERALL_STATUS="WARNING"
else
    echo -e "${GREEN}✓ Memory usage normal: ${MEM_USAGE}%${NC}"
fi
echo "\"memory\": {\"status\": \"$([[ ${#ISSUES[@]} -eq 0 ]] && echo OK || echo WARNING)\", \"usage\": $MEM_USAGE}," >> "$STATUS_FILE"

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ "$DISK_USAGE" -gt 85 ]; then
    echo -e "${RED}✗ Disk usage critical: ${DISK_USAGE}%${NC}"
    ISSUES+=("Disk usage high: ${DISK_USAGE}%")
    OVERALL_STATUS="WARNING"
else
    echo -e "${GREEN}✓ Disk usage normal: ${DISK_USAGE}%${NC}"
fi
echo "\"disk\": {\"status\": \"$([[ $DISK_USAGE -gt 85 ]] && echo WARNING || echo OK)\", \"usage\": $DISK_USAGE}," >> "$STATUS_FILE"

##############################################
# SERVICE CHECKS
##############################################

log "Checking services status..."

# Function to check service
check_service() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✓ $service is running${NC}"
        echo "\"$service\": {\"status\": \"running\"}," >> "$STATUS_FILE"
    else
        echo -e "${RED}✗ $service is not running${NC}"
        ISSUES+=("$service is down")
        OVERALL_STATUS="CRITICAL"
        echo "\"$service\": {\"status\": \"down\"}," >> "$STATUS_FILE"
    fi
}

check_service "nginx"
check_service "php8.2-fpm"
check_service "mysql"
check_service "redis-server"
check_service "openchs-ai-api"
check_service "openchs-ai-worker"

##############################################
# APPLICATION CHECKS
##############################################

log "Checking application health..."

# Check Nginx response
if curl -f -s -o /dev/null -w "%{http_code}" https://helpline.yourdomain.com/helpline/ | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✓ Helpline web application is accessible${NC}"
    echo "\"helpline_web\": {\"status\": \"accessible\"}," >> "$STATUS_FILE"
else
    echo -e "${RED}✗ Helpline web application is not accessible${NC}"
    ISSUES+=("Helpline web not accessible")
    OVERALL_STATUS="CRITICAL"
    echo "\"helpline_web\": {\"status\": \"inaccessible\"}," >> "$STATUS_FILE"
fi

# Check AI Service API
AI_HEALTH=$(curl -f -s http://localhost:8123/health 2>/dev/null || echo "ERROR")
if echo "$AI_HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ AI Service API is healthy${NC}"
    echo "\"ai_service\": {\"status\": \"healthy\"}," >> "$STATUS_FILE"
else
    echo -e "${RED}✗ AI Service API is not healthy${NC}"
    ISSUES+=("AI Service API unhealthy")
    OVERALL_STATUS="CRITICAL"
    echo "\"ai_service\": {\"status\": \"unhealthy\"}," >> "$STATUS_FILE"
fi

##############################################
# DATABASE CHECKS
##############################################

log "Checking database health..."

# Check MySQL connection
if mysql -e "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MySQL is accessible${NC}"
    
    # Check database size
    DB_SIZE=$(mysql -N -e "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) FROM information_schema.tables WHERE table_schema='helpline';")
    echo "  Database size: ${DB_SIZE} MB"
    
    # Check connection count
    CONN_COUNT=$(mysql -N -e "SHOW STATUS LIKE 'Threads_connected';" | awk '{print $2}')
    MAX_CONN=$(mysql -N -e "SHOW VARIABLES LIKE 'max_connections';" | awk '{print $2}')
    CONN_PCT=$(echo "scale=2; $CONN_COUNT / $MAX_CONN * 100" | bc)
    echo "  Connections: $CONN_COUNT / $MAX_CONN (${CONN_PCT}%)"
    
    if (( $(echo "$CONN_PCT > 80" | bc -l) )); then
        echo -e "${YELLOW}⚠ High connection usage${NC}"
        ISSUES+=("MySQL connections high: ${CONN_PCT}%")
        [ "$OVERALL_STATUS" = "OK" ] && OVERALL_STATUS="WARNING"
    fi
    
    echo "\"mysql\": {\"status\": \"accessible\", \"size_mb\": $DB_SIZE, \"connections\": $CONN_COUNT, \"max_connections\": $MAX_CONN}," >> "$STATUS_FILE"
else
    echo -e "${RED}✗ MySQL is not accessible${NC}"
    ISSUES+=("MySQL not accessible")
    OVERALL_STATUS="CRITICAL"
    echo "\"mysql\": {\"status\": \"inaccessible\"}," >> "$STATUS_FILE"
fi

##############################################
# REDIS CHECKS
##############################################

log "Checking Redis health..."

if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is accessible${NC}"
    
    # Get Redis info
    REDIS_MEM=$(redis-cli INFO memory | grep "used_memory_human" | cut -d':' -f2 | tr -d '\r')
    REDIS_KEYS=$(redis-cli DBSIZE | awk '{print $2}')
    echo "  Memory used: $REDIS_MEM"
    echo "  Keys: $REDIS_KEYS"
    
    echo "\"redis\": {\"status\": \"accessible\", \"memory\": \"$REDIS_MEM\", \"keys\": $REDIS_KEYS}," >> "$STATUS_FILE"
else
    echo -e "${RED}✗ Redis is not accessible${NC}"
    ISSUES+=("Redis not accessible")
    OVERALL_STATUS="CRITICAL"
    echo "\"redis\": {\"status\": \"inaccessible\"}," >> "$STATUS_FILE"
fi

##############################################
# AI SERVICE DETAILED CHECKS
##############################################

log "Checking AI Service details..."

# Check Celery workers
CELERY_WORKERS=$(curl -s http://localhost:8123/audio/workers/status 2>/dev/null | grep -o '"active":[0-9]*' | cut -d':' -f2 || echo "0")
if [ "$CELERY_WORKERS" -gt 0 ]; then
    echo -e "${GREEN}✓ Celery workers active: $CELERY_WORKERS${NC}"
    echo "\"celery\": {\"status\": \"active\", \"workers\": $CELERY_WORKERS}," >> "$STATUS_FILE"
else
    echo -e "${YELLOW}⚠ No active Celery workers${NC}"
    [ "$OVERALL_STATUS" = "OK" ] && OVERALL_STATUS="WARNING"
    echo "\"celery\": {\"status\": \"no_workers\", \"workers\": 0}," >> "$STATUS_FILE"
fi

# Check GPU status (if available)
if command -v nvidia-smi &> /dev/null; then
    GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1)
    GPU_MEM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | head -1)
    
    echo "  GPU Utilization: ${GPU_UTIL}%"
    echo "  GPU Memory: ${GPU_MEM} MB"
    echo "  GPU Temperature: ${GPU_TEMP}°C"
    
    if [ "$GPU_TEMP" -gt 85 ]; then
        echo -e "${YELLOW}⚠ GPU temperature high${NC}"
        ISSUES+=("GPU temperature high: ${GPU_TEMP}°C")
        [ "$OVERALL_STATUS" = "OK" ] && OVERALL_STATUS="WARNING"
    fi
    
    echo "\"gpu\": {\"status\": \"available\", \"utilization\": $GPU_UTIL, \"memory_mb\": $GPU_MEM, \"temperature\": $GPU_TEMP}," >> "$STATUS_FILE"
else
    echo "\"gpu\": {\"status\": \"not_available\"}," >> "$STATUS_FILE"
fi

##############################################
# FINALIZE STATUS
##############################################

# Remove trailing comma and close JSON
sed -i '$ s/,$//' "$STATUS_FILE"
echo "}, \"overall_status\": \"$OVERALL_STATUS\", \"issues\": [" >> "$STATUS_FILE"

for issue in "${ISSUES[@]}"; do
    echo "\"$issue\"," >> "$STATUS_FILE"
done

sed -i '$ s/,$//' "$STATUS_FILE"
echo "]}" >> "$STATUS_FILE"

##############################################
# SUMMARY AND ALERTS
##############################################

log "Health check completed. Overall status: $OVERALL_STATUS"

# Send alert if issues detected
if [ ${#ISSUES[@]} -gt 0 ]; then
    ALERT_SUBJECT="[OpenCHS] Health Check Alert - $OVERALL_STATUS"
    ALERT_BODY="Health check detected ${#ISSUES[@]} issue(s):\n\n"
    for issue in "${ISSUES[@]}"; do
        ALERT_BODY+="- $issue\n"
    done
    ALERT_BODY+="\nTimestamp: $(date)\n"
    ALERT_BODY+="\nFull report: $LOG_FILE"
    
    echo -e "$ALERT_BODY" | mail -s "$ALERT_SUBJECT" "$ALERT_EMAIL"
    log "Alert email sent to $ALERT_EMAIL"
fi

# Exit with appropriate code
[ "$OVERALL_STATUS" = "CRITICAL" ] && exit 2
[ "$OVERALL_STATUS" = "WARNING" ] && exit 1
exit 0
```

Make script executable:

```bash
chmod +x /usr/local/bin/openchs-health-check.sh
```

### Schedule Health Checks

```bash
# Add to crontab
crontab -e

# Run health check every 5 minutes
*/5 * * * * /usr/local/bin/openchs-health-check.sh >> /var/log/openchs/health-check-cron.log 2>&1
```

---

## Service Monitoring

### Individual Service Health Scripts

#### Helpline API Health Check

```bash
#!/bin/bash
# /usr/local/bin/check-helpline-api.sh

API_URL="https://helpline.yourdomain.com/helpline/api/health"
TIMEOUT=10

RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/api_response.txt --max-time $TIMEOUT "$API_URL")
HTTP_CODE="${RESPONSE: -3}"

if [ "$HTTP_CODE" = "200" ]; then
    echo "OK: Helpline API is healthy"
    exit 0
else
    echo "CRITICAL: Helpline API returned HTTP $HTTP_CODE"
    exit 2
fi
```

#### AI Service Health Check

```bash
#!/bin/bash
# /usr/local/bin/check-ai-service.sh

AI_URL="http://localhost:8123/health/detailed"
TIMEOUT=10

RESPONSE=$(curl -s --max-time $TIMEOUT "$AI_URL")

if echo "$RESPONSE" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    MODELS_STATUS=$(echo "$RESPONSE" | jq -r '.models_loaded')
    QUEUE_SIZE=$(echo "$RESPONSE" | jq -r '.queue.current_size')
    
    echo "OK: AI Service healthy | models=$MODELS_STATUS queue=$QUEUE_SIZE"
    exit 0
else
    echo "CRITICAL: AI Service unhealthy"
    exit 2
fi
```

### Database Health Monitoring

```bash
#!/bin/bash
# /usr/local/bin/check-database.sh

# Check connection
if ! mysql -e "SELECT 1" > /dev/null 2>&1; then
    echo "CRITICAL: Cannot connect to MySQL"
    exit 2
fi

# Check slow queries
SLOW_QUERIES=$(mysql -N -e "SHOW GLOBAL STATUS LIKE 'Slow_queries';" | awk '{print $2}')
echo "MySQL slow queries: $SLOW_QUERIES"

# Check replication (if configured)
SLAVE_STATUS=$(mysql -e "SHOW SLAVE STATUS\G" 2>/dev/null)
if [ -n "$SLAVE_STATUS" ]; then
    IO_RUNNING=$(echo "$SLAVE_STATUS" | grep "Slave_IO_Running" | awk '{print $2}')
    SQL_RUNNING=$(echo "$SLAVE_STATUS" | grep "Slave_SQL_Running" | awk '{print $2}')
    
    if [ "$IO_RUNNING" != "Yes" ] || [ "$SQL_RUNNING" != "Yes" ]; then
        echo "CRITICAL: MySQL replication not running"
        exit 2
    fi
fi

# Check table status
CRASHED_TABLES=$(mysql -N -e "
    SELECT COUNT(*) 
    FROM information_schema.tables 
    WHERE table_schema='helpline' 
    AND engine='MyISAM' 
    AND (data_length=0 OR index_length=0)
")

if [ "$CRASHED_TABLES" -gt 0 ]; then
    echo "WARNING: $CRASHED_TABLES crashed tables detected"
    exit 1
fi

echo "OK: Database is healthy"
exit 0
```

---

## Performance Metrics

### Application Performance Monitoring

```bash
#!/bin/bash
# /usr/local/bin/collect-performance-metrics.sh

METRICS_FILE="/var/log/openchs/metrics/$(date +%Y-%m-%d).metrics"
mkdir -p /var/log/openchs/metrics

# Timestamp
echo "[$(date -Iseconds)]" >> "$METRICS_FILE"

# System metrics
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')" >> "$METRICS_FILE"
echo "Memory: $(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')%" >> "$METRICS_FILE"
echo "Disk: $(df -h / | awk 'NR==2 {print $5}')" >> "$METRICS_FILE"

# Service metrics
echo "Nginx connections: $(ss -tan | grep :443 | wc -l)" >> "$METRICS_FILE"
echo "PHP-FPM processes: $(ps aux | grep php-fpm | wc -l)" >> "$METRICS_FILE"
echo "MySQL connections: $(mysql -N -e 'SHOW STATUS LIKE "Threads_connected";' | awk '{print $2}')" >> "$METRICS_FILE"

# Application metrics
ACTIVE_CASES=$(mysql -N helpline -e "SELECT COUNT(*) FROM kase WHERE status='open';")
echo "Active cases: $ACTIVE_CASES" >> "$METRICS_FILE"

QUEUE_SIZE=$(curl -s http://localhost:8123/audio/queue/status 2>/dev/null | jq -r '.queue_size' || echo "N/A")
echo "AI queue size: $QUEUE_SIZE" >> "$METRICS_FILE"

echo "---" >> "$METRICS_FILE"
```

### Response Time Monitoring

```bash
#!/bin/bash
# /usr/local/bin/check-response-time.sh

ENDPOINTS=(
    "https://helpline.yourdomain.com/helpline/"
    "https://helpline.yourdomain.com/helpline/api/health"
    "http://localhost:8123/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' "$endpoint")
    RESPONSE_CODE=$(curl -o /dev/null -s -w '%{http_code}\n' "$endpoint")
    
    echo "Endpoint: $endpoint"
    echo "  Response time: ${RESPONSE_TIME}s"
    echo "  HTTP code: $RESPONSE_CODE"
    
    # Alert if response time > 5 seconds
    if (( $(echo "$RESPONSE_TIME > 5.0" | bc -l) )); then
        echo "  WARNING: Slow response time"
    fi
    echo ""
done
```

---

## Alerting Configuration

### Email Alerting Setup

```bash
# Install mail utilities
sudo apt-get install -y mailutils

# Configure postfix or use external SMTP
sudo dpkg-reconfigure postfix
```

**SMTP Configuration: `/etc/postfix/main.cf`**

```conf
relayhost = [smtp.gmail.com]:587
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymity
smtp_tls_security_level = encrypt
```

**Create SMTP credentials: `/etc/postfix/sasl_passwd`**

```
[smtp.gmail.com]:587 your-email@gmail.com:your-app-password
```

```bash
sudo postmap /etc/postfix/sasl_passwd
sudo chmod 600 /etc/postfix/sasl_passwd
sudo systemctl restart postfix
```

### Alert Script

```bash
#!/bin/bash
# /usr/local/bin/send-alert.sh

ALERT_TYPE=$1  # critical, warning, info
MESSAGE=$2
RECIPIENT="admin@yourdomain.com"

SUBJECT="[OpenCHS Alert] $ALERT_TYPE: $(hostname)"

case $ALERT_TYPE in
    critical)
        PRIORITY="1"
        ;;
    warning)
        PRIORITY="3"
        ;;
    *)
        PRIORITY="5"
        ;;
esac

echo "$MESSAGE" | mail -s "$SUBJECT" -a "X-Priority: $PRIORITY" "$RECIPIENT"
```

### Slack Integration (Optional)

```bash
#!/bin/bash
# /usr/local/bin/send-slack-alert.sh

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
MESSAGE=$1
CHANNEL="#openchs-alerts"

curl -X POST "$WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    -d "{
        \"channel\": \"$CHANNEL\",
        \"username\": \"OpenCHS Monitor\",
        \"text\": \"$MESSAGE\",
        \"icon_emoji\": \":warning:\"
    }"
```

---

## Dashboard Setup

### Simple Status Dashboard

Create a simple status page:

**`/var/www/html/status/index.php`**

```php
<!DOCTYPE html>
<html>
<head>
    <title>OpenCHS System Status</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .status-ok { color: green; }
        .status-warning { color: orange; }
        .status-critical { color: red; }
        .metric { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>OpenCHS System Status</h1>
    <p>Last updated: <?php echo date('Y-m-d H:i:s'); ?></p>
    
    <?php
    $statusFile = '/var/run/openchs-health-status.json';
    if (file_exists($statusFile)) {
        $status = json_decode(file_get_contents($statusFile), true);
        $overallStatus = $status['overall_status'] ?? 'UNKNOWN';
        $statusClass = $overallStatus == 'OK' ? 'status-ok' : ($overallStatus == 'WARNING' ? 'status-warning' : 'status-critical');
        
        echo "<h2 class='$statusClass'>Overall Status: $overallStatus</h2>";
        
        if (!empty($status['issues'])) {
            echo "<h3>Issues:</h3><ul>";
            foreach ($status['issues'] as $issue) {
                echo "<li>$issue</li>";
            }
            echo "</ul>";
        }
        
        echo "<h3>Service Status:</h3>";
        foreach ($status['checks'] as $check => $data) {
            $checkStatus = $data['status'] ?? 'unknown';
            $checkClass = $checkStatus == 'running' || $checkStatus == 'accessible' || $checkStatus == 'healthy' || $checkStatus == 'OK' 
                ? 'status-ok' : 'status-warning';
            echo "<div class='metric'><strong>$check:</strong> <span class='$checkClass'>$checkStatus</span>";
            if (isset($data['usage'])) {
                echo " ($data[usage]%)";
            }
            echo "</div>";
        }
    } else {
        echo "<p class='status-critical'>Status file not found. Health checks may not be running.</p>";
    }
    ?>
</body>
</html>
```

---

## Troubleshooting Common Issues

### High CPU Usage

```bash
# Identify process causing high CPU
top -b -n 1 | head -20

# Check specific service
ps aux | grep -E 'nginx|php-fpm|mysql|python' | sort -nrk 3 | head -10

# Solution: Restart service or scale resources
sudo systemctl restart php8.2-fpm
```

### High Memory Usage

```bash
# Check memory consumers
ps aux --sort=-%mem | head -10

# Clear cache
sync; echo 3 > /proc/sys/vm/drop_caches

# Check for memory leaks in AI service
ps aux | grep python | awk '{print $6, $11}'
```

### Database Connection Errors

```bash
# Check MySQL status
sudo systemctl status mysql

# Check connection limit
mysql -e "SHOW VARIABLES LIKE 'max_connections';"
mysql -e "SHOW STATUS LIKE 'Threads_connected';"

# Kill stuck connections
mysql -e "SHOW PROCESSLIST;" | grep "Sleep" | awk '{print $1}' | xargs -I {} mysql -e "KILL {};"
```

### Slow Response Times

```bash
# Check Nginx access log for slow requests
awk '{print $NF}' /var/log/nginx/openchs-access.log | sort -n | tail -20

# Check MySQL slow query log
mysql -e "SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;"

# Check PHP-FPM status
curl http://localhost/status?full
```

---

## Next Steps

After setting up health checks:

1. **Configure Performance Tuning**: See [Performance Tuning](performance-tuning.md)
2. **Set Up Logging**: See [Logging & Auditing](logging-auditing.md)
3. **Plan Upgrades**: See [Upgrading OpenCHS](upgrading-openchs.md)

---

## Quick Reference

### Health Check Commands

```bash
# Run manual health check
/usr/local/bin/openchs-health-check.sh

# View health status
cat /var/run/openchs-health-status.json | jq .

# Check all services
systemctl status nginx php8.2-fpm mysql redis-server openchs-ai-api openchs-ai-worker

# View recent health check logs
tail -f /var/log/openchs/health-check.log

# Test email alerts
echo "Test alert" | mail -s "OpenCHS Test Alert" admin@yourdomain.com
```