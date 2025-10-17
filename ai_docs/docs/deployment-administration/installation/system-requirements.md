# System Requirements

## Overview

OpenCHS consists of two main services with different system requirements. This document outlines the hardware, software, and network requirements for deploying both services.

---

## Helpline Service Requirements

### Hardware Requirements

#### Minimum (Development/Testing)
- **CPU:** 2 cores (2.0 GHz+)
- **RAM:** 4 GB
- **Storage:** 20 GB SSD
- **Network:** 10 Mbps

#### Recommended (Small Production - up to 50 users)
- **CPU:** 4 cores (2.5 GHz+)
- **RAM:** 8 GB
- **Storage:** 100 GB SSD
- **Network:** 100 Mbps
- **Backup Storage:** 500 GB

#### High-Capacity (Large Production - 100+ users)
- **CPU:** 8+ cores (3.0 GHz+)
- **RAM:** 16 GB
- **Storage:** 500 GB SSD (RAID 10 recommended)
- **Network:** 1 Gbps
- **Backup Storage:** 2 TB

### Software Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| **Operating System** | Ubuntu 20.04+ / RHEL 8+ / Debian 11+ | 64-bit required |
| **PHP** | 8.2 or higher | With FPM |
| **MySQL** | 5.7+ or MariaDB 10.5+ | InnoDB required |
| **Nginx** | 1.18+ | Or Apache 2.4+ |
| **SSL/TLS** | TLS 1.2+ | Let's Encrypt recommended |

### PHP Extensions Required
```bash
php8.2-fpm
php8.2-mysql
php8.2-curl
php8.2-gd
php8.2-mbstring
php8.2-xml
php8.2-json
php8.2-zip
```

---

## AI Service Requirements

### Hardware Requirements

#### Minimum (CPU Only - Testing)
- **CPU:** 8 cores (3.0 GHz+)
- **RAM:** 16 GB
- **Storage:** 50 GB SSD
- **Network:** 100 Mbps

#### Recommended (GPU - Production)
- **CPU:** 16 cores (3.0 GHz+)
- **RAM:** 32 GB
- **Storage:** 100 GB SSD
- **GPU:** NVIDIA GPU with 16 GB+ VRAM
- **Network:** 1 Gbps

**Recommended GPU Models:**
- NVIDIA Tesla T4 (16GB)
- NVIDIA A10 (24GB)
- NVIDIA V100 (16GB/32GB)
- NVIDIA A100 (40GB/80GB)

#### High-Performance (Large Scale)
- **CPU:** 32+ cores
- **RAM:** 64 GB
- **Storage:** 500 GB NVMe SSD
- **GPU:** Multiple NVIDIA A100 (80GB)
- **Network:** 10 Gbps

### Software Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| **Operating System** | Ubuntu 20.04+ / RHEL 8+ | 64-bit required |
| **Docker** | 20.10+ | Docker Engine |
| **Docker Compose** | 2.0+ | For multi-container setup |
| **NVIDIA Driver** | 525+ | For GPU support |
| **NVIDIA Container Runtime** | Latest | For GPU in Docker |
| **CUDA** | 11.8+ | For GPU acceleration |
| **Python** | 3.11+ | If running outside Docker |

---

## Network Requirements

### Bandwidth Requirements

| Scenario | Minimum | Recommended |
|----------|---------|-------------|
| Small deployment (1-50 cases/day) | 10 Mbps | 100 Mbps |
| Medium deployment (50-200 cases/day) | 100 Mbps | 500 Mbps |
| Large deployment (200+ cases/day) | 500 Mbps | 1 Gbps |

### Port Requirements

#### Helpline Service
- **443** (HTTPS) - Web interface and API (required)
- **80** (HTTP) - Redirect to HTTPS (optional)
- **3306** (MySQL) - Database (internal only, not exposed)

#### AI Service
- **8123** (HTTP) - AI Service API (internal only)
- **6379** (Redis) - Task queue (internal only)

### Firewall Rules

**Incoming:**
```bash
# Helpline Service (public-facing)
Allow TCP 443 from 0.0.0.0/0
Allow TCP 80 from 0.0.0.0/0 (optional, for redirect)

# AI Service (internal only)
Allow TCP 8123 from helpline_server_ip only
```

**Outgoing:**
```bash
# For updates and external integrations
Allow TCP 443 to 0.0.0.0/0
Allow TCP 80 to 0.0.0.0/0
```

---

## Storage Requirements

