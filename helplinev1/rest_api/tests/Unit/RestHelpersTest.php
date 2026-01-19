<?php

namespace Tests\Unit;

use Tests\TestCase;

class RestHelpersTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        require_once __DIR__ . '/../../lib/rest.php';
    }

    public function test_G_Function(): void
    {
        $_GET['test_key'] = 'test_value';
        $this->assertEquals('test_value', _G('test_key'));
        $this->assertEquals('', _G('nonexistent'));
    }

    public function test_P_Function(): void
    {
        $_POST['post_key'] = 'post_value';
        $this->assertEquals('post_value', _P('post_key'));
        $this->assertEquals('', _P('nonexistent'));
    }

    public function test_S_Function(): void
    {
        $_SESSION['session_key'] = 'session_value';
        $this->assertEquals('session_value', _S('session_key'));
        $this->assertEquals('', _S('nonexistent'));
    }

    public function test_V_Function(): void
    {
        $array = ['key1' => 'value1', 'key2' => 'value2'];
        $this->assertEquals('value1', _V($array, 'key1'));
        $this->assertEquals('', _V($array, 'nonexistent'));
    }

    public function testVESC_Function(): void
    {
        // Test basic escaping
        $this->assertEquals('test', __VESC('test'));
        
        // Test HTML entity escaping
        $this->assertEquals('&lt;script&gt;', __VESC('<script>'));
        $this->assertEquals('&lt;div&gt;content&lt;/div&gt;', __VESC('<div>content</div>'));
        
        // Test null handling
        $this->assertEquals('', __VESC(null));
        
        // Test special characters
        $this->assertStringContainsString('\\n', __VESC("line1\nline2"));
    }

    public function testDateFunction(): void
    {
        $timestamp = 1609459200; // 2021-01-01 00:00:00 UTC
        $formatted = _date('Y-m-d', $timestamp);
        $this->assertEquals('2021-01-01', $formatted);
        
        // Test zero timestamp
        $this->assertEquals('', _date('Y-m-d', 0));
    }

    public function testEnumFunction(): void
    {
        // Setup test enum
        $GLOBALS['test_enum'] = [
            '1' => ['key1', 'Value One', 'extra1'],
            '2' => ['key2', 'Value Two', 'extra2'],
        ];
        
        $result = _enum('::test:0:1', '1');
        $this->assertEquals('Value One', $result);
        
        $result = _enum('::test:0:1', '2');
        $this->assertEquals('Value Two', $result);
        
        // Test multiple values
        $result = _enum('::test:0:1', '1,2');
        $this->assertEquals('Value One,Value Two', $result);
    }

    public function testPhoneFmtFunction(): void
    {
        $GLOBALS['COUNTRY_CODE'] = '+256';
        
        // Test 9-digit number
        $this->assertEquals('+256701234567', _phone_fmt('0701234567'));
        $this->assertEquals('+256701234567', _phone_fmt('701234567'));
        $this->assertEquals('+256701234567', _phone_fmt('+256701234567'));
        
        // Test other formats
        $this->assertEquals('256701234567', _phone_fmt('256701234567'));
    }

    public function testRandsFunction(): void
    {
        // Test numeric random string
        $rand = _rands(10, 'num');
        $this->assertEquals(10, strlen($rand));
        $this->assertMatchesRegularExpression('/^[0-9]{10}$/', $rand);
        
        // Test alphanumeric random string
        $rand = _rands(15, 'alpha');
        $this->assertEquals(15, strlen($rand));
        $this->assertMatchesRegularExpression('/^[0-9A-Za-z]{15}$/', $rand);
        
        // Test ASCII random string
        $rand = _rands(20, 'ascii');
        $this->assertEquals(20, strlen($rand));
    }

    public function testStr2tsFunction(): void
    {
        // Test "all" returns empty
        $this->assertEquals('', _str2ts('all'));
        
        // Test "today" returns timestamp for start of today
        $result = _str2ts('today');
        $this->assertIsNumeric($result);
        $this->assertGreaterThan(0, $result);
        
        // Test invalid string
        $this->assertEquals('', _str2ts('invalid_period'));
    }

    public function testValIdFunction(): void
    {
        $id1 = _val_id();
        usleep(1000); // Wait 1ms
        $id2 = _val_id();
        
        $this->assertIsNumeric($id1);
        $this->assertIsNumeric($id2);
        $this->assertGreaterThan($id1, $id2);
    }

    public function testValPhoneFunction(): void
    {
        $GLOBALS['COUNTRY_CODE'] = '+256';
        
        $phone = '0701234567';
        $result = _val_phone($phone);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $phone);
        
        // Test invalid phone
        $phone = 'abc';
        $result = _val_phone($phone);
        $this->assertEquals(1, $result);
        
        // Test too short
        $phone = '12';
        $result = _val_phone($phone);
        $this->assertEquals(1, $result);
    }

    public function testValEmailFunction(): void
    {
        // Valid emails
        $this->assertEquals(0, _val_email('test@example.com'));
        $this->assertEquals(0, _val_email('user.name@domain.co.uk'));
        $this->assertEquals(0, _val_email('user+tag@example.com'));
        
        // Invalid emails
        $this->assertEquals(1, _val_email(''));
        $this->assertEquals(1, _val_email('invalid'));
        $this->assertEquals(1, _val_email('invalid@'));
        $this->assertEquals(1, _val_email('@example.com'));
        $this->assertEquals(1, _val_email('user @example.com'));
    }

    public function testValErrorFunction(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $result = _val_error('contacts', 0, 'email', 'invalid@', 'INVALID', 'Invalid email');
        
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
        $this->assertEquals('error', $ERRORS[0][0]);
        $this->assertEquals('Invalid email', $ERRORS[0][1]);
        $this->assertEquals('INVALID', $ERRORS[0][2]);
    }

    public function testKvFunction(): void
    {
        $o = ['field1' => 'value1', 'field2' => 'value2'];
        $p = ['field3' => 'value3'];
        $op = '';
        
        // Test normal key
        $result = _kv('field1', $op, $o, $p);
        $this->assertEquals('value1', $result);
        $this->assertEquals('=', $op);
        
        // Test key from p array
        $result = _kv('field3', $op, $o, $p);
        $this->assertEquals('value3', $result);
        
        // Test operator parsing
        $result = _kv(':>:field1', $op, $o, $p);
        $this->assertEquals('value1', $result);
        $this->assertEquals('>', $op);
        
        // Test generated ID
        $result = _kv(':@#:field', $op, $o, $p);
        $this->assertStringContainsString('-', $result);
        $this->assertGreaterThan(10, strlen($result));
    }

    public function testModelKIdFunction(): void
    {
        // Setup test resources
        $GLOBALS['RESOURCES'] = [
            'contacts' => ['contact', '', '3', '0', '0', 'Contact'],
        ];
        
        $a = [['id', '', '0', '2']];
        $result = model_k_id('contacts', '', $a);
        $this->assertEquals('contact_id', $result);
        
        // Test with suffix
        $result = model_k_id('contacts', '_old', $a);
        $this->assertEquals('contact_old_id', $result);
    }
}
