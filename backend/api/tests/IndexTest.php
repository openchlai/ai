<?php
/**
 * Simplified test suite for index.php
 * Focusing on non-conflicting tests
 */

class IndexTest extends \PHPUnit\Framework\TestCase
{
    /**
     * Set up test environment before each test
     */
    protected function setUp(): void
    {
        // Reset globals
        $_GET = [];
        $_POST = [];
        $_SERVER['REQUEST_METHOD'] = 'GET';
        $_SERVER['REQUEST_URI'] = '/api/';
    }
    
    /**
     * Basic test to verify environment
     */
    public function testEnvironment()
    {
        $this->assertTrue(defined('PHPUNIT_RUNNING'));
        $this->assertEquals('localhost', $_SERVER['HTTP_HOST']);
    }
    
    /**
     * Test the _wallonly function with exten parameter
     */
    public function testWallonlyWithExten()
    {
        // Extract the function
        $functionCode = $this->extractFunction('_wallonly');
        if (!$functionCode) {
            $this->markTestSkipped('Could not extract _wallonly function');
            return;
        }
        
        // Create a test script
        $testCode = '<?php
// Error reporting
error_reporting(E_ALL);
ini_set("display_errors", 1);

// Common helper functions
function _S($key) {
    return $_SESSION[$key] ?? "";
}

function _G($key) {
    return $_GET[$key] ?? "";
}

function __VESC($val) {
    return $val;
}

// Required mock functions
function muu($cmd, $args) {
    echo "[TEST] muu called with: " . $cmd . ", " . $args . "\\n";
    return [
        "data" => "{}",
        "info" => ["http_code" => 200]
    ];
}

function qryp($query, $types = "", $params = [], $one_row = 0) {
    if ($query == "SELECT id, usn, exten, role FROM auth WHERE exten=?") {
        return ["1", "testuser", "123", "2"];
    }
    
    // Mock other queries as needed
    return [];
}

function rest_uri_get($u, $suffix, $id, &$fo, &$p, &$aa) {
    return 200;
}

function rest_uri_response($u, $suffix, $id, &$o, &$p, &$aa, $rt) {
    echo \'"cases":[["1","Test Case"]]\';
    return $rt;
}

// Session setup
$_SESSION = [
    "cc_user_id" => "1",
    "cc_user_exten" => "123",
    "cc_user_usn" => "testuser",
    "cc_user_contact_id" => "1",
    "cc_user_role" => "2"
];

// The function to test
' . $functionCode . '

// Run the test
$_GET["exten"] = "123";
$o = [];
$p = [];
ob_start();
$result = _wallonly($o, $p);
$output = ob_get_clean();
echo "RESULT: " . $result . "\\n";
echo "OUTPUT: " . $output;
?>';
        
        // Run the test
        $output = $this->runTestScript($testCode);
        
        // Check results
        $this->assertStringContainsString('RESULT: 200', $output);
        $this->assertStringContainsString('"users":', $output);
    }
    