### Helpline Service Storage

| Data Type | Growth Rate | Retention | Storage Calculation |
|-----------|-------------|-----------|---------------------|
| Database | ~10 MB per 100 cases | 7 years | Cases × 0.1 MB × 7 years |
| Audio Files | ~5 MB per recording | 1 year | Recordings/day × 5 MB × 365 |
| Documents | ~2 MB per case | 7 years | Cases × 2 MB × 7 years |
| Logs | ~100 MB per month | 1 year | 100 MB × 12 months |
| Backups | Database + Files | 90 days | (DB + Files) × 3 |

**Example Calculation (100 cases/day):**
```
Daily cases: 100
Annual cases: 36,500

Database: 36,500 × 0.1 MB × 7 = 25.6 GB
Audio files: 100 × 5 MB × 365 = 183 GB
Documents: 36,500 × 2 MB × 7 = 511 GB
Logs: 1.2 GB
Backups: ~200 GB

Total: ~920 GB minimum
Recommended: 2 TB with growth buffer
```

### AI Service Storage

| Component | Size | Notes |
|-----------|------|-------|
| Whisper Model | 3 GB | Large V3 Turbo |
| Translation Model | 500 MB | Custom Sw-En |
| NER Model | 100 MB | spaCy model |
| Classification Model | 500 MB | DistilBERT |
| Temp Audio Processing | Variable | 10-20 GB buffer |
| Redis Cache | 2-4 GB | In-memory |
| Logs | 50 MB/day | 5 GB for 90 days |

**Total: 20-30 GB minimum**  
**Recommended: 100 GB for comfort**

---

## Database Requirements

### MySQL Configuration

**Minimum Settings:**
```ini
[mysqld]
innodb_buffer_pool_size = 2G
max_connections = 200
query_cache_size = 64M
tmp_table_size = 64M
max_heap_table_size = 64M
```

**Recommended Settings (Production):**
```ini
[mysqld]
innodb_buffer_pool_size = 8G
max_connections = 500
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
query_cache_size = 256M
tmp_table_size = 256M
max_heap_table_size = 256M
innodb_file_per_table = 1
```

### Database Sizing

| Metric | Small | Medium | Large |
|--------|-------|--------|-------|
| Daily Cases | 1-50 | 50-200 | 200+ |
| Database Size (Year 1) | 5-10 GB | 20-50 GB | 100+ GB |
| Connections Needed | 50-100 | 100-300 | 300+ |
| Buffer Pool | 2-4 GB | 4-8 GB | 8-16 GB |

---

## Operating System Configuration

### Recommended OS Settings

**For Helpline Service (Ubuntu 20.04+):**
```bash
# Increase file descriptors
ulimit -n 65536

# Optimize kernel parameters
sysctl -w net.core.somaxconn=4096
sysctl -w net.ipv4.tcp_max_syn_backlog=4096
sysctl -w vm.swappiness=10
```

**For AI Service (Ubuntu 20.04+):**
```bash
# Increase shared memory for GPU
sysctl -w kernel.shmmax=68719476736
sysctl -w kernel.shmall=4294967296

# Optimize for high-performance computing
sysctl -w vm.swappiness=10
sysctl -w vm.dirty_ratio=10
sysctl -w vm.dirty_background_ratio=5
```

---

## Browser Requirements (End Users)

### Supported Browsers

| Browser | Minimum Version | Recommended |
|---------|----------------|-------------|
| **Chrome** | 90+ | Latest |
| **Firefox** | 88+ | Latest |
| **Safari** | 14+ | Latest |
| **Edge** | 90+ | Latest |

### Browser Requirements
- JavaScript enabled
- Cookies enabled
- WebSocket support
- TLS 1.2+ support

---

## Deployment Scenarios

### Scenario 1: Small NGO (1-50 users)

**Helpline Service:**
- Single server: 4 CPU, 8 GB RAM, 100 GB SSD
- MySQL on same server
- Ubuntu 20.04 LTS

**AI Service:**
- Single server: 8 CPU, 16 GB RAM, 50 GB SSD
- CPU-only (no GPU)
- Docker deployment

**Total Cost Estimate:** $100-200/month (cloud) or ~$2000 one-time (on-premise)

### Scenario 2: Medium Organization (50-200 users)

**Helpline Service:**
- Application server: 8 CPU, 16 GB RAM, 200 GB SSD
- Database server: 4 CPU, 8 GB RAM, 500 GB SSD
- Load balancer (optional)

