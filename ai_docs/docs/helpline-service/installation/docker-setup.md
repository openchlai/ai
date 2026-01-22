# Docker Installation & Deployment

Complete guide to deploying the Helpline Service using Docker and Docker Compose.

## Prerequisites

### System Requirements

**Minimum (Development)**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- Network: 1Mbps

**Recommended (Production)**
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 100GB+
- Network: 10Mbps

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Bash or similar shell

### Verify Installation

```bash
# Check Docker
docker --version
# Output: Docker version 20.10+

# Check Docker Compose
docker-compose --version
# Output: Docker Compose version 2.0+

# Verify Docker daemon is running
docker ps
# Output: Lists running containers
```

## Installation Steps

### 1. Clone Repository

```bash
# Clone the main repository
git clone https://github.com/openchlai/ai.git
cd ai/helplinev1

# Verify directory structure
ls -la
# Output should show:
# docker/
# application/
# rest_api/
# docker-compose.yml
# .env.example
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or use your preferred editor
```

**Essential Configuration:**

```bash
# Application Settings
APP_NAME=openCHS Helpline
APP_ENV=development
APP_PORT=8888
APP_DEBUG=false

# Database
MYSQL_ROOT_PASSWORD=SecureRootPassword123!
MYSQL_DATABASE=helpline_db
MYSQL_USER=helpline_user
MYSQL_PASSWORD=SecurePassword456!
MYSQL_PORT=3306

# Nginx
NGINX_PORT=80
NGINX_SSL_PORT=443

# PHP
PHP_ENV=development
PHP_MEMORY_LIMIT=512M
PHP_UPLOAD_MAX_FILESIZE=100M

# AI Service Integration (optional)
ENABLE_AI_SERVICE=false
AI_SERVICE_URL=http://ai-pipeline:8125
AI_SERVICE_API_KEY=your-api-key

# Logging
LOG_LEVEL=info
LOG_CHANNEL=stack
```

### 3. Build Images

```bash
# Build Docker images
docker-compose build

# This will build:
# - helpline-nginx (Nginx web server)
# - helpline-php (PHP-FPM backend)
# - helpline-mysql (MySQL database)
```

### 4. Start Services

```bash
# Start all services in background
docker-compose up -d

# Monitor startup progress
docker-compose logs -f

# Wait for all services to be ready (2-3 minutes)
# Press Ctrl+C to exit logs
```

### 5. Initialize Database

```bash
# The database initializes automatically on first startup
# Verify with:
docker-compose logs helpline-mysql | grep "ready for connections"

# If manual init needed:
docker-compose exec helpline-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD \
  -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;"
```

### 6. Verify Deployment

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                 STATUS      PORTS
# helpline-nginx       Up 2 min    0.0.0.0:80->80/tcp
# helpline-php         Up 2 min    9000/tcp
# helpline-mysql       Up 2 min    3306/tcp

# Test application endpoint
curl http://localhost:8888

# Test API health
curl http://localhost:8888/api/health
# Expected: {"status": "healthy"}
```

## Access the Application

### Web Interface

```
http://localhost:8888
```

**Default Credentials:**
- Username: `admin`
- Password: `password`

⚠️ Change default credentials immediately!

### API Endpoint

```
http://localhost:8888/api/v1
```

## Docker Compose File Structure

```yaml
version: '3.8'

services:
  helpline-nginx:
    # Reverse proxy and web server
    # Serves frontend and routes to backend

  helpline-php:
    # PHP-FPM application server
    # Runs backend REST API

  helpline-mysql:
    # MySQL database
    # Persists all application data

  # Optional: AI Pipeline
  ai-pipeline:
    # Python FastAPI service
    # Provides AI features (if enabled)
```

## Environment-Specific Setup

### Development

```bash
# .env configuration
APP_ENV=development
PHP_DEBUG=true
LOG_LEVEL=debug
MYSQL_PORT=3306

# Start with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Staging

```bash
# .env configuration
APP_ENV=staging
PHP_DEBUG=false
LOG_LEVEL=info
ENABLE_AI_SERVICE=true

# Scale PHP containers
docker-compose up -d --scale helpline-php=3

# Access via staging URL
# http://192.168.10.119/helpline
```

### Production

```bash
# .env configuration
APP_ENV=production
PHP_DEBUG=false
LOG_LEVEL=warn
MYSQL_PASSWORD=<use-strong-password>

# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Enable HTTPS
# Configure SSL certificates in nginx config
```

## Common Operations

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs helpline-php

# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail 100
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart helpline-php

# Stop and start
docker-compose down && docker-compose up -d
```

### Access Container Shell

```bash
# PHP container
docker-compose exec helpline-php bash

# MySQL container
docker-compose exec helpline-mysql bash

# Nginx container
docker-compose exec helpline-nginx sh
```

### Execute Commands

```bash
# Run artisan commands (if using framework)
docker-compose exec helpline-php php artisan migrate

# Run MySQL queries
docker-compose exec helpline-mysql mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE

# Check PHP version
docker-compose exec helpline-php php -v
```

## Backup and Recovery

### Backup Database

```bash
# Backup MySQL database
docker-compose exec helpline-mysql mysqldump \
  -u $MYSQL_USER -p$MYSQL_PASSWORD \
  $MYSQL_DATABASE > backup.sql

# Or use volume backup
docker run --rm -v helpline-mysql-volume:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mysql-backup.tar.gz /data
```

### Restore Database

```bash
# Restore from SQL backup
docker-compose exec -T helpline-mysql mysql \
  -u $MYSQL_USER -p$MYSQL_PASSWORD \
  $MYSQL_DATABASE < backup.sql
```

## Cleanup

### Stop Services

```bash
# Stop all containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and delete volumes
docker-compose down -v
```

### Clean Up Docker

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove all unused resources
docker system prune -a
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8888
lsof -i :8888

# Kill the process
kill -9 <PID>

# Or change port in .env
NGINX_PORT=8889
```

### Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply new group
newgrp docker

# Or use sudo
sudo docker-compose up -d
```

### Out of Disk Space

```bash
# Check disk usage
docker system df

# Clean up
docker system prune -a --volumes
```

### Services Won't Start

```bash
# View detailed logs
docker-compose logs --tail 200

# Check compose file syntax
docker-compose config

# Rebuild images
docker-compose build --no-cache

# Try again
docker-compose up -d
```

## Next Steps

- **[Configuration Guide](../configuration.md)** - Advanced configuration
- **[Development Guide](../development.md)** - Local development setup
- **[Deployment Workflow](#deployment-workflow)** - CI/CD integration
- **[API Reference](../api-reference/overview.md)** - API documentation

## Deployment Workflow

See the [Deployment Workflow](../deployment-workflow.md) guide for:
- Contributing with Git branches
- Creating Pull Requests to `dev`
- Automated staging deployment
- Production release process
