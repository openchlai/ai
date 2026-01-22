# Security Guide

## Overview

The AI Service is designed with security and privacy as core principles, especially for handling sensitive child protection data.

## Data Privacy

### PII Detection and Handling

The system includes built-in PII (Personally Identifiable Information) detection:

```bash
# Enable PII detection
ENABLE_PII_DETECTION=true

# Anonymize results
ANONYMIZE_RESULTS=true  # Replaces names with placeholders
```

### Data Retention

```bash
# Set data retention policy
DATA_RETENTION_HOURS=24  # Auto-delete after 24 hours

# Cleanup settings
CLEANUP_INTERVAL=300  # Check every 5 minutes
```

### Encryption

```bash
# Enable encryption at rest
DATABASE_ENCRYPTION=true

# Redis encryption
REDIS_USE_SSL=true
REDIS_SSL_CERT_REQS=required
```

## Authentication & Authorization

### JWT Authentication

```bash
# Enable authentication
ENABLE_AUTH=true

# Configure JWT
JWT_SECRET_KEY="your-very-long-secret-key-here"
JWT_ALGORITHM="HS256"
TOKEN_EXPIRY_MINUTES=60

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### API Key Management

```bash
# Generate API key
curl -X POST http://localhost:8125/auth/generate-key

# Use API key
curl -H "X-API-Key: your-api-key" http://localhost:8125/health
```

## Network Security

### HTTPS/TLS

```bash
# In nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### CORS Configuration

```bash
# Configure CORS
CORS_ORIGINS=["http://localhost:3000", "https://app.example.com"]
CORS_ALLOW_CREDENTIALS=true
```

### Firewall Rules

```bash
# Block external access to internal services
iptables -A INPUT -p tcp --dport 8125 -i eth0 -j DROP
iptables -A INPUT -p tcp --dport 8125 -i docker0 -j ACCEPT

# Or use UFW
ufw deny 8125/tcp
ufw allow 8125/tcp from 10.0.0.0/8
```

## Container Security

### Docker Security Best Practices

```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 aiservice
USER aiservice

# Use minimal base image
FROM python:3.11-slim

# Scan for vulnerabilities
# docker scan ai-service:latest

# Sign images
# docker trust sign ai-service:latest
```

### Kubernetes Security

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ai-service
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsReadOnlyRootFilesystem: true
    capabilities:
      drop:
        - ALL
  containers:
  - name: api
    securityContext:
      allowPrivilegeEscalation: false
    resources:
      limits:
        memory: "16Gi"
        cpu: "8"
```

## Secrets Management

### Store Secrets Securely

```bash
# Use environment variables (not in code)
export DATABASE_PASSWORD="secure-password"

# Or use secrets management service
# AWS Secrets Manager
# HashiCorp Vault
# Kubernetes Secrets

# Never commit secrets to git
echo ".env" >> .gitignore
echo "secrets/" >> .gitignore
```

### Rotate Credentials

```bash
# Rotate database password
# 1. Generate new password
# 2. Update in secrets manager
# 3. Restart services
docker-compose restart api-server celery-worker
```

## Audit & Logging

### Enable Audit Logging

```bash
# Log all API requests
LOG_LEVEL=INFO
LOG_API_REQUESTS=true
LOG_DB_QUERIES=true

# Store logs securely
LOG_FILE=/var/log/ai-service/app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=90
```

### Monitor Sensitive Operations

```bash
# Track data access
AUDIT_DATA_ACCESS=true

# Track model access
AUDIT_MODEL_ACCESS=true

# Track authentication events
AUDIT_AUTH_EVENTS=true
```

## Input Validation

### Audio Validation

```python
# Validate audio files
MAX_AUDIO_SIZE_MB=500  # Limit file size

# Supported formats
ALLOWED_AUDIO_FORMATS = ["wav", "mp3", "flac", "m4a", "ogg"]

# Check sample rate
MIN_SAMPLE_RATE=8000
MAX_SAMPLE_RATE=48000
```

### Text Input Validation

```python
# Validate text inputs
MAX_TEXT_LENGTH=10000
MIN_TEXT_LENGTH=1

# Sanitize inputs
SANITIZE_INPUTS=true
REMOVE_SPECIAL_CHARS=false
```

## Vulnerability Management

### Dependencies

```bash
# Check for vulnerable dependencies
pip install safety
safety check

# Or use
pip install pip-audit
pip-audit
```

### Regular Updates

```bash
# Check for updates
pip list --outdated

# Update safely
pip install --upgrade --upgrade-strategy eager pip setuptools wheel

# Update requirements
pip freeze > requirements-latest.txt
```

## Compliance

### GDPR Compliance

```bash
# Right to be forgotten
DELETE /api/v1/calls/{call_id}  # Deletes all associated data

# Data portability
GET /api/v1/calls/{call_id}/export?format=json

# Consent tracking
TRACK_CONSENT=true
REQUIRE_EXPLICIT_CONSENT=true
```

### HIPAA Compliance (if handling health data)

```bash
# Encryption required
DATABASE_ENCRYPTION=true
REDIS_ENCRYPTION=true
TRANSMISSION_ENCRYPTION=true

# Audit requirements
AUDIT_LOGGING=true
AUDIT_LOG_RETENTION=7  # years

# Access controls
ENABLE_AUTH=true
ENABLE_ROLE_BASED_ACCESS=true
```

### Child Protection Standards

```bash
# Enhanced data protection for child data
CHILD_DATA_PROTECTION=true

# Mandatory encryption
CHILD_DATA_ENCRYPTION=true

# Restricted access
CHILD_DATA_ACCESS_ROLES=["admin", "case_worker", "supervisor"]

# Enhanced audit logging
CHILD_DATA_AUDIT_LOGGING=true
```

## Security Incident Response

### Monitor for Suspicious Activity

```bash
# Monitor failed authentication attempts
MONITOR_FAILED_AUTH=true
FAILED_AUTH_THRESHOLD=5  # Lock after 5 failures

# Monitor unusual access patterns
MONITOR_UNUSUAL_ACCESS=true

# Alert on security events
SECURITY_ALERT_ENABLED=true
SECURITY_ALERT_EMAIL="security@example.com"
```

### Incident Response Checklist

1. **Detect**: Monitor logs for suspicious activity
2. **Contain**: Isolate affected systems
3. **Investigate**: Analyze logs and traces
4. **Remediate**: Fix vulnerabilities
5. **Document**: Record incident details
6. **Improve**: Update security policies

## Security Checklist

- [ ] Secrets are not committed to version control
- [ ] HTTPS/TLS enabled in production
- [ ] API authentication is enforced
- [ ] Rate limiting is configured
- [ ] Input validation is implemented
- [ ] Audit logging is enabled
- [ ] Data encryption is enabled
- [ ] Regular security updates are applied
- [ ] Firewall rules are configured
- [ ] Backups are encrypted and tested
- [ ] Incident response plan is documented
- [ ] Security training completed by team

## Reporting Security Issues

If you discover a security vulnerability, please email security@openchs.org with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

Do not publicly disclose vulnerabilities until they are patched.
