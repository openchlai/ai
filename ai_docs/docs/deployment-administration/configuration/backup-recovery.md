# Backup & Recovery

## Overview

This guide covers comprehensive backup and disaster recovery strategies for OpenCHS, including database backups, configuration backups, and complete system restoration procedures.

---

## Table of Contents

1. [Backup Strategy](#backup-strategy)
2. [Database Backups](#database-backups)
3. [Application Backups](#application-backups)
4. [AI Service Backups](#ai-service-backups)
5. [Automated Backup Scripts](#automated-backup-scripts)
6. [Restoration Procedures](#restoration-procedures)
7. [Disaster Recovery Plan](#disaster-recovery-plan)

---

## Backup Strategy

### Backup Types

| Type | Frequency | Retention | Purpose |
|------|-----------|-----------|---------|
| **Full Backup** | Weekly | 4 weeks | Complete system state |
| **Incremental Backup** | Daily | 7 days | Daily changes only |
| **Transaction Logs** | Hourly | 24 hours | Point-in-time recovery |
| **Configuration** | On change | 30 days | System settings |
| **AI Models** | On update | 2 versions | Model files |

### Backup Locations

```bash
# Primary backup location
/backup/openchs/

# Structure
/backup/openchs/
├── daily/
│   ├── 2024-01-15/
│   ├── 2024-01-16/
│   └── 2024-01-17/
├── weekly/
│   ├── week-01/
│   └── week-02/
├── monthly/
│   ├── 2024-01/
│   └── 2024-02/
└── offsite/
    └── synced-to-remote/
```

### 3-2-1 Backup Rule

- **3** copies of data
- **2** different storage media
- **1** copy offsite

```bash
# Implementation
1. Primary: Live database
2. Secondary: Local backup server
3. Tertiary: Remote/cloud storage
```

---

## Database Backups

### MySQL Full Backup

```bash
#!/bin/bash
# /usr/local/bin/backup-mysql-full.sh

# Configuration
BACKUP_DIR="/backup/openchs/mysql"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
DB_NAME="helpline"
DB_USER="root"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR/daily"

# Perform backup
mysqldump \
    --user="$DB_USER" \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --hex-blob \
    --databases "$DB_NAME" \
    --result-file="$BACKUP_DIR/daily/${DB_NAME}_${DATE}.sql"

# Compress backup
gzip "$BACKUP_DIR/daily/${DB_NAME}_${DATE}.sql"

# Calculate checksum
sha256sum "$BACKUP_DIR/daily/${DB_NAME}_${DATE}.sql.gz" > "$BACKUP_DIR/daily/${DB_NAME}_${DATE}.sql.gz.sha256"

# Remove old backups
find "$BACKUP_DIR/daily" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/daily" -name "*.sha256" -mtime +$RETENTION_DAYS -delete

# Log completion
echo "[$(date)] Database backup completed: ${DB_NAME}_${DATE}.sql.gz" >> /var/log/openchs/backup.log

# Verify backup integrity
if gunzip -t "$BACKUP_DIR/daily/${DB_NAME}_${DATE}.sql.gz" 2>/dev/null; then
    echo "[$(date)] Backup verification successful" >> /var/log/openchs/backup.log
else
    echo "[$(date)] ERROR: Backup verification failed!" >> /var/log/openchs/backup.log
    # Send alert email
    mail -s "ALERT: OpenCHS Backup Failed" admin@yourdomain.com < /dev/null
fi
```

### MySQL Incremental Backup

Enable binary logging for point-in-time recovery:

```bash
# MySQL configuration (/etc/mysql/mysql.conf.d/mysqld.cnf)
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
binlog_format = ROW
expire_logs_days = 7
max_binlog_size = 100M
```

**Backup binary logs:**

```bash
#!/bin/bash
# /usr/local/bin/backup-mysql-binlog.sh

BACKUP_DIR="/backup/openchs/mysql/binlog"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

mkdir -p "$BACKUP_DIR"

# Flush logs to start new binlog file
mysql -e "FLUSH LOGS;"

# Copy all binlog files except the current one
for binlog in $(mysql -N -e "SHOW BINARY LOGS;" | awk '{print $1}' | head -n -1); do
    if [ ! -f "$BACKUP_DIR/$binlog" ]; then
        cp "/var/log/mysql/$binlog" "$BACKUP_DIR/"
        gzip "$BACKUP_DIR/$binlog"
        echo "[$(date)] Backed up binlog: $binlog" >> /var/log/openchs/backup.log
    fi
done
```

### Specific Table Backups

```bash
# Backup specific critical tables
mysqldump \
    --user=root \
    --single-transaction \
    helpline \
    kase kase_activity contact disposition \
    > /backup/openchs/mysql/critical_tables_$(date +%Y-%m-%d).sql
```

---

## Application Backups

### Helpline System Application Backup

```bash
#!/bin/bash
# /usr/local/bin/backup-helpline-app.sh

BACKUP_DIR="/backup/openchs/application"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
APP_DIR="/var/www/html/helpline"

mkdir -p "$BACKUP_DIR"

# Backup application files
tar -czf "$BACKUP_DIR/helpline_app_${DATE}.tar.gz" \
    --exclude='*.log' \
    --exclude='cache/*' \
    --exclude='temp/*' \
    -C "$(dirname $APP_DIR)" \
    "$(basename $APP_DIR)"

# Backup configuration files
mkdir -p "$BACKUP_DIR/config"
cp -r /etc/nginx/sites-available/openchs "$BACKUP_DIR/config/nginx_${DATE}.conf"
cp -r /etc/php/8.2/fpm/pool.d/www.conf "$BACKUP_DIR/config/php-fpm_${DATE}.conf"
cp "$APP_DIR/.env" "$BACKUP_DIR/config/env_${DATE}"

# Backup uploads directory (if storing files locally)
if [ -d "$APP_DIR/storage/uploads" ]; then
    tar -czf "$BACKUP_DIR/uploads_${DATE}.tar.gz" \
        -C "$APP_DIR/storage" uploads
fi

echo "[$(date)] Application backup completed" >> /var/log/openchs/backup.log
```

### Configuration Backup

```bash
#!/bin/bash
# /usr/local/bin/backup-configs.sh

BACKUP_DIR="/backup/openchs/config"
DATE=$(date +%Y-%m-%d)

mkdir -p "$BACKUP_DIR/$DATE"

# System configurations
cp /etc/nginx/nginx.conf "$BACKUP_DIR/$DATE/"
cp /etc/nginx/sites-available/* "$BACKUP_DIR/$DATE/"
cp /etc/php/8.2/fpm/php-fpm.conf "$BACKUP_DIR/$DATE/"
cp /etc/php/8.2/fpm/pool.d/www.conf "$BACKUP_DIR/$DATE/"
cp /etc/mysql/mysql.conf.d/mysqld.cnf "$BACKUP_DIR/$DATE/"
cp /etc/redis/redis.conf "$BACKUP_DIR/$DATE/"

# Application configurations
cp /var/www/html/helpline/.env "$BACKUP_DIR/$DATE/helpline.env"
cp /opt/openchs-ai/.env "$BACKUP_DIR/$DATE/ai-service.env"

# SSL certificates
mkdir -p "$BACKUP_DIR/$DATE/ssl"
cp -r /etc/pki/openchs/* "$BACKUP_DIR/$DATE/ssl/" 2>/dev/null || true
cp -r /etc/letsencrypt/live/* "$BACKUP_DIR/$DATE/ssl/" 2>/dev/null || true

# Create archive
tar -czf "$BACKUP_DIR/config_${DATE}.tar.gz" -C "$BACKUP_DIR" "$DATE"
rm -rf "$BACKUP_DIR/$DATE"

echo "[$(date)] Configuration backup completed" >> /var/log/openchs/backup.log
```

---

## AI Service Backups

### AI Models Backup

```bash
#!/bin/bash
# /usr/local/bin/backup-ai-models.sh

BACKUP_DIR="/backup/openchs/ai-models"
DATE=$(date +%Y-%m-%d)
MODELS_DIR="/opt/openchs-ai/models"

mkdir -p "$BACKUP_DIR"

# Only backup if models have changed
CURRENT_HASH=$(find "$MODELS_DIR" -type f -exec md5sum {} \; | sort | md5sum | cut -d' ' -f1)
LAST_HASH_FILE="$BACKUP_DIR/.last_backup_hash"

if [ -f "$LAST_HASH_FILE" ]; then
    LAST_HASH=$(cat "$LAST_HASH_FILE")
else
    LAST_HASH=""
fi

if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
    echo "[$(date)] Models changed, creating backup..." >> /var/log/openchs/backup.log
    
    # Backup models
    tar -czf "$BACKUP_DIR/models_${DATE}.tar.gz" \
        -C "$(dirname $MODELS_DIR)" \
        "$(basename $MODELS_DIR)"
    
    # Save current hash
    echo "$CURRENT_HASH" > "$LAST_HASH_FILE"
    
    # Keep only last 2 model backups (they're large)
    ls -t "$BACKUP_DIR"/models_*.tar.gz | tail -n +3 | xargs -r rm
    
    echo "[$(date)] AI models backup completed" >> /var/log/openchs/backup.log
else
    echo "[$(date)] No changes in AI models, skipping backup" >> /var/log/openchs/backup.log
fi
```

### AI Service Data Backup

```bash
#!/bin/bash
# /usr/local/bin/backup-ai-data.sh

BACKUP_DIR="/backup/openchs/ai-data"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

mkdir -p "$BACKUP_DIR"

# Backup Redis data
redis-cli --rdb "$BACKUP_DIR/redis_${DATE}.rdb"
gzip "$BACKUP_DIR/redis_${DATE}.rdb"

# Backup logs
tar -czf "$BACKUP_DIR/logs_${DATE}.tar.gz" \
    /var/log/openchs/ \
    /opt/openchs-ai/logs/

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "redis_*.rdb.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "logs_*.tar.gz" -mtime +7 -delete

echo "[$(date)] AI service data backup completed" >> /var/log/openchs/backup.log
```

---

## Automated Backup Scripts

### Master Backup Script

```bash
#!/bin/bash
# /usr/local/bin/openchs-backup-all.sh

echo "========================================="
echo "OpenCHS Backup Started: $(date)"
echo "========================================="

# Run all backup scripts
/usr/local/bin/backup-mysql-full.sh
/usr/local/bin/backup-mysql-binlog.sh
/usr/local/bin/backup-helpline-app.sh
/usr/local/bin/backup-configs.sh
/usr/local/bin/backup-ai-models.sh
/usr/local/bin/backup-ai-data.sh

# Sync to offsite storage
/usr/local/bin/sync-to-offsite.sh

echo "========================================="
echo "OpenCHS Backup Completed: $(date)"
echo "========================================="

# Send summary email
SUMMARY="/tmp/backup-summary.txt"
echo "OpenCHS Backup Summary - $(date)" > "$SUMMARY"
echo "" >> "$SUMMARY"
echo "Backup Location: /backup/openchs/" >> "$SUMMARY"
echo "Disk Usage:" >> "$SUMMARY"
du -sh /backup/openchs/* >> "$SUMMARY"
echo "" >> "$SUMMARY"
echo "Recent Backups:" >> "$SUMMARY"
find /backup/openchs -name "*.gz" -mtime -1 -ls | awk '{print $11, $7}' >> "$SUMMARY"

mail -s "OpenCHS Backup Summary - $(date +%Y-%m-%d)" admin@yourdomain.com < "$SUMMARY"
rm "$SUMMARY"
```

### Offsite Sync Script

```bash
#!/bin/bash
# /usr/local/bin/sync-to-offsite.sh

BACKUP_DIR="/backup/openchs"
REMOTE_SERVER="backup@remote-server.com"
REMOTE_DIR="/backups/openchs"

# Sync to remote server using rsync
rsync -avz --delete \
    --exclude '*.tmp' \
    --exclude '*.log' \
    -e "ssh -i /root/.ssh/backup_key" \
    "$BACKUP_DIR/" \
    "$REMOTE_SERVER:$REMOTE_DIR/"

if [ $? -eq 0 ]; then
    echo "[$(date)] Offsite sync completed successfully" >> /var/log/openchs/backup.log
else
    echo "[$(date)] ERROR: Offsite sync failed!" >> /var/log/openchs/backup.log
    mail -s "ALERT: OpenCHS Offsite Backup Failed" admin@yourdomain.com < /dev/null
fi
```

### Cron Schedule

```bash
# Edit crontab
sudo crontab -e

# Add backup schedules
# Full backup daily at 2 AM
0 2 * * * /usr/local/bin/openchs-backup-all.sh >> /var/log/openchs/backup-cron.log 2>&1

# Binary log backup every 6 hours
0 */6 * * * /usr/local/bin/backup-mysql-binlog.sh >> /var/log/openchs/backup-cron.log 2>&1

# Configuration backup on changes (or daily)
0 3 * * * /usr/local/bin/backup-configs.sh >> /var/log/openchs/backup-cron.log 2>&1

# Offsite sync twice daily
0 4,16 * * * /usr/local/bin/sync-to-offsite.sh >> /var/log/openchs/backup-cron.log 2>&1
```

---

## Restoration Procedures

### Database Restoration

#### Full Database Restore

```bash
#!/bin/bash
# Restore from full backup

BACKUP_FILE="/backup/openchs/mysql/daily/helpline_2024-01-15_02-00-00.sql.gz"

# Stop application services
sudo systemctl stop nginx php8.2-fpm openchs-ai-api openchs-ai-worker

# Verify backup integrity
if ! gunzip -t "$BACKUP_FILE"; then
    echo "ERROR: Backup file is corrupted!"
    exit 1
fi

# Create restoration point
mysqldump --user=root --single-transaction helpline > /tmp/pre-restore-backup.sql

# Restore database
gunzip < "$BACKUP_FILE" | mysql --user=root

# Verify restoration
if mysql -e "USE helpline; SELECT COUNT(*) FROM kase;" > /dev/null 2>&1; then
    echo "Database restoration successful"
    # Start services
    sudo systemctl start php8.2-fpm nginx openchs-ai-api openchs-ai-worker
else
    echo "ERROR: Database restoration failed!"
    echo "Restoring from pre-restore backup..."
    mysql --user=root helpline < /tmp/pre-restore-backup.sql
fi
```

#### Point-in-Time Recovery

```bash
#!/bin/bash
# Restore to specific point in time using binary logs

FULL_BACKUP="/backup/openchs/mysql/daily/helpline_2024-01-15_02-00-00.sql.gz"
BINLOG_DIR="/backup/openchs/mysql/binlog"
STOP_DATETIME="2024-01-15 14:30:00"

# Stop services
sudo systemctl stop nginx php8.2-fpm openchs-ai-api openchs-ai-worker

# Restore full backup
gunzip < "$FULL_BACKUP" | mysql --user=root

# Apply binary logs up to specific time
for binlog in $(ls $BINLOG_DIR/mysql-bin.* | sort); do
    mysqlbinlog --stop-datetime="$STOP_DATETIME" "$binlog" | mysql --user=root
done

echo "Point-in-time recovery completed to: $STOP_DATETIME"

# Start services
sudo systemctl start php8.2-fpm nginx openchs-ai-api openchs-ai-worker
```

### Application Restoration

```bash
#!/bin/bash
# Restore application files

BACKUP_FILE="/backup/openchs/application/helpline_app_2024-01-15_02-00-00.tar.gz"
APP_DIR="/var/www/html/helpline"

# Stop services
sudo systemctl stop nginx php8.2-fpm

# Backup current version
sudo mv "$APP_DIR" "${APP_DIR}.backup.$(date +%Y%m%d)"

# Extract backup
sudo tar -xzf "$BACKUP_FILE" -C /var/www/html/

# Restore permissions
sudo chown -R nginx:nginx "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"

# Restore configuration
sudo cp /backup/openchs/config/env_2024-01-15 "$APP_DIR/.env"

# Clear cache
sudo rm -rf "$APP_DIR/cache/*"

# Start services
sudo systemctl start php8.2-fpm nginx

echo "Application restoration completed"
```

### AI Service Restoration

```bash
#!/bin/bash
# Restore AI service

MODELS_BACKUP="/backup/openchs/ai-models/models_2024-01-15.tar.gz"
CONFIG_BACKUP="/backup/openchs/config/config_2024-01-15.tar.gz"

# Stop AI services
sudo systemctl stop openchs-ai-api openchs-ai-worker

# Restore models
sudo rm -rf /opt/openchs-ai/models/*
sudo tar -xzf "$MODELS_BACKUP" -C /opt/openchs-ai/

# Restore configuration
tar -xzf "$CONFIG_BACKUP"
sudo cp 2024-01-15/ai-service.env /opt/openchs-ai/.env

# Restore Redis data
REDIS_BACKUP="/backup/openchs/ai-data/redis_2024-01-15_02-00-00.rdb.gz"
sudo systemctl stop redis-server
gunzip < "$REDIS_BACKUP" > /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb
sudo systemctl start redis-server

# Start AI services
sudo systemctl start openchs-ai-api openchs-ai-worker

echo "AI service restoration completed"
```

---

## Disaster Recovery Plan

### Recovery Time Objective (RTO) & Recovery Point Objective (RPO)

| Component | RTO | RPO |
|-----------|-----|-----|
| Database | 1 hour | 6 hours |
| Application | 30 minutes | 24 hours |
| AI Service | 2 hours | 24 hours |
| Full System | 4 hours | 24 hours |

### Emergency Restoration Procedure

```bash
#!/bin/bash
# /usr/local/bin/emergency-restore.sh
# Complete system restoration script

echo "======================================"
echo "OpenCHS Emergency Restoration"
echo "Started: $(date)"
echo "======================================"

# 1. Restore Database
echo "Step 1: Restoring database..."
LATEST_DB_BACKUP=$(ls -t /backup/openchs/mysql/daily/*.sql.gz | head -1)
gunzip < "$LATEST_DB_BACKUP" | mysql --user=root
echo "Database restored from: $LATEST_DB_BACKUP"

# 2. Restore Application
echo "Step 2: Restoring application..."
LATEST_APP_BACKUP=$(ls -t /backup/openchs/application/helpline_app_*.tar.gz | head -1)
sudo rm -rf /var/www/html/helpline
sudo tar -xzf "$LATEST_APP_BACKUP" -C /var/www/html/
sudo chown -R nginx:nginx /var/www/html/helpline
echo "Application restored from: $LATEST_APP_BACKUP"

# 3. Restore Configurations
echo "Step 3: Restoring configurations..."
LATEST_CONFIG_BACKUP=$(ls -t /backup/openchs/config/config_*.tar.gz | head -1)
tar -xzf "$LATEST_CONFIG_BACKUP"
CONFIG_DIR=$(basename "$LATEST_CONFIG_BACKUP" .tar.gz | sed 's/config_//')
sudo cp "$CONFIG_DIR"/* /etc/nginx/sites-available/ 2>/dev/null
sudo cp "$CONFIG_DIR"/php-fpm_*.conf /etc/php/8.2/fpm/pool.d/www.conf 2>/dev/null
sudo cp "$CONFIG_DIR"/helpline.env /var/www/html/helpline/.env 2>/dev/null
sudo cp "$CONFIG_DIR"/ai-service.env /opt/openchs-ai/.env 2>/dev/null

# 4. Restore AI Models
echo "Step 4: Restoring AI models..."
LATEST_MODELS_BACKUP=$(ls -t /backup/openchs/ai-models/models_*.tar.gz | head -1)
if [ -f "$LATEST_MODELS_BACKUP" ]; then
    sudo tar -xzf "$LATEST_MODELS_BACKUP" -C /opt/openchs-ai/
    echo "AI models restored from: $LATEST_MODELS_BACKUP"
fi

# 5. Restore Redis
echo "Step 5: Restoring Redis data..."
LATEST_REDIS_BACKUP=$(ls -t /backup/openchs/ai-data/redis_*.rdb.gz | head -1)
if [ -f "$LATEST_REDIS_BACKUP" ]; then
    sudo systemctl stop redis-server
    gunzip < "$LATEST_REDIS_BACKUP" > /var/lib/redis/dump.rdb
    sudo chown redis:redis /var/lib/redis/dump.rdb
    sudo systemctl start redis-server
    echo "Redis data restored from: $LATEST_REDIS_BACKUP"
fi

# 6. Restart all services
echo "Step 6: Restarting services..."
sudo systemctl restart mysql
sudo systemctl restart redis-server
sudo systemctl restart php8.2-fpm
sudo systemctl restart nginx
sudo systemctl restart openchs-ai-api
sudo systemctl restart openchs-ai-worker

# 7. Verify services
echo "Step 7: Verifying services..."
sleep 5
SERVICES="mysql redis-server php8.2-fpm nginx openchs-ai-api openchs-ai-worker"
for service in $SERVICES; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service is running"
    else
        echo "✗ $service failed to start"
    fi
done

echo "======================================"
echo "Emergency Restoration Completed"
echo "Finished: $(date)"
echo "======================================"

# Send notification
echo "OpenCHS emergency restoration completed at $(date)" | \
    mail -s "OpenCHS Emergency Restoration Complete" admin@yourdomain.com
```

### Disaster Recovery Checklist

- [ ] Identify failure point and scope
- [ ] Notify team and stakeholders
- [ ] Verify backup integrity
- [ ] Stop affected services
- [ ] Restore from latest backup
- [ ] Verify data integrity
- [ ] Restart services
- [ ] Test system functionality
- [ ] Monitor for issues
- [ ] Document incident
- [ ] Update recovery procedures

---

## Testing Backups

### Monthly Backup Test

```bash
#!/bin/bash
# /usr/local/bin/test-backup-restore.sh

TEST_DIR="/tmp/openchs-backup-test"
mkdir -p "$TEST_DIR"

echo "Testing backup restoration..."

# Test database backup
LATEST_DB_BACKUP=$(ls -t /backup/openchs/mysql/daily/*.sql.gz | head -1)
if gunzip -t "$LATEST_DB_BACKUP"; then
    echo "✓ Database backup is valid"
else
    echo "✗ Database backup is corrupted!"
    exit 1
fi

# Test application backup
LATEST_APP_BACKUP=$(ls -t /backup/openchs/application/helpline_app_*.tar.gz | head -1)
if tar -tzf "$LATEST_APP_BACKUP" > /dev/null; then
    echo "✓ Application backup is valid"
else
    echo "✗ Application backup is corrupted!"
    exit 1
fi

# Test configuration backup
LATEST_CONFIG_BACKUP=$(ls -t /backup/openchs/config/config_*.tar.gz | head -1)
if tar -tzf "$LATEST_CONFIG_BACKUP" > /dev/null; then
    echo "✓ Configuration backup is valid"
else
    echo "✗ Configuration backup is corrupted!"
    exit 1
fi

echo "All backup tests passed successfully"
rm -rf "$TEST_DIR"
```

---

## Next Steps

After setting up backup and recovery:

1. **Configure Monitoring**: See [System Health Checks](../maintenance-monitoring/system-health-checks.md)
2. **Set Up Performance Tuning**: See [Performance Tuning](../maintenance-monitoring/performance-tuning.md)
3. **Configure Logging**: See [Logging & Auditing](../maintenance-monitoring/logging-auditing.md)

---

## Quick Reference

### Important Backup Commands

```bash
# Manual database backup
mysqldump --user=root --single-transaction helpline | gzip > backup.sql.gz

# Manual application backup
tar -czf app-backup.tar.gz /var/www/html/helpline

# List recent backups
ls -lh /backup/openchs/mysql/daily/ | tail -10

# Check backup disk usage
du -sh /backup/openchs/*

# Test backup integrity
gunzip -t /backup/openchs/mysql/daily/latest.sql.gz

# Sync to remote
rsync -avz /backup/openchs/ user@remote:/backups/
```

### Emergency Contacts

- Primary Administrator: admin@yourdomain.com
- Backup Administrator: backup-admin@yourdomain.com
- 24/7 Support: +254-XXX-XXXXXX