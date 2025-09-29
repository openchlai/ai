# Authentication Guide

## System Architecture Overview

OpenCHS consists of two independent services with distinct authentication mechanisms:

1. **Helpline Service** - PHP/MySQL REST API for case management
2. **AI Service** - FastAPI/Python containerized AI pipeline

## Service Details

| Service | Technology | Port | Authentication | Base Path |
|---------|-----------|------|----------------|-----------|
| **Helpline API** | PHP 8.2 + MySQL | 443 (HTTPS) | Session-based (OTP) | `/helpline/api/` |
| **AI Pipeline** | FastAPI + Celery | 8123 | Token/API Key | `/audio/`, `/whisper/`, etc. |

---

## Helpline Service Authentication

### Technology Stack
- **Backend:** PHP 8.2 with PHP-FPM
- **Database:** MySQL with unix_socket authentication
- **Web Server:** Nginx with SSL/TLS
- **Session Storage:** MySQL `session` table

### Authentication Flow

#### Step 1: Request OTP
```bash
curl -X POST https://your-domain.com/helpline/api/sendOTP \
  -H "Content-Type: application/json" \
  -d '{
    "addr_addr": "user@example.com",
    "addr_type": "email"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent to user@example.com"
}
```

#### Step 2: Verify OTP
```bash
curl -X POST https://your-domain.com/helpline/api/verifyOTP \
  -H "Content-Type: application/json" \
  -d '{
    "addr_addr": "user@example.com",
    "otp": "123456"
  }'
```

**Response:**
Sets `HELPLINE_SESSION_ID` cookie for subsequent requests.

```json
{
  "success": true,
  "user": {
    "id": 123,
    "username": "operator_name",
    "role": "case_manager"
  }
}
```

#### Step 3: Make Authenticated Requests
```bash
curl -X GET https://your-domain.com/helpline/api/cases \
  -H "Cookie: HELPLINE_SESSION_ID=abc123xyz..."
```

#### Step 4: Logout
```bash
curl -X POST https://your-domain.com/helpline/api/logout \
  -H "Cookie: HELPLINE_SESSION_ID=abc123xyz..."
```

### Database Schema

**Sessions Table (`helpline.session`):**
```sql
CREATE TABLE session (
  session_id VARCHAR(255) PRIMARY KEY,
  user_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  ip_address VARCHAR(45),
  user_agent TEXT
);
```

**Authentication Table (`helpline.auth`):**
```sql
CREATE TABLE auth (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(20),
  role ENUM('admin', 'supervisor', 'case_manager', 'operator'),
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP NULL
);
```

---

## AI Service Authentication

### Technology Stack
- **Backend:** FastAPI 0.116+ (Python 3.11+)
- **Task Queue:** Celery with Redis
- **Container:** Docker with GPU support
- **Authentication:** API Key / Token-based (optional)

### API Endpoints (No Authentication Required by Default)

The AI service is designed for internal use and doesn't enforce authentication by default. It's accessed by the Helpline service backend.

#### Audio Processing
```bash
# Complete pipeline processing
curl -X POST http://localhost:8123/audio/process \
  -F "audio=@recording.wav" \
  -F "language=sw" \
  -F "include_translation=true"
```

#### Individual Model Services
```bash
# Transcription only
curl -X POST http://localhost:8123/whisper/transcribe \
  -F "audio=@recording.wav" \
  -F "language=sw"

# Translation only
curl -X POST http://localhost:8123/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Msichana mdogo ana miaka 12",
    "source_language": "sw",
    "target_language": "en"
  }'

# Named Entity Recognition
curl -X POST http://localhost:8123/ner/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Maria lives in Nairobi and works at City Hospital"
  }'
```

#### Health Checks
```bash
# Detailed system status
curl http://localhost:8123/health/detailed

# Model loading status
curl http://localhost:8123/health/models

# Worker status
curl http://localhost:8123/audio/workers/status
```

### Adding Authentication to AI Service (Optional)

For production deployments where AI service needs external access:

**Option 1: API Key Authentication**

```python
# app/middleware/auth.py
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("AI_SERVICE_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Usage in endpoint
@app.post("/audio/process")
async def process_audio(
    audio: UploadFile,
    api_key: str = Depends(verify_api_key)
):
    # Process audio
    pass
```

**Option 2: JWT Token Authentication**

```python
# app/middleware/jwt_auth.py
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## Development Environment Setup

### Helpline Service Setup

#### 1. Database Setup
```bash
# Create MySQL user with unix_socket authentication
sudo mysql -e "CREATE USER 'nginx'@'localhost' IDENTIFIED VIA unix_socket;"

