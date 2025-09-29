# Helpline API Endpoints

## Base URL
```
https://your-domain.com/helpline/api/
```

## Authentication
All endpoints require authentication via session cookie (`HELPLINE_SESSION_ID`) or API key.

---

## Authentication Endpoints

### Send OTP
Request one-time password for login.

**Endpoint:** `POST /sendOTP`

**Request:**
```json
{
  "addr_addr": "user@example.com",
  "addr_type": "email"  // or "phone"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent to user@example.com"
}
```

---

### Verify OTP
Verify OTP and establish session.

**Endpoint:** `POST /verifyOTP`

**Request:**
```json
{
  "addr_addr": "user@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 5,
    "username": "operator_john",
    "role": "operator"
  }
}
```

Sets `HELPLINE_SESSION_ID` cookie.

---

### Change Password
Change user password (requires authentication).

**Endpoint:** `POST /changeAuth`

**Request:**
```json
{
  "old_password": "current_password",
  "new_password": "new_secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

### Logout
Terminate current session.

**Endpoint:** `POST /logout`

**Request:** Empty body

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Case Management Endpoints

### List Cases
Retrieve cases with filtering and pagination.

**Endpoint:** `GET /cases`

**Query Parameters:**
- `status` - Filter by status (open, assigned, in_progress, resolved, closed)
- `priority` - Filter by priority (low, medium, high, critical)
- `category` - Filter by category
- `assigned_user_id` - Filter by assigned user
- `created_after` - ISO 8601 date
- `limit` - Results per page (default: 20)
- `offset` - Pagination offset (default: 0)

**Example Request:**
```bash
curl -X GET "https://your-domain.com/helpline/api/cases?status=open&priority=high&limit=10" \
  -H "Cookie: HELPLINE_SESSION_ID=your-session-id"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "case_number": "CASE-2025-001234",
      "title": "Child safety concern",
      "description": "Reported concern about child welfare",
      "category": "abuse",
      "priority": "high",
      "status": "open",
      "reporter_phone": "+254700123456",
      "child_name": "Maria W.",
      "child_age": 12,
      "assigned_user_id": null,
      "created_at": "2025-09-26T14:30:00Z",
      "updated_at": "2025-09-26T14:30:00Z"
    }
  ],
  "pagination": {
    "total": 45,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

---

### Get Case
Retrieve single case by ID.

**Endpoint:** `GET /cases/{id}`

**Example Request:**
```bash
curl -X GET "https://your-domain.com/helpline/api/cases/123" \
  -H "Cookie: HELPLINE_SESSION_ID=your-session-id"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "case_number": "CASE-2025-001234",
    "title": "Child safety concern",
    "description": "Detailed case description...",
    "category": "abuse",
    "subcategory": "physical_abuse",
    "priority": "high",
    "status": "open",
    "reporter_name": "Anonymous",
    "reporter_phone": "+254700123456",
    "reporter_email": "reporter@example.com",
    "child_name": "Maria W.",
    "child_age": 12,
    "child_gender": "female",
    "child_location": "Nairobi, Kibera",
    "assigned_user_id": 8,
    "assigned_user": {
      "id": 8,
      "username": "case_manager_maria",
      "role": "case_manager"
    },
    "ai_transcript": "Transcribed call text...",
    "ai_translation": "Translated text...",
    "ai_risk_level": "high",
    "ai_confidence": 0.94,
    "created_at": "2025-09-26T14:30:00Z",
    "updated_at": "2025-09-26T15:45:00Z",
    "created_by": 5
  }
}
```

---

### Create Case
Create a new case.

**Endpoint:** `POST /cases`

**Request:**
```json
{
  "title": "Child safety concern",
  "description": "Detailed description of the concern",
  "category": "abuse",
  "subcategory": "physical_abuse",
  "priority": "high",
  "reporter_name": "Anonymous",
  "reporter_phone": "+254700123456",
  "reporter_email": "reporter@example.com",
  "reporter_relationship": "neighbor",
  "child_name": "Maria W.",
  "child_age": 12,
  "child_gender": "female",
  "child_location": "Nairobi, Kibera"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "case_number": "CASE-2025-001234",
    "status": "open",
    "created_at": "2025-09-26T14:30:00Z"
  },
  "message": "Case created successfully"
}
```

---

### Update Case
Update existing case.

**Endpoint:** `PUT /cases/{id}` or `POST /cases/{id}`

**Request:**
```json
{
  "status": "assigned",
  "assigned_user_id": 8,
  "priority": "critical",
  "notes": "Escalated due to immediate danger"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "case_number": "CASE-2025-001234",
    "status": "assigned",
    "updated_at": "2025-09-26T15:45:00Z"
  },
  "message": "Case updated successfully"
}
```

---

### Delete Case
Delete a case (admin only).

**Endpoint:** `DELETE /cases/{id}`

**Response:**
```json
{
  "success": true,
  "message": "Case deleted successfully"
}
```

---

## Case Activity Endpoints

### Get Case Activities
Retrieve activity history for a case.

**Endpoint:** `GET /cases/{id}/activities`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 456,
      "activity_type": "status_change",
      "description": "Case status changed from open to assigned",
      "previous_value": "open",
      "new_value": "assigned",
      "user_name": "supervisor_jane",
      "created_at": "2025-09-26T15:45:00Z"
    },
    {
      "id": 455,
      "activity_type": "note",
      "description": "Initial assessment completed",
      "user_name": "case_manager_maria",
      "created_at": "2025-09-26T15:30:00Z"
    }
  ]
}
```

---

### Add Case Activity
Log new activity on a case.

**Endpoint:** `POST /cases/{id}/activities`

**Request:**
```json
{
  "activity_type": "note",
  "description": "Follow-up call completed. Family receiving support."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 457,
    "created_at": "2025-09-27T10:00:00Z"
  }
}
```

---

## Communication Endpoints

### Log Communication
Record communication (call, SMS, email, etc.).

**Endpoint:** `POST /communications`

**Request:**
```json
{
  "case_id": 123,
  "contact_type": "call",
  "direction": "inbound",
  "contact_address": "+254700123456",
  "contact_name": "Maria's Mother",
  "duration": 180,
  "call_status": "answered",
  "disposition_id": 50,
  "disposition_notes": "Case created, immediate follow-up required",
  "message": "Caller reported urgent child safety concern"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 789,
    "case_id": 123,
    "created_at": "2025-09-26T14:25:00Z"
  }
}
```

---

### Get Communications
Retrieve communications for a case.

**Endpoint:** `GET /cases/{id}/communications`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 789,
      "contact_type": "call",
      "direction": "inbound",
      "contact_address": "+254700123456",
      "duration": 180,
      "call_status": "answered",
      "disposition": "case_created",
      "audio_file_path": "/uploads/audio/call_789.wav",
      "audio_processed": true,
      "created_at": "2025-09-26T14:25:00Z"
    }
  ]
}
```

