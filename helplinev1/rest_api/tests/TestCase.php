<?php

namespace Tests;

use PHPUnit\Framework\TestCase as BaseTestCase;
use PHPUnit\Framework\MockObject\MockObject;

class TestCase extends BaseTestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Reset global variables before each test
        $GLOBALS['ERRORS'] = [];
        
        // Reset session data
        $_SESSION = [];
        $_GET = [];
        $_POST = [];
        $_FILES = [];
        $_SERVER = [];
        
        // Set up default server variables
        $_SERVER['REQUEST_METHOD'] = 'GET';
        $_SERVER['REQUEST_URI'] = '/';
        $_SERVER['REMOTE_ADDR'] = '127.0.0.1';
        $_SERVER['HTTP_USER_AGENT'] = 'PHPUnit Test';
    }

    protected function tearDown(): void
    {
        // Clean up after each test
        $GLOBALS['ERRORS'] = [];
        
        parent::tearDown();
    }

    /**
     * Create a mock database result
     */
    protected function createMockDbResult(array $rows = []): MockObject
    {
        $mock = $this->createMock(\mysqli_result::class);
        
        $rowIndex = 0;
        $mock->method('fetch_row')
            ->willReturnCallback(function() use ($rows, &$rowIndex) {
                if ($rowIndex < count($rows)) {
                    return $rows[$rowIndex++];
                }
                return null;
            });
            
        return $mock;
    }

    /**
     * Set up session with user data
     */
    protected function setUpUserSession(
        int $userId = 1,
        string $username = 'test_user',
        int $role = 1,
        string $exten = '123'
    ): void {
        $_SESSION['cc_user_id'] = $userId;
        $_SESSION['cc_user_usn'] = $username;
        $_SESSION['cc_user_role'] = $role;
        $_SESSION['cc_user_exten'] = $exten;
        $_SESSION['cc_user_contact_id'] = 1;
        $_SESSION['cc_user_agentno'] = 'agent_' . $userId;
    }

    /**
     * Mock the qryp function
     */
    protected function mockQryp($returnValue = null): void
    {
        if (!function_exists('qryp')) {
            eval('
                function qryp($q, $argt, $argv, $r = 0, $db = "db") {
                    return $GLOBALS["test_qryp_result"] ?? null;
                }
            ');
        }
        $GLOBALS['test_qryp_result'] = $returnValue;
    }

    /**
     * Assert that an error was added to global ERRORS array
     */
    protected function assertHasError(?string $expectedMessage = null): void
    {
        $this->assertNotEmpty($GLOBALS['ERRORS'], 'Expected errors array to not be empty');
        
        if ($expectedMessage !== null) {
            $found = false;
            foreach ($GLOBALS['ERRORS'] as $error) {
                if (isset($error[1]) && strpos($error[1], $expectedMessage) !== false) {
                    $found = true;
                    break;
                }
            }
            $this->assertTrue($found, "Expected error message containing '{$expectedMessage}' not found");
        }
    }
}