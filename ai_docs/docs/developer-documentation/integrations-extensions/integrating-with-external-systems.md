# Integrating with External Systems

## Overview

OpenCHS provides multiple integration methods for external systems to interact with the platform, including REST APIs, webhooks, and data import/export capabilities. This document guides developers on integrating their systems with OpenCHS.

## Integration Methods

### 1. REST API Integration
Direct API access for real-time operations

### 2. Webhook Events
Push notifications for system events

### 3. Data Import/Export
Bulk data transfer via CSV/JSON

### 4. Database Integration
Direct database access (read-only recommended)

---

## REST API Integration

### Authentication

All API requests require authentication using session-based auth or API keys.

**Session-Based (for web applications):**
```bash
# Step 1: Request OTP
curl -X POST https://your-domain.com/helpline/api/sendOTP \
  -H "Content-Type: application/json" \
  -d '{"addr_addr": "user@example.com", "addr_type": "email"}'

# Step 2: Verify OTP
curl -X POST https://your-domain.com/helpline/api/verifyOTP \
  -H "Content-Type: application/json" \
  -d '{"addr_addr": "user@example.com", "otp": "123456"}'
  
# Response includes HELPLINE_SESSION_ID cookie
```

**API Key (for system integrations):**
```bash
# Request with API key header
curl -X GET https://your-domain.com/helpline/api/cases \
  -H "X-API-Key: your-api-key-here"
```

### Common Integration Patterns

#### Pattern 1: Case Creation from External System

External CRM or ticketing system creating cases in OpenCHS:

```javascript
// Node.js example
const axios = require('axios');

class OpenCHSIntegration {
  constructor(baseUrl, apiKey) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
      }
    });
  }

  async createCase(caseData) {
    try {
      const response = await this.client.post('/helpline/api/cases', {
        title: caseData.title,
        description: caseData.description,
        category: caseData.category,
        priority: caseData.priority,
        reporter_phone: caseData.reporterPhone,
        reporter_email: caseData.reporterEmail
      });
      
      return {
        success: true,
        caseId: response.data.id,
        caseNumber: response.data.case_number
      };
    } catch (error) {
      console.error('Failed to create case:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async getCaseStatus(caseId) {
    const response = await this.client.get(`/helpline/api/cases/${caseId}`);
    return response.data;
  }

  async updateCase(caseId, updates) {
    const response = await this.client.put(
      `/helpline/api/cases/${caseId}`,
      updates
    );
    return response.data;
  }
}

// Usage
const openchs = new OpenCHSIntegration(
  'https://helpline.example.com',
  'your-api-key'
);

// Create case from your system
const result = await openchs.createCase({
  title: 'Child safety concern from hotline',
  description: 'Caller reported concern about child welfare',
  category: 'abuse',
  priority: 'high',
  reporterPhone: '+254700123456',
  reporterEmail: 'reporter@example.com'
});

console.log('Created case:', result.caseNumber);
```

#### Pattern 2: Syncing Cases to External System

Pull cases from OpenCHS to your system:

```python
# Python example
import requests
from datetime import datetime, timedelta

class OpenCHSSync:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'X-API-Key': api_key})
    
    def get_cases_since(self, since_date):
        """Get all cases created/updated since a specific date"""
        response = self.session.get(
            f'{self.base_url}/helpline/api/cases',
            params={
                'updated_since': since_date.isoformat(),
                'limit': 100
            }
        )
        response.raise_for_status()
        return response.json()
    
    def sync_to_external_system(self, external_api):
        """Sync recent cases to external CRM"""
        # Get cases from last hour
        since_date = datetime.now() - timedelta(hours=1)
        cases = self.get_cases_since(since_date)
        
        for case in cases:
            # Transform to external format
            external_case = {
                'external_id': case['case_number'],
                'title': case['title'],
                'status': case['status'],
                'priority': case['priority'],
                'created_at': case['created_at']
            }
            
            # Create or update in external system
            external_api.upsert_case(external_case)

# Usage
sync = OpenCHSSync('https://helpline.example.com', 'your-api-key')
sync.sync_to_external_system(your_crm_api)
```

#### Pattern 3: Real-Time Status Updates

Monitor case status changes:

