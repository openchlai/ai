# Configuring Communication Channels

## Overview

OpenCHS supports multiple communication channels to receive and manage cases from various sources. This guide covers the configuration and management of phone, web chat, SMS, email, and social media channels.

---

## Table of Contents

1. [Supported Channels](#supported-channels)
2. [Phone System Integration](#phone-system-integration)
3. [Web Chat Configuration](#web-chat-configuration)
4. [SMS Gateway Setup](#sms-gateway-setup)
5. [Email Integration](#email-integration)
6. [Social Media Integration](#social-media-integration)
7. [Channel Management](#channel-management)

---

## Supported Channels

### Channel Types

| Channel | Status | Use Case | Integration Complexity |
|---------|--------|----------|----------------------|
| **Phone/Voice** | ✅ Primary | Crisis calls, counseling | Medium |
| **Web Chat** | ✅ Available | Online support, inquiries | Low |
| **SMS** | ✅ Available | Text-based support | Medium |
| **Email** | ✅ Available | Non-urgent cases | Low |
| **WhatsApp** | 🔄 Optional | Messaging support | High |
| **Facebook** | 🔄 Optional | Social media outreach | High |
| **Telegram** | 🔄 Optional | Secure messaging | Medium |

### Channel Configuration Table

```sql
-- View configured channels
SELECT 
    id,
    name,
    type,
    status,
    config,
    created_at
FROM helpline.chan
ORDER BY type, name;
```

---

## Phone System Integration

### VoIP/PBX Configuration

OpenCHS integrates with SIP-based phone systems (Asterisk, FreePBX, 3CX).

#### Database Configuration

```sql
-- Add phone channel
INSERT INTO helpline.chan (name, type, status, config)
VALUES (
    'Main Helpline',
    'phone',
    'active',
    JSON_OBJECT(
        'provider', 'asterisk',
        'extension', '1000',
        'queue', 'helpline_queue',
        'recording', true,
        'dtmf_menu', true,
        'ai_transcription', true
    )
);
```

#### Asterisk Integration

**Configuration: `/etc/asterisk/extensions.conf`**

```conf
[helpline-incoming]
; Incoming call handling
exten => 1000,1,Answer()
exten => 1000,n,Set(CHANNEL(language)=en)
exten => 1000,n,Background(welcome)
exten => 1000,n,WaitExten(10)

; IVR Menu
exten => 1,1,Goto(emergency,1)
exten => 2,1,Goto(general-inquiry,1)
exten => 3,1,Goto(callback-request,1)

; Route to counselors
[general-inquiry]
exten => 1,1,Set(CALLERID(name)=Helpline Call)
exten => 1,n,Queue(helpline_queue,t,,,300)
exten => 1,n,Voicemail(1000@helpline)
exten => 1,n,Hangup()

; Emergency routing
[emergency]
exten => 1,1,Set(PRIORITY=urgent)
exten => 1,n,Queue(emergency_queue,t,,,180)
exten => 1,n,Hangup()

; Call recording
[helpline_queue]
exten => _X.,1,Set(MONITOR_FILENAME=/var/spool/asterisk/monitor/${UNIQUEID})
exten => _X.,n,MixMonitor(${MONITOR_FILENAME}.wav,b)
exten => _X.,n,Dial(${ARG1},30)
```

**Queue Configuration: `/etc/asterisk/queues.conf`**

```conf
[helpline_queue]
strategy = leastrecent
timeout = 30
retry = 5
maxlen = 20
announce-frequency = 60
announce-holdtime = yes
announce-position = yes
periodic-announce = queue-periodic-announce
periodic-announce-frequency = 60
member => SIP/counselor1
member => SIP/counselor2
member => SIP/counselor3
```

#### AGI Script Integration

Create an AGI script to log calls to OpenCHS:

**`/var/lib/asterisk/agi-bin/openchs-call-logger.php`**

```php
#!/usr/bin/php
<?php
// OpenCHS Call Logger AGI Script

// Read AGI environment
$agi = array();
while (!feof(STDIN)) {
    $line = trim(fgets(STDIN));
    if ($line === '') break;
    list($key, $value) = explode(':', $line, 2);
    $agi[trim($key)] = trim($value);
}

// Extract call details
$caller_id = $agi['agi_callerid'];
$extension = $agi['agi_extension'];
$uniqueid = $agi['agi_uniqueid'];
$channel = $agi['agi_channel'];

// Connect to database
$db = new PDO('mysql:host=localhost;dbname=helpline', 'nginx', '', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
]);

// Log call to database
$stmt = $db->prepare("
    INSERT INTO contact (phone, channel_id, call_id, status, created_at)
    VALUES (?, (SELECT id FROM chan WHERE type='phone' LIMIT 1), ?, 'incoming', NOW())
");
$stmt->execute([$caller_id, $uniqueid]);

// Return success
echo "200 result=1\n";
?>
```

Make script executable:
```bash
chmod +x /var/lib/asterisk/agi-bin/openchs-call-logger.php
```

### Call Recording Integration

```bash
# Configure recording storage
RECORDING_DIR="/var/spool/asterisk/monitor"
mkdir -p "$RECORDING_DIR"
chown asterisk:asterisk "$RECORDING_DIR"

# Post-processing script for recordings
cat > /usr/local/bin/process-call-recording.sh <<'EOF'
#!/bin/bash
RECORDING_FILE="$1"
CALL_ID="$2"

# Convert to appropriate format
sox "$RECORDING_FILE" -r 16000 -c 1 "${RECORDING_FILE}.processed.wav"

# Move to storage
mv "${RECORDING_FILE}.processed.wav" /var/www/html/helpline/storage/recordings/

# Update database
mysql helpline -e "
    UPDATE contact 
    SET recording_path='/storage/recordings/$(basename ${RECORDING_FILE}.processed.wav)' 
    WHERE call_id='$CALL_ID'
"

# Trigger AI transcription (optional)
curl -X POST http://localhost:8123/audio/process \
    -F "audio=@/var/www/html/helpline/storage/recordings/$(basename ${RECORDING_FILE}.processed.wav)" \
    -F "case_id=$CALL_ID"
EOF

chmod +x /usr/local/bin/process-call-recording.sh
```

---

## Web Chat Configuration

### Enable Web Chat Widget

**Location: `/var/www/html/helpline/config/channels.php`**

```php
<?php
return [
    'web_chat' => [
        'enabled' => true,
        'widget_url' => 'https://helpline.yourdomain.com/helpline/chat',
        'auto_assign' => true,
        'max_concurrent_chats' => 5,
        'typing_indicator' => true,
        'file_upload' => true,
        'max_file_size' => 5242880, // 5MB
        'offline_message' => true,
        'business_hours' => [
            'monday' => ['08:00-17:00'],
            'tuesday' => ['08:00-17:00'],
            'wednesday' => ['08:00-17:00'],
            'thursday' => ['08:00-17:00'],
            'friday' => ['08:00-17:00'],
            'saturday' => ['09:00-13:00'],
            'sunday' => 'closed',
        ],
    ],
];
```

### Database Configuration

```sql
-- Add web chat channel
INSERT INTO helpline.chan (name, type, status, config)
VALUES (
    'Website Chat',
    'web_chat',
    'active',
    JSON_OBJECT(
        'widget_enabled', true,
        'auto_greet', true,
        'greet_message', 'Hello! How can we help you today?',
        'greet_delay', 3,
        'allow_anonymous', true,
        'require_email', false,
        'max_concurrent', 5
    )
);
```

### Embed Chat Widget

Add to your website:

```html
<!-- OpenCHS Chat Widget -->
<script>
  window.OpenCHSChat = {
    apiUrl: 'https://helpline.yourdomain.com/helpline/api',
    channelId: 'web_chat',
    position: 'bottom-right',
    theme: {
      primaryColor: '#007bff',
      fontFamily: 'Arial, sans-serif'
    }
  };
</script>
<script src="https://helpline.yourdomain.com/helpline/chat-widget.js"></script>
```

### WebSocket Configuration (Real-time Chat)

**Nginx WebSocket Proxy**:

```nginx
# Add to /etc/nginx/sites-available/openchs
location /chat-ws {
    proxy_pass http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 86400;
}
```

---

## SMS Gateway Setup

### Twilio Integration

**Configuration: `/var/www/html/helpline/config/channels.php`**

```php
<?php
return [
    'sms' => [
        'enabled' => true,
        'provider' => 'twilio',
        'credentials' => [
            'account_sid' => env('TWILIO_ACCOUNT_SID'),
            'auth_token' => env('TWILIO_AUTH_TOKEN'),
            'phone_number' => env('TWILIO_PHONE_NUMBER'),
        ],
        'webhook_url' => 'https://helpline.yourdomain.com/helpline/api/webhooks/sms',
        'auto_reply' => true,
        'keywords' => [
            'HELP' => 'auto_response_help',
            'STOP' => 'unsubscribe',
            'URGENT' => 'priority_escalation',
        ],
    ],
];
```

**Environment Variables: `.env`**

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

### Database Configuration

```sql
-- Add SMS channel
INSERT INTO helpline.chan (name, type, status, config)
VALUES (
    'SMS Helpline',
    'sms',
    'active',
    JSON_OBJECT(
        'provider', 'twilio',
        'phone_number', '+1234567890',
        'auto_reply', true,
        'keyword_detection', true,
        'character_limit', 160
    )
);
```

### Webhook Handler

**Create: `/var/www/html/helpline/api/webhooks/sms.php`**

```php
<?php
// Twilio SMS Webhook Handler

require_once __DIR__ . '/../bootstrap.php';

// Validate Twilio signature
$validator = new \Twilio\Security\RequestValidator(getenv('TWILIO_AUTH_TOKEN'));
$signature = $_SERVER['HTTP_X_TWILIO_SIGNATURE'] ?? '';
$url = 'https://' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];

if (!$validator->validate($signature, $url, $_POST)) {
    http_response_code(403);
    exit('Invalid signature');
}

// Extract SMS details
$from = $_POST['From'];
$body = $_POST['Body'];
$messageSid = $_POST['MessageSid'];

// Log to database
$db = getDbConnection();
$stmt = $db->prepare("
    INSERT INTO contact (phone, message, channel_id, external_id, status, created_at)
    VALUES (?, ?, (SELECT id FROM chan WHERE type='sms' LIMIT 1), ?, 'received', NOW())
");
$stmt->execute([$from, $body, $messageSid]);
$contactId = $db->lastInsertId();

// Check for keywords
$keywords = ['HELP', 'URGENT', 'EMERGENCY'];
foreach ($keywords as $keyword) {
    if (stripos($body, $keyword) !== false) {
        // Auto-create case
        $stmt = $db->prepare("
            INSERT INTO kase (contact_id, priority, status, created_at)
            VALUES (?, 'high', 'open', NOW())
        ");
        $stmt->execute([$contactId]);
        break;
    }
}

// Send auto-reply
$response = new \Twilio\TwiML\MessagingResponse();
$response->message('Thank you for contacting our helpline. A counselor will respond shortly.');

header('Content-Type: text/xml');
echo $response;
```

### Africa's Talking Integration (Alternative)

```php
<?php
// Africa's Talking SMS Configuration
return [
    'sms' => [
        'enabled' => true,
        'provider' => 'africastalking',
        'credentials' => [
            'username' => env('AT_USERNAME'),
            'api_key' => env('AT_API_KEY'),
            'short_code' => env('AT_SHORT_CODE'),
        ],
        'webhook_url' => 'https://helpline.yourdomain.com/helpline/api/webhooks/sms-at',
    ],
];
```

---

## Email Integration

### IMAP Configuration

**Configuration: `/var/www/html/helpline/config/channels.php`**

```php
<?php
return [
    'email' => [
        'enabled' => true,
        'imap' => [
            'host' => env('IMAP_HOST', 'imap.gmail.com'),
            'port' => env('IMAP_PORT', 993),
            'username' => env('IMAP_USERNAME'),
            'password' => env('IMAP_PASSWORD'),
            'encryption' => 'ssl',
            'validate_cert' => true,
        ],
        'smtp' => [
            'host' => env('SMTP_HOST', 'smtp.gmail.com'),
            'port' => env('SMTP_PORT', 587),
            'username' => env('SMTP_USERNAME'),
            'password' => env('SMTP_PASSWORD'),
            'encryption' => 'tls',
            'from_address' => env('MAIL_FROM_ADDRESS', 'helpline@yourdomain.com'),
            'from_name' => env('MAIL_FROM_NAME', 'OpenCHS Helpline'),
        ],
        'polling_interval' => 60, // seconds
        'auto_reply' => true,
        'create_case_on_receive' => true,
    ],
];
```

### Database Configuration

```sql
-- Add email channel
INSERT INTO helpline.chan (name, type, status, config)
VALUES (
    'Email Support',
    'email',
    'active',
    JSON_OBJECT(
        'email_address', 'helpline@yourdomain.com',
        'auto_reply', true,
        'signature', 'OpenCHS Helpline Team',
        'max_attachment_size', 10485760
    )
);
```

### Email Polling Script

**Create: `/usr/local/bin/openchs-email-poller.php`**

```php
#!/usr/bin/php
<?php
// Email Polling Script for OpenCHS

require_once '/var/www/html/helpline/vendor/autoload.php';

$config = require '/var/www/html/helpline/config/channels.php';
$emailConfig = $config['email'];

// Connect to IMAP
$mailbox = new \PhpImap\Mailbox(
    '{' . $emailConfig['imap']['host'] . ':' . $emailConfig['imap']['port'] . '/imap/ssl}INBOX',
    $emailConfig['imap']['username'],
    $emailConfig['imap']['password']
);

// Get unread emails
$mailIds = $mailbox->searchMailbox('UNSEEN');

if (!$mailIds) {
    exit(0);
}

$db = new PDO('mysql:host=localhost;dbname=helpline', 'nginx', '');

foreach ($mailIds as $mailId) {
    $mail = $mailbox->getMail($mailId);
    
    // Insert into database
    $stmt = $db->prepare("
        INSERT INTO contact (email, subject, message, channel_id, status, created_at)
        VALUES (?, ?, ?, (SELECT id FROM chan WHERE type='email' LIMIT 1), 'received', NOW())
    ");
    $stmt->execute([
        $mail->fromAddress,
        $mail->subject,
        $mail->textPlain ?: $mail->textHtml
    ]);
    
    $contactId = $db->lastInsertId();
    
    // Create case
    $stmt = $db->prepare("
        INSERT INTO kase (contact_id, priority, status, created_at)
        VALUES (?, 'normal', 'open', NOW())
    ");
    $stmt->execute([$contactId]);
    
    // Mark as read
    $mailbox->markMailAsRead($mailId);
    
    // Send auto-reply
    if ($emailConfig['auto_reply']) {
        $transport = (new Swift_SmtpTransport($emailConfig['smtp']['host'], $emailConfig['smtp']['port']))
            ->setUsername($emailConfig['smtp']['username'])
            ->setPassword($emailConfig['smtp']['password'])
            ->setEncryption($emailConfig['smtp']['encryption']);
        
        $mailer = new Swift_Mailer($transport);
        
        $message = (new Swift_Message('Re: ' . $mail->subject))
            ->setFrom([$emailConfig['smtp']['from_address'] => $emailConfig['smtp']['from_name']])
            ->setTo([$mail->fromAddress])
            ->setBody('Thank you for contacting our helpline. We have received your message and will respond within 24 hours.');
        
        $mailer->send($message);
    }
}
```

**Add to crontab:**

```bash
# Check emails every 5 minutes
*/5 * * * * /usr/local/bin/openchs-email-poller.php >> /var/log/openchs/email-poller.log 2>&1
```

---

## Social Media Integration

### WhatsApp Business API

**Configuration:**

```php
<?php
return [
    'whatsapp' => [
        'enabled' => false, // Enable after setup
        'provider' => 'twilio', // or 'whatsapp_business_api'
        'credentials' => [
            'account_sid' => env('TWILIO_ACCOUNT_SID'),
            'auth_token' => env('TWILIO_AUTH_TOKEN'),
            'whatsapp_number' => env('WHATSAPP_NUMBER'), // Format: whatsapp:+1234567890
        ],
        'webhook_url' => 'https://helpline.yourdomain.com/helpline/api/webhooks/whatsapp',
        'template_namespace' => env('WHATSAPP_TEMPLATE_NAMESPACE'),
    ],
];
```

### Facebook Messenger Integration

```php
<?php
return [
    'facebook' => [
        'enabled' => false,
        'page_access_token' => env('FB_PAGE_ACCESS_TOKEN'),
        'verify_token' => env('FB_VERIFY_TOKEN'),
        'app_secret' => env('FB_APP_SECRET'),
        'webhook_url' => 'https://helpline.yourdomain.com/helpline/api/webhooks/facebook',
    ],
];
```

---

## Channel Management

### Enable/Disable Channels

```sql
-- Disable channel
UPDATE helpline.chan
SET status = 'inactive'
WHERE type = 'sms';

-- Enable channel
UPDATE helpline.chan
SET status = 'active'
WHERE type = 'sms';
```

### Channel Statistics

```sql
-- View channel usage statistics
SELECT 
    c.name AS channel_name,
    c.type,
    c.status,
    COUNT(co.id) AS total_contacts,
    COUNT(CASE WHEN co.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) AS contacts_last_7_days,
    COUNT(CASE WHEN co.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) AS contacts_last_30_days
FROM helpline.chan c
LEFT JOIN helpline.contact co ON c.id = co.channel_id
GROUP BY c.id
ORDER BY total_contacts DESC;
```

### Channel Routing Rules

```sql
-- Create channel routing table
CREATE TABLE IF NOT EXISTS helpline.channel_routing (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    channel_id INT UNSIGNED,
    condition_type VARCHAR(50), -- keyword, time, priority
    condition_value VARCHAR(255),
    action_type VARCHAR(50), -- assign_team, escalate, auto_reply
    action_value TEXT,
    priority INT DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES chan(id)
);

-- Example: Route urgent SMS to emergency team
INSERT INTO helpline.channel_routing (channel_id, condition_type, condition_value, action_type, action_value)
VALUES (
    (SELECT id FROM chan WHERE type='sms'),
    'keyword',
    'URGENT|EMERGENCY',
    'assign_team',
    'emergency_team'
);
```

---

## Testing Channels

### Test Phone System

```bash
# Test call to extension
asterisk -rx "originate SIP/1000 application Playback demo-thanks"

# Check queue status
asterisk -rx "queue show helpline_queue"

# View active calls
asterisk -rx "core show channels"
```

### Test Web Chat

```bash
# Test chat API endpoint
curl -X POST https://helpline.yourdomain.com/helpline/api/chat/start \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "Hello, this is a test"
  }'
```

### Test SMS

```bash
# Send test SMS via Twilio
curl -X POST https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json \
  --data-urlencode "To=+1234567890" \
  --data-urlencode "From=$TWILIO_PHONE_NUMBER" \
  --data-urlencode "Body=Test message from OpenCHS" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

---

## Next Steps

After configuring communication channels:

1. **Set Up Monitoring**: See [System Health Checks](../maintenance-monitoring/system-health-checks.md)
2. **Configure Performance**: See [Performance Tuning](../maintenance-monitoring/performance-tuning.md)
3. **Review Logs**: See [Logging & Auditing](../maintenance-monitoring/logging-auditing.md)

---

## Quick Reference

### Channel Status Commands

```bash
# View all channels
mysql helpline -e "SELECT * FROM chan;"

# Check channel configuration
mysql helpline -e "SELECT name, type, status, config FROM chan WHERE type='sms';"

# Count contacts by channel
mysql helpline -e "
SELECT c.name, COUNT(co.id) 
FROM chan c 
LEFT JOIN contact co ON c.id = co.channel_id 
GROUP BY c.id;
"
```