# Configuration System Guide

> Complete reference for understanding and managing `config.php`

## Overview

`config.php` is the **central nervous system** of the helpline application. It's a single PHP file that:

- Connects backend PHP to the MySQL database
- Exposes configuration to frontend JavaScript as global variables
- Defines the complete category taxonomy for case classification
- Configures external integrations (VoIP, WhatsApp, national ID lookup)
- Adapts automatically to different deployment environments

**Critical**: Every configuration change requires a full application reload (backend restart + frontend page refresh).

## Table of Contents

1. [How It Works](#how-it-works)
   - [The Bridge Pattern](#the-bridge-pattern)
2. [Configuration Sections](#configuration-sections)
   - [Database Connection](#1-database-connection)
   - [VoIP/WebRTC Settings](#2-voipwebrtc-settings)
   - [Application Settings](#3-application-settings)
   - [API Gateway Integration](#4-api-gateway-integration)
   - [Category Taxonomy](#5-category-taxonomy)
   - [Disposition Codes](#6-disposition-codes)
3. [The Category System](#the-category-system)
4. [Complete Taxonomy Reference](#complete-taxonomy-reference)
   - [Case Classification Categories](#1-case-classification-categories)
   - [Demographics & Identity Categories](#2-demographics--identity-categories)
   - [Socioeconomic Context Categories](#3-socioeconomic-context-categories)
   - [Call Disposition Categories](#4-call-disposition-categories)
5. [Special Category IDs](#special-category-ids)
6. [Data Flow Example](#data-flow-example)
7. [Dynamic Host Detection](#dynamic-host-detection)
8. [Configuration Checklist](#configuration-checklist)
9. [Extracting the Complete Taxonomy](#extracting-the-complete-taxonomy)
10. [Adding New Categories](#adding-new-categories)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)
13. [Practical Examples](#practical-examples)
14. [Configuration Variables Reference](#configuration-variables-reference)
15. [Quick Reference Card](#quick-reference-card)
16. [Summary](#summary)

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

## Complete Taxonomy Reference

The system uses **25 category hierarchies** organized into four functional groups:

### 1. Case Classification Categories

These categories classify the nature and details of abuse cases:

| Category Root | Config Variable | Root ID | Purpose |
|--------------|-----------------|---------|---------|
| **Types of Abuse** | `CASE_CATEGORY_ROOT_ID` | 362557 | Primary abuse classification (Physical, Sexual, Emotional, Economic, etc.) |
| **Case Assessment** | `CASE_ASSESSMENT_ROOT_ID` | 236694 | Risk assessment and urgency levels |
| **Justice/Legal Actions** | `CASE_JUSTICE_ROOT_ID` | 236687 | Legal proceedings and police involvement |
| **Referrals** | `CASE_REFERALS_ROOT_ID` | 236707 | Organizations/services the client was referred to |
| **Services Provided** | `CASE_SERVICES_ROOT_ID` | 113 | Direct services provided by helpline (counseling, legal aid, etc.) |
| **How Client Heard About 116** | `CASE_KNOW_ABOUT_116_ROOT_ID` | 236700 | Marketing/outreach effectiveness tracking |

**Example hierarchy for Types of Abuse:**
```
Types of Abuse (362557)
├── Physical Abuse (362263)
│   ├── Hitting/Beating
│   ├── Burning
│   └── Restraint
├── Sexual Abuse (362271)
│   ├── Rape
│   ├── Sexual Assault
│   ├── Child Sexual Abuse
│   └── Sexual Harassment
├── Emotional/Psychological Abuse (362279)
│   ├── Threats
│   ├── Humiliation
│   └── Isolation
└── Economic Abuse (362287)
    ├── Property Denial
    ├── Financial Control
    └── Employment Sabotage
```

### 2. Demographics & Identity Categories

These classify client and perpetrator demographics:

| Category Root | Config Variable | Root ID | Purpose |
|--------------|-----------------|---------|---------|
| **Age Groups** | `AGE_GROUP_ROOT_ID` | 101 | Age brackets (0-5, 6-12, 13-17, 18-24, 25-34, etc.) |
| **Sex/Gender** | `SEX_ROOT_ID` | 120 | Male, Female, Other/Prefer not to say |
| **Nationality** | `NATIONALITY_ROOT_ID` | 126 | Country of origin |
| **National ID Types** | `NATIONAL_ID_TYPE_ROOT_ID` | 362409 | Birth certificate, national ID, passport, etc. |
| **Languages** | `LANGUAGE_ROOT_ID` | 123 | Primary language spoken |
| **Tribes** | `TRIBE_ROOT_ID` | 133 | Ethnic/tribal affiliation |
| **Marital Status** | `MARITAL_STATUS_ROOT_ID` | 236654 | Single, married, divorced, widowed, etc. |

### 3. Socioeconomic Context Categories

These capture the client's living situation and vulnerabilities:

| Category Root | Config Variable | Root ID | Purpose |
|--------------|-----------------|---------|---------|
| **Locations** | `LOCATION_ROOT_ID` | 88 | Geographic hierarchy (Region → District → County → SubCounty → Parish → Village) |
| **Relationship to Perpetrator** | `RELATIONSHIP_ROOT_ID` | 236634 | Parent, spouse, stranger, teacher, etc. |
| **Disability Types** | `DISABILITY_ROOT_ID` | 236669 | Physical, mental, visual, hearing impairments |
| **Reasons Not in School** | `NOT_IN_SCHOOL_ROOT_ID` | 362466 | If child is out of school, why? |
| **Shares Home With** | `SHARES_HOME_ROOT_ID` | 236631 | Household composition |
| **Employment Status** | `EMPLOYMENT_STATUS_ROOT_ID` | 236648 | Employed, unemployed, student, etc. |
| **Health Status** | `HEALTH_STATUS_ROOT_ID` | 236660 | General health condition |
| **School Types** | `SCHOOL_TYPE_ROOT_ID` | 236711 | Public, private, boarding, etc. |
| **School Levels** | `SCHOOL_LEVEL_ROOT_ID` | 236712 | Primary, secondary, tertiary |
| **HIV Status** | `HIV_STATUS_ROOT_ID` | 105 | Positive, negative, unknown |
| **Household Types** | `HOUSEHOLD_TYPE_ROOT_ID` | 236674 | Single-parent, extended family, child-headed, etc. |

### 4. Call Disposition Categories

Track the outcome of each call:

| Category Root | Config Variable | Root ID | Purpose |
|--------------|-----------------|---------|---------|
| **Call Dispositions** | `DISPOSITION_ROOT_ID` | 362515 | What happened during the call (new case, follow-up, info only, etc.) |

**Specific Disposition IDs** (used in business logic):
```php
$DISPOSITION_ID_DEFAULT         = "362527";  // Default wrap-up
$DISPOSITION_ID_COMPLETE        = "362527";  // Call completed successfully
$DISPOSITION_ID_NEW_CASE        = "363037";  // New case created
$DISPOSITION_ID_FOLLOWUP        = "362556";  // Follow-up call
$DISPOSITION_ID_EDIT            = "362556";  // Editing existing record
$DISPOSITION_ID_CONTACT_NEW     = "363034";  // New contact created
$DISPOSITION_ID_CONTACT_EDIT    = "363033";  // Contact edited
$DISPOSITION_ID_CASE_UPDATE     = "363035";  // Case updated
$DISPOSITION_ID_CASE_UPDATE_FOLLOWUP = "363032";  // Case updated during follow-up
$DISPOSITION_ID_CASE_EDIT       = "363036";  // Case edited
$DISPOSITION_ID_CASE_EDIT_FOLLOWUP   = "363031";  // Case edited during follow-up
```

## Special Category IDs

These specific category IDs trigger special business logic in the application:

| Variable | ID(s) | Triggers |
|----------|-------|----------|
| `CASE_CATEGORY_ABUSE_ID` | 87 | General abuse indicator |
| `CASE_CATEGORY_SEXUAL_ABUSE_ID` | 362271 | Requires medical referral checkbox, GBV tracking |
| `CASE_CATEGORY_PHYSICAL_N_SEXUAL_ABUSE_ID` | 362263,362271 | Combined physical + sexual abuse |
| `CASE_SERVICE_REFERAL_ID` | 117 | Service marked as referral |
| `CASE_SERVICE_POLICE_ID` | 362036 | Police service selected |
| `CASE_SERVICE_OTHER_ID` | 362042 | "Other" service (shows text field) |
| `CASE_REFERAL_OTHER_ID` | 362009 | "Other" referral (shows text field) |
| `MARITAL_STATUS_WITH_SPOUSE_ID` | 362019,236657,236658,362020,236656 | Married/cohabiting statuses |

**Example usage in code:**
```javascript
// In app/case.js - Sexual abuse triggers additional fields
if (selectedCategoryId == CASE_CATEGORY_SEXUAL_ABUSE_ID) {
    document.getElementById('medical_referral_section').style.display = 'block';
    document.getElementById('gbv_tracking_fields').style.display = 'block';
}
```

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

## Extracting the Complete Taxonomy

To export the full category hierarchy from your database:

### Method 1: Using the Extraction Script

Run the included `extract_taxonomy.php` script:

```bash
php extract_taxonomy.php > taxonomy_output.txt
```

This generates a complete tree of all categories with their IDs, organized by root category.

### Method 2: Direct SQL Query

```sql
-- Get all categories under a specific root (e.g., Types of Abuse)
SELECT id, name, name_sw, level
FROM category
WHERE parent_id = '362557'
  AND active = 1
ORDER BY name;

-- Get the entire category tree
SELECT c1.id AS root_id, c1.name AS root_name,
       c2.id AS child_id, c2.name AS child_name,
       c3.id AS grandchild_id, c3.name AS grandchild_name
FROM category c1
LEFT JOIN category c2 ON c2.parent_id = c1.id
LEFT JOIN category c3 ON c3.parent_id = c2.id
WHERE c1.parent_id IS NULL OR c1.parent_id = ''
ORDER BY c1.name, c2.name, c3.name;
```

### Method 3: Via API

```javascript
// From browser console or frontend code
fetch('/api/category?parent_id=362557')
    .then(r => r.json())
    .then(categories => console.table(categories));
```

## Adding New Categories

To add a new category to the taxonomy:

1. **Insert into database:**
   ```sql
   INSERT INTO category (name, name_sw, parent_id, level, active)
   VALUES ('New Abuse Type', 'Aina Mpya', '362557', 2, 1);
   ```

2. **No config change needed** - The category appears immediately in dropdowns

3. **Optional: Add to config** if you need to reference it in business logic:
   ```php
   // In config.php
   $CASE_CATEGORY_NEW_ABUSE_ID = "123456";  // Use the new ID
   ```

4. **Update JavaScript** if special handling is required:
   ```javascript
   // In app/case.js
   if (categoryId == CASE_CATEGORY_NEW_ABUSE_ID) {
       // Special logic here
   }
   ```

## Troubleshooting

### Categories Not Loading

**Symptom:** Dropdowns are empty or show "Loading..."

**Debug steps:**
```javascript
// 1. Check if config variables are defined (browser console)
console.log(CASE_CATEGORY_ROOT_ID);  // Should output: "362557"
console.log(typeof CASE_CATEGORY_ROOT_ID);  // Should be "string"

// 2. Test the API endpoint directly
fetch('/api/category?parent_id=362557')
    .then(r => r.json())
    .then(data => console.log(data))
    .catch(err => console.error('API Error:', err));

// 3. Check for JavaScript errors
// Open browser DevTools → Console tab
```

**Common fixes:**
- Verify `config.php` is included in `index.php`
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check that `parent_id` column exists in `category` table
- Verify database contains data: `SELECT COUNT(*) FROM category;`

### Database Connection Failed

**Symptom:** `mysqli_connect()` errors or "Access denied"

**Debug steps:**
```bash
# 1. Verify MySQL is running
sudo systemctl status mysqld

# 2. Check socket exists and has correct permissions
ls -l /var/lib/mysql/mysql.sock
# Should show: srwxrwxrwx (socket file)

# 3. Test credentials
mysql -u nginx -p -S /var/lib/mysql/mysql.sock helpline
# Enter password when prompted (empty string if THE_DB_PASSWD is '')

# 4. Verify database exists
mysql -u nginx -p -S /var/lib/mysql/mysql.sock -e "SHOW DATABASES;"

# 5. Check user permissions
mysql -u root -p -e "SHOW GRANTS FOR 'nginx'@'localhost';"
```

**Common fixes:**
- Grant permissions: `GRANT ALL ON helpline.* TO 'nginx'@'localhost';`
- Restart MySQL: `sudo systemctl restart mysqld`
- Update socket path in config.php to match actual socket location
- If using TCP instead of socket, change to: `new mysqli(THE_DB_HOST, THE_DB_USN, THE_DB_PASSWD, THE_DB_NAME, 3306);`

### VoIP Not Working

**Symptom:** "Connection failed" or phones don't ring

**Debug steps:**
```javascript
// 1. Verify SIP configuration (browser console)
console.log('SIP Host:', VA_SIP_HOST);  // Should be your server hostname
console.log('ICE Host:', VA_ICE_HOST);  // STUN server
console.log('AMI Host:', VA_AMI_HOST);  // Asterisk Manager Interface

// 2. Check WebSocket connection
// Open browser DevTools → Network tab → WS filter
// Look for connection to ws://YOUR_HOST:8089/ws
```

```bash
# 3. Verify Asterisk is running
sudo asterisk -rx "core show version"

# 4. Check WebSocket is listening
sudo netstat -tlnp | grep 8089
# Should show: tcp ... :8089 ... LISTEN

# 5. Test AMI endpoint
curl -v https://YOUR_HOST/ami/
# Should return Asterisk Manager Interface response

# 6. Check SIP peers
sudo asterisk -rx "sip show peers"
```

**Common fixes:**
- Start Asterisk: `sudo systemctl start asterisk`
- Enable WebSocket in `/etc/asterisk/http.conf`: `enabled=yes`, `bindaddr=0.0.0.0`
- Check firewall: `sudo firewall-cmd --add-port=8089/tcp --permanent && sudo firewall-cmd --reload`
- Verify certificates for HTTPS (WebRTC requires secure context)
- Check browser console for CORS errors

### WhatsApp/SMS Not Sending

**Symptom:** Messages fail silently or return errors

**Debug steps:**
```bash
# 1. Test API Gateway authentication
curl -X POST https://demo-openchs.bitz-itc.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"ausername","password":"apassword"}'
# Should return: {"token": "..."}

# 2. Check message send endpoint
curl -X POST https://backend.bitz-itc.com/api/whatsapp/send/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to":"254712345678","message":"Test"}'
```

**Common fixes:**
- Update credentials in config.php: `$API_GATEWAY_USN`, `$API_GATEWAY_PASS`
- Verify API endpoints are accessible (not blocked by firewall)
- Check message format (phone numbers must include country code)
- Review API Gateway documentation for rate limits

### Wrong Categories Showing

**Symptom:** Dropdown shows unexpected categories or wrong language

**Debug steps:**
```sql
-- 1. Verify parent-child relationships
SELECT id, name, parent_id, level
FROM category
WHERE parent_id = 'YOUR_ROOT_ID'
ORDER BY name;

-- 2. Check for orphaned categories
SELECT id, name, parent_id
FROM category
WHERE parent_id NOT IN (SELECT id FROM category)
  AND parent_id IS NOT NULL
  AND parent_id != '';

-- 3. Verify active flag
SELECT id, name, active
FROM category
WHERE parent_id = 'YOUR_ROOT_ID';
```

**Common fixes:**
- Set correct `parent_id`: `UPDATE category SET parent_id = '362557' WHERE id = 'XXX';`
- Activate category: `UPDATE category SET active = 1 WHERE id = 'XXX';`
- Fix level hierarchy: `UPDATE category SET level = 2 WHERE parent_id IN (SELECT id FROM category WHERE level = 1);`

### Configuration Not Taking Effect

**Symptom:** Changes to config.php don't appear in the application

**Checklist:**
- [ ] Save config.php file
- [ ] Restart PHP-FPM: `sudo systemctl restart php-fpm`
- [ ] Clear OPcache: `sudo systemctl restart php-fpm` (or add `opcache.revalidate_freq=0` in dev)
- [ ] Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- [ ] Clear browser cache completely
- [ ] Check for syntax errors: `php -l config.php`
- [ ] Verify file permissions: `ls -l config.php` (should be readable by web server)

### Performance Issues with Categories

**Symptom:** Slow dropdown loading, timeouts

**Optimizations:**
```sql
-- 1. Add index on parent_id
CREATE INDEX idx_parent_id ON category(parent_id);

-- 2. Add composite index for common queries
CREATE INDEX idx_parent_active ON category(parent_id, active);

-- 3. Analyze table
ANALYZE TABLE category;

-- 4. Check table size
SELECT
    COUNT(*) as total_categories,
    COUNT(DISTINCT parent_id) as unique_parents,
    MAX(level) as max_depth
FROM category;
```

**Frontend optimizations:**
```javascript
// Cache categories in localStorage
localStorage.setItem('categories_' + rootId, JSON.stringify(categories));

// Lazy load deep hierarchies
// Only fetch children when parent is expanded
```

## Best Practices

### Development

1. **Never hardcode values**
   ```javascript
   // BAD
   if (categoryId == "362271") { ... }

   // GOOD
   if (categoryId == CASE_CATEGORY_SEXUAL_ABUSE_ID) { ... }
   ```

2. **Test after changes**
   ```bash
   # After editing config.php:
   sudo systemctl restart php-fpm
   # Then hard-refresh browser (Ctrl+Shift+R)
   ```

3. **Use version control**
   ```bash
   # Before making changes
   git diff config.php
   git commit -m "Update API Gateway endpoints"
   ```

4. **Comment your changes**
   ```php
   // Added 2025-01-15: New referral type for mental health services
   $CASE_REFERAL_MENTAL_HEALTH_ID = "400123";
   ```

### Category Management

5. **Maintain hierarchy consistency**
   - All categories under a root should have the same `level` value
   - Parent categories should have `level` = N, children `level` = N+1
   - Never create circular references (A → B → A)

6. **Use meaningful names**
   ```sql
   -- BAD
   INSERT INTO category (name) VALUES ('Type 1');

   -- GOOD
   INSERT INTO category (name, name_sw) VALUES ('Physical Abuse - Hitting', 'Unyanyasaji wa Kimwili - Kupiga');
   ```

7. **Provide translations**
   - Always include `name_sw` (Kiswahili) for bilingual support
   - Keep translations synchronized

8. **Mark inactive categories, don't delete**
   ```sql
   -- Don't delete old categories (breaks historical data)
   -- DELETE FROM category WHERE id = '123';

   -- Instead, deactivate
   UPDATE category SET active = 0 WHERE id = '123';
   ```

### Security

9. **Don't commit sensitive credentials**
   ```bash
   # Use environment variables or separate config file
   # Add to .gitignore:
   config.local.php
   ```

10. **Validate database input**
    ```php
    // All database queries use prepared statements (handled by lib/rest.php)
    // Never concatenate user input into SQL
    ```

11. **Restrict API Gateway credentials**
    - Use separate credentials for dev/staging/production
    - Rotate passwords regularly
    - Monitor API usage for anomalies

### Production Deployment

12. **Update environment-specific settings**
    ```php
    // Development
    define('ENVIRONMENT', 'development');
    $CASE_ID_PREFIX = "DEV-";
    error_reporting(E_ALL);

    // Production
    define('ENVIRONMENT', 'production');
    $CASE_ID_PREFIX = "CASE-";
    error_reporting(0);
    ```

13. **Use strong database passwords**
    ```php
    // Development
    define('THE_DB_PASSWD', '');

    // Production
    define('THE_DB_PASSWD', 'kJ9#mP2$vL8qR5nZ');
    ```

14. **Document all category IDs with business logic**
    ```php
    // Keep this list updated when adding conditional logic
    // CATEGORY IDS USED IN BUSINESS LOGIC:
    // - 362271: Sexual Abuse (triggers medical referral required)
    // - 362263: Physical Abuse (triggers injury documentation)
    // - 117: Referral service (shows referral organization field)
    ```

## Practical Examples

### Example 1: Adding a New Abuse Type

**Scenario:** Add "Financial Fraud" as a new abuse category

```sql
-- 1. Insert into database
INSERT INTO category (name, name_sw, parent_id, level, active, created_on, created_by)
VALUES (
    'Financial Fraud',
    'Ulaghai wa Fedha',
    '362557',  -- Types of Abuse root
    2,         -- Child of root (level 1) so this is level 2
    1,         -- Active
    NOW(),
    'admin'
);

-- 2. Get the new ID
SELECT id FROM category WHERE name = 'Financial Fraud';
-- Returns: 400500 (example)
```

```php
// 3. Add to config.php (if you need to reference it in code)
$CASE_CATEGORY_FINANCIAL_FRAUD_ID = "400500";
```

```javascript
// 4. Use in frontend logic (app/case.js)
if (categoryId == CASE_CATEGORY_FINANCIAL_FRAUD_ID) {
    // Show fields for transaction details
    document.getElementById('transaction_details_section').style.display = 'block';
}
```

### Example 2: Changing API Gateway Endpoint

**Scenario:** Migrate from demo to production API Gateway

```php
// Before (in config.php)
$API_GATEWAY_AUTH = "https://demo-openchs.bitz-itc.com/api/token/";
$API_GATEWAY_SEND_MSG = "https://backend.bitz-itc.com/api/whatsapp/send/";

// After
$API_GATEWAY_AUTH = "https://api.openchs.example.org/api/token/";
$API_GATEWAY_SEND_MSG = "https://api.example.org/api/whatsapp/send/";
$API_GATEWAY_USN = "production_user";
$API_GATEWAY_PASS = "production_secure_password";
```

```bash
# Test the new endpoint
curl -X POST https://api.openchs.example.org/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"production_user","password":"production_secure_password"}'

# Restart PHP-FPM to apply changes
sudo systemctl restart php-fpm
```

### Example 3: Multi-Environment Configuration

**Scenario:** Use different settings based on hostname

```php
// Detect environment from hostname
$hostname = explode(":", $_SERVER["HTTP_HOST"])[0];

if (strpos($hostname, 'localhost') !== false || strpos($hostname, '127.0.0.1') !== false) {
    // Development
    define('ENVIRONMENT', 'development');
    $CASE_ID_PREFIX = "DEV-";
    $API_GATEWAY_AUTH = "https://demo-openchs.bitz-itc.com/api/token/";
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
} elseif (strpos($hostname, 'staging') !== false) {
    // Staging
    define('ENVIRONMENT', 'staging');
    $CASE_ID_PREFIX = "STG-";
    $API_GATEWAY_AUTH = "https://staging-api.example.org/api/token/";
    error_reporting(E_ALL);
    ini_set('display_errors', 0);
} else {
    // Production
    define('ENVIRONMENT', 'production');
    $CASE_ID_PREFIX = "CASE-";
    $API_GATEWAY_AUTH = "https://api.example.org/api/token/";
    error_reporting(0);
}
```

### Example 4: Custom Location Hierarchy

**Scenario:** Adapt to a different country's administrative divisions

```php
// Kenya (current)
$LOCATION_HIERARCHY = '"","Region","District","County","SubCounty","Parish","Village","Constituency"';
$COUNTRY_CODE = "254";

// Tanzania
$LOCATION_HIERARCHY = '"","Zone","Region","District","Ward","Village"';
$COUNTRY_CODE = "255";

// Uganda
$LOCATION_HIERARCHY = '"","Region","District","County","SubCounty","Parish","Village"';
$COUNTRY_CODE = "256";
```

```sql
-- Update location categories in database to match hierarchy
UPDATE category SET level = 1 WHERE parent_id = '88' AND name IN ('Central', 'Eastern', 'Western');  -- Regions
UPDATE category SET level = 2 WHERE parent_id IN (SELECT id FROM category WHERE level = 1 AND parent_id = '88');  -- Districts
```

## Configuration Variables Reference

### Complete Variable List

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| **Database** |
| `THE_DB_USN` | Constant | `'nginx'` | MySQL username |
| `THE_DB_PASSWD` | Constant | `''` | MySQL password (empty in dev) |
| `THE_DB_HOST` | Constant | `'localhost'` | MySQL host |
| `THE_DB_NAME` | Constant | `'helpline'` | Database name |
| `THE_DB_SOCK` | Constant | `'/var/lib/mysql/mysql.sock'` | Unix socket path |
| `THE_APP_ID` | Constant | `'hlp'` | Application identifier |
| `DAT` | Constant | `'/home/dat/helpline'` | Data directory for recordings/exports |
| **VoIP** |
| `VA_SIP_USER_PREFIX` | Variable | `''` | SIP username prefix |
| `VA_SIP_PASS_PREFIX` | Variable | `'23kdefrtgos09812100'` | SIP password prefix |
| `VA_SIP_HOST` | Variable | Auto-detected | WebRTC SIP server hostname |
| `VA_ICE_HOST` | Variable | `'stun:stun.l.google.com:19302'` | STUN server for NAT traversal |
| `VA_AMI_HOST` | Variable | Auto-detected | Asterisk Manager Interface endpoint |
| `VA_ATI_HOST` | Variable | Auto-detected | Agent notification endpoint |
| **Application** |
| `APP_LOGO` | Variable | `'/helpline/images/logo.png'` | Logo path for UI |
| `COUNTRY_CODE` | Variable | `'254'` | Country calling code (Kenya) |
| `CASE_ID_PREFIX` | Variable | `'TEST -'` | Case number prefix |
| `LOCATION_HIERARCHY` | Variable | CSV string | Administrative division labels |
| `RECORDING_ARCHIVE_URL` | Variable | `''` | External archive for old recordings |
| **API Gateway** |
| `API_GATEWAY_USN` | Variable | `'ausername'` | WhatsApp/SMS gateway username |
| `API_GATEWAY_PASS` | Variable | `'apassword'` | WhatsApp/SMS gateway password |
| `API_GATEWAY_AUTH` | Variable | URL | Token authentication endpoint |
| `API_GATEWAY_SEND_MSG` | Variable | URL | Message sending endpoint |
| `API_GATEWAY_CLOSE_MSG` | Variable | URL | Chat session close endpoint |

See **Complete Taxonomy Reference** section above for all 25+ category root variables.

## Quick Reference Card

### Essential Category Root IDs

```
Case Classification:
├─ Types of Abuse: 362557
├─ Case Assessment: 236694
├─ Justice/Legal: 236687
├─ Referrals: 236707
└─ Services: 113

Demographics:
├─ Age Groups: 101
├─ Sex/Gender: 120
├─ Marital Status: 236654
├─ Nationality: 126
└─ Languages: 123

Location & Context:
├─ Locations: 88
├─ Relationships: 236634
├─ Employment: 236648
└─ Disabilities: 236669

Call Management:
└─ Dispositions: 362515
```

### Most-Used Specific IDs

```php
// Sexual abuse (triggers medical referral)
$CASE_CATEGORY_SEXUAL_ABUSE_ID = "362271";

// Disposition codes
$DISPOSITION_ID_NEW_CASE = "363037";
$DISPOSITION_ID_FOLLOWUP = "362556";
$DISPOSITION_ID_COMPLETE = "362527";

// Services
$CASE_SERVICE_POLICE_ID = "362036";
$CASE_SERVICE_REFERAL_ID = "117";
```

### Emergency Checklist

**Config not working?**
1. `php -l config.php` - Check syntax
2. `sudo systemctl restart php-fpm` - Restart PHP
3. Ctrl+Shift+R - Hard refresh browser
4. Check browser console for JS errors

**Categories not loading?**
1. `SELECT COUNT(*) FROM category WHERE parent_id = 'ROOT_ID';` - Verify data exists
2. Check network tab for `/api/category` calls
3. Verify `active = 1` on categories

**Database connection failing?**
1. `mysql -u nginx -p -S /var/lib/mysql/mysql.sock helpline` - Test connection
2. Check socket path: `ls -l /var/lib/mysql/mysql.sock`
3. Verify user permissions: `SHOW GRANTS FOR 'nginx'@'localhost';`

## Summary

`config.php` is the **single source of truth** for the entire helpline system:

### What It Does
- **Backend**: Provides database credentials, constants, and business logic IDs
- **Frontend**: Exposes configuration as JavaScript global variables
- **Taxonomy**: Defines 25+ category hierarchies for case classification
- **Integrations**: Configures VoIP (Asterisk), WhatsApp/SMS (API Gateway), national ID lookup
- **Portability**: Auto-detects hostname for seamless deployment across environments

### Key Concepts
1. **Category Roots** - Each `*_ROOT_ID` points to a top-level category in the database
2. **Dynamic Loading** - Categories are fetched via API, not hardcoded
3. **Business Logic IDs** - Specific category IDs trigger special behaviors (e.g., 362271 = sexual abuse requires medical referral)
4. **Bilingual Support** - All categories have English (`name`) and Kiswahili (`name_sw`) translations
5. **No Build Step** - Changes take effect immediately after PHP-FPM restart + browser refresh

### Impact of Changes
- Changing a root ID affects which categories appear in dropdowns
- Changing a business logic ID may break conditional workflows
- Changing database credentials breaks the entire application
- Changing API endpoints affects WhatsApp, SMS, and ID lookup features

**Rule of thumb**: Test thoroughly in development before changing production config.

---

**Need to extract full taxonomy?** Run: `php extract_taxonomy.php > taxonomy.txt`

**Need help?** Check the Troubleshooting section above for specific error messages.