```python
import time

class CaseMonitor:
    def __init__(self, openchs_client):
        self.client = openchs_client
        self.last_check = datetime.now()
    
    def poll_for_updates(self, callback):
        """Poll for case updates every minute"""
        while True:
            try:
                # Get cases updated since last check
                cases = self.client.get_cases_since(self.last_check)
                
                for case in cases:
                    # Trigger callback for each update
                    callback(case)
                
                self.last_check = datetime.now()
                time.sleep(60)  # Poll every minute
                
            except Exception as e:
                print(f"Error polling updates: {e}")
                time.sleep(60)

# Usage
def handle_case_update(case):
    print(f"Case {case['case_number']} updated to {case['status']}")
    # Send notification, update dashboard, etc.

monitor = CaseMonitor(openchs)
monitor.poll_for_updates(handle_case_update)
```

---

## AI Service Integration

### Processing Audio Files

External systems can submit audio files for AI processing:

```python
import requests

class AIServiceClient:
    def __init__(self, ai_service_url):
        self.base_url = ai_service_url
    
    def transcribe_and_analyze(self, audio_file_path, language='sw'):
        """Submit audio for complete AI pipeline"""
        with open(audio_file_path, 'rb') as audio_file:
            response = requests.post(
                f'{self.base_url}/audio/process',
                files={'audio': audio_file},
                data={
                    'language': language,
                    'include_translation': 'true',
                    'include_classification': 'true'
                }
            )
        
        return response.json()
    
    def check_processing_status(self, task_id):
        """Check status of async processing"""
        response = requests.get(
            f'{self.base_url}/audio/task/{task_id}'
        )
        return response.json()

# Usage
ai_client = AIServiceClient('http://localhost:8123')

# Process audio file
result = ai_client.transcribe_and_analyze('call_recording.wav', 'sw')

print(f"Transcript: {result['transcript']}")
print(f"Translation: {result['translation']}")
print(f"Risk Level: {result['classification']['priority']}")
```

### Streaming Real-Time Results

```python
import requests

def process_with_streaming(audio_path):
    """Get real-time updates as audio is processed"""
    with open(audio_path, 'rb') as audio:
        response = requests.post(
            'http://localhost:8123/audio/process-stream',
            files={'audio': audio},
            data={'language': 'sw'},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                event = json.loads(line)
                
                if event['type'] == 'transcription_progress':
                    print(f"Transcription: {event['progress']}%")
                elif event['type'] == 'transcription_complete':
                    print(f"Text: {event['data']['text']}")
                elif event['type'] == 'classification_complete':
                    print(f"Risk: {event['data']['risk_level']}")
```

---

## Data Import/Export

### CSV Import

Import cases from CSV file:

```php
<?php
// import_cases.php
require_once 'vendor/autoload.php';

class CaseImporter {
    private $db;
    
    public function importFromCSV($filepath) {
        $file = fopen($filepath, 'r');
        
        // Skip header row
        fgetcsv($file);
        
        $imported = 0;
        $errors = [];
        
        while (($row = fgetcsv($file)) !== FALSE) {
            try {
                $this->createCase([
                    'case_number' => $row[0],
                    'title' => $row[1],
                    'description' => $row[2],
                    'category' => $row[3],
                    'priority' => $row[4],
                    'reporter_phone' => $row[5]
                ]);
                $imported++;
            } catch (Exception $e) {
                $errors[] = "Row {$row[0]}: {$e->getMessage()}";
            }
        }
        
        fclose($file);
        
        return [
            'imported' => $imported,
            'errors' => $errors
        ];
    }
    
    private function createCase($data) {
        // Validation
        if (empty($data['title'])) {
            throw new Exception('Title is required');
        }
        
        // Insert into database
        $sql = "INSERT INTO kase (case_number, title, description, category, priority, reporter_phone, created_at)
                VALUES (?, ?, ?, ?, ?, ?, NOW())";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute([
            $data['case_number'],
            $data['title'],
            $data['description'],
            $data['category'],
            $data['priority'],
            $data['reporter_phone']
        ]);
    }
}

// Usage
$importer = new CaseImporter($db);
$result = $importer->importFromCSV('cases.csv');

echo "Imported: {$result['imported']} cases\n";
if (!empty($result['errors'])) {
    echo "Errors:\n";
    foreach ($result['errors'] as $error) {
        echo "  - $error\n";
    }
}
?>
```

### JSON Export

Export cases to JSON:

```php
<?php
// export_cases.php

class CaseExporter {
    private $db;
    
    public function exportToJSON($filters = []) {
        $cases = $this->getCases($filters);
        $json = json_encode($cases, JSON_PRETTY_PRINT);
        
        // Save to file
        $filename = 'cases_export_' . date('Y-m-d_His') . '.json';
        file_put_contents($filename, $json);
        
        return $filename;
    }
    
    private function getCases($filters) {
        $sql = "SELECT k.*, u.username as assigned_to
                FROM kase k
                LEFT JOIN auth u ON k.assigned_user_id = u.id
                WHERE 1=1";
        
        $params = [];
        
        if (!empty($filters['status'])) {
            $sql .= " AND k.status = ?";
            $params[] = $filters['status'];
        }
        
        if (!empty($filters['created_after'])) {
            $sql .= " AND k.created_at >= ?";
            $params[] = $filters['created_after'];
        }
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

// Usage
$exporter = new CaseExporter($db);
$filename = $exporter->exportToJSON([
    'status' => 'resolved',
    'created_after' => '2025-01-01'
]);

echo "Exported to: $filename\n";
?>
```

