# Configuration Guide

Complete guide to configuring the Helpline Service.

## Environment Variables

### Location
```
.env (root directory)
.env.example (reference template)
```

### Application Settings

```bash
# Application Name and Environment
APP_NAME=openCHS Helpline
APP_ENV=development  # development, staging, production
APP_DEBUG=false      # true for development, false for production
APP_PORT=8888

# Application URL
APP_URL=http://localhost:8888

# Timezone
APP_TIMEZONE=UTC
```

### Database Configuration

```bash
# MySQL Connection
DB_HOST=helpline-mysql
DB_PORT=3306
DB_DATABASE=helpline_db
DB_USERNAME=helpline_user
DB_PASSWORD=SecurePassword123!

# Root Password (for init)
MYSQL_ROOT_PASSWORD=SecureRootPassword456!

# Connection Pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### Web Server Configuration

```bash
# Nginx Settings
NGINX_PORT=80
NGINX_SSL_PORT=443
NGINX_WORKER_PROCESSES=auto

# PHP Settings
PHP_MEMORY_LIMIT=512M
PHP_UPLOAD_MAX_FILESIZE=100M
PHP_EXECUTION_TIME=300
PHP_FPM_WORKERS=4
```

### Authentication & Security

```bash
# Session Configuration
SESSION_LIFETIME=120  # minutes
SESSION_SECURE=false  # true for HTTPS only
REMEMBER_ME_DURATION=30  # days

# JWT Configuration (if using API)
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY=3600  # seconds

# Password Requirements
MIN_PASSWORD_LENGTH=8
REQUIRE_SPECIAL_CHARS=true
REQUIRE_NUMBERS=true
REQUIRE_UPPERCASE=true

# MFA (Multi-Factor Authentication)
ENABLE_MFA=false
ENABLE_TOTP=false
```

### Email Configuration

```bash
# Mail Server
MAIL_DRIVER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS=noreply@openchs.org
MAIL_FROM_NAME="openCHS Helpline"

# Alternative: Mailgun
MAIL_DRIVER=mailgun
MAILGUN_DOMAIN=your-domain
MAILGUN_SECRET=your-key
```

### AI Service Integration

```bash
# Enable/Disable AI Features
ENABLE_AI_SERVICE=false  # true to enable

# AI Service Connection
AI_SERVICE_URL=http://ai-pipeline:8125
AI_SERVICE_TIMEOUT=300
AI_SERVICE_API_KEY=your-api-key

# AI Features
ENABLE_TRANSCRIPTION=false
ENABLE_TRANSLATION=false
ENABLE_ENTITY_EXTRACTION=false
ENABLE_CLASSIFICATION=false
ENABLE_SUMMARIZATION=false

# Default Languages
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,sw,ar,fr
```

### Logging & Monitoring

```bash
# Logging
LOG_LEVEL=info  # debug, info, warning, error, critical
LOG_CHANNEL=stack
LOG_FILE_PATH=/var/log/helpline/app.log
LOG_MAX_SIZE=10M
LOG_RETENTION_DAYS=30

# Error Reporting
ERROR_REPORTING=true
SENTRY_DSN=https://your-sentry-key@sentry.io/project-id

# Performance Monitoring
ENABLE_QUERY_LOG=false
SLOW_QUERY_THRESHOLD=1000  # milliseconds
```

### File Storage

```bash
# Local Storage
STORAGE_PATH=/storage
MAX_FILE_SIZE=104857600  # 100MB
ALLOWED_EXTENSIONS=pdf,doc,docx,jpg,png,xlsx,zip

# Cloud Storage (optional)
STORAGE_DRIVER=local  # local, s3, gcs
AWS_S3_BUCKET=your-bucket
AWS_S3_REGION=us-east-1
```

### VoIP Integration

```bash
# Asterisk/FreeSWITCH Integration
ENABLE_VOIP=false
VOIP_SERVER=192.168.1.100
VOIP_PORT=5060
VOIP_USERNAME=helpline
VOIP_PASSWORD=secure-password

# Recording
ENABLE_CALL_RECORDING=false
RECORDING_PATH=/recordings
```

### SMS Integration

```bash
# SMS Provider
SMS_PROVIDER=twilio  # twilio, nexmo, custom

# Twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Nexmo
NEXMO_API_KEY=your-api-key
NEXMO_API_SECRET=your-api-secret
```

### Rate Limiting

```bash
# API Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60  # seconds

# Login Attempts
LOGIN_MAX_ATTEMPTS=5
LOGIN_LOCKOUT_DURATION=900  # seconds
```

### Data Privacy

```bash
# GDPR Compliance
ENABLE_GDPR_MODE=false
DATA_RETENTION_DAYS=2555  # 7 years
AUTO_DELETE_OLD_DATA=false

