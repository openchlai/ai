# Task Management System - Django REST API

## Overview
This Task Management System is a comprehensive Django REST Framework (DRF) API that provides robust functionality for creating, assigning, tracking, and completing tasks within a multi-tenant environment. The system integrates with cases, workflows, and notifications to provide a complete productivity solution.

## Features

### Task Management
- Create, read, update, and delete tasks
- Assign tasks to users
- Set priorities and due dates
- Track task status (Pending, In Progress, Completed, etc.)
- Parent-child task relationships

### Organization
- Tag tasks with customizable labels
- Add comments and attachments
- Set reminders for important deadlines
- Full audit logging of all changes

### Integration
- Link tasks to specific cases
- Connect with workflow automation
- Generate notifications for assignments and updates

### Reporting
- Dashboard with task statistics
- Completion trend analysis
- Overdue task tracking
- Workload distribution metrics

## API Endpoints

### Tasks
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks/` | GET | List all tasks (with filtering) |
| `/api/tasks/` | POST | Create new task |
| `/api/tasks/{id}/` | GET | Retrieve task details |
| `/api/tasks/{id}/` | PUT/PATCH | Update task |
| `/api/tasks/{id}/` | DELETE | Delete task |

### Task Comments
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks/{task_id}/comments/` | GET | List all comments for a task |
| `/api/tasks/{task_id}/comments/` | POST | Add new comment to task |
| `/api/comments/{id}/` | GET | Retrieve comment |
| `/api/comments/{id}/` | PUT/PATCH | Update comment |
| `/api/comments/{id}/` | DELETE | Delete comment |

### Task Attachments
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks/{task_id}/attachments/` | GET | List all attachments for a task |
| `/api/tasks/{task_id}/attachments/` | POST | Upload new attachment |
| `/api/attachments/{id}/` | GET | Retrieve attachment metadata |
| `/api/attachments/{id}/` | DELETE | Delete attachment |

### Task Tags
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tags/` | GET | List all available tags |
| `/api/tags/` | POST | Create new tag |
| `/api/tags/{id}/` | GET | Retrieve tag details |
| `/api/tags/{id}/` | PUT/PATCH | Update tag |
| `/api/tags/{id}/` | DELETE | Delete tag |

### Dashboard
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks/dashboard/` | GET | Get task statistics and overview |
| `/api/tasks/stats/` | GET | Get completion trends |

## Filtering and Searching
All list endpoints support powerful filtering options:

### Task Filtering Parameters
- status: Filter by task status (pending, in_progress, completed)
- priority: Filter by priority level (1-4)
- due_date: Filter by due date (exact, range)
- assigned_to: Filter by assignee ID
- created_by: Filter by creator ID
- case: Filter by linked case ID
- tags: Filter by tag IDs
- overdue=true: Only show overdue tasks
- mine=true: Only show tasks assigned to current user
- q: Full-text search across title, description, and comments

### Sorting
Tasks can be sorted by:
- due_date
- priority
- created_at
- updated_at

Example: `/api/tasks/?ordering=-priority,due_date`

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer {your_token}
```

## Permissions
- All endpoints require authentication
- Users can only access tasks within their tenant
- Task assignment respects user roles and permissions
- Only task creators or admins can delete tasks/comments

## Request/Response Examples

### Create Task
**Request:**
```http
POST /api/tasks/
Content-Type: application/json
Authorization: Bearer {your_token}

{
    "title": "Complete project documentation",
    "description": "Write API documentation for all endpoints",
    "priority": 3,
    "due_date": "2023-12-15T17:00:00Z",
    "assigned_to_id": "550e8400-e29b-41d4-a716-446655440000",
    "case_id": "550e8400-e29b-41d4-a716-446655440001",
    "tag_ids": [1, 3]
}
```

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "title": "Complete project documentation",
    "description": "Write API documentation for all endpoints",
    "priority": 3,
    "priority_display": "High",
    "status": "pending",
    "status_display": "Pending",
    "due_date": "2023-12-15T17:00:00Z",
    "created_at": "2023-12-01T09:30:00Z",
    "updated_at": "2023-12-01T09:30:00Z",
    "is_overdue": false,
    "progress": 0,
    "assigned_to": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Doe",
        "email": "john@example.com"
    },
    "tags": [
        {"id": 1, "name": "Documentation", "color": "#3498db"},
        {"id": 3, "name": "High Priority", "color": "#e74c3c"}
    ]
}
```