# Create database
sudo mysql -e "CREATE DATABASE helpline;"

# Import schema
sudo mysql helpline < /usr/src/OpenChs/rest_api/uchl.sql

# Grant permissions
sudo mysql -e "
GRANT SELECT, INSERT ON helpline.* TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.auth TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.contact TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.kase TO 'nginx'@'localhost';
GRANT DELETE ON helpline.session TO 'nginx'@'localhost';
FLUSH PRIVILEGES;"
```

#### 2. PHP-FPM Configuration
```bash
# Install PHP and extensions
sudo apt-get install php8.2 php8.2-fpm php8.2-mysql

# Configure PHP-FPM
sudo nano /etc/php/8.2/fpm/pool.d/www.conf
```

**Key settings in `www.conf`:**
```ini
user = nginx
group = nginx
listen = /run/php/php8.2-fpm.sock
listen.owner = nginx
listen.group = nginx
```

#### 3. Nginx Configuration
```bash
# Install Nginx
sudo apt-get install nginx

# Copy SSL certificates
sudo mkdir -p /etc/pki/openchs/private
sudo cp openchs.crt /etc/pki/openchs/
sudo cp openchs.key /etc/pki/openchs/private/
```

**Nginx server block:**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    root /var/www/html;

    ssl_certificate "/etc/pki/openchs/openchs.crt";
    ssl_certificate_key "/etc/pki/openchs/private/openchs.key";
    ssl_protocols TLSv1.2 TLSv1.3;

    location /helpline/ {
        index index.php index.html;
        try_files $uri $uri/ /helpline/api/index.php?$args;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php8.2-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

#### 4. Deploy Application
```bash
# Copy application files
sudo cp -r /path/to/helpline/files/* /var/www/html/helpline/

# Set permissions
sudo chown -R nginx:nginx /var/www/html/helpline/
sudo chmod -R 755 /var/www/html/helpline/

# Restart services
sudo systemctl restart php8.2-fpm
sudo systemctl restart nginx
```

### AI Service Setup

#### 1. Clone and Configure
```bash
git clone <ai-service-repo>
cd ai-service

# Copy environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Key environment variables:**
```bash
# Core settings
DEBUG=false
LOG_LEVEL=INFO
MAX_CONCURRENT_GPU_REQUESTS=1
REQUEST_TIMEOUT=300

# Redis configuration
REDIS_URL=redis://localhost:6379/0
REDIS_TASK_DB=1

# Optional authentication
AI_SERVICE_API_KEY=your-secure-api-key
```

#### 2. Start with Docker
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ai-pipeline
```

#### 3. Verify Installation
```bash
# Check API health
curl http://localhost:8123/health/detailed

# Check GPU availability
curl http://localhost:8123/health/models

# Test transcription
curl -X POST http://localhost:8123/whisper/transcribe \
  -F "audio=@test_audio.wav" \
  -F "language=en"
```

---

## Cross-Service Integration

### Helpline Calling AI Service

The Helpline backend (PHP) calls the AI service for audio processing:

```php
<?php
// helpline/api/services/AIServiceClient.php

class AIServiceClient {
    private $baseUrl;
    private $apiKey;
    
    public function __construct() {
        $this->baseUrl = getenv('AI_SERVICE_URL') ?: 'http://localhost:8123';
        $this->apiKey = getenv('AI_SERVICE_API_KEY');
    }
    
    public function transcribeAudio($audioPath, $language = 'sw') {
        $ch = curl_init();
        
        $postFields = [
            'audio' => new CURLFile($audioPath),
            'language' => $language,
            'include_translation' => 'true'
        ];
        
        $headers = [];
        if ($this->apiKey) {
            $headers[] = "X-API-Key: {$this->apiKey}";
        }
        
        curl_setopt_array($ch, [
            CURLOPT_URL => "{$this->baseUrl}/audio/process",
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $postFields,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 300
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception("AI Service error: HTTP $httpCode");
        }
        
        return json_decode($response, true);
    }
    
    public function getTaskStatus($taskId) {
        $ch = curl_init();
        
        curl_setopt_array($ch, [
            CURLOPT_URL => "{$this->baseUrl}/audio/task/{$taskId}",
            CURLOPT_RETURNTRANSFER => true
        ]);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
}
?>
```

**Usage in case processing:**
```php
<?php
// Example: Process audio when case is created
$aiClient = new AIServiceClient();

try {
    // Transcribe and analyze audio
    $result = $aiClient->transcribeAudio(
        $_FILES['audio']['tmp_name'],
        'sw'  // Swahili
    );
    
    // Store results in case
    $caseData = [
        'transcript' => $result['transcript'],
        'translation' => $result['translation'],
        'entities' => json_encode($result['entities']),
        'classification' => $result['classification']['main_category'],
        'priority' => $result['classification']['priority']
    ];
    
    // Save to database
    saveCaseData($caseData);
    
} catch (Exception $e) {
    error_log("AI processing failed: " . $e->getMessage());
    // Handle error - case can still be created without AI analysis
}
?>
```

---

## Testing Authentication

### Helpline Service Tests

```bash
# Test OTP flow
curl -X POST https://localhost/helpline/api/sendOTP \
  -k \  # Skip SSL verification for local testing
  -H "Content-Type: application/json" \
  -d '{"addr_addr": "test@example.com", "addr_type": "email"}'

# Check session creation
sudo mysql -e "SELECT * FROM helpline.session ORDER BY created_at DESC LIMIT 5;"
```

### AI Service Tests

```bash
# Test health endpoint
curl http://localhost:8123/health/detailed | jq

# Test audio processing
curl -X POST http://localhost:8123/whisper/transcribe \
  -F "audio=@sample.wav" \
  -F "language=en" | jq

# Test worker status
curl http://localhost:8123/audio/workers/status | jq
```

---

## Security Considerations

### Helpline Service Security

**SSL/TLS Configuration:**
- Use strong ciphers (already configured in nginx)
- TLS 1.2 and 1.3 only
- HSTS headers recommended

**Session Security:**
```php
// session_config.php
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1);  // HTTPS only
ini_set('session.cookie_samesite', 'Lax');
ini_set('session.gc_maxlifetime', 86400);  // 24 hours
```

**Database Security:**
- Unix socket authentication (no passwords over network)
- Minimal permissions per user
- Regular session cleanup

### AI Service Security

**Network Isolation:**
```yaml
# docker-compose.yml
services:
  ai-pipeline:
    networks:
      - internal
    # Only expose to Helpline service, not public internet
```

**API Key Protection:**
```bash
# .env
AI_SERVICE_API_KEY=$(openssl rand -hex 32)

# Rotate keys periodically
# Store in secure secret management system
```

---

## Troubleshooting

### Helpline Service Issues

**1. "Session not found" errors**
```bash
# Check session table
sudo mysql -e "SELECT COUNT(*) FROM helpline.session;"

# Check PHP session configuration
php -i | grep session

# View PHP-FPM logs
sudo tail -f /var/log/php8.2-fpm.log
```

**2. "Database connection failed"**
```bash
# Verify unix socket authentication
sudo mysql -e "SELECT user, host, plugin FROM mysql.user WHERE user='nginx';"

# Check PHP-FPM user
ps aux | grep php-fpm

# Test connection
sudo -u nginx mysql -e "SELECT 1;"
```

**3. "OTP not sending"**
```bash
# Check PHP mail configuration
php -i | grep mail

# View nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### AI Service Issues

**1. "Model loading failed"**
```bash
# Check model files
docker-compose exec ai-pipeline ls -la /app/models/

# Check GPU availability
docker-compose exec ai-pipeline nvidia-smi

# View detailed logs
docker-compose logs ai-pipeline | grep -i "model"
```

**2. "Worker not responding"**
```bash
# Check Celery worker status
docker-compose exec celery-worker celery -A app.celery_app inspect active

# Restart workers
docker-compose restart celery-worker

# Check Redis connectivity
docker-compose exec ai-pipeline redis-cli ping
```

**3. "Out of memory errors"**
```bash
# Check GPU memory
docker stats

# Adjust concurrent requests
# Edit .env: MAX_CONCURRENT_GPU_REQUESTS=1

# Restart services
docker-compose restart
```

---

## Production Deployment Checklist

### Helpline Service
- [ ] SSL certificates properly installed
- [ ] Database backups configured
- [ ] Session cleanup cron job setup
- [ ] PHP-FPM tuned for production load
- [ ] Nginx configured with security headers
- [ ] Firewall rules limiting access
- [ ] Monitoring and logging enabled

### AI Service
- [ ] GPU drivers and CUDA installed
- [ ] Docker volumes for model persistence
- [ ] Redis persistence enabled
- [ ] Resource limits configured
- [ ] Health check monitoring setup
- [ ] Log aggregation configured
- [ ] Backup AI service instance ready

This authentication guide provides complete setup and integration instructions for both the Helpline PHP/MySQL service and the AI FastAPI/Docker service in the OpenCHS system.