---

## File Upload Endpoints

### Upload Attachment
Upload file to a case.

**Endpoint:** `POST /cases/{id}/attachments`

**Request:** Multipart form data
```
file: <binary file data>
description: "Medical report"
file_type: "document"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 234,
    "filename": "medical_report_abc123.pdf",
    "file_size": 524288,
    "file_type": "document",
    "uploaded_at": "2025-09-26T16:00:00Z"
  }
}
```

---

### List Attachments
Get all attachments for a case.

**Endpoint:** `GET /cases/{id}/attachments`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 234,
      "filename": "medical_report.pdf",
      "original_filename": "Medical Report - Maria.pdf",
      "file_size": 524288,
      "mime_type": "application/pdf",
      "file_type": "document",
      "description": "Medical report from hospital",
      "uploaded_by": "case_manager_maria",
      "uploaded_at": "2025-09-26T16:00:00Z"
    }
  ]
}
```

---

## User Management Endpoints

### Get Current User
Get authenticated user details.

**Endpoint:** `GET /users/me`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "username": "operator_john",
    "email": "john@helpline.org",
    "role": "operator",
    "organization": "Nairobi Helpline",
    "permissions": [
      "create_case",
      "update_case",
      "receive_calls"
    ],
    "last_login": "2025-09-26T08:00:00Z"
  }
}
```

---

### List Users
Get all users (supervisor/admin only).

**Endpoint:** `GET /users`

**Query Parameters:**
- `role` - Filter by role
- `is_active` - Filter by active status

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "username": "operator_john",
      "email": "john@helpline.org",
      "role": "operator",
      "organization": "Nairobi Helpline",
      "is_active": true,
      "last_login": "2025-09-26T08:00:00Z"
    }
  ]
}
```

---

## Disposition Endpoints

### List Dispositions
Get available call dispositions.

**Endpoint:** `GET /dispositions`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 50,
      "code": "CASE_NEW",
      "name": "New Case Created",
      "category": "case_created",
      "is_active": true
    },
    {
      "id": 51,
      "code": "INFO_PROVIDED",
      "name": "Information Provided",
      "category": "information",
      "is_active": true
    }
  ]
}
```

---

## Statistics Endpoints

### Case Statistics
Get case statistics for dashboard.

**Endpoint:** `GET /statistics/cases`

**Query Parameters:**
- `period` - Time period (today, week, month, year)
- `start_date` - Custom start date
- `end_date` - Custom end date

**Response:**
```json
{
  "success": true,
  "data": {
    "total_cases": 1234,
    "open_cases": 45,
    "assigned_cases": 23,
    "in_progress_cases": 12,
    "resolved_cases": 1154,
    "by_priority": {
      "critical": 5,
      "high": 15,
      "medium": 20,
      "low": 5
    },
    "by_category": {
      "abuse": 25,
      "neglect": 10,
      "education": 5,
      "health": 5
    },
    "avg_resolution_time_hours": 48
  }
}
```

---

## Search Endpoints

### Search Cases
Full-text search across cases.

**Endpoint:** `GET /search/cases`

**Query Parameters:**
- `q` - Search query
- `fields` - Fields to search (title, description, case_number)
- `limit` - Results limit

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "case_number": "CASE-2025-001234",
      "title": "Child safety concern",
      "relevance_score": 0.95,
      "matched_fields": ["title", "description"]
    }
  ]
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

**Common Error Codes:**
- `UNAUTHORIZED` (401) - Authentication required
- `FORBIDDEN` (403) - Insufficient permissions
- `NOT_FOUND` (404) - Resource not found
- `VALIDATION_ERROR` (400) - Invalid input data
- `INTERNAL_ERROR` (500) - Server error

---

## Rate Limiting

See [API Rate Limiting](api-rate-limiting-throttling.md) for details.

---

## Examples

### Complete Case Creation Flow

```bash
# 1. Login
curl -X POST https://your-domain.com/helpline/api/sendOTP \
  -d '{"addr_addr":"user@example.com","addr_type":"email"}'

curl -X POST https://your-domain.com/helpline/api/verifyOTP \
  -d '{"addr_addr":"user@example.com","otp":"123456"}' \
  -c cookies.txt

# 2. Create case
curl -X POST https://your-domain.com/helpline/api/cases \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Child safety concern",
    "priority": "high",
    "category": "abuse",
    "reporter_phone": "+254700123456"
  }'

# 3. Add activity
curl -X POST https://your-domain.com/helpline/api/cases/123/activities \
  -b cookies.txt \
  -d '{"activity_type":"note","description":"Initial assessment"}'
```