    /**
     * Test the _dash function
     */
    public function testDashFunction()
    {
        // Extract the function
        $functionCode = $this->extractFunction('_dash');
        if (!$functionCode) {
            $this->markTestSkipped('Could not extract _dash function');
            return;
        }
        
        // Create a test script
        $testCode = '<?php
// Error reporting
error_reporting(E_ALL);
ini_set("display_errors", 1);

// Common helper functions
function _S($key) {
    return $_SESSION[$key] ?? "";
}

function _G($key) {
    return $_GET[$key] ?? "";
}

function __VESC($val) {
    return $val;
}

function _str2ts($period) {
    return time();
}

// Mock functions needed by _dash
function ctx_rights($u, &$aa, &$av, &$p, $rights) {
    $aa["w"] = "";
    $aa["s"] = "";
}

function k_c($t, $k, $v, &$aa, &$av) {
    $aa["w"] .= " AND $k = ?";
    $av[] = $v[0];
}

function k_d($t, $k, $v, &$aa, &$av) {
    $aa["w"] .= " AND $k >= ?";
    $av[] = $v[0];
}

// Define our custom result class
class CustomResultSet {
    private $data = [];
    private $index = 0;
    
    public function __construct($data) {
        $this->data = $data;
    }
    
    public function fetch_row() {
        if ($this->index < count($this->data)) {
            return $this->data[$this->index++];
        }
        return false;
    }
}

// Mock database function
function qryp($query, $types = "", $params = [], $one_row = 0) {
    echo "[dash] " . $query . " | " . json_encode($params) . " | " . $_SESSION["cc_user_role"] . "\\n";
    
    // Create a custom result set for the query
    return new CustomResultSet([
        ["call", "10"],
        ["sms", "5"],
        ["email", "8"],
        ["social", "7"]
    ]);
}

// THIS IS THE KEY FIX: Add mysqli_fetch_row function
function mysqli_fetch_row($result) {
    // If the result is our custom class, use its fetch_row method
    if ($result instanceof CustomResultSet) {
        return $result->fetch_row();
    }
    return false;
}

// Session and globals
$_SESSION = [
    "cc_user_id" => "1",
    "cc_user_exten" => "123",
    "cc_user_usn" => "testuser",
    "cc_user_contact_id" => "1",
    "cc_user_role" => "2"
];

$GLOBALS["RIGHTS_2"] = [
    "cases" => ["r" => 1, "w" => 1]
];

// The function to test
' . $functionCode . '

// Run the test
$_GET["dash_period"] = "this_month";
$_GET["dash_gbv"] = "both";
$_GET["dash_src"] = "all";

$o = [];
$p = [];
ob_start();
$result = _dash($o, $p);
$output = ob_get_clean();

echo "RESULT: " . $result . "\\n";
echo "OUTPUT: " . substr($output, 0, 200) . "...";  // Truncate output for readability
?>';
        
        // Run the test
        $output = $this->runTestScript($testCode);
        
        // Check results
        $this->assertStringContainsString('RESULT: 200', $output);
    }
    
    /**
     * Test the _agent function
     */
    public function testAgentFunction()
    {
        // Extract the function
        $functionCode = $this->extractFunction('_agent');
        if (!$functionCode) {
            $this->markTestSkipped('Could not extract _agent function');
            return;
        }
        
        // Create a test script
        $testCode = '<?php
// Error reporting
error_reporting(E_ALL);
ini_set("display_errors", 1);

// Common helper functions
function _S($key) {
    return $_SESSION[$key] ?? "";
}

// Mock functions
function muu($cmd, $args) {
    echo "[TEST] muu called with: " . $cmd . ", " . $args . "\\n";
    if ($cmd == "ati" && $args == "sync?c=-1&") {
        return [
            "data" => \'{"ati":{"uid123":["123","Agent Name"]}}\',
            "info" => ["http_code" => 200]
        ];
    }
    if ($cmd == "ami" && $args == "sync?c=-1&") {
        return [
            "data" => \'{"channels":{"uid123":["123","Agent Channel"]}}\',
            "info" => ["http_code" => 200]
        ];
    }
    return [
        "data" => "{}",
        "info" => ["http_code" => 200]
    ];
}

function qryp($query, $types = "", $params = [], $one_row = 0) {
    return ["1", "Test Campaign"];
}

// Session setup
$_SESSION = [
    "cc_user_id" => "1",
    "cc_user_exten" => "123",
    "cc_user_usn" => "testuser",
    "cc_user_contact_id" => "1",
    "cc_user_role" => "2"
];

$GLOBALS["VA_SIP_USER_PREFIX"] = "SIP/";

// The function to test
' . $functionCode . '

// Run the test
echo "[agent] request " . json_encode(["action" => "0"]) . " | " . $_SESSION["cc_user_usn"] . " " . $_SESSION["cc_user_exten"] . "\\n";

$o = ["action" => "0"];
$result = _agent($o);

echo "RESULT: " . $result;
?>';
        
        // Run the test
        $output = $this->runTestScript($testCode);
        
        // Check results
        $this->assertStringContainsString('RESULT: 203', $output);
        $this->assertStringContainsString('[TEST] muu called with: ati, sync?c=-1&', $output);
    }
    
