# Case Data Schema

## Overview

The case management system stores all child protection cases, communications, and related information in the `helpline` MySQL database. This document describes the core data structures for contributors working on case-related features.

## Core Tables

### `kase` - Main Cases Table

Primary table storing case information.

```sql
CREATE TABLE kase (
  id INT PRIMARY KEY AUTO_INCREMENT,
  case_number VARCHAR(50) UNIQUE NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  subcategory VARCHAR(50),
  priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
  status ENUM('open', 'assigned', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
  
  -- Reporter information
  reporter_name VARCHAR(255),
  reporter_phone VARCHAR(20),
  reporter_email VARCHAR(255),
  reporter_relationship VARCHAR(100),
  
  -- Child information
  child_name VARCHAR(255),
  child_age INT,
  child_gender ENUM('male', 'female', 'other', 'unknown'),
  child_location VARCHAR(255),
  
  -- Assignment
  assigned_user_id INT,
  assigned_organization VARCHAR(255),
  
  -- AI-generated fields
  ai_transcript TEXT,
  ai_translation TEXT,
  ai_entities JSON,
  ai_classification VARCHAR(100),
  ai_risk_level ENUM('low', 'medium', 'high', 'critical'),
  ai_confidence DECIMAL(3,2),
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by INT,
  updated_by INT,
  
  FOREIGN KEY (assigned_user_id) REFERENCES auth(id),
  FOREIGN KEY (created_by) REFERENCES auth(id),
  INDEX idx_status (status),
  INDEX idx_priority (priority),
  INDEX idx_created_at (created_at)
);
```

**Field Descriptions:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `case_number` | VARCHAR(50) | Unique case identifier | "CASE-2025-001234" |
| `title` | VARCHAR(255) | Brief case description | "Child safety concern reported" |
| `category` | VARCHAR(50) | Main case category | "abuse", "neglect", "education" |
| `priority` | ENUM | Case urgency level | "high", "critical" |
| `ai_entities` | JSON | Extracted entities from AI | {"PERSON": ["Maria"], "LOC": ["Nairobi"]} |
| `ai_risk_level` | ENUM | AI-assessed risk | "high", "critical" |

### `kase_activity` - Case Activities

Tracks all actions and updates on cases.

```sql
CREATE TABLE kase_activity (
  id INT PRIMARY KEY AUTO_INCREMENT,
  kase_id INT NOT NULL,
  activity_type ENUM('note', 'status_change', 'assignment', 'escalation', 'resolution'),
  description TEXT,
  previous_value VARCHAR(255),
  new_value VARCHAR(255),
  
  -- User information
  user_id INT,
  user_name VARCHAR(255),
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address VARCHAR(45),
  
  FOREIGN KEY (kase_id) REFERENCES kase(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES auth(id),
  INDEX idx_kase_id (kase_id),
  INDEX idx_created_at (created_at)
);
```

**Activity Types:**
- `note` - General case note or comment
- `status_change` - Case status updated
- `assignment` - Case assigned to user/organization
- `escalation` - Case escalated to supervisor
- `resolution` - Case marked as resolved

### `contact` - Communications Log

Records all communications related to cases (calls, SMS, emails, web forms).

```sql
CREATE TABLE contact (
  id INT PRIMARY KEY AUTO_INCREMENT,
  kase_id INT,
  contact_type ENUM('call', 'sms', 'email', 'web', 'whatsapp') NOT NULL,
  direction ENUM('inbound', 'outbound') NOT NULL,
  
  -- Contact details
  contact_address VARCHAR(255),  -- Phone/email/username
  contact_name VARCHAR(255),
  
  -- Communication content
  subject VARCHAR(255),
  message TEXT,
  duration INT,  -- For calls, in seconds
  
  -- Call-specific fields
  call_id VARCHAR(100),
  call_status ENUM('answered', 'missed', 'busy', 'failed'),
  
  -- Audio processing
  audio_file_path VARCHAR(500),
  audio_processed BOOLEAN DEFAULT FALSE,
  
  -- Disposition
  disposition_id INT,
  disposition_notes TEXT,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by INT,
  
  FOREIGN KEY (kase_id) REFERENCES kase(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES auth(id),
  FOREIGN KEY (disposition_id) REFERENCES disposition(id),
  INDEX idx_kase_id (kase_id),
  INDEX idx_contact_type (contact_type),
  INDEX idx_created_at (created_at)
);
```

### `disposition` - Call Outcomes

Categorizes communication outcomes.

