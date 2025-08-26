-- MySQL initialization script for Docker environment
-- This adapts the original unix_socket authentication to standard MySQL auth

-- Create the main application user
CREATE USER IF NOT EXISTS 'helpline_user'@'%' IDENTIFIED BY 'helpline_pass';

-- Create a user with the same name as the original for compatibility
-- This allows the application to work with minimal config changes
CREATE USER IF NOT EXISTS 'nginx'@'%' IDENTIFIED BY '';

-- Grant permissions as specified in the original documentation
GRANT SELECT, INSERT ON helpline.* TO 'helpline_user'@'%';
GRANT UPDATE ON helpline.auth TO 'helpline_user'@'%';
GRANT UPDATE ON helpline.contact TO 'helpline_user'@'%';
GRANT UPDATE ON helpline.kase TO 'helpline_user'@'%';
GRANT UPDATE ON helpline.kase_activity TO 'helpline_user'@'%';
GRANT UPDATE ON helpline.activity TO 'helpline_user'@'%';
GRANT UPDATE ON helpline.disposition TO 'helpline_user'@'%';
GRANT DELETE ON helpline.session TO 'helpline_user'@'%';
GRANT UPDATE ON helpline.chan TO 'helpline_user'@'%';

-- Grant same permissions to nginx user for compatibility
GRANT SELECT, INSERT ON helpline.* TO 'nginx'@'%';
GRANT UPDATE ON helpline.auth TO 'nginx'@'%';
GRANT UPDATE ON helpline.contact TO 'nginx'@'%';
GRANT UPDATE ON helpline.kase TO 'nginx'@'%';
GRANT UPDATE ON helpline.kase_activity TO 'nginx'@'%';
GRANT UPDATE ON helpline.activity TO 'nginx'@'%';
GRANT UPDATE ON helpline.disposition TO 'nginx'@'%';
GRANT DELETE ON helpline.session TO 'nginx'@'%';
GRANT UPDATE ON helpline.chan TO 'nginx'@'%';

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;

-- Display created users for verification
SELECT User, Host FROM mysql.user WHERE User IN ('helpline_user', 'nginx');
Alter table kase ADD column ref char(255);