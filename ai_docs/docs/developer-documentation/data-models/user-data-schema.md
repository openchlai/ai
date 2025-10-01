# User Data Schema

## Overview

The user management system handles authentication, authorization, and user profiles for the OpenCHS platform. This document describes the data structures for contributors working on user-related features.

## Core Tables

### `auth` - User Accounts

Primary table for user authentication and profiles.

```sql
CREATE TABLE auth (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(20) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  
  -- Profile information
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  display_name VARCHAR(200),
  
  -- Role and permissions
  role ENUM('system_admin', 'supervisor', 'case_manager', 'operator', 'ai_analyst', 'developer') NOT NULL,
  organization VARCHAR(255),
  department VARCHAR(100),
  
  -- Account status
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,
  requires_password_change BOOLEAN DEFAULT FALSE,
  
  -- Security
  two_factor_enabled BOOLEAN DEFAULT FALSE,
  two_factor_secret VARCHAR(255),
  failed_login_attempts INT DEFAULT 0,
  locked_until TIMESTAMP NULL,
  last_password_change TIMESTAMP,
  
  -- Activity tracking
  last_login TIMESTAMP NULL,
  last_activity TIMESTAMP NULL,
  login_count INT DEFAULT 0,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by INT,
  
  INDEX idx_username (username),
  INDEX idx_email (email),
  INDEX idx_role (role),
  INDEX idx_is_active (is_active)
);
```

**Role Descriptions:**

| Role | Access Level | Permissions |
|------|--------------|-------------|
| `system_admin` | Full system access | All operations, user management, system config |
| `supervisor` | Regional oversight | View all cases, assign cases, manage team |
| `case_manager` | Case handling | Create/update cases, view assigned cases |
| `operator` | Call handling | Create cases, log communications, basic operations |
| `ai_analyst` | AI services | Access AI models, view analytics, system monitoring |
| `developer` | API access | Programmatic API access, read-only for dev purposes |

### `session` - Active Sessions

Tracks user sessions for authentication.

```sql
CREATE TABLE session (
  session_id VARCHAR(255) PRIMARY KEY,
  user_id INT NOT NULL,
  
  -- Session details
  ip_address VARCHAR(45),
  user_agent TEXT,
  device_info VARCHAR(255),
  
  -- OTP tracking
  otp_code VARCHAR(10),
  otp_sent_at TIMESTAMP NULL,
  otp_expires_at TIMESTAMP NULL,
  otp_verified BOOLEAN DEFAULT FALSE,
  
  -- Session management
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  
  FOREIGN KEY (user_id) REFERENCES auth(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_expires_at (expires_at)
);
```

### `permission` - Granular Permissions

Defines specific permissions beyond role-based access.

```sql
CREATE TABLE permission (
  id INT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  is_system BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Permission Categories:**
- `case_management` - Case CRUD operations
- `communication` - Communication handling
- `reporting` - Analytics and reports
- `ai_services` - AI model access
- `user_management` - User administration
- `system_config` - System configuration

**Standard Permissions:**
```sql
-- Case Management
('view_all_cases', 'View All Cases', 'Access to view all cases in system')
('create_case', 'Create Case', 'Create new cases')
('update_case', 'Update Case', 'Modify existing cases')
('delete_case', 'Delete Case', 'Delete cases')
('assign_case', 'Assign Case', 'Assign cases to users')
('escalate_case', 'Escalate Case', 'Escalate cases to supervisors')

-- Communication
('receive_calls', 'Receive Calls', 'Handle incoming calls')
('make_calls', 'Make Calls', 'Initiate outbound calls')
('send_sms', 'Send SMS', 'Send SMS messages')
('send_email', 'Send Email', 'Send email messages')

-- AI Services
('access_ai_transcription', 'AI Transcription', 'Use voice transcription')
('access_ai_translation', 'AI Translation', 'Use translation services')
('access_ai_classification', 'AI Classification', 'Use case classification')

-- Reporting
('view_analytics', 'View Analytics', 'Access analytics dashboard')
('export_data', 'Export Data', 'Export case data')
('view_reports', 'View Reports', 'Access standard reports')
('create_reports', 'Create Reports', 'Create custom reports')