```sql
CREATE TABLE disposition (
  id INT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category ENUM('case_created', 'referral', 'information', 'prank', 'no_response'),
  is_active BOOLEAN DEFAULT TRUE,
  display_order INT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Common Dispositions:**
- `CASE_NEW` - New case created from call
- `CASE_UPDATE` - Existing case updated
- `REFERRAL_GIVEN` - Caller referred to services
- `INFO_PROVIDED` - Information/guidance provided
- `PRANK_CALL` - Identified as prank
- `SILENT_CALL` - No response from caller
- `FOLLOW_UP_SCHEDULED` - Follow-up scheduled

### `attachment` - File Attachments

Stores files attached to cases.

```sql
CREATE TABLE attachment (
  id INT PRIMARY KEY AUTO_INCREMENT,
  kase_id INT NOT NULL,
  filename VARCHAR(255) NOT NULL,
  original_filename VARCHAR(255),
  file_path VARCHAR(500) NOT NULL,
  file_size INT,
  mime_type VARCHAR(100),
  file_type ENUM('audio', 'document', 'image', 'other'),
  
  -- Description
  description TEXT,
  
  -- Processing status (for audio files)
  processing_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
  ai_task_id VARCHAR(100),
  
  -- Metadata
  uploaded_by INT,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (kase_id) REFERENCES kase(id) ON DELETE CASCADE,
  FOREIGN KEY (uploaded_by) REFERENCES auth(id),
  INDEX idx_kase_id (kase_id),
  INDEX idx_processing_status (processing_status)
);
```

## JSON Field Structures

### `ai_entities` (JSON)

Structure of AI-extracted entities:

```json
{
  "PERSON": ["Maria Wanjiku", "Dr. John Kamau"],
  "LOC": ["Nairobi", "Kibera", "Kenya"],
  "ORG": ["Kenyatta Hospital", "Police Station"],
  "DATE": ["2025-09-26"],
  "TIME": ["14:30"],
  "AGE": ["12 years old"],
  "PHONE": ["+254700123456"]
}
```

**Entity Types:**
- `PERSON` - Names of people mentioned
- `LOC` - Locations (cities, neighborhoods, addresses)
- `ORG` - Organizations (hospitals, schools, police)
- `DATE` - Dates mentioned
- `TIME` - Times mentioned
- `AGE` - Age references
- `PHONE` - Phone numbers

## Data Relationships

```
┌─────────────┐
│    kase     │
│ (Main Case) │
└──────┬──────┘
       │
       ├─────────┐
       │         │
       ▼         ▼
┌─────────────┐ ┌─────────────┐
│kase_activity│ │   contact   │
│(Activities) │ │(Communica-  │
│             │ │  tions)     │
└─────────────┘ └──────┬──────┘
                       │
       ┌───────────────┤
       │               │
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│disposition  │ │ attachment  │
│(Outcomes)   │ │  (Files)    │
└─────────────┘ └─────────────┘
```

## Example Queries

### Create a New Case

```sql
INSERT INTO kase (
  case_number,
  title,
  description,
  category,
  priority,
  reporter_phone,
  child_name,
  child_age,
  created_by
) VALUES (
  'CASE-2025-001234',
  'Child safety concern',
  'Reported concern about child welfare',
  'abuse',
  'high',
  '+254700123456',
  'Maria W.',
  12,
  5  -- user_id
);
```

### Get Cases with Latest Activity

```sql
SELECT 
    k.id,
    k.case_number,
    k.title,
    k.status,
    k.priority,
    MAX(ka.created_at) as last_activity,
    u.username as assigned_to
FROM 
    kase k
    LEFT JOIN kase_activity ka ON k.id = ka.kase_id
    LEFT JOIN auth u ON k.assigned_user_id = u.id
WHERE 
    k.status IN ('open', 'assigned', 'in_progress')
GROUP BY 
    k.id
ORDER BY 
    last_activity DESC
LIMIT 20;
```

### Get Complete Case with Communications

```sql
SELECT 
    k.*,
    c.id as contact_id,
    c.contact_type,
    c.message,
    c.created_at as contact_date,
    d.name as disposition
FROM 
    kase k
    LEFT JOIN contact c ON k.id = c.kase_id
    LEFT JOIN disposition d ON c.disposition_id = d.id
WHERE 
    k.case_number = 'CASE-2025-001234'
ORDER BY 
    c.created_at DESC;
```

### Update Case with AI Results

```sql
UPDATE kase SET
    ai_transcript = 'Transcribed text...',
    ai_translation = 'Translated text...',
    ai_entities = '{"PERSON": ["Maria"], "LOC": ["Nairobi"]}',
    ai_classification = 'child_protection',
    ai_risk_level = 'high',
    ai_confidence = 0.94,
    updated_at = NOW(),
    updated_by = 1
WHERE 
    id = 123;
```

## Data Validation Rules

### Case Creation
- `case_number` must be unique
- `title` is required
- `priority` defaults to 'medium'
- `status` defaults to 'open'
- Either `reporter_phone` or `reporter_email` should be provided

### Child Information
- `child_age` must be 0-18
- `child_gender` must be valid enum value
- Child information should be anonymized in logs

### AI Fields
- `ai_confidence` must be between 0.00 and 1.00
- `ai_entities` must be valid JSON
- `ai_risk_level` triggers automatic assignment for 'critical' cases

## Privacy Considerations

### Sensitive Data
The following fields contain Personally Identifiable Information (PII):
- `reporter_name`, `reporter_phone`, `reporter_email`
- `child_name`, `child_location`
- `contact.contact_address`, `contact.message`
- `ai_transcript`, `ai_translation`

### Data Protection
- All PII should be encrypted at rest
- Access logs maintained for all PII access
- Data retention policies apply:
  - Active cases: Indefinite
  - Resolved cases: 7 years
  - AI transcripts: 1 year after case closure
- Anonymization applied for analytics/reporting

### Access Control
- Case managers can view assigned cases only
- Supervisors can view all cases in their region
- System administrators have full access
- Audit logs track all data access

## Contributing Guidelines

### When Adding New Fields
1. Update this documentation
2. Create database migration script
3. Update API endpoints
4. Add validation rules
5. Consider privacy implications
6. Update test fixtures

### Best Practices
- Always use prepared statements
- Validate all user inputs
- Log all data modifications
- Handle NULL values appropriately
- Use transactions for multi-table updates
- Index frequently queried fields

For more information on using these schemas in your code, see the [API Reference](../api-reference/helpline-api-endpoints.md).