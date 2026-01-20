# Architecture

Technical architecture overview of the Helpline Service.

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Users / Clients                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│         Nginx Reverse Proxy & Load Balancer                 │
│  • SSL/TLS Termination                                      │
│  • Static File Serving                                      │
│  • Request Routing                                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
┌──────────────────┐  ┌─────────────────┐
│  PHP-FPM         │  │  PHP-FPM        │
│  Application     │  │  Application    │
│  (Scaled)        │  │  (Scaled)       │
└────────┬─────────┘  └─────────┬───────┘
         │                      │
         └──────────┬───────────┘
                    ↓
        ┌───────────────────────┐
        │   MySQL Database      │
        │  • Cases              │
        │  • Clients            │
        │  • Users              │
        │  • Communications     │
        └───────────────────────┘
```

## Component Layers

### 1. Frontend Layer (PHP + JavaScript)

**Purpose:** User interface and client-side logic

**Technologies:**
- PHP templates
- HTML5
- CSS3
- JavaScript (ES6+)
- AJAX for dynamic updates

**Components:**
- Dashboard
- Case Management UI
- User Management
- Reporting & Analytics
- Communication Interface

### 2. API Layer (PHP REST API)

**Purpose:** Provide backend services and data access

**Structure:**
```
rest_api/
├── api/                    # Endpoint handlers
│   ├── v1/
│   │   ├── cases.php
│   │   ├── clients.php
│   │   ├── users.php
│   │   ├── communications.php
│   │   └── dashboard.php
│   └── middleware/         # Authentication, validation
├── lib/                    # Core libraries
│   ├── rest.php           # REST framework
│   ├── session.php        # Session management
│   ├── database.php       # Database connection
│   └── auth.php           # Authentication
└── config/                # Database schemas
```

**Endpoints:**
- `/api/v1/cases` - Case management
- `/api/v1/clients` - Client management
- `/api/v1/users` - User management
- `/api/v1/communications` - Messages and calls
- `/api/v1/dashboard` - Analytics and reporting

### 3. Data Layer (MySQL)

**Purpose:** Persistent data storage

**Main Tables:**
- `users` - System users and agents
- `cases` - Case records
- `clients` - Client/caller information
- `communications` - Messages, calls, SMS
- `case_notes` - Case documentation
- `attachments` - File attachments
- `audit_logs` - System audit trail

**Relationships:**
```
users
├── cases (created_by)
├── communications (user_id)
└── audit_logs (user_id)

cases
├── clients
├── communications
├── case_notes
└── attachments

clients
├── communications
└── case_history
```

### 4. Container Layer (Docker)

**Services:**

| Service | Image | Purpose |
|---------|-------|---------|
| nginx | nginx:alpine | Web server & reverse proxy |
| php | php:8.2-fpm | Application runtime |
| mysql | mysql:8.0 | Database server |
| ai-pipeline | openchlai/ai | Optional AI services |

## Request Flow

### Case Creation Flow

```
1. User submits form in browser
   ↓
2. JavaScript posts to /api/v1/cases
   ↓
3. Nginx routes to PHP-FPM
   ↓
4. API handler validates input
   ↓
5. Authenticate user (session/JWT)
   ↓
6. Check permissions
   ↓
7. Create case in database
   ↓
8. Return response (JSON)
   ↓
9. JavaScript updates UI
   ↓
10. Dashboard refreshes
```

### Real-time Communication Flow

```
1. User sends message via web UI
   ↓
2. AJAX request to /api/v1/communications
   ↓
3. Message stored in database
   ↓
4. If VoIP enabled: Forward to phone system
   ↓
5. If SMS enabled: Send via SMS provider
   ↓
6. Broadcast to relevant agents
   ↓
7. UI updates in real-time
```

## Scalability Architecture

### Horizontal Scaling

```
Load Balancer
     ↓
   ┌─┴─┐
   ↓   ↓
 PHP  PHP
   ├─ ─┤
   ↓   ↓
  DB (Replicated)
```

**Strategy:**
- Multiple PHP-FPM containers behind load balancer
- MySQL master-slave replication (optional)
- Shared session storage (Redis or DB)
- Stateless API design

### Vertical Scaling

- Increase PHP memory limit
- Optimize database queries
- Enable caching
- Use database connection pooling

### Configuration

```bash
# docker-compose.yml
services:
  php:
    deploy:
      replicas: 3  # Scale to 3 instances

