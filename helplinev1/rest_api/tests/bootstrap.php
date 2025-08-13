<?php

// Test bootstrap file
require_once __DIR__ . '/../vendor/autoload.php';

// Set up test environment
define('THE_DB_HOST', 'localhost');
define('THE_DB_USN', 'test_user');
define('THE_DB_PASSWD', 'test_pass');
define('THE_DB_NAME', 'test_helpline');
define('THE_DB_SOCK', null);
define('DAT', __DIR__ . '/../test_data');

// Create test data directory if it doesn't exist
if (!is_dir(DAT)) {
    mkdir(DAT, 0777, true);
    mkdir(DAT . '/files', 0777, true);
    mkdir(DAT . '/calls', 0777, true);
}

// Mock global variables and functions that might be needed
$GLOBALS['COUNTRY_CODE'] = '+256';
$GLOBALS['API_GATEWAY_USN'] = 'test_user';
$GLOBALS['API_GATEWAY_PASS'] = 'test_pass';
$GLOBALS['API_GATEWAY_SEND_MSG'] = 'http://test.gateway/send';
$GLOBALS['API_GATEWAY_CLOSE_MSG'] = 'http://test.gateway/close/';
$GLOBALS['RECORDING_ARCHIVE_URL'] = 'http://test.archive/';

// Define missing constants that are referenced in model.php
$GLOBALS['DISPOSITION_ID_COMPLETE'] = '999';
$GLOBALS['DISPOSITION_ID_CONTACT_NEW'] = '888';
$GLOBALS['DISPOSITION_ROOT_ID'] = '777';
$GLOBALS['AGE_GROUP_ROOT_ID'] = '666';

// Mock database connections for testing
$GLOBALS['db'] = null;
$GLOBALS['db2'] = null;

// Set up error reporting
error_reporting(E_ALL & ~E_WARNING & ~E_NOTICE);
ini_set('display_errors', 1);

// Mock functions that might not exist in test environment
if (!function_exists('mysqli_fetch_row')) {
    function mysqli_fetch_row($result) {
        if (is_object($result) && method_exists($result, 'fetch_row')) {
            return $result->fetch_row();
        }
        return null;
    }
}

if (!function_exists('session_regenerate_id')) {
    function session_regenerate_id($delete_old_session = false) {
        return true;
    }
}

if (!function_exists('session_id')) {
    function session_id($id = null) {
        static $session_id = 'test_session_123';
        if ($id !== null) {
            $session_id = $id;
        }
        return $session_id;
    }
}

if (!function_exists('session_destroy')) {
    function session_destroy() {
        global $_SESSION;
        $_SESSION = [];
        return true;
    }
}

if (!function_exists('xdebug_get_headers')) {
    function xdebug_get_headers() {
        return headers_list();
    }
}

if (!function_exists('headers_list')) {
    function headers_list() {
        return ['HTTP/1.1 200 OK', 'Content-Type: application/json'];
    }
}

// Start session for tests that need it
if (session_status() === PHP_SESSION_NONE && !headers_sent()) {
    @session_start();
}