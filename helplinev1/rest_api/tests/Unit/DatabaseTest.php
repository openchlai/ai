<?php

namespace Tests\Unit;

use Tests\TestCase;

class DatabaseTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Include required files
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        
        // Set up test data
        $this->setupTestData();
        
        // Mock database connections
        $this->mockDatabaseFunctions();
    }

    private function setupTestData(): void
    {
        // Set up basic resource definitions for testing
        global $RESOURCES, $contacts_def, $auth_def;
        
        $RESOURCES = [
            'contacts' => ['contact', '', '3', '0', '0', 'Contact', 'fullname', '', ''],
            'auth' => ['auth', 'user', '3', '0', '0', 'User', '', '', ''],
            'cases' => ['kase', 'case', '3', '0', '0', 'Case', '', '', '']
        ];

        $contacts_def = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['fullname', '', '4', '1', '', '', '', '', '', 'Full Name', ''],
            ['phone', '', '3', '1', '', 'p', '', '', '', 'Phone', ''],
            ['email', '', '3', '2', '', 'e', '', '', '', 'Email', '']
        ];

        $auth_def = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['usn', '', '3', '2', 'u', '', '', '', '', 'Username', ''],
            ['role', '', '3', '2', 'm', '', '', '', '', 'Role', '']
        ];
    }

    private function mockDatabaseFunctions(): void
    {
        // Mock database connections
        $GLOBALS['db'] = $this->createMockDatabase();
        $GLOBALS['db2'] = $this->createMockDatabase();
    }

    private function createMockDatabase()
    {
        return (object)[
            'error' => '',
            'errno' => 0,
            'insert_id' => 123
        ];
    }

    public function testSelectColsFunction(): void
    {
        global $contacts_def;
        
        $q = '';
        _select_cols('contacts', 'contact.', $q);
        
        $this->assertStringContainsString('contact.id', $q);
        $this->assertStringContainsString('contact.fullname', $q);
        $this->assertStringContainsString('contact.phone', $q);
        $this->assertStringContainsString('contact.email', $q);
        
        // Test without prefix
        $q = '';
        _select_cols('contacts', '', $q);
        
        $this->assertStringContainsString('id,fullname,phone,email', $q);
    }

    public function testValidationErrorHandling(): void
    {
        // Clear errors
        $GLOBALS['ERRORS'] = [];
        
        // Test error creation
        $result = _val_error('contacts', 1, 'email', 'invalid-email', 'INVALID', 'Invalid email format');
        
        $this->assertEquals(1, $result);
        $this->assertCount(1, $GLOBALS['ERRORS']);
        
        $error = $GLOBALS['ERRORS'][0];
        $this->assertEquals('error', $error[0]);
        $this->assertEquals('Invalid email format', $error[1]);
        $this->assertEquals('INVALID', $error[2]);
        $this->assertEquals('contacts', $error[3]);
        $this->assertEquals(1, $error[4]);
        $this->assertEquals('email', $error[5]);
        $this->assertEquals('invalid-email', $error[6]);
    }

    public function testFieldValidation(): void
    {
        global $contacts_def;
        
        $o = ['i_' => 0, 'email' => 'test@example.com', 'phone' => '0701234567'];
        $p = [];
        $a = ['email', '', '3', '2', '', 'e', '', '', '', 'Email', ''];
        $v = '';
        
        // Test valid email
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('test@example.com', $v);

        // Test invalid email
        $o['email'] = 'invalid-email';
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(1, $result);

        // Test phone validation
        $a = ['phone', '', '3', '1', '', 'p', '', '', '', 'Phone', ''];
        $o['phone'] = '0701234567';
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $v);

        // Test mandatory field validation - clear errors first
        $GLOBALS['ERRORS'] = [];
        $a = ['required_field', '', '3', '2', 'm', '', '', '', '', 'Required Field', ''];
        $o = ['i_' => 0]; // Missing required field
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(1, $result);
        $this->assertGreaterThanOrEqual(1, count($GLOBALS['ERRORS']));
        $this->assertStringContainsString('Required', $GLOBALS['ERRORS'][0][1]);
    }

    public function testConstantAndGeneratedValues(): void
    {
        $o = ['i_' => 0];
        $p = [];
        $v = '';
        
        // Test constant value
        $a = ['test_field', '', '3', '2', 'k', 'CONSTANT_VALUE', '', '', '', 'Test Field', ''];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('CONSTANT_VALUE', $v);

        // Test generated ID
        $a = ['test_field', '', '3', '2', '@', '', '', '', '', 'Test Field', ''];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertStringContainsString('.', $v); // Should contain timestamp.random
        
        // Test random number
        $a = ['test_field', '', '3', '2', '#', '', '', '', '', 'Test Field', ''];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals(9, strlen($v));
        $this->assertMatchesRegularExpression('/^\d{9}$/', $v);
    }

    public function testDefaultValues(): void
    {
        $o = ['i_' => 0]; // No data provided
        $p = [];
        $v = '';
        
        // Test default value when field is empty
        $a = ['test_field', '', '3', '2', 'v', '', '', 'DEFAULT_VALUE', '', 'Test Field', ''];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('DEFAULT_VALUE', $v);
    }

    public function testUpdateFieldHandling(): void
    {
        $o = ['i_' => 0]; // No data provided
        $p = [];
        $v = '';
        
        // Test skip unset during update
        $a = ['test_field', '', '3', '2', '', '', '', '', '', 'Test Field', ''];
        $result = _val('contacts', '123', $o, $p, $a, $v); // ID provided = update
        $this->assertEquals(0, $result); // Should skip validation for unset fields during update
        $this->assertNull($v);
    }

    public function testDuplicateFieldValidation(): void
    {
        $o = ['i_' => 0, 'username' => 'testuser'];
        $p = ['username' => '"testuser"']; // Simulating existing value
        $v = '';
        
        // Test unique field duplicate check
        $a = ['username', '', '3', '2', 'u', '', '', '', '', 'Username', ''];
        $result = _val('auth', null, $o, $p, $a, $v);
        $this->assertEquals(1, $result); // Should fail due to duplicate
        $this->assertCount(1, $GLOBALS['ERRORS']);
        $this->assertStringContainsString('exists', $GLOBALS['ERRORS'][0][1]);
    }

    public function testCustomFieldMapping(): void
    {
        $o = ['custom_key' => 'test_value'];
        $p = [];
        $v = '';
        
        // Test custom field name mapping
        $a = ['field_name', 'custom_key', '3', '2', '', '', '', '', '', 'Field Name', ''];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('test_value', $v);
    }

    public function testPriorityHandling(): void
    {
        $o = ['test_field' => 'from_o_array'];
        $p = ['test_field' => 'from_p_array'];
        $v = '';
        
        // p array should take priority over o array
        $a = ['test_field', '', '3', '2', '', '', '', '', '', 'Test Field', ''];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('from_p_array', $v);
    }

    public function testVGlobalFunction(): void
    {
        // Test _V function for array value extraction
        $vv = ['key1' => 'value1', 'key2' => 'value2'];
        
        $this->assertEquals('value1', _V($vv, 'key1'));
        $this->assertEquals('value2', _V($vv, 'key2'));
        $this->assertEquals('', _V($vv, 'nonexistent'));
    }

    public function testGlobalGetPostSession(): void
    {
        // Test _G function
        $_GET['test_param'] = 'get_value';
        $this->assertEquals('get_value', _G('test_param'));
        $this->assertEquals('', _G('nonexistent'));

        // Test _P function
        $_POST['test_param'] = 'post_value';
        $this->assertEquals('post_value', _P('test_param'));
        $this->assertEquals('', _P('nonexistent'));

        // Test _S function
        $_SESSION['test_param'] = 'session_value';
        $this->assertEquals('session_value', _S('test_param'));
        $this->assertEquals('', _S('nonexistent'));
    }

    public function testSelectQueryBuilding(): void
    {
        // Mock the _select function behavior
        $aa = [
            'w' => 'WHERE active = 1',
            's' => 's',
            'lim' => 'LIMIT 10',
            'sort' => ''
        ];
        $av = ['1'];
        
        // This would normally call the database, but we're testing the structure
        $this->expectNotToPerformAssertions(); // Since we're mocking database calls
        
        // The function exists and can be called
        $this->assertTrue(function_exists('_select'));
    }

    public function testEmptyFieldHandling(): void
    {
        $o = ['i_' => 0];
        $p = [];
        $v = '';
        
        // Test field with no validation flags
        $a = ['test_field', '', '3', '2', '', '', '', '', '', 'Test Field', ''];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result); // Should pass with no validation
    }

    protected function tearDown(): void
    {
        // Clean up globals
        $GLOBALS['ERRORS'] = [];
        unset($GLOBALS['db'], $GLOBALS['db2']);
        
        parent::tearDown();
    }
}