# Or:
docker-compose up -d --scale helpline-php=3
```

## Data Flow Architecture

### Case Processing Pipeline

```
Incoming Call/Message
      ↓
Receive & Store
      ↓
Categorize (Manual)
      ↓
Create Case Record
      ↓
Assign to Agent
      ↓
Optional: Send to AI Pipeline
      ├─ Transcription
      ├─ Translation
      ├─ Entity Extraction
      ├─ Classification
      └─ Summarization
      ↓
Update Case with Analysis
      ↓
Generate Insights
      ↓
Notify Supervisor
      ↓
Dashboard Update
```

## Security Architecture

### Authentication Flow

```
User Login
    ↓
Validate Credentials
    ↓
Generate Session/Token
    ↓
Store in Session/Database
    ↓
Return to Client
    ↓
Include in Requests
    ↓
Verify on Each Request
```

### Authorization

```
Request
  ↓
Check User Role
  ↓
Check Permissions
  ├─ Admin: All access
  ├─ Supervisor: Team access
  └─ Agent: Own cases only
  ↓
Approve or Deny
```

### Data Security

- Password hashing: bcrypt
- Session encryption: Secure cookies
- Database: SQL prepared statements
- API: HTTPS/TLS
- Audit logging: All actions logged

## Performance Optimization

### Caching Strategy

```
Request
  ↓
Check Cache
├─ HIT → Return cached
└─ MISS
    ↓
  Query Database
    ↓
  Cache Result
    ↓
  Return Response
```

**Cache Layers:**
- Browser cache (HTML, CSS, JS)
- Application cache (query results)
- Database query cache
- Redis (session store)

### Database Optimization

- Indexing on frequently queried fields
- Query optimization
- Connection pooling
- Read replicas (optional)

### API Optimization

- Pagination (default: 20 items per page)
- Filtering to reduce dataset
- Lazy loading
- Compression (gzip)

## Integration Points

### External Systems

1. **VoIP System** (Optional)
   - Asterisk/FreeSWITCH
   - Inbound call routing
   - Call recording
   - Real-time transcription

2. **SMS Gateway** (Optional)
   - Twilio / Nexmo
   - Inbound SMS receiving
   - Outbound SMS sending
   - SMS threading

3. **AI Pipeline** (Optional)
   - Transcription service
   - Translation service
   - Entity extraction
   - Case classification
   - Summarization

4. **Email** (Optional)
   - Notifications
   - Reports
   - User communications

## Deployment Architecture

### Development

```
Single Docker Compose
├── Nginx (1)
├── PHP-FPM (1)
└── MySQL (1)
```

### Staging

```
Docker Compose with Scaling
├── Nginx (1)
├── PHP-FPM (3)
├── MySQL (1)
└── Optional: AI Pipeline
```

### Production

```
Kubernetes Cluster
├── Ingress Controller
├── PHP Pods (5+)
├── MySQL StatefulSet
├── Redis (Session)
├── Optional: AI Service
└── Monitoring Stack
```

## Disaster Recovery

### Backup Strategy

- Database: Daily backups
- Files: Continuous sync
- Retention: 30 days minimum
- Testing: Weekly restore tests

### High Availability

- Database replication (master-slave)
- Load balancing
- Automated failover
- Health checks every 30s

### Recovery Time Objectives

| System | RTO | RPO |
|--------|-----|-----|
| Database | 1 hour | 1 hour |
| API | 5 min | 5 min |
| Files | 1 day | 1 day |

## Monitoring Architecture

### Metrics Collected

- Request count & response times
- Error rates
- Database query performance
- Server resources (CPU, memory, disk)
- User activity

### Alerting

- High error rates
- Slow response times
- Database performance
- Disk space low
- Service unavailability

## Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| **UI** | PHP, HTML5, CSS3, JavaScript |
| **API** | PHP REST API |
| **Database** | MySQL 8.0+ |
| **Server** | Nginx |
| **Container** | Docker & Docker Compose |
| **Cache** | Redis (optional) |
| **VoIP** | Asterisk (optional) |
| **AI** | Python/FastAPI (optional) |
