# Contacts App

A multi-tenant contact management system for tracking customers, partners, and stakeholders with full CRM capabilities.

## Table of Contents
- [Features](#features)
- [Data Model](#data-model)
- [API Documentation](#api-documentation)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Permissions](#permissions)
- [Testing](#testing)
- [Deployment Notes](#deployment-notes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Contact Management**: Full CRUD operations for contact records
- **Organization Tracking**: Company, department, and job title associations
- **Communication Preferences**: Track methods (email/phone/SMS) and opt-outs

### Advanced Features
- **Smart Tagging**: Color-coded tags with configurable categories
- **Dynamic Grouping**: Create contact lists for campaigns or segments
- **Interaction Timeline**: Chronological history of all communications
- **Data Validation**: Email/phone validation and duplicate prevention

### Technical Features
- **Multi-tenancy**: Isolated data per tenant with shared schema
- **RESTful API**: JSON API with OAuth2 authentication
- **Performance**: Optimized queries with prefetching
- **Audit Logging**: Track all changes to contact records

## Data Model

### Core Entities
| Entity | Description | Key Fields |
|--------|-------------|------------|
| `Contact` | Primary contact record | first_name, last_name, email, phone |
| `ContactType` | Contact classification | name, description |
| `ContactTag` | Categorization labels | name, color |
| `ContactGroup` | Contact collections | name, description |
| `ContactInteraction` | Communication history | type, notes, date |

### Relationships
- Contact ↔ ContactType: Many-to-Many
- Contact ↔ ContactTag: Many-to-Many
- Contact ↔ ContactGroup: Many-to-Many
- Contact → ContactInteraction: One-to-Many

![Contacts ER Diagram](docs/contacts_er_diagram.png)

## API Documentation

### Base URL
`https://api.yourdomain.com/v1/contacts`

### Endpoints
| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/contacts/` | GET | List contacts | `page`, `page_size`, `search` |
| `/contacts/` | POST | Create contact | `Contact` object |
| `/contacts/{id}/` | GET | Contact details | - |
| `/contacts/{id}/` | PUT | Update contact | `Contact` object |
| `/contacts/{id}/` | DELETE | Delete contact | - |
| `/contacts/types/` | GET | List types | - |
| `/contacts/tags/` | GET | List tags | - |
| `/contacts/groups/` | GET | List groups | - |
| `/contacts/{id}/interactions/` | GET | List interactions | `date_from`, `date_to` |

### Example Requests
```bash
# Create contact
curl -X POST https://api.yourdomain.com/v1/contacts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com"
  }'
```

# Filter contacts
```bash
curl "https://api.yourdomain.com/v1/contacts?type=1&active=true"
```

# Setup

## Requirements
- Python 3.8+
- Django 4.1+
- PostgreSQL 12+
- Redis (for caching)

## Installation
Add to settings.py:

```python
INSTALLED_APPS = [
    ...
    'apps.tenant.contacts',
    'rest_framework',
    'django_filters',
]
```

Configure database in settings.py:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'contacts_db',
        'USER': 'contacts_user',
        'PASSWORD': 'securepassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Run migrations:

```bash
python manage.py makemigrations contacts
python manage.py migrate contacts
```

## Configuration

### Required Settings

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.tenant.contacts.pagination.ContactsPagination',
    'PAGE_SIZE': 25
}
```

### Optional Settings

```python
CONTACTS_CONFIG = {
    'MAX_TAGS_PER_CONTACT': 10,
    'DEFAULT_COUNTRY': 'US',
    'AUTO_CLEAN_PHONE_NUMBERS': True,
    'EMAIL_VERIFICATION': False,  # Set to True in production
}
```

## Usage Examples

### Python Client

```python
from contacts.client import ContactAPIClient

client = ContactAPIClient(api_key="your_api_key")

# Create contact
new_contact = client.create_contact(
    first_name="Michael",
    last_name="Brown",
    email="<michael@example.com>",
    tags=["VIP", "Sales Lead"]
)

# Search contacts
results = client.search_contacts(
    query="Acme Inc",
    filters={"type": "Customer", "active": True}
)
```

### Webhooks
Configure in admin panel to receive:

- contact.created
- contact.updated
- interaction.created

## Permissions

| Role | Access Level |
|------|--------------|
| Tenant Admin | Full CRUD on all contacts |
| Regular User | CRUD on own contacts, read-only others |
| API Client | Configurable per client |

## Testing

### Running Tests

```bash
# Unit tests
pytest apps/tenant/contacts/tests/unit

# Integration tests
pytest apps/tenant/contacts/tests/integration

# With coverage
coverage run -m pytest apps/tenant/contacts/tests
coverage report -m
```

### Test Coverage
- 95% Model layer
- 85% API endpoints
- 80% Permission system

## Deployment Notes

### Production Checklist
- Enable database backups
- Configure rate limiting
- Set up monitoring (Sentry/Datadog)
- Enable email verification
- Audit permission assignments

### Performance Tips
- Use Redis caching for frequent queries
- Add database indexes for common filters
- Schedule nightly maintenance tasks

## Troubleshooting

### Common Issues

#### Duplicate Contacts
Solution: Enable UNIQUE_TOGETHER constraint in settings

#### Slow Queries
Solution: Add index to frequently filtered fields

#### Permission Denied
Solution: Verify tenant membership and role assignments