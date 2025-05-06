<?php
/**
 * PHPUnit Bootstrap File - Function Handler Approach
 */

// Define PHPUNIT_RUNNING constant
if (!defined('PHPUNIT_RUNNING')) {
    define('PHPUNIT_RUNNING', true);
}

// Set server variables needed by config.php
$_SERVER['HTTP_HOST'] = 'localhost';
$_SERVER['REMOTE_ADDR'] = '127.0.0.1';
$_SERVER['REQUEST_URI'] = '/api/';

// Setup mock session
$_SESSION = [
    'cc_user_id' => '1',
    'cc_user_exten' => '123',
    'cc_user_usn' => 'testuser',
    'cc_user_contact_id' => '1',
    'cc_user_role' => '2'
];

// Define necessary globals
$GLOBALS['RIGHTS_2'] = [
    'cases' => ['r' => 1, 'w' => 1],
    'contacts' => ['r' => 1, 'w' => 1],
    'messages' => ['r' => 1, 'w' => 1]
];

// Define other globals needed by the application
$GLOBALS['CASE_ID_PREFIX'] = 'CASE-';
$GLOBALS['AGE_GROUP_ROOT_ID'] = '10';
$GLOBALS['VA_SIP_USER_PREFIX'] = 'SIP/';
$GLOBALS['API_GATEWAY_SEND_MSG'] = 'http://example.com/api/send';
$GLOBALS['API_GATEWAY_CLOSE_MSG'] = 'http://example.com/api/close/';
$GLOBALS['RECORDING_ARCHIVE_URL'] = 'http://example.com/archive/';

// Setup mock data repositories
$GLOBALS['_TEST_QRYP_RESULTS'] = [];
$GLOBALS['_TEST_MUU_RESULTS'] = [];
$GLOBALS['_TEST_KURL_RESULTS'] = [];
$GLOBALS['_TEST_REST_RESULTS'] = [];

// Mock database connections 
$GLOBALS['db'] = new stdClass();
$GLOBALS['db2'] = new stdClass();

// Create a list of function names from index.php
// This helps us create appropriate mocks
$GLOBALS['_TEST_FUNCTION_LIST'] = [
    'copy_from_pabx',
    'muu',
    'notify',
    '_notify_',
    'message_out',
    '_message_in',
    '_sup',
    '_chan',
    '_agent',
    '_wallonly',
    '_dash',
    '_home',
    '_request_',
    'qryp',
    'ctx_rights',
    'k_c',
    'k_d',
    'kurl',
    'rest_uri_parse',
    'rest_uri_get',
    'rest_uri_post',
    'rest_uri_response',
    'rest_uri_response_error',
    '_S',
    '_G',
    '__VESC',
    '_val_id',
    '_rands',
    '_str2ts',
    'ss',
    'auth',
    'changeAuthAdmin',
    'changeAuth',
    '_sendOTP',
    '_verifyOTP',
    'model_k_id',
    '_dup'
];

// Helper function to extract a function from index.php
function extractFunction($functionName) {
    $code = file_get_contents(dirname(__FILE__) . '/index.php');
    preg_match('/function ' . preg_quote($functionName) . '[^{]*{.*?^}/ms', $code, $matches);
    
    if (count($matches) === 0) {
        return null;
    }
    
    return $matches[0];
}

// Common helper functions needed by many tests
function _S($key) {
    return $_SESSION[$key] ?? '';
}

function _G($key) {
    return $_GET[$key] ?? '';
}

function __VESC($val) {
    return $val;
}

function _val_id() {
    return time();
}

function _rands($len, $type = "alnum") {
    return "12345";
}

function _str2ts($period) {
    switch($period) {
        case 'today': return strtotime('today');
        case 'yesterday': return strtotime('yesterday');
        case 'this_week': return strtotime('monday this week');
        case 'this_month': return strtotime('first day of this month');
        default: return time();
    }
}

// DO NOT include any application files here