    /**
     * Test the message_out function
     */
    public function testMessageOutFunction()
    {
        // Extract the function
        $functionCode = $this->extractFunction('message_out');
        if (!$functionCode) {
            $this->markTestSkipped('Could not extract message_out function');
            return;
        }
        
        // Create a test script
        $testCode = '<?php
// Error reporting
error_reporting(E_ALL);
ini_set("display_errors", 1);

// Mock functions
function muu($cmd, $args) {
    echo "[TEST] muu called with: " . $cmd . ", " . $args . "\\n";
    return [
        "data" => "{}",
        "info" => ["http_code" => 200]
    ];
}

function kurl($url, $timeout, $data, $headers) {
    echo "[TEST] kurl called with URL: " . $url . "\\n";
    echo "[TEST] kurl data: " . $data . "\\n";
    return [
        "data" => \'{"success":true}\',
        "info" => ["http_code" => 200]
    ];
}

// Required globals
$GLOBALS["API_GATEWAY_USN"] = "testuser";
$GLOBALS["API_GATEWAY_PASS"] = "testpass";
$GLOBALS["API_GATEWAY_SEND_MSG"] = "http://example.com/api/send";
$GLOBALS["API_GATEWAY_CLOSE_MSG"] = "http://example.com/api/close/";

// The function to test
' . $functionCode . '

// Run the test
$o = [
    "src" => "sms",
    "src_address" => "1234567890",
    "src_msg" => "Test message",
    "src_uid" => "msg-123"
];
$p = [];

message_out($o, $p);

echo "TEST COMPLETED";
?>';
        
        // Run the test
        $output = $this->runTestScript($testCode);
        
        // Check results
        $this->assertStringContainsString('[TEST] kurl called with URL: http://example.com/api/send', $output);
        $this->assertStringContainsString('TEST COMPLETED', $output);
    }
    
    /**
     * Test the _message_in function
     */
    public function testMessageInFunction()
    {
        // Extract the function
        $functionCode = $this->extractFunction('_message_in');
        if (!$functionCode) {
            $this->markTestSkipped('Could not extract _message_in function');
            return;
        }
        
        // Create a test script
        $testCode = '<?php
// Error reporting
error_reporting(E_ALL);
ini_set("display_errors", 1);

// Helper functions
function _val_id() {
    return "123456789";
}

function _rands($len, $type = "alnum") {
    return "987654321";
}

// Mock functions
function rest_uri_post($u, $suffix, $id, &$o, &$p) {
    echo "[TEST] rest_uri_post called for: " . $u . "\\n";
    $p["msg_id"] = "msg-123";
    return 201;
}

function rest_uri_get($u, $suffix, $id, &$fo, &$p, &$aa) {
    echo "[TEST] rest_uri_get called for: " . $u . "\\n";
    return 200;
}

function rest_uri_response($u, $suffix, $id, &$o, &$p, &$aa, $rt) {
    echo "[TEST] rest_uri_response called with rt=" . $rt . "\\n";
    return $rt;
}

function muu($cmd, $args) {
    echo "[TEST] muu called with: " . $cmd . ", " . $args . "\\n";
    return [
        "data" => "{}",
        "info" => ["http_code" => 200]
    ];
}

// The function to test
' . $functionCode . '

// Run the test
$o = [
    "channel" => "sms",
    "session_id" => "sess123",
    "message_id" => "msg123",
    "from" => "1234567890",
    "message" => "This is a test message",
    "timestamp" => "' . time() . '",
    "mime" => "text/plain"
];
$p = [];

$result = _message_in($o, $p);

echo "RESULT: " . $result;
?>';
        
        // Run the test
        $output = $this->runTestScript($testCode);
        
        // Check results
        $this->assertStringContainsString('rest_uri_post called for: messages', $output);
    }
    