-- Administration
('manage_users', 'Manage Users', 'Create and modify user accounts')
('manage_roles', 'Manage Roles', 'Define roles and permissions')
('view_audit_log', 'View Audit Log', 'Access system audit logs')
('system_config', 'System Configuration', 'Modify system settings')
```

### `user_permission` - User-Specific Permissions

Assigns additional permissions to users beyond their role.

```sql
CREATE TABLE user_permission (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  permission_id INT NOT NULL,
  
  granted_by INT,
  granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NULL,
  
  FOREIGN KEY (user_id) REFERENCES auth(id) ON DELETE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permission(id) ON DELETE CASCADE,
  FOREIGN KEY (granted_by) REFERENCES auth(id),
  UNIQUE KEY unique_user_permission (user_id, permission_id),
  INDEX idx_user_id (user_id)
);
```

### `role_permission` - Role Default Permissions

Defines default permissions for each role.

```sql
CREATE TABLE role_permission (
  id INT PRIMARY KEY AUTO_INCREMENT,
  role ENUM('system_admin', 'supervisor', 'case_manager', 'operator', 'ai_analyst', 'developer') NOT NULL,
  permission_id INT NOT NULL,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (permission_id) REFERENCES permission(id) ON DELETE CASCADE,
  UNIQUE KEY unique_role_permission (role, permission_id),
  INDEX idx_role (role)
);
```

### `audit_log` - User Activity Tracking

Comprehensive logging of user actions.

```sql
CREATE TABLE audit_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  
  -- Action details
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50),
  resource_id INT,
  description TEXT,
  
  -- Request details
  ip_address VARCHAR(45),
  user_agent TEXT,
  request_method VARCHAR(10),
  request_path VARCHAR(500),
  
  -- Result
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT,
  
  -- Timestamp
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES auth(id) ON DELETE SET NULL,
  INDEX idx_user_id (user_id),
  INDEX idx_action (action),
  INDEX idx_created_at (created_at),
  INDEX idx_resource (resource_type, resource_id)
);
```

**Logged Actions:**
- `user.login` - User logged in
- `user.logout` - User logged out
- `user.password_change` - Password changed
- `case.create` - Case created
- `case.update` - Case updated
- `case.delete` - Case deleted
- `case.view` - Case viewed (PII access)
- `case.export` - Case data exported
- `ai.transcribe` - AI transcription used
- `system.config_change` - System configuration modified

## Permission System

### Role-Based Access Control (RBAC)

```
User
  └─ Has Role (single)
      └─ Has Default Permissions (many)
  └─ Has Additional Permissions (many)
```

### Permission Check Logic

```php
<?php
class PermissionChecker {
    public function userHasPermission(int $userId, string $permissionCode): bool {
        // Get user's role
        $user = $this->getUserById($userId);
        
        // Check role permissions
        $rolePermissions = $this->getRolePermissions($user['role']);
        if (in_array($permissionCode, $rolePermissions)) {
            return true;
        }
        
        // Check user-specific permissions
        $userPermissions = $this->getUserPermissions($userId);
        if (in_array($permissionCode, $userPermissions)) {
            // Check if permission hasn't expired
            if ($this->isPermissionActive($userId, $permissionCode)) {
                return true;
            }
        }
        
        return false;
    }
}
?>
```

## Example Queries

### Create New User

```sql
INSERT INTO auth (
  username,
  email,
  phone,
  password_hash,
  first_name,
  last_name,
  role,
  organization,
  created_by
) VALUES (
  'jkamau',
  'jkamau@helpline.org',
  '+254700123456',
  '$2y$10$encrypted_password_hash',
  'John',
  'Kamau',
  'case_manager',
  'Nairobi Helpline',
  1  -- created by admin
);
```

### Create Session with OTP

```sql
-- Generate session
INSERT INTO session (
  session_id,
  user_id,
  ip_address,
  user_agent,
  otp_code,
  otp_sent_at,
  otp_expires_at,
  expires_at
) VALUES (
  'sess_abc123xyz',
  5,
  '192.168.1.100',
  'Mozilla/5.0...',
  '123456',
  NOW(),
  DATE_ADD(NOW(), INTERVAL 5 MINUTE),
  DATE_ADD(NOW(), INTERVAL 24 HOUR)
);

-- Verify OTP and mark as verified
UPDATE session 
SET otp_verified = TRUE,
    last_activity = NOW()
WHERE session_id = 'sess_abc123xyz'
  AND otp_code = '123456'
  AND otp_expires_at > NOW();
```

### Check User Permissions

```sql
-- Get all permissions for a user
SELECT DISTINCT p.code, p.name
FROM permission p
WHERE p.id IN (
  -- Role permissions
  SELECT permission_id 
  FROM role_permission 
  WHERE role = (SELECT role FROM auth WHERE id = 5)
  
  UNION
  
  -- User-specific permissions
  SELECT permission_id 
  FROM user_permission 
  WHERE user_id = 5 
    AND (expires_at IS NULL OR expires_at > NOW())
)
ORDER BY p.code;
```

### Get User's Active Sessions

```sql
SELECT 
    s.session_id,
    s.ip_address,
    s.created_at,
    s.last_activity,
    TIMESTAMPDIFF(MINUTE, s.last_activity, NOW()) as minutes_inactive
