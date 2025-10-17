# Contribution Guide

## Welcome to OpenCHS

Thank you for your interest in contributing to the AI-Enhanced Child Helpline System! This project directly supports child protection services in Kenya, Uganda, Tanzania, and Lesotho, helping protect vulnerable children through technology.

## Table of Contents
- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Testing Requirements](#testing-requirements)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [Getting Help](#getting-help)

---

## Quick Start

### Prerequisites
- **For Helpline Service:** PHP 8.2+, MySQL 5.7+, Nginx
- **For AI Service:** Docker 20.10+, Docker Compose 2.0+, Python 3.11+
- **Optional:** NVIDIA GPU for AI model acceleration
- **Tools:** Git, curl, text editor

### First Contribution in 5 Steps

1. **Fork and clone:**
   ```bash
   git clone git@github.com:your-username/ai.git
   cd ai
   ```

2. **Choose your area:**
   - `helplinev1/` - PHP case management system
   - `ai_service/` - Python AI processing pipeline
   - `frontend/` - React/Vue.js user interface
   - `docs/` - Documentation improvements

3. **Set up development environment** (see [Development Setup](#development-setup))

4. **Make your changes and test:**
   ```bash
   # For helpline changes
   # Test PHP code manually
   
   # For AI service changes
   cd ai_service
   python -m pytest tests/
   ```

5. **Submit pull request** (see [Pull Request Process](#pull-request-process))

---

## System Architecture

OpenCHS consists of two main services:

```
┌─────────────────────────────────────────────────────────┐
│                    OpenCHS Platform                      │
├──────────────────────────┬──────────────────────────────┤
│   Helpline Service       │      AI Service              │
│   (PHP/MySQL/Nginx)      │   (Python/FastAPI/Docker)    │
│                          │                              │
│   - Case Management      │   - Voice Transcription      │
│   - User Authentication  │   - Language Translation     │
│   - Communication Logs   │   - Case Classification      │
│   - File Management      │   - Entity Recognition       │
│   - Real-time Call Ops   │   - Risk Assessment          │
└──────────────────────────┴──────────────────────────────┘
```

### Technology Stack

| Component | Helpline Service | AI Service |
|-----------|-----------------|------------|
| **Language** | PHP 8.2 | Python 3.11+ |
| **Framework** | Custom REST API | FastAPI |
| **Database** | MySQL 5.7+ | Redis (queue) |
| **Web Server** | Nginx + PHP-FPM | Uvicorn |
| **Container** | N/A | Docker + Compose |
| **Task Queue** | N/A | Celery |

---

## Development Setup

### Helpline Service Setup

#### 1. Install Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y php8.2 php8.2-fpm php8.2-mysql nginx mysql-server

# macOS
brew install php@8.2 nginx mysql
```

#### 2. Database Setup
```bash
# Start MySQL
sudo systemctl start mysql  # Linux
brew services start mysql   # macOS

# Create database and user
sudo mysql << EOF
CREATE USER 'nginx'@'localhost' IDENTIFIED VIA unix_socket;
CREATE DATABASE helpline;
GRANT SELECT, INSERT, UPDATE, DELETE ON helpline.* TO 'nginx'@'localhost';
FLUSH PRIVILEGES;
EOF

# Import schema
cd helplinev1
sudo mysql helpline < rest_api/uchl.sql
```

#### 3. Configure PHP-FPM
```bash
# Edit PHP-FPM pool configuration
sudo nano /etc/php/8.2/fpm/pool.d/www.conf
```

**Key settings:**
```ini
user = nginx
group = nginx
listen = /run/php/php8.2-fpm.sock
listen.owner = nginx
listen.group = nginx
```

#### 4. Configure Nginx
```bash
# Create local development config
sudo nano /etc/nginx/sites-available/openchs-dev
```

**Development configuration:**
```nginx
server {
    listen 8080;
    server_name localhost;
    root /path/to/ai/helplinev1/public;

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

```bash
# Enable site and restart
sudo ln -s /etc/nginx/sites-available/openchs-dev /etc/nginx/sites-enabled/
sudo systemctl restart php8.2-fpm nginx
```

#### 5. Verify Setup
```bash
# Test PHP
php -v

# Test database connection
sudo -u nginx mysql -e "SELECT 1;"

# Test API endpoint
curl http://localhost:8080/helpline/api/health
```

### AI Service Setup

#### 1. Install Docker
```bash
# Follow official Docker installation guide
# https://docs.docker.com/engine/install/

# Verify installation
docker --version
docker-compose --version
```

#### 2. Configure Environment
```bash
cd ai_service
cp .env.example .env

# Edit configuration
nano .env
```

**Development `.env` settings:**
```bash
DEBUG=true
LOG_LEVEL=DEBUG
MAX_CONCURRENT_GPU_REQUESTS=1
REDIS_URL=redis://redis:6379/0
```

#### 3. Start Services
```bash
# Build and start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 4. Verify Setup
```bash
# Check health
curl http://localhost:8123/health/detailed

# Test transcription
curl -X POST http://localhost:8123/whisper/transcribe \
  -F "audio=@test_audio.wav" \
  -F "language=en"
```

### Frontend Setup (If Contributing)

```bash
cd frontend
npm install
npm run dev
```

---

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical production fixes
- `docs/description` - Documentation updates

### Creating a Feature Branch

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/add-case-priority-filter

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "feat(helpline): add priority filter to case list API"

# Push to your fork
git push origin feature/add-case-priority-filter
```

### Commit Message Format

Use conventional commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style (formatting, no logic change)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

**Scopes:**
- `helpline` - Helpline service changes
- `ai` - AI service changes
- `frontend` - Frontend changes
- `docs` - Documentation
- `deploy` - Deployment configurations

**Examples:**
```
feat(ai): add support for Luganda language transcription
fix(helpline): correct session timeout calculation
docs(api): update authentication flow documentation
test(ai): add unit tests for translation service
```

---

## Testing Requirements

### Coverage Requirements (UNICEF Compliance)
- **Minimum:** 80% overall coverage
- **AI Service:** 80% coverage required
- **Helpline Service:** 80% coverage required
- **New Features:** 100% coverage for new code

### Helpline Service Testing

**Manual Testing:**
```bash
# Test case creation
curl -X POST http://localhost:8080/helpline/api/cases \
  -H "Content-Type: application/json" \
  -H "Cookie: HELPLINE_SESSION_ID=test-session" \
  -d '{
    "title": "Test Case",
    "priority": "high",
    "category": "abuse"
  }'

# Verify in database
sudo mysql -e "SELECT * FROM helpline.kase ORDER BY created_at DESC LIMIT 1;"
```

**PHP Unit Tests (if available):**
```bash
cd helplinev1
./vendor/bin/phpunit tests/
```

### AI Service Testing

**Unit Tests:**
```bash
cd ai_service

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_transcription.py -v

# Run with coverage
python -m pytest --cov=app tests/ --cov-report=html
```

**Integration Tests:**
```bash
# Test complete audio pipeline
python -m pytest tests/test_integration.py -v

# Test individual models
python -m pytest tests/test_models/ -v
```

**Manual API Testing:**
```bash
# Test transcription
curl -X POST http://localhost:8123/whisper/transcribe \
  -F "audio=@sample.wav" \
  -F "language=sw"

# Test translation
curl -X POST http://localhost:8123/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mtoto ana miaka kumi",
    "source_language": "sw",
    "target_language": "en"
  }'
```

### Testing Checklist

Before submitting a pull request:

- [ ] All existing tests pass
- [ ] New features have tests with 100% coverage
- [ ] Manual testing completed for user-facing changes
- [ ] API endpoints tested with curl/Postman
- [ ] No broken links in documentation
- [ ] Code follows style guidelines

---

## Code Standards

### PHP Code Standards (Helpline Service)

**Follow PSR-12 coding style:**
```php
<?php
// Good: Clear function names, type hints, documentation
class CaseManager
{
    /**
     * Create a new case with validation
     *
     * @param array $caseData Case information
     * @return array Created case details
     * @throws ValidationException
     */
    public function createCase(array $caseData): array
    {
        // Validate input
        $this->validateCaseData($caseData);
        
        // Insert into database
        $caseId = $this->db->insert('kase', $caseData);
        
        return $this->getCaseById($caseId);
    }
}
```

**Key guidelines:**
- Use type hints for parameters and return types
- Add PHPDoc comments for public methods
- Use meaningful variable names
- Keep functions focused and small
- Validate all user inputs
- Use prepared statements for SQL queries

### Python Code Standards (AI Service)

**Follow PEP 8 and use type hints:**
```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service for audio transcription using Whisper model."""
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: str = "en",
        task: str = "transcribe"
    ) -> Dict[str, any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: ISO language code (default: "en")
            task: Task type - "transcribe" or "translate"
            
        Returns:
            Dictionary containing transcription results
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            TranscriptionError: If transcription fails
        """
        logger.info(f"Transcribing audio: {audio_path}")
        
        # Validate inputs
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Process audio
        result = self.model.transcribe(audio_path, language=language)
        
        return {
            "text": result["text"],
            "language": language,
            "confidence": result.get("confidence", 0.0)
        }
```

**Key guidelines:**
- Use type hints for all function signatures
- Add docstrings for all public functions
- Use meaningful variable names
- Keep functions focused (single responsibility)
- Use logging instead of print statements
- Handle exceptions appropriately
- Use list/dict comprehensions when appropriate

### SQL Standards

```sql
-- Good: Readable, properly formatted
SELECT 
    k.id,
    k.title,
    k.priority,
    k.created_at,
    u.username AS assigned_to
FROM 
    kase k
    LEFT JOIN auth u ON k.assigned_user_id = u.id
WHERE 
    k.status = 'open'
    AND k.priority IN ('high', 'critical')
ORDER BY 
    k.created_at DESC
LIMIT 20;

-- Use parameterized queries in PHP
$stmt = $pdo->prepare("
    SELECT * FROM kase 
    WHERE status = :status 
    AND created_at > :date
");
$stmt->execute([
    'status' => $status,
    'date' => $date
]);
```

### Documentation Standards

- Update relevant documentation for code changes
- Include code examples in API documentation
- Keep README files up to date
- Add inline comments for complex logic
- Document all environment variables
- Include setup instructions for new features

---

## Pull Request Process

### Before Submitting

1. **Sync with latest develop:**
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout your-feature-branch
   git rebase develop
   ```

2. **Run tests:**
   ```bash
   # For AI service
   cd ai_service && python -m pytest tests/
   
   # For helpline service
   # Manual testing or PHPUnit if available
   ```

3. **Check code quality:**
   ```bash
   # Python
   black app/  # Format code
   flake8 app/  # Check style
   
   # PHP
   # Ensure PSR-12 compliance
   ```

### Creating Pull Request

**Use this template:**

```markdown
## Description
Brief description of changes and why they're needed.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Components Changed
- [ ] Helpline Service (PHP)
- [ ] AI Service (Python)
- [ ] Frontend
- [ ] Documentation
- [ ] Infrastructure

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Branch is up to date with develop

## Screenshots (if applicable)
Add screenshots for UI changes.

## Related Issues
Closes #123
```

### Review Process

1. **Automated checks run:** Tests, linting, coverage
2. **Maintainer review:** Code quality, architecture, tests
3. **Feedback iteration:** Address review comments
4. **Approval and merge:** Maintainer merges when approved

### After Merge

- Delete your feature branch
- Update your local develop branch
- Check deployment status (if applicable)

---

## Getting Help

### Documentation
- **API Reference:** See `api-reference/` directory
- **Architecture:** See `ARCHITECTURE.md`
- **Deployment:** See `deployment-administration/`

### Communication
- **GitHub Issues:** Report bugs and request features
- **GitHub Discussions:** Ask questions and share ideas
- **Pull Request Comments:** Get feedback on code

### Common Issues

**Helpline Setup Issues:**
- Database connection: Check unix_socket authentication
- PHP-FPM errors: Check user/group permissions
- Nginx errors: Check configuration syntax

**AI Service Issues:**
- Docker errors: Check Docker daemon is running
- Model loading: Ensure sufficient disk space
- GPU errors: Check NVIDIA drivers and runtime

**General Issues:**
- Search existing issues before creating new ones
- Include error messages and logs
- Describe steps to reproduce
- Mention your environment (OS, versions)

---

## Recognition

Contributors are recognized through:
- Contributor list in README
- Release notes acknowledgments
- GitHub contributor stats
- Special recognition for significant contributions

Thank you for contributing to child protection through technology! Every contribution, no matter how small, helps protect vulnerable children worldwide.