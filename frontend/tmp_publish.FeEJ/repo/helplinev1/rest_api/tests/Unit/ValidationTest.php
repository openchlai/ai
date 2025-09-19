<?php

namespace Tests\Unit;

use Tests\TestCase;

class ValidationTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Include required files
        require_once __DIR__ . '/../../api/model.php';
        require_once __DIR__ . '/../../lib/rest.php';
        
        // Set up required global variables
        $GLOBALS['COUNTRY_CODE'] = '+256';
        $GLOBALS['src_enum'] = [
            'call' => ['', '', '', '1', ''], // Phone validation required
            'email' => ['', '', '', '0', ''], // Email validation
            'sms' => ['', '', '', '1', ''], // Phone validation required
        ];
    }

    public function testPhoneValidation(): void
    {
        // Test valid phone number
        $phone = '0701234567';
        $result = _val_phone($phone);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $phone);

        // Test invalid phone number - too short
        $phone = '123';
        $result = _val_phone($phone);
        $this->assertEquals(1, $result);

        // Test invalid phone number - contains letters
        $phone = 'abc123def';
        $result = _val_phone($phone);
        $this->assertEquals(1, $result);

        // Test valid international format
        $phone = '+256701234567';
        $result = _val_phone($phone);
        $this->assertEquals(0, $result);
    }

    public function testEmailValidation(): void
    {
        // Test valid email
        $this->assertEquals(0, _val_email('test@example.com'));
        $this->assertEquals(0, _val_email('user.name+tag@domain.co.uk'));
        $this->assertEquals(0, _val_email('user123@test-domain.com'));

        // Test invalid emails
        $this->assertEquals(1, _val_email(''));
        $this->assertEquals(1, _val_email('invalid-email'));
        $this->assertEquals(1, _val_email('@domain.com'));
        $this->assertEquals(1, _val_email('user@'));
        $this->assertEquals(1, _val_email('user..name@domain.com'));
    }

    public function testAddressValidation(): void
    {
        // Test phone address validation
        $phone = '0701234567';
        $o = ['src' => 'call'];
        $result = _val_addr($o, $phone);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $phone);

        // Test invalid phone address
        $phone = 'invalid';
        $result = _val_addr($o, $phone);
        $this->assertEquals(1, $result);

        // Test missing src
        $phone = '0701234567';
        $o = [];
        $result = _val_addr($o, $phone);
        $this->assertEquals(1, $result);

        // Test invalid src
        $phone = '0701234567';
        $o = ['src' => 'invalid_src'];
        $result = _val_addr($o, $phone);
        $this->assertEquals(1, $result);
    }

    public function testPhoneFormatting(): void
    {
        // Test Uganda format
        $GLOBALS['COUNTRY_CODE'] = '+256';
        
        $this->assertEquals('+256701234567', _phone_fmt('0701234567'));
        $this->assertEquals('+256701234567', _phone_fmt(' 0701234567'));
        $this->assertEquals('+256701234567', _phone_fmt('+256701234567'));
        $this->assertEquals('1234567890', _phone_fmt('1234567890')); // 10 digits, not 9
        
        // Test edge cases
        $this->assertEquals('', _phone_fmt(''));
        $this->assertEquals('123', _phone_fmt('123'));
        $this->assertEquals('12345678901234567890', _phone_fmt('12345678901234567890'));
    }

    public function testRandomStringGeneration(): void
    {
        // Test numeric random string
        $random = _rands(8, 'num');
        $this->assertEquals(8, strlen($random));
        $this->assertMatchesRegularExpression('/^\d{8}$/', $random);

        // Test alphanumeric random string
        $random = _rands(10, 'alpha');
        $this->assertEquals(10, strlen($random));
        $this->assertMatchesRegularExpression('/^[0-9A-Za-z]{10}$/', $random);

        // Test ASCII random string
        $random = _rands(6, 'ascii');
        $this->assertEquals(6, strlen($random));
        $this->assertMatchesRegularExpression('/^[0-9A-Za-z@!#$]{6}$/', $random);

        // Test edge case - zero length
        $random = _rands(0, 'num');
        $this->assertEquals('', $random);
    }

    public function testValueEscaping(): void
    {
        // Test HTML escaping - __VESC uses json_encode internally
        $result = __VESC('<script>');
        $this->assertStringContainsString('&lt;', $result);
        $this->assertStringContainsString('&gt;', $result);
        
        // Test regular text
        $this->assertEquals('normal text', __VESC('normal text'));
        $this->assertEquals('123456', __VESC('123456'));
        
        // Test special characters - json_encode adds backslashes
        $result = __VESC("test \n newline");
        $this->assertStringContainsString('\\n', $result);
        
        // Test quotes - json_encode handles quotes
        $result = __VESC('quotes "test"');
        $this->assertStringContainsString('\\"', $result);
        
        // Test empty string
        $this->assertEquals('', __VESC(''));
    }

    public function testDateFormatting(): void
    {
        // Test valid timestamp
        $timestamp = 1640995200; // 2022-01-01 00:00:00 UTC
        $this->assertEquals('2022', _date('Y', $timestamp));
        $this->assertEquals('01 Jan 2022', _date('d M Y', $timestamp));
        
        // Test zero timestamp
        $this->assertEquals('', _date('Y', 0));
        
        // Test current time
        $now = time();
        $this->assertEquals(date('Y', $now), _date('Y', $now));
    }

    public function testEnumFormatting(): void
    {
        // Set up test enum
        $GLOBALS['test_enum'] = [
            '0' => ['0', 'No', ''],
            '1' => ['1', 'Yes', ''],
            '2' => ['2', 'Maybe', '']
        ];

        // Test single value
        $this->assertEquals('Yes', _enum('::test:0:1', '1'));
        $this->assertEquals('No', _enum('::test:0:1', '0'));

        // Test multiple values
        $this->assertEquals('No,Yes', _enum('::test:0:1', '0,1'));
        
        // Test missing enum
        $this->assertEquals('1', _enum('::missing:0:1', '1'));
        
        // Test invalid format
        $this->assertEquals('1', _enum('invalid', '1'));
        
        // Test empty value
        $this->assertEquals('', _enum('::test:0:1', ''));
    }

    public function testStr2TsFunction(): void
    {
        // Test "all" period
        $this->assertEquals('', _str2ts('all'));
        
        // Test "today" period
        $result = _str2ts('today');
        $this->assertIsNumeric($result);
        $this->assertGreaterThan(0, $result);
        
        // Test "this_month" period
        $result = _str2ts('this_month');
        $this->assertStringContainsString(';', $result);
        $parts = explode(';', $result);
        $this->assertCount(2, $parts);
        $this->assertIsNumeric($parts[0]);
        $this->assertIsNumeric($parts[1]);
        
        // Test "this_year" period
        $result = _str2ts('this_year');
        $this->assertStringContainsString(';', $result);
        
        // Test invalid period
        $this->assertEquals('', _str2ts('invalid_period'));
    }

    public function testValidationErrors(): void
    {
        // Clear errors before test
        $GLOBALS['ERRORS'] = [];
        
        // Test error creation
        _val_error('test_resource', 1, 'test_field', 'test_value', 'INVALID', 'Test error message');
        
        $this->assertCount(1, $GLOBALS['ERRORS']);
        $this->assertEquals('error', $GLOBALS['ERRORS'][0][0]);
        $this->assertEquals('Test error message', $GLOBALS['ERRORS'][0][1]);
        $this->assertEquals('INVALID', $GLOBALS['ERRORS'][0][2]);
        $this->assertEquals('test_resource', $GLOBALS['ERRORS'][0][3]);
        $this->assertEquals(1, $GLOBALS['ERRORS'][0][4]);
        $this->assertEquals('test_field', $GLOBALS['ERRORS'][0][5]);
        $this->assertEquals('test_value', $GLOBALS['ERRORS'][0][6]);
    }

    public function testValidIdGeneration(): void
    {
        $id1 = _val_id();
        $id2 = _val_id();
        
        $this->assertIsNumeric($id1);
        $this->assertIsNumeric($id2);
        $this->assertNotEquals($id1, $id2); // Should be different due to timestamp
        $this->assertGreaterThan(0, $id1);
        $this->assertGreaterThan(0, $id2);
    }

    public function testKvFunction(): void
    {
        // Test regular key-value extraction
        $o = ['test_key' => 'test_value'];
        $p = [];
        $op = '';
        
        $result = _kv('test_key', $op, $o, $p);
        $this->assertEquals('test_value', $result);
        $this->assertEquals('=', $op);

        // Test with prefix colon (special handling)
        $result = _kv(':like:phone:default_phone', $op, $o, $p);
        $this->assertEquals('like', $op);

        // Test priority - p array over o array
        $p = ['test_key' => 'priority_value'];
        $result = _kv('test_key', $op, $o, $p);
        $this->assertEquals('priority_value', $result);

        // Test space prefix (constant value)
        $result = _kv(' constant_value', $op, $o, $p);
        $this->assertEquals('constant_value', $result);
    }

    public function testModelKeyIdGeneration(): void
    {
        // Set up test resources
        $GLOBALS['RESOURCES'] = [
            'test_resource' => ['test_table', 'test_alias', '', '', '', '', '', '', '']
        ];
        
        $a = [['id', '']];
        $result = model_k_id('test_resource', '_suffix', $a);
        $this->assertEquals('test_alias_suffix_id', $result);

        // Test with custom key
        $a = [['id', 'custom_key']];
        $result = model_k_id('test_resource', '_suffix', $a);
        $this->assertEquals('custom_key_suffix', $result);

        // Test with empty alias
        $GLOBALS['RESOURCES']['test_resource'][1] = '';
        $a = [['id', '']];
        $result = model_k_id('test_resource', '_suffix', $a);
        $this->assertEquals('test_table_suffix_id', $result);
    }
}
