<?php
/**
 * PHPUnit Bootstrap File for REST API Tests
 */

// Define PHPUNIT_RUNNING constant
if (!defined('PHPUNIT_RUNNING')) {
    define('PHPUNIT_RUNNING', true);
}

// Set server variables
$_SERVER['HTTP_HOST'] = 'localhost';
$_SERVER['REMOTE_ADDR'] = '127.0.0.1';
$_SERVER['REQUEST_URI'] = '/api/';
$_SERVER['REQUEST_METHOD'] = 'GET';
$_SERVER['CONTENT_TYPE'] = 'application/json';

// Setup mock session
$_SESSION = [
    'cc_user_id' => '1',
    'cc_user_exten' => '123',
    'cc_user_usn' => 'testuser',
    'cc_user_contact_id' => '1',
    'cc_user_role' => '2'
];

// Setup mock data
$_GET = [];
$_POST = [];
$_FILES = [];

// Define constants
if (!defined('DAT')) {
    define('DAT', dirname(__FILE__) . '/test_data');
}

// Create test directories
if (!is_dir(DAT)) @mkdir(DAT, 0777, true);
if (!is_dir(DAT . '/users')) @mkdir(DAT . '/users', 0777, true);
if (!is_dir(DAT . '/csv')) @mkdir(DAT . '/csv', 0777, true);

// Application globals
$GLOBALS['COUNTRY_CODE'] = '+254';
$GLOBALS['ERRORS'] = [];

// Mock RIGHTS system
$GLOBALS['RIGHTS_2'] = [
    'users' => ['1', '1', '1', '0'],
    'contacts' => ['1', '1', '1', '0'],
    'messages' => ['1', '1', '1', '0'],
    'cases' => ['1', '1', '1', '0']
];

$GLOBALS['RIGHTS_99'] = [
    'users' => ['1', '1', '1', '1'],
    'contacts' => ['1', '1', '1', '1'],
    'messages' => ['1', '1', '1', '1'],
    'cases' => ['1', '1', '1', '1']
];

// Mock RESOURCES
$GLOBALS['RESOURCES'] = [
    'users' => ['users', 'user', '3', '2', '0', 'User', 'id DESC'],
    'contacts' => ['contacts', 'contact', '3', '2', '0', 'Contact', 'id DESC']
];

// Mock model definitions
$GLOBALS['users_def'] = [
    ['id', 'user_id', '0', '4', '', '', '', '', '', 'ID'],
    ['name', 'user_name', '3', '1', 'm', '', '', '', '', 'Name'],
    ['email', 'user_email', '3', '1', 'm', 'e', '', '', '', 'Email'],
    ['phone', 'user_phone', '3', '1', 'o', 'p', '', '', '', 'Phone'],
    ['created_on', '', '0', '3', '', '', '', '', '', 'Created']
];

$GLOBALS['contacts_def'] = [
    ['id', 'contact_id', '0', '4', '', '', '', '', '', 'ID'],
    ['user_id', '', '3', '4', 'm', 'f', '', '', '', 'User ID'],
    ['name', 'contact_name', '3', '1', 'm', '', '', '', '', 'Contact Name'],
    ['email', 'contact_email', '3', '1', 'o', 'e', '', '', '', 'Email']
];

// Session-specific mock arrays
$GLOBALS['addr_dup'] = [
    ['addr', 'SELECT id FROM addr WHERE addr=?', 's', 'addr_id']
];

$GLOBALS['otp_dup'] = [
    ['otp_addr', 'SELECT id, addr_id, addr FROM otp WHERE addr=? AND expiry>UNIX_TIMESTAMP(Now())', 's', 'otp_id,otp_addr_id,otp_addr']
];

$GLOBALS['auth_dup'] = [
    ['addr', 'SELECT id, contact_id, role FROM auth WHERE usn=?', 's', 'auth_id,auth_contact_id,auth_contact_role']
];

$GLOBALS['contacts_dup'] = [
    ['contact_id', 'SELECT email FROM contacts WHERE id=?', 's', 'contact_email']
];

$GLOBALS['otpv_dup'] = [
    ['otp_id,otp', 'SELECT addr_id, addr FROM otp WHERE id=? AND otp=? AND expiry>UNIX_TIMESTAMP(Now())', 'ss', 'otp_addr_id,otp_addr']
];

// Mock column mappings
$GLOBALS['users_k'] = ['id' => 0, 'name' => 1, 'email' => 2, 'phone' => 3, 'created_on' => 4];
$GLOBALS['contacts_k'] = ['id' => 0, 'user_id' => 1, 'name' => 2, 'email' => 3];

// Mock enums
$GLOBALS['status_enum'] = [
    '1' => ['1', 'Active', 'Active', '1'],
    '2' => ['2', 'Inactive', 'Inactive', '0'],
    '3' => ['3', 'Pending', 'Pending', '1']
];