FROM 
    session s
WHERE 
    s.user_id = 5
    AND s.expires_at > NOW()
ORDER BY 
    s.last_activity DESC;
```

### Log User Action

```sql
INSERT INTO audit_log (
  user_id,
  action,
  resource_type,
  resource_id,
  description,
  ip_address,
  request_method,
  request_path
) VALUES (
  5,
  'case.view',
  'case',
  123,
  'Viewed case CASE-2025-001234',
  '192.168.1.100',
  'GET',
  '/helpline/api/cases/123'
);
```

## Security Best Practices

### Password Management

```php
<?php
// Hash password (using bcrypt)
$passwordHash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);

// Verify password
if (password_verify($inputPassword, $storedHash)) {
    // Password correct
    // Check if rehash needed (e.g., cost changed)
    if (password_needs_rehash($storedHash, PASSWORD_BCRYPT, ['cost' => 12])) {
        $newHash = password_hash($inputPassword, PASSWORD_BCRYPT, ['cost' => 12]);
        // Update database with new hash
    }
}
?>
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Not in common password dictionary
- Not same as last 5 passwords

### Session Management

```php
<?php
class SessionManager {
    const SESSION_LIFETIME = 86400; // 24 hours
    const INACTIVITY_TIMEOUT = 3600; // 1 hour
    
    public function validateSession(string $sessionId): bool {
        $session = $this->getSession($sessionId);
        
        if (!$session) {
            return false;
        }
        
        // Check if expired
        if (strtotime($session['expires_at']) < time()) {
            $this->deleteSession($sessionId);
            return false;
        }
        
        // Check inactivity
        $inactiveMinutes = (time() - strtotime($session['last_activity'])) / 60;
        if ($inactiveMinutes > self::INACTIVITY_TIMEOUT / 60) {
            $this->deleteSession($sessionId);
            return false;
        }
        
        // Update last activity
        $this->updateSessionActivity($sessionId);
        
        return true;
    }
    
    public function cleanupExpiredSessions(): int {
        $sql = "DELETE FROM session WHERE expires_at < NOW()";
        return $this->db->exec($sql);
    }
}
?>
```

### Account Lockout

```php
<?php
class AccountSecurity {
    const MAX_FAILED_ATTEMPTS = 5;
    const LOCKOUT_DURATION = 1800; // 30 minutes
    
    public function recordFailedLogin(int $userId): void {
        $sql = "UPDATE auth 
                SET failed_login_attempts = failed_login_attempts + 1
                WHERE id = ?";
        $this->db->execute($sql, [$userId]);
        
        $attempts = $this->getFailedAttempts($userId);
        
        if ($attempts >= self::MAX_FAILED_ATTEMPTS) {
            $this->lockAccount($userId);
        }
    }
    
    private function lockAccount(int $userId): void {
        $lockUntil = date('Y-m-d H:i:s', time() + self::LOCKOUT_DURATION);
        
        $sql = "UPDATE auth 
                SET locked_until = ?
                WHERE id = ?";
        $this->db->execute($sql, [$lockUntil, $userId]);
        
        // Log security event
        $this->logSecurityEvent($userId, 'account.locked');
    }
}
?>
```

## Data Privacy

### Personally Identifiable Information (PII)

The following fields contain PII and require special handling:
- `email`
- `phone`
- `first_name`, `last_name`
- `ip_address` (in session and audit_log)

### GDPR Compliance

**Right to Access:**
```sql
-- Export all user data
SELECT * FROM auth WHERE id = 5;
SELECT * FROM session WHERE user_id = 5;
SELECT * FROM user_permission WHERE user_id = 5;
SELECT * FROM audit_log WHERE user_id = 5;
```

**Right to Erasure:**
```sql
-- Anonymize user (keep audit trail)
UPDATE auth SET
    username = CONCAT('deleted_user_', id),
    email = NULL,
    phone = NULL,
    first_name = 'Deleted',
    last_name = 'User',
    password_hash = 'DELETED',
    is_active = FALSE
WHERE id = 5;

-- Delete sessions
DELETE FROM session WHERE user_id = 5;

-- Anonymize audit logs
UPDATE audit_log SET
    ip_address = '0.0.0.0',
    user_agent = 'ANONYMIZED'
WHERE user_id = 5;
```

## Contributing Guidelines

When modifying user-related features:

1. Always validate user inputs
2. Use prepared statements for SQL queries
3. Log authentication and authorization events
4. Implement rate limiting for authentication endpoints
5. Test permission checks thoroughly
6. Update audit logs for sensitive operations
7. Consider GDPR implications for new PII fields
8. Document new permissions in this file

For more information, see the [Authentication Guide](../api-reference/authentication.md).