**AI Service:**
- GPU server: 16 CPU, 32 GB RAM, 100 GB SSD, Tesla T4 GPU
- Docker deployment

**Total Cost Estimate:** $500-800/month (cloud) or ~$8000 one-time (on-premise)

### Scenario 3: National Helpline (200+ users)

**Helpline Service:**
- Application servers: 2×(16 CPU, 32 GB RAM, 500 GB SSD)
- Database cluster: 3×(8 CPU, 16 GB RAM, 1 TB SSD)
- Load balancer
- CDN for static assets

**AI Service:**
- GPU servers: 2×(32 CPU, 64 GB RAM, 500 GB SSD, A100 GPU)
- Redis cluster
- Docker Swarm or Kubernetes

**Total Cost Estimate:** $2000-5000/month (cloud) or ~$50,000 one-time (on-premise)

---

## Cloud Provider Recommendations

### AWS
- **Helpline:** EC2 t3.large or t3.xlarge
- **AI Service:** g4dn.xlarge or g5.xlarge (GPU)
- **Database:** RDS MySQL t3.medium or t3.large
- **Storage:** EBS gp3 volumes

### Google Cloud
- **Helpline:** n2-standard-4 or n2-standard-8
- **AI Service:** n1-standard-8 with T4 GPU
- **Database:** Cloud SQL MySQL (db-n1-standard-2)
- **Storage:** Persistent SSD

### Azure
- **Helpline:** Standard_D4s_v3 or Standard_D8s_v3
- **AI Service:** Standard_NC4as_T4_v3 (GPU)
- **Database:** Azure Database for MySQL (GP_Gen5_2)
- **Storage:** Premium SSD

---

## Performance Expectations

### Helpline Service

| Metric | Target |
|--------|--------|
| API Response Time | < 200ms (95th percentile) |
| Page Load Time | < 2 seconds |
| Concurrent Users | As per hardware tier |
| Database Queries | < 50ms average |
| Uptime | 99.9% |

### AI Service

| Metric | Target (GPU) | Target (CPU) |
|--------|--------------|--------------|
| Transcription | 2-5 sec/min audio | 10-20 sec/min audio |
| Translation | < 1 second | < 3 seconds |
| Classification | < 500ms | < 2 seconds |
| Complete Pipeline | 15-30 seconds | 60-120 seconds |
| Throughput | 10+ concurrent | 2-3 concurrent |

---

## Compatibility Matrix

### Tested Configurations

| Helpline OS | AI Service OS | MySQL | PHP | Status |
|-------------|---------------|-------|-----|--------|
| Ubuntu 20.04 | Ubuntu 20.04 | 8.0 | 8.2 | ✅ Tested |
| Ubuntu 22.04 | Ubuntu 22.04 | 8.0 | 8.2 | ✅ Tested |
| RHEL 8 | Ubuntu 20.04 | 8.0 | 8.2 | ✅ Tested |
| Debian 11 | Ubuntu 20.04 | 10.5 | 8.2 | ✅ Tested |

---

## Pre-Installation Checklist

Before proceeding with installation, ensure:

**Helpline Service:**
- [ ] Server meets minimum hardware requirements
- [ ] Operating system is 64-bit Ubuntu 20.04+ or RHEL 8+
- [ ] Root or sudo access available
- [ ] Ports 80, 443 available
- [ ] Domain name configured (optional but recommended)
- [ ] SSL certificate obtained

**AI Service:**
- [ ] Server meets minimum hardware requirements
- [ ] GPU drivers installed (if using GPU)
- [ ] Docker and Docker Compose installed
- [ ] NVIDIA Container Runtime installed (if GPU)
- [ ] At least 50 GB free storage for models
- [ ] Network connectivity to Helpline service

**Network:**
- [ ] Firewall rules configured
- [ ] DNS records configured
- [ ] Bandwidth meets requirements
- [ ] Internal network between services configured

**Data:**
- [ ] Backup strategy planned
- [ ] Data retention policies defined
- [ ] Disaster recovery plan prepared

---

## Next Steps

After verifying system requirements:
1. See [On-Premise Installation Guide](on-premise-installation-guide.md) for server installation
2. See [Cloud Deployment](cloud-deployment.md) for cloud provider setup
3. See [Docker/Kubernetes Setup](docker-kubernetes-setup.md) for container deployment

For questions about system requirements, contact: support@bitz-itc.com