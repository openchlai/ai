<?php

namespace Tests\Unit;

use Tests\TestCase;

class SessionManagerTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Include required files
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        require_once __DIR__ . '/../../lib/session.php';
        
        // Mock the database functions for session tests
        $this->mockSessionFunctions();
    }

    private function mockSessionFunctions(): void
    {
        // Mock qryp function for session database operations
        if (!function_exists('qryp')) {
            eval('
                function qryp($q, $argt, $argv, $r = 0, $db = "db") {
                    global $test_session_data;
                    
                    if (strpos($q, "SELECT data FROM session") !== false) {
                        return $test_session_data["read_result"] ?? null;
                    }
                    
                    if (strpos($q, "UPDATE session SET access") !== false) {
                        return true;
                    }
                    
                    if (strpos($q, "INSERT INTO session") !== false) {
                        return 1; // Insert successful
                    }
                    
                    if (strpos($q, "DELETE FROM session") !== false) {
                        return 1; // Delete successful
                    }
                    
                    if (strpos($q, "SELECT created_on, ss_id") !== false) {
                        return $test_session_data["gc_result"] ?? null;
                    }
                    
                    return $test_session_data["default_result"] ?? null;
                }
            ');
        }

        // Mock mysqli_fetch_row for session garbage collection
        if (!function_exists('mysqli_fetch_row')) {
            eval('
                function mysqli_fetch_row($result) {
                    global $test_session_data;
                    static $call_count = 0;
                    
                    if (!$result) return null;
                    
                    $rows = $test_session_data["gc_rows"] ?? [];
                    if ($call_count < count($rows)) {
                        return $rows[$call_count++];
                    }
                    
                    $call_count = 0; // Reset for next test
                    return null;
                }
            ');
        }
    }

    public function testSessionIdExtraction(): void
    {
        // Test with Bearer authorization header
        $_SERVER['HTTP_AUTHORIZATION'] = 'Bearer test_token_123';
        
        $sessionId = ss_id('default_session');
        $this->assertEquals('test_token_123', $sessionId);

        // Test with lowercase bearer
        $_SERVER['HTTP_AUTHORIZATION'] = 'bearer test_token_456';
        $sessionId = ss_id('default_session');
        $this->assertEquals('test_token_456', $sessionId);

        // Test without authorization header
        unset($_SERVER['HTTP_AUTHORIZATION']);
        $sessionId = ss_id('default_session');
        $this->assertEquals('test_session_123', $sessionId); // From bootstrap mock
        
        // Test with invalid authorization type
        $_SERVER['HTTP_AUTHORIZATION'] = 'Basic dGVzdDp0ZXN0';
        $sessionId = ss_id('default_session');
        $this->assertEquals('test_session_123', $sessionId);
    }

    public function testSessionOpenClose(): void
    {
        $this->assertTrue(ss_open('/tmp', 'HELPLINE_SESSION'));
        $this->assertTrue(ss_close());
    }

    public function testSessionRead(): void
    {
        global $test_session_data;
        
        // Test successful session read
        $test_session_data['read_result'] = ['1|testuser|agent123|200|1|1'];
        
        $_SERVER['HTTP_AUTHORIZATION'] = 'Bearer test_session_token';
        
        $result = ss_read('test_session_token');
        
        // Should return empty string as per function design
        $this->assertEquals('', $result);
        
        // Check that session variables were set
        $this->assertEquals('1', $_SESSION['cc_user_id']);
        $this->assertEquals('testuser', $_SESSION['cc_user_usn']);
        $this->assertEquals('agent123', $_SESSION['cc_user_agentno']);
        $this->assertEquals('200', $_SESSION['cc_user_exten']);
        $this->assertEquals('1', $_SESSION['cc_user_contact_id']);
        $this->assertEquals('1', $_SESSION['cc_user_role']);

        // Test session not found
        $test_session_data['read_result'] = null;
        $result = ss_read('nonexistent_session');
        $this->assertEquals('', $result);
    }

    public function testSessionWrite(): void
    {
        $result = ss_write('test_session', 'test_data');
        $this->assertTrue($result);
    }

    protected function tearDown(): void
    {
        // Clean up global test data
        global $test_session_data;
        $test_session_data = [];
        
        parent::tearDown();
    }
}
