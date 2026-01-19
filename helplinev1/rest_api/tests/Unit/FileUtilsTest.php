<?php

namespace Tests\Unit;

use Tests\TestCase;

class FileUtilsTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        require_once __DIR__ . '/../../lib/rest.php';
        
        $_SESSION['cc_user_id'] = '1';
        $_SESSION['cc_user_role'] = '1';
    }

    public function testSelectColsFunction(): void
    {
        // Setup test definition
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['fullname', '', '3', '1', '', '', '', '', '', 'Full Name', ''],
            ['email', '', '3', '2', '', 'e', '', '', '', 'Email', ''],
        ];
        
        $q = '';
        _select_cols('contacts', '', $q);
        
        $this->assertStringContainsString('id', $q);
        $this->assertStringContainsString('fullname', $q);
        $this->assertStringContainsString('email', $q);
    }

    public function testValFunctionWithConstantField(): void
    {
        $a = ['field', '', '0', '2', 'k', 'constant_value', '', '', '', 'Field', ''];
        $o = [];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(0, $result);
        $this->assertEquals('constant_value', $v);
    }

    public function testValFunctionWithGeneratedId(): void
    {
        $a = ['id', '', '0', '2', '@', '', '', '', '', 'ID', ''];
        $o = [];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(0, $result);
        $this->assertIsString($v);
        $this->assertStringContainsString('.', $v);
        $this->assertGreaterThan(10, strlen($v));
    }

    public function testValFunctionWithRandomNumber(): void
    {
        $a = ['otp', '', '0', '2', '#', '', '', '', '', 'OTP', ''];
        $o = [];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(0, $result);
        $this->assertIsString($v);
        $this->assertEquals(9, strlen($v));
        $this->assertMatchesRegularExpression('/^[0-9]{9}$/', $v);
    }

    public function testValFunctionWithMandatoryField(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $a = ['fullname', '', '3', '1', 'm', '', '', '', '', 'Full Name', ''];
        $o = ['i_' => 0, 'fullname' => ''];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
        $this->assertStringContainsString('Required', $ERRORS[0][1]);
    }

    public function testValFunctionWithDefaultValue(): void
    {
        $a = ['status', '', '3', '1', 'v', '', '', '1', '', 'Status', ''];
        $o = [];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(0, $result);
        $this->assertEquals('1', $v);
    }

    public function testValFunctionWithLengthValidation(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        // Test minimum length
        $a = ['code', '', '3', '1', '', 'l', '5', '10', '', 'Code', ''];
        $o = ['i_' => 0, 'code' => '123'];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertGreaterThan(0, $result);
        $this->assertGreaterThan(0, count($ERRORS));
        
        // Test maximum length
        $ERRORS = [];
        $o = ['i_' => 0, 'code' => '12345678901'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertGreaterThan(0, $result);
        $this->assertGreaterThan(0, count($ERRORS));
    }

    public function testValFunctionWithEmailValidation(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $a = ['email', '', '3', '2', '', 'e', '', '', '', 'Email', ''];
        
        // Valid email
        $o = ['i_' => 0, 'email' => 'test@example.com'];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        
        // Invalid email
        $ERRORS = [];
        $o = ['i_' => 0, 'email' => 'invalid-email'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
        $this->assertStringContainsString('Email', $ERRORS[0][1]);
    }

    public function testValFunctionWithPhoneValidation(): void
    {
        global $ERRORS;
        $GLOBALS['COUNTRY_CODE'] = '+256';
        $ERRORS = [];
        
        $a = ['phone', '', '3', '1', '', 'p', '', '', '', 'Phone', ''];
        
        // Valid phone
        $o = ['i_' => 0, 'phone' => '0701234567'];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $v);
        
        // Invalid phone
        $ERRORS = [];
        $o = ['i_' => 0, 'phone' => 'abc'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
        $this->assertStringContainsString('Phone', $ERRORS[0][1]);
    }

    public function testValFunctionWithUniqueField(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $a = ['username', '', '3', '1', 'u', '', '', '', '', 'Username', ''];
        $o = ['i_' => 0, 'username' => 'testuser'];
        $p = ['username' => 'TESTUSER']; // Same value, different case
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
        $this->assertStringContainsString('DUPLICATE', $ERRORS[0][2]);
    }

    public function testCsvColsKFunction(): void
    {
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['fullname', '', '3', '1', '', '', '', '', '', 'Full Name', ''],
            ['email', '', '3', '2', '', 'e', '', '', '', 'Email', ''],
        ];
        
        $GLOBALS['contacts_csv'] = ['id', 'fullname', 'email'];
        
        $result = _csv_cols_k('contacts');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('id', $result);
        $this->assertArrayHasKey('fullname', $result);
        $this->assertArrayHasKey('email', $result);
    }

    public function testCsvColsVFunction(): void
    {
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['fullname', '', '3', '1', '', '', '', '', '', 'Full Name', ''],
        ];
        
        $GLOBALS['contacts_csv'] = ['id', 'fullname'];
        
        $row = [123, 'John Doe'];
        $result = _csv_cols_v('contacts', $row);
        
        $this->assertIsArray($result);
        $this->assertEquals(123, $result['id']);
        $this->assertEquals('John Doe', $result['fullname']);
    }
}
