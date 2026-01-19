<?php

namespace Tests\Unit;

use Tests\TestCase;

class RequestResponseTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        require_once __DIR__ . '/../../lib/rest.php';
        
        $_SESSION['cc_user_id'] = '1';
        $_SESSION['cc_user_role'] = '1';
        $_SESSION['cc_user_usn'] = 'testuser';
        
        $GLOBALS['COUNTRY_CODE'] = '+256';
    }

    public function testGetParameterFunction(): void
    {
        $_GET['param1'] = 'value1';
        $_GET['param2'] = 'value2';
        
        $this->assertEquals('value1', _G('param1'));
        $this->assertEquals('value2', _G('param2'));
        $this->assertEquals('', _G('nonexistent'));
    }

    public function testPostParameterFunction(): void
    {
        $_POST['field1'] = 'data1';
        $_POST['field2'] = 'data2';
        
        $this->assertEquals('data1', _P('field1'));
        $this->assertEquals('data2', _P('field2'));
        $this->assertEquals('', _P('missing'));
    }

    public function testSessionParameterFunction(): void
    {
        $_SESSION['user_id'] = '123';
        $_SESSION['username'] = 'testuser';
        
        $this->assertEquals('123', _S('user_id'));
        $this->assertEquals('testuser', _S('username'));
        $this->assertEquals('', _S('missing_key'));
    }

    public function testVArrayFunction(): void
    {
        $data = [
            'key1' => 'value1',
            'key2' => 'value2',
            'nested' => ['inner' => 'value3']
        ];
        
        $this->assertEquals('value1', _V($data, 'key1'));
        $this->assertEquals('value2', _V($data, 'key2'));
        $this->assertEquals('', _V($data, 'missing'));
        
        // Test with nested array
        $nested = $data['nested'];
        $this->assertEquals('value3', _V($nested, 'inner'));
    }

    public function testVESCSecurityEscaping(): void
    {
        // Test XSS prevention
        $malicious = '<script>alert("XSS")</script>';
        $escaped = __VESC($malicious);
        $this->assertStringNotContainsString('<script>', $escaped);
        $this->assertStringContainsString('&lt;', $escaped);
        $this->assertStringContainsString('&gt;', $escaped);
        
        // Test SQL injection characters
        $sql = "'; DROP TABLE users; --";
        $escaped = __VESC($sql);
        $this->assertIsString($escaped);
        
        // Test various quotes
        $quotes = "It's a \"test\"";
        $escaped = __VESC($quotes);
        $this->assertIsString($escaped);
    }

    public function testPhoneFormatInternational(): void
    {
        $GLOBALS['COUNTRY_CODE'] = '+1';
        
        // US number
        $result = _phone_fmt('5551234567');
        $this->assertEquals('+15551234567', $result);
        
        // With country code
        $result = _phone_fmt('+15551234567');
        $this->assertEquals('15551234567', $result);
        
        // With zero prefix
        $result = _phone_fmt('05551234567');
        $this->assertEquals('+15551234567', $result);
    }

    public function testRandomStringGenerationDistribution(): void
    {
        // Generate multiple random strings and check uniqueness
        $strings = [];
        for ($i = 0; $i < 50; $i++) {
            $strings[] = _rands(10, 'num');
        }
        
        $unique = array_unique($strings);
        // Should have at least 45 unique strings out of 50
        $this->assertGreaterThan(45, count($unique));
        
        // Test alpha
        $strings = [];
        for ($i = 0; $i < 50; $i++) {
            $strings[] = _rands(15, 'alpha');
        }
        
        $unique = array_unique($strings);
        $this->assertGreaterThan(48, count($unique));
    }

    public function testEnumWithMissingGlobal(): void
    {
        // When enum doesn't exist, should return original value
        $result = _enum('::nonexistent:0:1', '123');
        $this->assertEquals('123', $result);
    }

    public function testDateFormatEdgeCases(): void
    {
        // Test epoch
        $this->assertEquals('', _date('Y-m-d', 0));
        
        // Test future date
        $future = strtotime('2030-12-31');
        $result = _date('Y-m-d', $future);
        $this->assertEquals('2030-12-31', $result);
        
        // Test past date
        $past = strtotime('1990-01-01');
        $result = _date('Y-m-d', $past);
        $this->assertEquals('1990-01-01', $result);
    }

    public function testValEmailEdgeCases(): void
    {
        // Very long email
        $longEmail = str_repeat('a', 50) . '@' . str_repeat('b', 50) . '.com';
        $result = _val_email($longEmail);
        $this->assertEquals(0, $result);
        
        // Email with numbers
        $this->assertEquals(0, _val_email('user123@domain456.com'));
        
        // Email with hyphens
        $this->assertEquals(0, _val_email('user-name@domain-name.com'));
        
        // Email with underscores
        $this->assertEquals(0, _val_email('user_name@domain_name.com'));
    }

    public function testValPhoneEdgeCases(): void
    {
        $GLOBALS['COUNTRY_CODE'] = '+256';
        
        // Maximum length
        $phone = '123456789012345'; // 15 digits
        $result = _val_phone($phone);
        $this->assertEquals(0, $result);
        
        // Minimum length
        $phone = '123'; // 3 digits
        $result = _val_phone($phone);
        $this->assertEquals(0, $result);
        
        // Just over minimum
        $phone = '1234';
        $result = _val_phone($phone);
        $this->assertEquals(0, $result);
    }

    public function testKvOperators(): void
    {
        $o = ['val' => '100'];
        $p = [];
        $op = '';
        
        // Test greater than operator
        $result = _kv(':>:val', $op, $o, $p);
        $this->assertEquals('100', $result);
        $this->assertEquals('>', $op);
        
        // Test less than operator
        $result = _kv(':<:val', $op, $o, $p);
        $this->assertEquals('100', $result);
        $this->assertEquals('<', $op);
        
        // Test not equal operator
        $result = _kv(':!=:val', $op, $o, $p);
        $this->assertEquals('100', $result);
        $this->assertEquals('!=', $op);
    }

    public function testValIdUniqueness(): void
    {
        $ids = [];
        
        // Generate 100 IDs rapidly
        for ($i = 0; $i < 100; $i++) {
            $ids[] = _val_id();
        }
        
        // All should be unique
        $unique = array_unique($ids);
        $this->assertCount(100, $unique);
        
        // All should be numeric
        foreach ($ids as $id) {
            $this->assertIsNumeric($id);
            $this->assertGreaterThan(0, $id);
        }
    }

    public function testModelKIdVariations(): void
    {
        $GLOBALS['RESOURCES'] = [
            'contacts' => ['contact', '', '3'],
            'users' => ['auth', 'usr', '3'],
            'cases' => ['kase', 'case', '3'],
        ];
        
        // Standard case
        $a = [['id', '', '0']];
        $this->assertEquals('contact_id', model_k_id('contacts', '', $a));
        
        // With alias
        $this->assertEquals('usr_id', model_k_id('users', '', $a));
        
        // With different field name
        $a = [['case_id', '', '0']];
        $this->assertEquals('case_case_id', model_k_id('cases', '', $a));
        
        // With custom suffix
        $a = [['id', '', '0']];
        $this->assertEquals('contact_old_id', model_k_id('contacts', '_old', $a));
    }

    public function testStr2tsAllTimePeriods(): void
    {
        // Test all period types
        $periods = [
            'all', 'today', 'this_week', 'this_month', 'this_year',
            'last_3_month', 'last_6_month', 'last_9_month'
        ];
        
        foreach ($periods as $period) {
            $result = _str2ts($period);
            $this->assertIsString($result);
            
            if ($period !== 'all') {
                // Non-empty result for valid periods
                if (in_array($period, ['this_week', 'this_month', 'this_year', 'last_3_month', 'last_6_month', 'last_9_month'])) {
                    $this->assertStringContainsString(';', $result);
                }
            } else {
                $this->assertEquals('', $result);
            }
        }
    }

    public function testValErrorMultipleErrors(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        // Generate multiple errors
        _val_error('contacts', 0, 'field1', 'val1', 'ERR1', 'Error 1');
        _val_error('contacts', 0, 'field2', 'val2', 'ERR2', 'Error 2');
        _val_error('contacts', 0, 'field3', 'val3', 'ERR3', 'Error 3');
        
        $this->assertCount(3, $ERRORS);
        $this->assertEquals('Error 1', $ERRORS[0][1]);
        $this->assertEquals('Error 2', $ERRORS[1][1]);
        $this->assertEquals('Error 3', $ERRORS[2][1]);
    }

    public function testValWithCombinedFlags(): void
    {
        global $ERRORS;
        $GLOBALS['COUNTRY_CODE'] = '+256';
        
        // Mandatory + Phone validation
        $ERRORS = [];
        $a = ['phone', '', '3', '1', 'm', 'p', '', '', '', 'Phone', ''];
        
        // Valid
        $o = ['i_' => 0, 'phone' => '0701234567'];
        $p = [];
        $v = null;
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $v);
        
        // Missing mandatory
        $ERRORS = [];
        $o = ['i_' => 0];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(1, $result);
        
        // Invalid format
        $ERRORS = [];
        $o = ['i_' => 0, 'phone' => 'invalid'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(1, $result);
    }
}
