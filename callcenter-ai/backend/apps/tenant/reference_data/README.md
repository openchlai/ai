# Reference Data Management System

A flexible, multi-tenant reference data solution for Django applications. This system provides structured storage and management of enumerations, taxonomies, and configurable lookup values with support for hierarchical relationships, metadata validation, and audit logging.

## Features

- **Type-Safe Reference Data**: Define custom reference data types (e.g. `countries`, `order_statuses`) with validation rules
- **Multi-Tenancy Support**: Configure whether data types are tenant-specific or global
- **Hierarchical Data**: Model parent-child relationships (e.g. product categories)
- **Rich Metadata**: Attach JSON metadata to entries with schema validation
- **Audit Trail**: Full history tracking of all changes
- **System-Managed Types**: Protect critical enums from accidental modification
- **Optimized Lookups**: Database indexing and cache-friendly design

---

## Models

### ReferenceDataType

Master catalog of available reference data types. Defines:
- Whether the type is tenant-specific or global (`is_tenant_specific`)
- Allowed metadata keys and validation schema (`allowed_metadata_keys`, `validation_schema`)
- System-managed protection flag (`is_system_managed`)

### ReferenceData

Stores individual reference data entries with:
- Tenant association (for tenant-specific types)
- Unique code/display value pairs
- Sort ordering and activity status (`sort_order`, `is_active`)
- Parent-child relationships (`parent`)
- Versioned changes (`version`)
- Flexible metadata (`metadata`), validated against type schema

### ReferenceDataHistory

Tracks all modifications to reference data entries including:
- Previous state snapshot (`previous_data`)
- Changed fields (`changed_fields`)
- Version alignment with main table (`version`)
- Change reason (`change_reason`)

---

## Usage Examples

### 1. Defining a New Reference Data Type
```python
product_type = ReferenceDataType.objects.create(
    name="product_categories",
    description="Hierarchical classification of products",
    is_tenant_specific=True,
    allowed_metadata_keys=["icon", "color"],
    validation_schema={
        "type": "object",
        "properties": {
            "icon": {"type": "string"},
            "color": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"}
        }
    }
)
```

### 2. Adding Reference Data Entries
```python
electronics = ReferenceData.objects.create(
    tenant=current_tenant,
    data_type=product_type,
    code="electronics",
    display_value="Electronics",
    metadata={"icon": "chip", "color": "#3B82F6"}
)

laptops = ReferenceData.objects.create(
    tenant=current_tenant,
    data_type=product_type,
    code="laptops",
    display_value="Laptops",
    parent=electronics,
    sort_order=1
)
```

### 3. Querying Reference Data
```python
# Get all active entries for a type
categories = ReferenceData.objects.filter(
    tenant=request.tenant,
    data_type__name="product_categories",
    is_active=True
).order_by("sort_order")

# Get hierarchical tree
def get_tree(parent=None):
    queryset = ReferenceData.objects.filter(parent=parent)
    return {
        item: get_tree(parent=item)
        for item in queryset
    }
```

---

## API Considerations

**Type Endpoints:**
- `GET /api/reference-data-types/` - List available types
- `POST /api/reference-data-types/` - Create new type (admin only)

**Data Endpoints:**
- `GET /api/reference-data/{type-name}/` - Get all entries for type
- `POST /api/reference-data/{type-name}/` - Create new entry
- `PATCH /api/reference-data/{type-name}/{code}/` - Update entry

**Security:**
- Validate tenant context for tenant-specific types
- Enforce system-managed type protections
- Implement permission checks (e.g., only admins can modify types)

---

## Best Practices

**Caching Strategy:**
- Cache entire reference data types when possible
- Use tenant+type as cache keys
- Implement cache invalidation on write operations

**Migration Patterns:**
- For system-managed types, use data migrations to populate initial values
- Consider using fixtures for global reference data

**Performance:**
- Add `select_related('data_type')` when querying entries
- Use `prefetch_related('children')` for hierarchical views
- Consider denormalizing frequently accessed fields

---

## Installation

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'apps.reference_data',
]
```

Run migrations:
```bash
python manage.py makemigrations reference_data
python manage.py migrate
```

---

## Dependencies

- Django (with PostgreSQL recommended)
- `django.contrib.postgres` for ArrayField
- `jsonschema` for metadata validation

---

## Helper Function: `get_public_tenant()`

A utility function to fetch the global, shared tenant instance (e.g., the tenant with `schema_name='public'`). This is used as the default tenant for `ReferenceData` entries belonging to a type marked as non-tenant-specific.
*(Note: The implementation may be commented out and can be activated or replaced with a project-level setting like `settings.PUBLIC_TENANT_ID`.)*

---

This system powers your application's standardized lookups and configurable enumerations while maintaining data integrity across tenants.

---

This README includes:
1. Clear feature overview
2. Model explanations
3. Practical code examples
4. API design considerations
5. Performance best practices
6. Installation instructions

Would you like me to add any specific sections such as:
- Detailed API documentation?
- Example caching implementation?
- Testing strategies?
- Sample migration files?