# Development Guide

Guide for developers contributing to the Helpline Service.

## Development Environment Setup

### Prerequisites

- Docker & Docker Compose
- Git
- Code editor (VS Code recommended)
- Basic knowledge of PHP, JavaScript, MySQL
- Familiarity with REST APIs

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/openchlai/ai.git
cd ai/helplinev1

# 2. Setup environment
cp .env.example .env

# 3. Configure for development
# Edit .env:
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=debug

# 4. Start containers
docker-compose up -d

# 5. Access application
open http://localhost:8888
```

## Project Structure

```
helplinev1/
├── application/          # Frontend (PHP, JS, CSS)
│   ├── views/           # UI templates
│   ├── assets/          # CSS, JS, images
│   └── config/          # Frontend configuration
├── rest_api/            # Backend API
│   ├── api/             # Endpoint implementations
│   ├── lib/             # Core libraries
│   │   ├── rest.php
│   │   ├── session.php
│   │   └── database.php
│   └── config/          # Database schemas
├── docker/              # Docker configuration
│   ├── nginx/          # Nginx configuration
│   ├── php/            # PHP configuration
│   └── mysql/          # MySQL init scripts
└── docker-compose.yml   # Service orchestration
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature

# Verify you're on the right branch
git branch
```

### 2. Make Changes

```bash
# Frontend changes
# Edit files in application/

# Backend changes
# Edit files in rest_api/

# Database changes
# Update sql files in docker/mysql/
```

### 3. Test Changes

```bash
# Development server automatically hot-reloads
# Just refresh your browser

# Clear cache if needed
docker-compose exec helpline-php php -r "system('rm -rf storage/cache/*');"

# Check logs for errors
docker-compose logs -f helpline-php
```

### 4. Debug with Logging

```php
// In PHP code
error_log("Debug message: " . json_encode($data));

// View logs
docker-compose logs -f helpline-php | grep "Debug message"
```

### 5. Commit and Push

```bash
# Stage changes
git add .

# Commit with message
git commit -m "Add feature: description"

# Push to remote
git push origin feature/your-feature
```

## Backend Development (PHP REST API)

### Creating New API Endpoint

1. **Create endpoint handler** in `rest_api/api/`:

```php
<?php
// rest_api/api/v1/cases.php

class CasesAPI {
    protected $db;

    public function __construct($db) {
        $this->db = $db;
    }

    public function create($request) {
        // Validate input
        if (empty($request['case_type'])) {
            return ['error' => 'Case type required'];
        }

        // Create case
        $query = "INSERT INTO cases (case_type, description, created_at)
                 VALUES (?, ?, NOW())";
        $stmt = $this->db->prepare($query);
        $stmt->execute([$request['case_type'], $request['description']]);

        return ['id' => $this->db->lastInsertId(), 'status' => 'created'];
    }
}
```

2. **Register route** in router:

```php
// rest_api/lib/router.php
$router->post('/cases', 'CasesAPI@create');
```

3. **Test endpoint**:

```bash
curl -X POST http://localhost:8888/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{"case_type": "abuse", "description": "..."}'
```

### Database Queries

```php
// Simple query
$query = "SELECT * FROM users WHERE id = ?";
$stmt = $db->prepare($query);
$stmt->execute([$id]);
$result = $stmt->fetch();

// Insert
$query = "INSERT INTO cases (type, description) VALUES (?, ?)";
$stmt = $db->prepare($query);
$stmt->execute([$type, $description]);

// Update
$query = "UPDATE cases SET status = ? WHERE id = ?";
$stmt = $db->prepare($query);
$stmt->execute([$status, $id]);

// Always use prepared statements to prevent SQL injection
```

## Frontend Development (JavaScript/CSS)

### File Organization

```
application/
├── views/
│   ├── cases/
│   │   ├── list.php
│   │   ├── create.php
│   │   └── detail.php
│   ├── dashboard.php
│   └── layout.php
├── assets/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js
│   │   └── api.js
│   └── images/
```

### Creating New Page

1. **Create view** file `application/views/cases/list.php`:

```php
<?php include '../layout.php'; ?>
<div class="container">
    <h1>Cases</h1>
    <button onclick="newCase()" class="btn-primary">New Case</button>
    <table id="casesTable">
        <thead>
            <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="casesBody"></tbody>
    </table>
