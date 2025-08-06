# Case Management Module

A comprehensive case tracking and workflow automation system for multi-tenant environments.

![Case Management Workflow](docs/case_workflow.png) *(Example workflow diagram)*

## Table of Contents
- [Features](#features)
- [Data Model](#data-model)
- [API Documentation](#api-documentation)
- [Setup & Configuration](#setup--configuration)
- [Usage Examples](#usage-examples)
- [Permissions](#permissions)
- [Workflow Automation](#workflow-automation)
- [Testing](#testing)
- [Deployment Notes](#deployment-notes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Case Lifecycle Management**: Full CRUD operations with configurable statuses
- **Multi-channel Creation**: Cases from web, email, API, etc. (REQ-CT-001)
- **Custom Intake Forms**: Dynamic forms per case type (REQ-CT-002)
- **Unique Identifiers**: Auto-generated case numbers (REQ-CT-003)

### Advanced Features
- **Workflow Automation**: JSON-configurable business rules (REQ-WA-001 to WA-007)
- **SLA Tracking**: Response/resolution time monitoring with escalation paths
- **Document Management**: File attachments with version control (REQ-CD-001, CD-002)
- **Case Relationships**: Parent-child and related case linking (REQ-CT-008)

### Technical Features
- **Multi-tenancy**: Isolated data per tenant
- **RESTful API**: JSON API with OAuth2 authentication
- **Audit Logging**: Complete history of all case changes
- **Performance Optimized**: Efficient queries with prefetching

## Data Model

### Core Entities
| Entity | Description | Key Fields |
|--------|-------------|------------|
| `Case` | Main case record | case_number, title, status, priority |
| `CaseType` | Case classification | name, form_schema, workflow_definition |
| `CaseStatus` | Lifecycle states | name, is_closed, allowed_transitions |
| `CaseNote` | Activity tracking | content, is_internal, document |
| `CaseWorkflow` | Automation rules | trigger_event, condition, actions |

### Relationships
```mermaid
erDiagram
    Case ||--o{ CaseNote : has
    Case ||--o{ CaseAttachment : has
    Case }|--|| CaseType : of
    Case }|--|| CaseStatus : in
    CaseStatus ||--o{ CaseStatusTransition : allows
    Case ||--o{ RelatedCase : links_to
````
  # API Documentation

  ## Base URL
  [https://api.yourdomain.com/v1/cases](https://api.yourdomain.com/v1/cases)

  ## Key Endpoints
  | Endpoint | Method | Description | Parameters |
  |----------|--------|-------------|------------|
  | /cases/ | GET | List cases | status, priority, assigned_to |
  | /cases/ | POST | Create case | Case object |
  | /cases/{id}/ | PUT | Update case | Case object |
  | /cases/bulk-update/ | POST | Mass update | case_ids, update_fields |
  | /cases/{id}/notes/ | POST | Add note | content, document_id |
  | /cases/{id}/workflows/ | GET | Available actions | - |

  ## Example Requests

  ### Create a case
  ```bash
  curl -X POST https://api.yourdomain.com/v1/cases \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Login issues",
      "description": "User cannot access system",
      "case_type_id": 1,
      "contact_id": 123
    }'
  ```

  ### Update case status
  ```bash
  curl -X PUT https://api.yourdomain.com/v1/cases/456 \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"status_id": 3}'
  ```

  ## Setup & Configuration

  ### Prerequisites
  - Python 3.8+
  - Django 4.1+
  - PostgreSQL 12+
  - Redis (for workflow queues)

  ### Installation
  Add to INSTALLED_APPS:

  ```python
  INSTALLED_APPS = [
      ...
      'apps.tenant.cases',
      'django_filters',
  ]
  ```

  Configure settings:

  ```python
  # Case-specific settings
  CASE_CONFIG = {
      'DEFAULT_PRIORITY': 2,  # Medium
      'AUTO_ASSIGN_INITIAL_STATUS': True,
      'WORKFLOW_ENGINE': 'celery',  # or 'sync'
  }
  ```

  Run migrations:

  ```bash
  python manage.py makemigrations cases
  python manage.py migrate cases
  ```

  ## Usage Examples

  ### Python Client
  ```python
  from cases.client import CaseManager

  cm = CaseManager(api_key="your_api_key")

  # Create high-priority case
  case = cm.create_case(
      title="Server outage",
      description="Production server down",
      case_type="incident",
      priority=4,  # Critical
      contact="[admin@company.com](mailto:admin@company.com)"
  )

  # Add timeline note
  cm.add_note(
      case_id=case.id,
      content="Called provider, waiting for callback",
      is_internal=True
  )

  # Escalate case
  cm.update_case(
      case_id=case.id,
      status="escalated",
      assigned_to="[senior.support@company.com](mailto:senior.support@company.com)"
  )
  ```

  ### Webhook Events
  Configure in admin panel to receive:
  - case.created
  - case.status_changed
  - sla.breached

  ## Permissions
  | Role | Access Level |
  |------|--------------|
  | Tenant Admin | Full CRUD + workflow configuration |
  | Case Worker | Create/update assigned cases |
  | Reporter | Create cases + view own |
  | API Client | Configurable per client |

  ## Workflow Automation

  ### Example Workflow Definition
  ```json
  {
    "trigger_event": "status_changed",
    "condition": {
      "field": "status",
      "operator": "equals",
      "value": "escalated"
    },
    "actions": [
      {
        "type": "email",
        "template": "escalation_notice",
        "recipients": ["team_lead@example.com"]
      },
      {
        "type": "update_field",
        "field": "priority",
        "value": 4
      }
    ]
  }
  ```

  ## Testing

  ### Test Suite
  ```bash
  # Run all tests
  pytest apps/tenant/cases/tests/

  # With coverage
  coverage run -m pytest apps/tenant/cases/tests/
  coverage report -m
  ```

  ### Test Coverage
  - Models: 95%
  - API Endpoints: 90%
  - Workflows: 85%
  - Permissions: 100%

  ## Deployment Notes

  ### Production Checklist
  - Configure database backups
  - Set up monitoring for SLA breaches
  - Enable case archiving for closed cases
  - Configure rate limiting

  ### Performance Tips
  Add database indexes for:

  ```python
  indexes = [
      models.Index(fields=['status', 'priority']),
      models.Index(fields=['due_date']),
  ]
  ```

  - Use Redis caching for frequent queries
  - Schedule nightly maintenance tasks

  ## Troubleshooting
  | Issue | Solution |
  |-------|----------|
  | Status transitions failing | Check CaseStatusTransition rules |
  | SLA breaches not detected | Verify CaseSLA business hours |
  | Slow case listings | Add select_related for status/type |
  | Permission denied | Check tenant membership and role |
