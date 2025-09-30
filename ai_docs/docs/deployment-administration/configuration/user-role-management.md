# User Role Management

## Overview

OpenCHS implements a comprehensive role-based access control (RBAC) system to manage user permissions and access levels. This guide covers user creation, role assignment, and permission management for the Helpline system.

---

## Table of Contents

1. [User Roles Overview](#user-roles-overview)
2. [Creating Users](#creating-users)
3. [Managing Roles](#managing-roles)
4. [Permission Management](#permission-management)
5. [Authentication & Authorization](#authentication--authorization)
6. [Best Practices](#best-practices)

---

## User Roles Overview

### Default Roles

OpenCHS provides five default roles with hierarchical permissions:

| Role | Description | Access Level |
|------|-------------|--------------|
| **Super Admin** | Full system access and configuration | All permissions |
| **Administrator** | Manages users, cases, and reports | Most permissions except system config |
| **Supervisor** | Oversees counselors and reviews cases | Case management and team oversight |
| **Counselor** | Handles calls and manages assigned cases | Case entry and updates |
| **Viewer** | Read-only access to reports | View-only permissions |

### Permission Matrix

| Permission | Super Admin | Administrator | Supervisor | Counselor | Viewer |
|------------|-------------|---------------|------------|-----------|--------|
| Manage Users | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage Roles | ✅ | ✅ | ❌ | ❌ | ❌ |
| System Configuration | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create Cases | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit Own Cases | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit All Cases | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete Cases | ✅ | ✅ | ❌ | ❌ | ❌ |
| View All Cases | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| Generate Reports | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Export Data | ✅ | ✅ | ✅ | ❌ | ❌ |
| AI Service Access | ✅ | ✅ | ✅ | ✅ | ❌ |

✅ = Full access  
⚠️ = Limited access (own/assigned cases only)  
❌ = No access

---

## Creating Users

### Via Web Interface

1. **Login as Administrator**
   - Navigate to: `https://helpline.yourdomain.com/helpline/admin`
   - Enter admin credentials

2. **Access User Management**
   - Click on "Users" in the sidebar
   - Click "Add New User" button

3. **Fill User Details**
   ```
   First Name: John
   Last Name: Doe
   Email: john.doe@example.com
   Username: jdoe
   Role: Counselor
   Status: Active
   ```

4. **Set Initial Password**
   - Generate secure password or allow user to set on first login
   - Enable "Force Password Change on First Login" (recommended)

5. **Assign Additional Permissions** (Optional)
   - Select custom permissions if needed
   - Assign to specific teams or departments

### Via Database (Manual)

```sql
-- Insert new user
INSERT INTO helpline.auth (username, email, password_hash, role, status, created_at)
VALUES ('jdoe', 'john.doe@example.com', '$2y$10$password_hash_here', 'counselor', 'active', NOW());

-- Set user profile information
INSERT INTO helpline.user_profile (user_id, first_name, last_name, phone, department)
VALUES (LAST_INSERT_ID(), 'John', 'Doe', '+254712345678', 'Child Protection');
```

### Via API

```bash
# Create user via API
curl -X POST https://helpline.yourdomain.com/helpline/api/v1/users \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jdoe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "counselor",
    "password": "SecurePassword123!",
    "force_password_change": true,
    "status": "active"
  }'
```

### Bulk User Import

Create a CSV file with user data:

```csv
username,email,first_name,last_name,role,department,phone
jdoe,john.doe@example.com,John,Doe,counselor,Child Protection,+254712345678
jsmith,jane.smith@example.com,Jane,Smith,supervisor,Mental Health,+254723456789
```

Import via command line:

```bash
# Run import script
php artisan users:import /path/to/users.csv
```

---

## Managing Roles

### Creating Custom Roles

```sql
-- Create custom role in database
INSERT INTO helpline.roles (name, display_name, description, level, created_at)
VALUES ('team_lead', 'Team Lead', 'Leads a specific team of counselors', 3, NOW());

-- Assign permissions to the role
INSERT INTO helpline.role_permissions (role_id, permission_id)
SELECT 
    (SELECT id FROM helpline.roles WHERE name = 'team_lead'),
    id
FROM helpline.permissions
WHERE name IN (
    'view_cases',
    'create_cases',
    'edit_own_cases',
    'assign_cases',
    'view_team_reports'
);
```

### Modifying Existing Roles

```sql
-- Update role permissions
-- Remove permission
DELETE FROM helpline.role_permissions
WHERE role_id = (SELECT id FROM helpline.roles WHERE name = 'counselor')
AND permission_id = (SELECT id FROM helpline.permissions WHERE name = 'delete_cases');

-- Add permission
INSERT INTO helpline.role_permissions (role_id, permission_id)
VALUES (
    (SELECT id FROM helpline.roles WHERE name = 'counselor'),
    (SELECT id FROM helpline.permissions WHERE name = 'export_own_cases')
);
```

### Role Hierarchy

Define role hierarchy for inheritance:

```sql
-- Define role hierarchy (higher level inherits lower level permissions)
-- Level 5: Super Admin
-- Level 4: Administrator
-- Level 3: Supervisor
-- Level 2: Counselor
-- Level 1: Viewer

UPDATE helpline.roles SET level = 5 WHERE name = 'super_admin';
UPDATE helpline.roles SET level = 4 WHERE name = 'administrator';
UPDATE helpline.roles SET level = 3 WHERE name = 'supervisor';
UPDATE helpline.roles SET level = 2 WHERE name = 'counselor';
UPDATE helpline.roles SET level = 1 WHERE name = 'viewer';
```

---

## Permission Management

### Available Permissions

```sql
-- List all available permissions
SELECT 
    p.name,
    p.display_name,
    p.category,
    p.description
FROM helpline.permissions p
ORDER BY p.category, p.display_name;
```

### Permission Categories

1. **User Management**
   - `manage_users`: Create, edit, delete users
   - `manage_roles`: Create, edit roles and permissions
   - `view_users`: View user list and profiles

2. **Case Management**
   - `create_cases`: Create new cases
   - `edit_own_cases`: Edit assigned cases
   - `edit_all_cases`: Edit any case
   - `delete_cases`: Delete cases
   - `view_own_cases`: View assigned cases
   - `view_all_cases`: View all cases
   - `assign_cases`: Assign cases to users
   - `close_cases`: Close completed cases

3. **Reporting**
   - `view_reports`: Access reports dashboard
   - `generate_reports`: Create custom reports
   - `export_reports`: Export report data
   - `view_analytics`: Access analytics dashboard

4. **AI Service**
   - `use_ai_service`: Access AI processing features
   - `view_ai_insights`: View AI-generated insights
   - `manage_ai_settings`: Configure AI service settings

5. **System**
   - `system_configuration`: Access system settings
   - `view_audit_logs`: View system audit logs
   - `manage_integrations`: Configure external integrations
   - `backup_restore`: Perform backup and restore operations

### Granting Individual Permissions

```sql
-- Grant specific permission to a user (overrides role permissions)
INSERT INTO helpline.user_permissions (user_id, permission_id, granted)
VALUES (
    (SELECT id FROM helpline.auth WHERE username = 'jdoe'),
    (SELECT id FROM helpline.permissions WHERE name = 'export_reports'),
    TRUE
);

-- Revoke specific permission from a user
INSERT INTO helpline.user_permissions (user_id, permission_id, granted)
VALUES (
    (SELECT id FROM helpline.auth WHERE username = 'jdoe'),
    (SELECT id FROM helpline.permissions WHERE name = 'delete_cases'),
    FALSE
);
```

### Checking User Permissions

```sql
-- Check if user has specific permission
SELECT 
    u.username,
    r.display_name AS role,
    p.name AS permission,
    CASE 
        WHEN up.granted IS NOT NULL THEN up.granted
        WHEN rp.permission_id IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS has_permission
FROM helpline.auth u
JOIN helpline.roles r ON u.role = r.name
LEFT JOIN helpline.user_permissions up ON u.id = up.user_id
LEFT JOIN helpline.role_permissions rp ON r.id = rp.role_id
LEFT JOIN helpline.permissions p ON 
    (up.permission_id = p.id OR rp.permission_id = p.id)
WHERE u.username = 'jdoe'
AND p.name = 'edit_all_cases';
```

---

## Authentication & Authorization

### Password Policies

Configure in `/var/www/html/helpline/config/auth.php`:

```php
<?php
return [
    'passwords' => [
        'min_length' => 8,
        'require_uppercase' => true,
        'require_lowercase' => true,
        'require_numbers' => true,
        'require_special_chars' => true,
        'expiry_days' => 90,
        'history_count' => 5, // Can't reuse last 5 passwords
        'max_attempts' => 5,
        'lockout_duration' => 30, // minutes
    ],
    
    'session' => [
        'lifetime' => 480, // 8 hours
        'idle_timeout' => 60, // minutes
        'force_reauth_for_sensitive' => true,
    ],
    
    'mfa' => [
        'enabled' => false,
        'required_for_admins' => true,
        'methods' => ['totp', 'sms'],
    ],
];
```

### Session Management

```sql
-- View active sessions
SELECT 
    s.session_id,
    u.username,
    u.email,
    s.ip_address,
    s.user_agent,
    s.last_activity,
    TIMESTAMPDIFF(MINUTE, s.last_activity, NOW()) AS idle_minutes
FROM helpline.session s
JOIN helpline.auth u ON s.user_id = u.id
WHERE s.expires_at > NOW()
ORDER BY s.last_activity DESC;

-- Terminate user sessions (force logout)
DELETE FROM helpline.session
WHERE user_id = (SELECT id FROM helpline.auth WHERE username = 'jdoe');

-- Terminate idle sessions
DELETE FROM helpline.session
WHERE last_activity < DATE_SUB(NOW(), INTERVAL 60 MINUTE);
```

### Two-Factor Authentication (2FA)

Enable 2FA for enhanced security:

```sql
-- Enable 2FA for user
UPDATE helpline.auth
SET 
    two_factor_enabled = TRUE,
    two_factor_method = 'totp'
WHERE username = 'admin';

-- Require 2FA for specific roles
UPDATE helpline.roles
SET require_two_factor = TRUE
WHERE name IN ('super_admin', 'administrator');
```

---

## Best Practices

### User Account Security

1. **Strong Password Requirements**
   ```bash
   # Password must contain:
   - At least 8 characters
   - Upper and lowercase letters
   - Numbers
   - Special characters (!@#$%^&*)
   ```

2. **Regular Password Rotation**
   ```sql
   -- Find users who haven't changed password in 90+ days
   SELECT 
       username,
       email,
       last_password_change,
       DATEDIFF(NOW(), last_password_change) AS days_since_change
   FROM helpline.auth
   WHERE last_password_change < DATE_SUB(NOW(), INTERVAL 90 DAY)
   OR last_password_change IS NULL;
   ```

3. **Account Lockout Policy**
   ```sql
   -- Check locked accounts
   SELECT username, email, locked_at, failed_login_attempts
   FROM helpline.auth
   WHERE status = 'locked';
   
   -- Unlock account
   UPDATE helpline.auth
   SET 
       status = 'active',
       locked_at = NULL,
       failed_login_attempts = 0
   WHERE username = 'jdoe';
   ```

### Role Assignment Guidelines

1. **Principle of Least Privilege**
   - Assign minimum required permissions
   - Grant additional permissions only when justified
   - Regular permission audits

2. **Separation of Duties**
   - No single user should have complete control
   - Critical operations require multiple approvers
   - Separate administrative and operational roles

3. **Regular Access Reviews**
   ```sql
   -- Users with administrative access
   SELECT 
       u.username,
       u.email,
       r.display_name AS role,
       u.last_login,
       u.created_at
   FROM helpline.auth u
   JOIN helpline.roles r ON u.role = r.name
   WHERE r.level >= 3
   ORDER BY u.last_login DESC;
   ```

### Audit Logging

Enable comprehensive audit logging:

```sql
-- Create audit log table
CREATE TABLE IF NOT EXISTS helpline.audit_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED,
    action VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id INT UNSIGNED,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created_at (created_at)
);

-- Query audit logs
SELECT 
    al.id,
    u.username,
    al.action,
    al.resource_type,
    al.resource_id,
    al.ip_address,
    al.created_at
FROM helpline.audit_log al
LEFT JOIN helpline.auth u ON al.user_id = u.id
WHERE al.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY al.created_at DESC
LIMIT 100;
```

### User Lifecycle Management

1. **New User Onboarding**
   ```bash
   # Onboarding checklist
   ✓ Create user account
   ✓ Assign appropriate role
   ✓ Set temporary password
   ✓ Enable force password change
   ✓ Provide training materials
   ✓ Document access granted
   ```

2. **User Deactivation**
   ```sql
   -- Deactivate user (soft delete)
   UPDATE helpline.auth
   SET 
       status = 'inactive',
       deactivated_at = NOW(),
       deactivated_by = 'admin_username'
   WHERE username = 'jdoe';
   
   -- Terminate all sessions
   DELETE FROM helpline.session
   WHERE user_id = (SELECT id FROM helpline.auth WHERE username = 'jdoe');
   ```

3. **User Deletion**
   ```sql
   -- Hard delete user (use with caution)
   -- First, reassign or archive their cases
   UPDATE helpline.kase
   SET assigned_to = NULL, notes = CONCAT(notes, '\n[User deleted: jdoe]')
   WHERE assigned_to = (SELECT id FROM helpline.auth WHERE username = 'jdoe');
   
   -- Delete user records
   DELETE FROM helpline.user_permissions WHERE user_id = (SELECT id FROM helpline.auth WHERE username = 'jdoe');
   DELETE FROM helpline.user_profile WHERE user_id = (SELECT id FROM helpline.auth WHERE username = 'jdoe');
   DELETE FROM helpline.audit_log WHERE user_id = (SELECT id FROM helpline.auth WHERE username = 'jdoe');
   DELETE FROM helpline.auth WHERE username = 'jdoe';
   ```

---

## Common Administrative Tasks

### Reset User Password

**Via Web Interface:**
1. Navigate to Users → Select User
2. Click "Reset Password"
3. Choose method: Email link or Set new password
4. Check "Force password change on next login"

**Via Database:**
```sql
-- Generate new password hash (use bcrypt)
-- For demonstration, using PHP command line:
-- php -r "echo password_hash('NewPassword123!', PASSWORD_BCRYPT);"

UPDATE helpline.auth
SET 
    password_hash = '$2y$10$generated_hash_here',
    force_password_change = TRUE,
    last_password_change = NULL
WHERE username = 'jdoe';
```

### Unlock Locked Account

```sql
-- Unlock user account after failed login attempts
UPDATE helpline.auth
SET 
    status = 'active',
    locked_at = NULL,
    failed_login_attempts = 0
WHERE username = 'jdoe';
```

### Change User Role

```sql
-- Change user role
UPDATE helpline.auth
SET 
    role = 'supervisor',
    updated_at = NOW(),
    updated_by = 'admin_username'
WHERE username = 'jdoe';

-- Log the change in audit log
INSERT INTO helpline.audit_log (user_id, action, resource_type, resource_id, old_values, new_values, ip_address)
VALUES (
    (SELECT id FROM helpline.auth WHERE username = 'admin_username'),
    'role_change',
    'user',
    (SELECT id FROM helpline.auth WHERE username = 'jdoe'),
    JSON_OBJECT('role', 'counselor'),
    JSON_OBJECT('role', 'supervisor'),
    '127.0.0.1'
);
```

### View User Activity

```sql
-- Recent user activity
SELECT 
    u.username,
    u.email,
    u.last_login,
    u.login_count,
    COUNT(DISTINCT k.id) AS cases_handled,
    COUNT(DISTINCT ka.id) AS activities_logged
FROM helpline.auth u
LEFT JOIN helpline.kase k ON u.id = k.assigned_to
LEFT JOIN helpline.kase_activity ka ON u.id = ka.user_id
WHERE u.status = 'active'
GROUP BY u.id
ORDER BY u.last_login DESC;
```

### Bulk Role Assignment

```sql
-- Assign role to multiple users
UPDATE helpline.auth
SET role = 'counselor'
WHERE username IN ('user1', 'user2', 'user3', 'user4');

-- Assign role based on department
UPDATE helpline.auth u
JOIN helpline.user_profile up ON u.id = up.user_id
SET u.role = 'supervisor'
WHERE up.department = 'Child Protection'
AND u.role = 'counselor';
```

---

## Security Reports

### Generate User Access Report

```sql
-- Comprehensive user access report
SELECT 
    u.id,
    u.username,
    u.email,
    r.display_name AS role,
    u.status,
    u.two_factor_enabled,
    u.last_login,
    u.last_password_change,
    DATEDIFF(NOW(), u.last_password_change) AS password_age_days,
    u.failed_login_attempts,
    GROUP_CONCAT(DISTINCT p.name) AS additional_permissions
FROM helpline.auth u
JOIN helpline.roles r ON u.role = r.name
LEFT JOIN helpline.user_permissions up ON u.id = up.user_id AND up.granted = TRUE
LEFT JOIN helpline.permissions p ON up.permission_id = p.id
GROUP BY u.id
ORDER BY r.level DESC, u.username;
```

### Inactive Users Report

```sql
-- Find users who haven't logged in recently
SELECT 
    username,
    email,
    role,
    last_login,
    DATEDIFF(NOW(), last_login) AS days_since_login,
    status
FROM helpline.auth
WHERE last_login < DATE_SUB(NOW(), INTERVAL 30 DAY)
OR last_login IS NULL
ORDER BY last_login ASC;
```

### Permission Changes Report

```sql
-- Recent permission changes from audit log
SELECT 
    al.created_at,
    admin.username AS changed_by,
    target.username AS target_user,
    al.action,
    al.old_values,
    al.new_values
FROM helpline.audit_log al
JOIN helpline.auth admin ON al.user_id = admin.id
JOIN helpline.auth target ON al.resource_id = target.id
WHERE al.resource_type = 'user'
AND al.action IN ('role_change', 'permission_grant', 'permission_revoke')
AND al.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY al.created_at DESC;
```

---

## Integration with AI Service

### AI Service Access Control

Users with `use_ai_service` permission can access AI features. Configure access in the application:

```php
// Check if user can use AI service
if (hasPermission($user, 'use_ai_service')) {
    // Allow access to AI processing endpoints
    $aiService->processAudio($audioFile);
}
```

### AI Usage Tracking

```sql
-- Track AI service usage by user
CREATE TABLE IF NOT EXISTS helpline.ai_usage_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED,
    case_id INT UNSIGNED,
    service_type VARCHAR(50), -- transcription, translation, etc.
    processing_time DECIMAL(10,2),
    file_size_mb DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_case_id (case_id),
    INDEX idx_created_at (created_at)
);

-- Query AI usage by user
SELECT 
    u.username,
    COUNT(*) AS total_requests,
    SUM(aul.processing_time) AS total_processing_time,
    AVG(aul.processing_time) AS avg_processing_time,
    SUM(aul.file_size_mb) AS total_data_processed
FROM helpline.ai_usage_log aul
JOIN helpline.auth u ON aul.user_id = u.id
WHERE aul.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY u.id
ORDER BY total_requests DESC;
```

---

## Troubleshooting

### User Cannot Login

**Check account status:**
```sql
SELECT 
    username,
    email,
    status,
    locked_at,
    failed_login_attempts,
    password_hash IS NOT NULL AS has_password
FROM helpline.auth
WHERE username = 'jdoe';
```

**Common issues:**
- Account locked due to failed login attempts
- Account status set to 'inactive'
- Password expired
- Session conflicts

**Resolution:**
```sql
-- Unlock and reset
UPDATE helpline.auth
SET 
    status = 'active',
    locked_at = NULL,
    failed_login_attempts = 0
WHERE username = 'jdoe';
```

### Permission Denied Errors

**Check user permissions:**
```sql
-- Verify user has required permission
SELECT 
    u.username,
    u.role,
    p.name AS permission,
    CASE 
        WHEN up.granted IS NOT NULL THEN up.granted
        WHEN rp.permission_id IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS has_permission
FROM helpline.auth u
JOIN helpline.roles r ON u.role = r.name
LEFT JOIN helpline.role_permissions rp ON r.id = rp.role_id
LEFT JOIN helpline.permissions p ON rp.permission_id = p.id
LEFT JOIN helpline.user_permissions up ON u.id = up.user_id AND up.permission_id = p.id
WHERE u.username = 'jdoe'
AND p.name = 'edit_all_cases';
```

### Session Issues

**Clear stuck sessions:**
```sql
-- Remove expired sessions
DELETE FROM helpline.session
WHERE expires_at < NOW();

-- Clear all sessions for troubleshooting
DELETE FROM helpline.session;
```

---

## Next Steps

After setting up user roles and permissions:

1. **Configure Communication Channels**: See [Configuring Communication Channels](configuring-communication-channels.md)
2. **Set Up Backup & Recovery**: See [Backup & Recovery](backup-recovery.md)
3. **Configure Monitoring**: See [System Health Checks](../maintenance-monitoring/system-health-checks.md)

---

## Quick Reference Commands

### Common SQL Queries

```sql
-- List all users
SELECT id, username, email, role, status FROM helpline.auth;

-- List all roles
SELECT name, display_name, level FROM helpline.roles ORDER BY level DESC;

-- List all permissions
SELECT name, display_name, category FROM helpline.permissions ORDER BY category, name;

-- Get user details with role
SELECT u.*, r.display_name AS role_name 
FROM helpline.auth u 
JOIN helpline.roles r ON u.role = r.name 
WHERE u.username = 'jdoe';

-- Active sessions count
SELECT COUNT(*) FROM helpline.session WHERE expires_at > NOW();
```

### User Management Scripts

```bash
# Create admin user script
#!/bin/bash
mysql -u root helpline <<EOF
INSERT INTO auth (username, email, password_hash, role, status, created_at)
VALUES (
    'admin',
    'admin@yourdomain.com',
    '\$2y\$10\$your_bcrypt_hash_here',
    'super_admin',
    'active',
    NOW()
);
EOF

# List all users
mysql -u root helpline -e "SELECT username, email, role FROM auth;"

# Reset admin password
mysql -u root helpline -e "UPDATE auth SET password_hash='NEW_HASH', force_password_change=TRUE WHERE username='admin';"
```