</div>

<script>
function loadCases() {
    fetch('/api/v1/cases')
        .then(r => r.json())
        .then(data => {
            // Populate table
        });
}

window.onload = loadCases;
</script>
```

2. **Add route** in router

3. **Style with CSS** in `assets/css/style.css`

## Testing

### Manual Testing

```bash
# Test in browser
http://localhost:8888

# Test API directly
curl http://localhost:8888/api/v1/cases

# Test with Postman
# Import endpoints into Postman
# Set base URL to http://localhost:8888/api/v1
```

### Running Tests

```bash
# If using PHPUnit
docker-compose exec helpline-php ./vendor/bin/phpunit

# If using Jest for JavaScript
docker-compose exec helpline-php npm test
```

## Database Migrations

### Create New Table

1. **Create migration file** `docker/mysql/migrations/001_create_cases.sql`:

```sql
CREATE TABLE IF NOT EXISTS cases (
    id INT PRIMARY KEY AUTO_INCREMENT,
    case_type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_case_type ON cases(case_type);
CREATE INDEX idx_status ON cases(status);
```

2. **Apply migration**:

```bash
# Migrations run automatically on container start
# Or manually:
docker-compose exec helpline-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD \
  -D $MYSQL_DATABASE < migrations/001_create_cases.sql
```

## Common Development Tasks

### View Live Logs

```bash
# PHP logs
docker-compose logs -f helpline-php

# Nginx logs
docker-compose logs -f helpline-nginx

# MySQL logs
docker-compose logs -f helpline-mysql
```

### Access Container Shell

```bash
# PHP container
docker-compose exec helpline-php bash

# Run PHP directly
docker-compose exec helpline-php php -r "phpinfo();"

# MySQL container
docker-compose exec helpline-mysql bash
docker-compose exec helpline-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD
```

### Clear Application Cache

```bash
docker-compose exec helpline-php php -r "
    @array_map('unlink', glob('storage/cache/*'));
    echo 'Cache cleared';
"
```

### Restart a Service

```bash
docker-compose restart helpline-php
docker-compose restart helpline-nginx
docker-compose restart helpline-mysql
```

### Install PHP Dependencies

```bash
docker-compose exec helpline-php composer install
```

## Code Standards

### PHP Code Style

```php
<?php
// Use PSR-12 coding standards

class CaseManager {
    private $database;

    public function __construct($db) {
        $this->database = $db;
    }

    public function getCase($id) {
        // Method body
        return $case;
    }
}

// 4-space indentation
// No trailing spaces
// Single quotes for strings (unless interpolation)
```

### JavaScript Style

```javascript
// Use ES6+ syntax
const CaseAPI = {
    async getCase(id) {
        const response = await fetch(`/api/v1/cases/${id}`);
        return response.json();
    },

    async createCase(data) {
        const response = await fetch('/api/v1/cases', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
};
```

## Git Workflow Reminder

```bash
# Create feature branch
git checkout -b feature/feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/feature-name

# Create Pull Request (GitHub)
# Request review
# Wait for approval
# Merge to dev (automatic staging deploy)

# Test in staging: http://192.168.10.119/helpline
```

## Debugging Tips

### Enable Debug Mode

```bash
# In .env
APP_DEBUG=true
LOG_LEVEL=debug

# Restart
docker-compose restart
```

### Check Error Logs

```bash
# View full error details
docker-compose logs -f helpline-php | grep -A 10 "Error"

# Or check log file directly
docker-compose exec helpline-php tail -f /var/log/helpline/error.log
```

### Database Debugging

```bash
# Connect to MySQL
docker-compose exec helpline-mysql mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE

# Run queries
SELECT * FROM cases LIMIT 5;
EXPLAIN SELECT * FROM cases WHERE id = 1;
```

## Resources

- [PHP Documentation](https://www.php.net/)
- [REST API Best Practices](https://restfulapi.net/)
- [MySQL Optimization](https://dev.mysql.com/doc/)
- [JavaScript ES6+](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference)
- [Git Basics](https://git-scm.com/book/en/v2)
