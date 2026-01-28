# Configuration System Guide

> Understanding how `config.php` powers the helpline system

## Overview

`config.php` is the central configuration file that defines all system-wide settings. It acts as a bridge between the PHP backend and JavaScript frontend, providing database credentials, API endpoints, and the category taxonomy that drives case management.

## How It Works

### The Bridge Pattern

The config file is included by both server-side and client-side entry points:

```
config.php
    ├── Backend (api/index.php)
    │   └── Uses PHP constants and variables directly
    │
    └── Frontend (index.php)
        └── Converts PHP variables to JavaScript globals
```

**Backend Usage:**
```php
// api/index.php
require_once 'config.php';

// Direct access to constants
$db = new mysqli(THE_DB_HOST, THE_DB_USN, THE_DB_PASSWD, THE_DB_NAME);
```

**Frontend Usage:**
```php
// index.php
require_once 'config.php';
?>
<script>
// PHP variables become JavaScript globals
var CASE_CATEGORY_ROOT_ID = "<?=$CASE_CATEGORY_ROOT_ID?>";
var VA_SIP_HOST = "<?=$VA_SIP_HOST?>";
</script>
```

## Configuration Sections

### 1. Database Connection
```php
define('THE_DB_USN', 'nginx');
define('THE_DB_NAME', 'helpline');
define('THE_DB_SOCK', '/var/lib/mysql/mysql.sock');
```

Uses Unix socket for fast local MySQL connections. These constants are used throughout the backend for all database operations.

### 2. VoIP/WebRTC Settings
```php
$VA_SIP_HOST = explode(":",$_SERVER["HTTP_HOST"])[0];
$VA_ICE_HOST = "stun:stun.l.google.com:19302";
$VA_AMI_HOST = "https://".explode(":",$_SERVER["HTTP_HOST"])[0]."/ami/";
```

**Dynamic host detection** - extracts the current server hostname so the same config works across dev/staging/production environments. The SIP and AMI endpoints adapt automatically.

### 3. Application Settings
```php
$COUNTRY_CODE = "254";  // Kenya
$CASE_ID_PREFIX = "TEST -";
$LOCATION_HIERARCHY = '"","Region","District","County","SubCounty","Parish","Village","Constituency"';
```

Country-specific settings for phone validation and administrative location structure.

### 4. API Gateway Integration
```php
$API_GATEWAY_AUTH = "https://demo-openchs.bitz-itc.com/api/token/";
$API_GATEWAY_SEND_MSG = "https://backend.bitz-itc.com/api/whatsapp/send/";
```

External service endpoints for WhatsApp messaging and national ID lookups.

### 5. Category Taxonomy
```php
$CASE_CATEGORY_ROOT_ID = "362557";      // Types of abuse
$AGE_GROUP_ROOT_ID = "101";             // Age ranges
$SEX_ROOT_ID = "120";                   // Gender
$MARITAL_STATUS_ROOT_ID = "236654";     // Marital status
// ... 20+ more category roots
```

**The Heart of the System** - These IDs point to root nodes in a hierarchical category tree stored in the database. Each root has child categories that form dropdowns in the UI.

### 6. Disposition Codes
```php
$DISPOSITION_ID_NEW_CASE = "363037";
$DISPOSITION_ID_FOLLOWUP = "362556";
$DISPOSITION_ID_COMPLETE = "362527";
```

Call wrap-up codes that track what happened during each call (new case created, follow-up, etc.). Used for reporting and analytics.

## The Category System

The most important concept in the config is the **category taxonomy system**.

### How It Works

1. **Database Structure**: Categories are stored hierarchically in the `category` table
   ```sql
   SELECT * FROM category WHERE parent_id = 362557;  -- Get abuse types
   ```

2. **Config Points to Roots**: Each `*_ROOT_ID` variable points to a top-level category
   ```
   CASE_CATEGORY_ROOT_ID (362557)
   ├── Physical Abuse (362263)
   ├── Sexual Abuse (362271)
   ├── Emotional Abuse (362279)
   └── Economic Abuse (362287)
   ```

