# Quick Start Guide

Get up and running with the Helpline Service in 10 minutes.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git
- 4GB RAM minimum
- 20GB disk space

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/openchlai/ai.git
cd ai/helplinev1
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` to set your configuration:

```bash
# Database
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_DATABASE=helpline_db
MYSQL_USER=helpline_user
MYSQL_PASSWORD=helpline_password

# Application
APP_NAME=openCHS Helpline
APP_PORT=8888
APP_ENV=development

# AI Service (optional)
AI_SERVICE_URL=http://ai-pipeline:8125
ENABLE_AI_SERVICE=true
```

### 3. Start Services

```bash
# Build and start all containers
docker-compose up -d

# Wait for services to initialize (2-3 minutes)
sleep 180

# Verify services are running
docker-compose ps
```

### 4. Access the Application

Open your browser and navigate to:

```
http://localhost:8888
```

**Default Credentials:**
- Username: `admin`
- Password: `password`

⚠️ **Important**: Change the default password immediately on first login.

## Verify Installation

### Check Services

```bash
# View all running containers
docker-compose ps

# Expected output:
# NAME               STATUS
# helpline-nginx     Up
# helpline-php       Up
# helpline-mysql     Up
# ai-pipeline        Up (if enabled)
```

### Test API

```bash
# Test health endpoint
curl http://localhost:8888/api/health

# Expected response:
# {"status": "healthy"}
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f helpline-php
```

## First Steps in the Application

### 1. Log In
- Navigate to http://localhost:8888
- Enter admin credentials
- Change default password

### 2. Create Your First User
1. Go to **Settings** → **Users**
2. Click **Add User**
3. Fill in user details
4. Select user role (Agent, Supervisor, Admin)
5. Save

### 3. Create a Case
1. Go to **Cases** → **New Case**
2. Fill in client information
3. Describe the situation
4. Select case category
5. Submit

### 4. Monitor Dashboard
1. Go to **Dashboard**
2. View real-time statistics
3. Monitor agent performance
4. Check call queue status

## Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clear data)
docker-compose down -v
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Verify Docker is running
docker ps

# Restart services
docker-compose restart
```

### Can't Access Application

```bash
# Check if port 8888 is in use
lsof -i :8888

# Check container is running
docker-compose ps helpline-nginx

# View nginx logs
docker-compose logs helpline-nginx
```

### Database Connection Error

```bash
# Check MySQL is running
docker-compose ps helpline-mysql

# View MySQL logs
docker-compose logs helpline-mysql

# Verify credentials in .env match docker-compose.yml
```

## Next Steps

- **[Installation & Deployment](./installation/overview.md)** - Full deployment guide
- **[Configuration Guide](./configuration.md)** - Advanced configuration
- **[API Reference](./api-reference/overview.md)** - API documentation
- **[Development Guide](./development.md)** - Contributing & extending
- **[Deployment Workflow](#deployment-workflow)** - CI/CD setup

## Deployment Workflow

### For Development

```bash
# 1. Clone from main repo
git clone https://github.com/openchlai/ai.git
cd ai/helplinev1

# 2. Create your feature branch
git checkout -b feature/my-feature

# 3. Make changes and test locally

# 4. Push to your branch
git push origin feature/my-feature

# 5. Create Pull Request to dev branch
# (via GitHub)

# 6. Once merged with dev, automatically deployed to:
# http://192.168.10.119/helpline
```

### For Production

Deployment to production follows approval and testing processes defined in your CI/CD pipeline.