# PII Handling
ENCRYPT_PII_FIELDS=true
MASK_PHONE_NUMBERS=true
MASK_EMAIL_ADDRESSES=true
```

## Configuration by Environment

### Development

```bash
# .env for local development
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=debug

MYSQL_ROOT_PASSWORD=root
MYSQL_PASSWORD=password
DB_HOST=helpline-mysql

ENABLE_AI_SERVICE=false
SESSION_SECURE=false

MAIL_DRIVER=log
```

### Staging

```bash
# .env for staging deployment
APP_ENV=staging
APP_DEBUG=false
LOG_LEVEL=info

DB_HOST=staging-db.example.com
DB_PASSWORD=<strong-password>

ENABLE_AI_SERVICE=true
AI_SERVICE_URL=http://staging-ai:8125

SESSION_SECURE=true
SESSION_LIFETIME=480

MAIL_DRIVER=smtp
MAIL_HOST=smtp.gmail.com
```

### Production

```bash
# .env for production deployment
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=warn

DB_HOST=prod-db.example.com
DB_PASSWORD=<very-strong-password>

ENABLE_AI_SERVICE=true
AI_SERVICE_URL=https://ai.prod.example.com

SESSION_SECURE=true
SESSION_LIFETIME=120

MAIL_DRIVER=smtp
ERROR_REPORTING=true
SENTRY_DSN=<your-sentry-dsn>
```

## Advanced Configuration

### Database Connection Pool

```bash
# Optimize for your workload
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### PHP Performance Tuning

```bash
# Memory and Execution
PHP_MEMORY_LIMIT=1024M  # Production
PHP_EXECUTION_TIME=600
PHP_MAX_INPUT_VARS=10000

# Opcache (Performance)
OPCACHE_ENABLE=true
OPCACHE_MEMORY_CONSUMPTION=256
OPCACHE_INTERNED_STRINGS_BUFFER=16
```

### Nginx Optimization

```bash
# Caching Headers
ENABLE_BROWSER_CACHE=true
CACHE_CONTROL_MAX_AGE=3600

# Compression
ENABLE_GZIP=true
GZIP_LEVEL=6

# SSL/TLS
ENABLE_HSTS=true
HSTS_MAX_AGE=31536000
```

## Security Best Practices

### Secrets Management

```bash
# Never commit .env to version control
echo ".env" >> .gitignore

# Use strong random passwords
# PHP: openssl_random_pseudo_bytes(32)
# Linux: openssl rand -base64 32

# Rotate secrets regularly
ADMIN_PASSWORD=<change-monthly>
JWT_SECRET=<change-quarterly>
```

### SSL/TLS Configuration

```bash
# Enable HTTPS
ENABLE_SSL=true
SSL_CERTIFICATE=/etc/ssl/certs/certificate.crt
SSL_PRIVATE_KEY=/etc/ssl/private/private.key

# Force HTTPS redirect
FORCE_HTTPS=true
SECURE_HSTS=true
```

### Database Security

```bash
# Use strong passwords
DB_PASSWORD=<generate-with-openssl>

# Restrict database user
DB_HOST=127.0.0.1  # Not 0.0.0.0
DB_PORT=3306

# Regular backups
BACKUP_SCHEDULE=daily
BACKUP_RETENTION_DAYS=30
```

## Configuration Validation

### Check Configuration

```bash
# Verify environment variables are set
docker-compose exec helpline-php php -r "
  \$env_vars = ['APP_ENV', 'DB_HOST', 'DB_PASSWORD'];
  foreach(\$env_vars as \$var) {
    echo \$var . ': ' . getenv(\$var) . PHP_EOL;
  }
"

# Test database connection
docker-compose exec helpline-php php -r "
  \$conn = new mysqli(
    getenv('DB_HOST'),
    getenv('DB_USERNAME'),
    getenv('DB_PASSWORD'),
    getenv('DB_DATABASE')
  );
  echo \$conn->connect_error ? 'Failed' : 'Success';
"
```

## Troubleshooting

### Configuration Not Applied

```bash
# Rebuild containers
docker-compose build --no-cache

# Restart services
docker-compose restart

# View current configuration
docker-compose exec helpline-php php -i
```

### Database Connection Failed

```bash
# Check credentials in .env
cat .env | grep DB_

# Test connection
docker-compose exec helpline-mysql mysql -u $DB_USERNAME -p$DB_PASSWORD

# View MySQL logs
docker-compose logs helpline-mysql
```

### Mail Not Sending

```bash
# Test mail configuration
docker-compose exec helpline-php php -r "
  \$mail = mail('test@example.com', 'Test', 'Body');
  echo \$mail ? 'Success' : 'Failed';
"

# Check mail logs
docker-compose logs | grep mail
```

## References

- [PHP Configuration](https://www.php.net/manual/en/ini.core.php)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [MySQL Configuration](https://dev.mysql.com/doc/refman/8.0/en/)