$GLOBALS['role_enum'] = [
    '1' => ['1', 'Admin', 'Administrator', '1'],
    '2' => ['2', 'User', 'Regular User', '1'],
    '3' => ['3', 'Guest', 'Guest User', '0']
];

$GLOBALS['src_enum'] = [
    'email' => ['email', 'Email', 'Email Address', '0'],
    'sms' => ['sms', 'SMS', 'Phone Number', '1'],
    'voice' => ['voice', 'Voice', 'Phone Number', '1']
];

// Mock METRICS
$GLOBALS['METRICS'] = [
    'count' => ['COUNT(*)', '', 'COUNT(*)', 'COUNT(*)', '', '', ''],
    'sum' => ['SUM', '', 'SUM', 'SUM', '', '', ''],
    'avg' => ['AVG', '', 'AVG', 'AVG', '', '', '']
];

// Mock database
$GLOBALS['db'] = (object)[
    'insert_id' => 1,
    'affected_rows' => 1,
    'errno' => 0,
    'error' => ''
];
$GLOBALS['db2'] = $GLOBALS['db'];

// Mock API definitions
$GLOBALS['users_api'] = [['users', '', '', '1', '1']];
$GLOBALS['contacts_api'] = [['contacts', '', '', '1', '1']];
$GLOBALS['FN'] = ['home' => true, 'auth' => true, 'ss' => true];

// Mock mysqli functions - only if not already defined
if (!function_exists('mysqli_stmt_init')) {
    function mysqli_stmt_init($link) { return (object)['prepared' => false]; }
    function mysqli_stmt_prepare($stmt, $query) { $stmt->query = $query; return true; }
    function mysqli_stmt_bind_param($stmt, $types, ...$vars) { $stmt->params = $vars; return true; }
    function mysqli_stmt_execute($stmt) { return true; }
    function mysqli_stmt_get_result($stmt) { return (object)['data' => [['1', 'Test', 'test@example.com']]]; }
    function mysqli_fetch_array($result, $type = 3) { static $called = false; if (!$called) { $called = true; return ['1', 'Test', 'test@example.com']; } return null; }
    function mysqli_fetch_row($result) { static $called = false; if (!$called) { $called = true; return ['1', 'Test', 'test@example.com']; } return null; }
    function mysqli_stmt_insert_id($stmt) { return 123; }
    function mysqli_insert_id($link) { return 123; }
    function mysqli_stmt_affected_rows($stmt) { return 1; }
    function mysqli_errno($link) { return 0; }
    function mysqli_error($link) { return ''; }
}

// Define constants
if (!defined('MYSQLI_BOTH')) define('MYSQLI_BOTH', 3);
if (!defined('MYSQLI_NUM')) define('MYSQLI_NUM', 2);

// Helper functions
if (!function_exists('copy_from_pabx')) {
    function copy_from_pabx($uid) { return true; }
}

// Session-specific mock functions
if (!function_exists('session_set_save_handler')) {
    function session_set_save_handler($open, $close, $read, $write, $destroy, $gc) {
        return true;
    }
}

if (!function_exists('session_name')) {
    function session_name($name = null) {
        return $name ?? 'PHPUNIT_SESSION';
    }
}

if (!function_exists('session_start')) {
    function session_start(array $options = []) {
        return true;
    }
}

if (!function_exists('session_regenerate_id')) {
    function session_regenerate_id($delete_old = false) {
        return true;
    }
}

if (!function_exists('session_id')) {
    function session_id($id = null) {
        return $id ?? 'phpunit_session_' . rand(1000, 9999);
    }
}

if (!function_exists('session_destroy')) {
    function session_destroy() {
        $_SESSION = [];
        return true;
    }
}

if (!function_exists('header')) {
    function header($string, $replace = true, $http_response_code = null) {
        // Mock header function - just return true for testing
        return true;
    }
}

if (!function_exists('time')) {
    function time() {
        return 1734567890; // Fixed timestamp for testing
    }
}

// Check if rest.php exists and provide helpful error message
$rest_file_paths = [
    dirname(__FILE__) . '/../lib/rest.php',      // From api/ directory
    dirname(__FILE__) . '/../../lib/rest.php',   // From api/tests/ directory  
    dirname(__FILE__) . '/lib/rest.php'          // Alternative location
];

$rest_file_found = false;
foreach ($rest_file_paths as $path) {
    if (file_exists($path)) {
        $rest_file_found = true;
        break;
    }
}

if (!$rest_file_found) {
    echo "Warning: rest.php not found at any of these locations:\n";
    foreach ($rest_file_paths as $path) {
        echo "  - $path\n";
    }
    echo "Please ensure rest.php is in the correct location.\n";
}