---

## Database Integration (Read-Only)

For analytics and reporting, external systems can access the database directly:

### Read-Only User Setup

```sql
-- Create read-only user for external system
CREATE USER 'external_readonly'@'%' IDENTIFIED BY 'secure_password';

-- Grant SELECT only on specific tables
GRANT SELECT ON helpline.kase TO 'external_readonly'@'%';
GRANT SELECT ON helpline.contact TO 'external_readonly'@'%';
GRANT SELECT ON helpline.kase_activity TO 'external_readonly'@'%';
GRANT SELECT ON helpline.fact_* TO 'external_readonly'@'%';
GRANT SELECT ON helpline.mv_* TO 'external_readonly'@'%';

FLUSH PRIVILEGES;
```

### Python Database Connection

```python
import pymysql
import pandas as pd

class OpenCHSDatabase:
    def __init__(self, host, database, user, password):
        self.connection = pymysql.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def get_cases_dataframe(self, status=None):
        """Get cases as pandas DataFrame for analysis"""
        query = "SELECT * FROM kase"
        
        if status:
            query += f" WHERE status = '{status}'"
        
        return pd.read_sql(query, self.connection)
    
    def get_daily_metrics(self, days=30):
        """Get daily metrics for reporting"""
        query = f"""
            SELECT * FROM fact_case_daily
            WHERE metric_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
            ORDER BY metric_date DESC
        """
        return pd.read_sql(query, self.connection)

# Usage
db = OpenCHSDatabase(
    host='helpline.example.com',
    database='helpline',
    user='external_readonly',
    password='secure_password'
)

# Get all open cases
open_cases = db.get_cases_dataframe(status='open')
print(f"Open cases: {len(open_cases)}")

# Get metrics for dashboard
metrics = db.get_daily_metrics(days=7)
print(metrics[['metric_date', 'new_cases', 'resolved_cases']])
```

---

## Best Practices

### Security

1. **Use API Keys:** Don't embed credentials in code
2. **HTTPS Only:** Always use secure connections
3. **Rate Limiting:** Implement retry logic with exponential backoff
4. **Error Handling:** Gracefully handle API errors
5. **Logging:** Log all integration activities for debugging

### Performance

1. **Batch Operations:** Use batch APIs when available
2. **Pagination:** Handle large datasets with pagination
3. **Caching:** Cache frequently accessed data
4. **Async Processing:** Use async for long-running operations
5. **Connection Pooling:** Reuse database connections

### Data Integrity

1. **Validation:** Validate data before sending
2. **Idempotency:** Handle duplicate requests gracefully
3. **Transactions:** Use database transactions for consistency
4. **Error Recovery:** Implement retry mechanisms
5. **Monitoring:** Monitor integration health and errors

### Example: Robust Integration Class

```python
import requests
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """Decorator for retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

class RobustOpenCHSClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    @retry_on_failure(max_retries=3, delay=2)
    def create_case(self, case_data):
        """Create case with retry logic"""
        # Validate data
        self._validate_case_data(case_data)
        
        response = self.session.post(
            f'{self.base_url}/helpline/api/cases',
            json=case_data,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    def _validate_case_data(self, data):
        """Validate case data before submission"""
        required_fields = ['title', 'category', 'priority']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if data['priority'] not in ['low', 'medium', 'high', 'critical']:
            raise ValueError(f"Invalid priority: {data['priority']}")
```

---

## Troubleshooting

### Common Issues

**Authentication Failures:**
```bash
# Check API key validity
curl -X GET https://your-domain.com/helpline/api/health \
  -H "X-API-Key: your-api-key"

# Response should be 200 OK
```

**Connection Timeouts:**
```python
# Increase timeout for slow networks
response = requests.post(
    url,
    json=data,
    timeout=60  # 60 seconds
)
```

**Rate Limiting:**
```python
# Handle rate limit errors
try:
    response = client.post(url, json=data)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        retry_after = int(e.response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
        # Retry request
```

For additional support, contact the OpenCHS development team or consult the [API Reference](../api-reference/overview.md).