    /**
     * Test the _home function
     */
    public function testHomeFunction()
    {
        // Extract the function
        $functionCode = $this->extractFunction('_home');
        if (!$functionCode) {
            $this->markTestSkipped('Could not extract _home function');
            return;
        }
        
        // Create a test script
        $testCode = '<?php
// Error reporting
error_reporting(E_ALL);
ini_set("display_errors", 1);

// Mock functions
function ss() {
    echo \'"session":{"active":true}\';
    return true;
}

function rest_uri_get($u, $suffix, $id, &$fo, &$p, &$aa) {
    echo "[TEST] rest_uri_get called for: " . $u . "\\n";
    return 200;
}

function rest_uri_response($u, $suffix, $id, &$o, &$p, &$aa, $rt) {
    echo \'"\'.$u.\'":[["1","Test Data"]]\';
    return $rt;
}

// Mock _dash function (defined in the file we are testing)
function _dash(&$o, &$p) {
    echo \'"dash":[["this_month","both","all","1683123456","",""]],\';
    echo \'"case_source":{"call":["call","10 Cases"],"total":["total","10 Cases"]}\';
    return 200;
}

// Setup globals
$GLOBALS["RIGHTS_2"] = [
    "cases" => ["r" => 1, "w" => 1]
];

// Session
$_SESSION = [
    "cc_user_id" => "1",
    "cc_user_exten" => "123",
    "cc_user_usn" => "testuser",
    "cc_user_contact_id" => "1",
    "cc_user_role" => "2"
];

// The function to test
' . $functionCode . '

// Run the test
$o = [];
$p = ["auth_id" => "1"];
ob_start();
$result = _home($o, $p);
$output = ob_get_clean();

echo "RESULT: " . $result . "\\n";
echo "OUTPUT: " . substr($output, 0, 100) . "..."; // Truncate for readability
?>';
        
        // Run the test
        $output = $this->runTestScript($testCode);
        
        // Check results
        $this->assertStringContainsString('RESULT: 200', $output);
        $this->assertStringContainsString('rest_uri_get called for: auth', $output);
    }
    
    /**
     * Test the notify function
     */
    public function testNotifyFunction()
    {
        // Extract the function
        $functionCode = $this->extractFunction('notify');
        if (!$functionCode) {
            $this->markTestSkipped('Could not extract notify function');
            return;
        }
        
        // Create a test script
        $testCode = '<?php
// Error reporting
error_reporting(E_ALL);
ini_set("display_errors", 1);

// Define missing constant
define("num", "0123456789");

// Mock functions
function _val_id() {
    return "123456789";
}

function _rands($len, $type = "alnum") {
    return "987654321";
}

function rest_uri_post($u, $suffix, $id, &$o, &$p) {
    echo "[TEST] rest_uri_post called for: " . $u . "\\n";
    echo "[TEST] with params: " . json_encode($p) . "\\n";
    return 201;
}

// The function to test
' . $functionCode . '

// Run the test
$o = [
    "src_ts" => "",
    "src" => "",
    "src_uid" => ""
];
$p = [
    "activity_" => "test_activity"
];

notify("escalation", "2", $o, $p);

echo "TEST COMPLETED";
?>';
        
        // Run the test
        $output = $this->runTestScript($testCode);
        
        // Check results
        $this->assertStringContainsString('rest_uri_post called for: activities', $output);
        $this->assertStringContainsString('TEST COMPLETED', $output);
    }
  
    
    /**
     * Helper method to extract a function from index.php
     */
    private function extractFunction($functionName)
    {
        $code = file_get_contents(dirname(__FILE__) . '/../index.php');
        preg_match('/function ' . preg_quote($functionName) . '[^{]*{.*?^}/ms', $code, $matches);
        
        if (count($matches) === 0) {
            return null;
        }
        
        return $matches[0];
    }
    
    /**
     * Helper method to run a test script
     */
    private function runTestScript($script)
    {
        // Write script to temp file
        $tempFile = sys_get_temp_dir() . '/php_test_' . uniqid() . '.php';
        file_put_contents($tempFile, $script);
        
        // Execute the script
        $output = shell_exec('php ' . escapeshellarg($tempFile) . ' 2>&1');
        
        // Clean up
        unlink($tempFile);
        
        return $output;
    }
}