3. **Frontend Loads Dynamically**: JavaScript reads the root ID and fetches categories from the API
   ```javascript
   // Loads all abuse types into dropdown
   ajax_get('/api/category?parent_id=' + CASE_CATEGORY_ROOT_ID, function(categories) {
       // Populate dropdown...
   });
   ```

### Why This Matters

- **No code changes needed** - Add categories in the database and they appear in the UI
- **Standardized reporting** - Every case is classified using the same taxonomy
- **Multi-language support** - Categories have translations (English/Kiswahili)
- **Business logic** - Specific category IDs trigger workflows (e.g., sexual abuse requires medical referral)

## Data Flow Example

Here's how a complete request uses the config:

```
1. User loads page
   └── index.php includes config.php
       └── Outputs CASE_CATEGORY_ROOT_ID as JavaScript global

2. JavaScript loads case form
   └── app/case.js reads CASE_CATEGORY_ROOT_ID
       └── Calls /api/category?parent_id=362557

3. Backend processes request
   └── api/index.php includes config.php
       └── Uses THE_DB_* constants to connect to MySQL
           └── Queries categories and returns JSON

4. Frontend renders dropdown
   └── User selects "Sexual Abuse" (362271)
       └── JavaScript checks if ID matches CASE_CATEGORY_SEXUAL_ABUSE_ID
           └── Shows additional required fields (medical referral)

5. User submits case
   └── Backend validates using CASE_CATEGORY_SEXUAL_ABUSE_ID
       └── Saves to database with proper disposition code
```

## Dynamic Host Detection

One clever feature: the config automatically detects the current hostname:

```php
$VA_SIP_HOST = explode(":",$_SERVER["HTTP_HOST"])[0];
```

**Example:**
- Access via `https://helpline.example.com:8443/`
- `$_SERVER["HTTP_HOST"]` = `"helpline.example.com:8443"`
- `explode(":")` splits into `["helpline.example.com", "8443"]`
- Take first element: `"helpline.example.com"`

**Result**: Same config file works on:
- Development: `localhost`
- Staging: `staging.helpline.org`
- Production: `helpline.example.com`

## Configuration Checklist

### Required Setup
- [ ] MySQL socket path is correct and accessible
- [ ] Timezone matches deployment location (`Africa/Kampala` for Kenya)
- [ ] Data directory exists: `/home/dat/helpline`
- [ ] All category root IDs exist in database

### VoIP Integration
- [ ] Asterisk server is running
- [ ] WebSocket port 8089 is accessible
- [ ] AMI endpoint responds at `/ami/`

### External Services
- [ ] API Gateway credentials are valid
- [ ] Test WhatsApp message sends successfully

### Production Checklist
- [ ] Change `CASE_ID_PREFIX` from `"TEST -"` to production value
- [ ] Set strong database password (not empty)
- [ ] Verify all category hierarchies are complete
- [ ] Update API Gateway endpoints to production URLs

## Troubleshooting

### Categories Not Loading
```javascript
// Debug in browser console
console.log(CASE_CATEGORY_ROOT_ID);  // Should output: "362557"
```
If undefined, check that `config.php` is included in `index.php`.

### Database Connection Failed
```bash
# Verify socket exists
ls -l /var/lib/mysql/mysql.sock

# Test connection
mysql -u nginx -p helpline
```

### VoIP Not Working
```javascript
// Check SIP host
console.log(VA_SIP_HOST);  // Should be your server hostname
```
Ensure hostname is accessible and Asterisk is running.

## Best Practices

1. **Never hardcode values** - Use config variables throughout the codebase
2. **Test after changes** - Reload both frontend and backend after editing config
3. **Keep categories organized** - Maintain clear hierarchies in the database
4. **Document custom IDs** - If you add specific category IDs for business logic, document them
5. **Backup before changes** - Config changes affect the entire system

## Summary

`config.php` is the configuration spine that:
- Provides database connectivity to the backend
- Exposes settings to the frontend as JavaScript globals
- Defines the category taxonomy used for case classification
- Configures external integrations (VoIP, WhatsApp, ID lookup)
- Adapts automatically to different environments via dynamic host detection

**Single source of truth** → Changes here propagate throughout the entire application.
