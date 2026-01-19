<?php

namespace Tests\Unit;

use Tests\TestCase;

class ErrorHandlingTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        require_once __DIR__ . '/../../lib/rest.php';
        
        $GLOBALS['COUNTRY_CODE'] = '+256';
        $_SESSION['cc_user_id'] = '1';
        $_SESSION['cc_user_role'] = '1';
    }

    public function testPhoneFmtWithEmptyString(): void
    {
        $result = _phone_fmt('');
        $this->assertEquals('', $result);
    }

    public function testPhoneFmtWithSpacesOnly(): void
    {
        $result = _phone_fmt('   ');
        $this->assertEquals('', $result);
    }

    public function testPhoneFmtWithPlusPrefix(): void
    {
        $result = _phone_fmt('+256701234567');
        $this->assertEquals('256701234567', $result);
    }

    public function testPhoneFmtWithZeroPrefix(): void
    {
        $result = _phone_fmt('0701234567');
        $this->assertEquals('+256701234567', $result);
    }

    public function testPhoneFmtWithMixedSpaces(): void
    {
        $result = _phone_fmt('0 701234567');
        $this->assertEquals('+256701234567', $result);
    }

    public function testVESCWithSpecialChars(): void
    {
        $result = __VESC('test&value');
        // VESC escapes < and > but not &
        $this->assertIsString($result);
    }

    public function testVESCWithQuotes(): void
    {
        $result = __VESC('test"value');
        $this->assertStringContainsString('\\', $result);
    }

    public function testVESCWithBackslash(): void
    {
        $result = __VESC('test\\value');
        $this->assertIsString($result);
    }

    public function testVESCWithNewlines(): void
    {
        $result = __VESC("line1\nline2\rline3");
        $this->assertIsString($result);
        $this->assertStringContainsString('\\', $result);
    }

    public function testVESCWithTabs(): void
    {
        $result = __VESC("col1\tcol2\tcol3");
        $this->assertIsString($result);
    }

    public function testVESCWithNullAndNumbers(): void
    {
        $this->assertEquals('', __VESC(null));
        $this->assertEquals('0', __VESC(0));
        $this->assertEquals('123', __VESC(123));
        $this->assertEquals('123.45', __VESC(123.45));
    }

    public function testValEmailWithComplexAddresses(): void
    {
        // Valid complex emails
        $this->assertEquals(0, _val_email('first.last@example.com'));
        $this->assertEquals(0, _val_email('user+tag@sub.domain.com'));
        $this->assertEquals(0, _val_email('test_email@test-domain.org'));
        $this->assertEquals(0, _val_email('a@b.co'));
    }

    public function testValEmailWithInvalidFormats(): void
    {
        $this->assertEquals(1, _val_email('user@'));
        $this->assertEquals(1, _val_email('@domain.com'));
        $this->assertEquals(1, _val_email('user space@domain.com'));
        $this->assertEquals(1, _val_email('user..double@domain.com'));
        $this->assertEquals(1, _val_email('user@domain'));
    }

    public function testValPhoneWithVariousFormats(): void
    {
        $GLOBALS['COUNTRY_CODE'] = '+256';
        
        // 10-digit number
        $phone = '0712345678';
        $this->assertEquals(0, _val_phone($phone));
        $this->assertEquals('+256712345678', $phone);
        
        // 12-digit number
        $phone = '256712345678';
        $this->assertEquals(0, _val_phone($phone));
        $this->assertEquals('256712345678', $phone);
        
        // Edge cases
        $phone = '123'; // Valid but short
        $this->assertEquals(0, _val_phone($phone));
    }

    public function testValPhoneWithInvalidFormats(): void
    {
        $phone = 'notaphone';
        $this->assertEquals(1, _val_phone($phone));
        
        $phone = '12'; // Too short
        $this->assertEquals(1, _val_phone($phone));
        
        $phone = ''; // Empty
        $this->assertEquals(1, _val_phone($phone));
    }

    public function testRandsConsistency(): void
    {
        // Test that rands produces unique values
        $rand1 = _rands(20, 'alpha');
        $rand2 = _rands(20, 'alpha');
        
        $this->assertNotEquals($rand1, $rand2);
        $this->assertEquals(20, strlen($rand1));
        $this->assertEquals(20, strlen($rand2));
    }

    public function testDateWithVariousTimestamps(): void
    {
        // Test epoch returns empty
        $this->assertEquals('', _date('Y-m-d', 0));
        
        // Test valid dates
        $this->assertEquals('2000-01-01', _date('Y-m-d', 946684800));
        $result = _date('Y-m-d', 1609372800);
        $this->assertMatchesRegularExpression('/^\d{4}-\d{2}-\d{2}$/', $result);
    }

    public function testDateWithDifferentFormats(): void
    {
        $timestamp = 1609459200; // 2021-01-01 00:00:00 UTC
        
        $this->assertEquals('2021', _date('Y', $timestamp));
        $this->assertEquals('01', _date('m', $timestamp));
        $this->assertEquals('2021-01-01 00:00:00', _date('Y-m-d H:i:s', $timestamp));
        $this->assertEquals('Friday', _date('l', $timestamp));
    }

    public function testEnumWithNonExistentKey(): void
    {
        $GLOBALS['test_enum'] = [
            '1' => ['key1', 'Value One'],
        ];
        
        // Non-existent key should return the original value
        $result = _enum('::test:0:1', '999');
        $this->assertEquals('999', $result);
    }

    public function testEnumWithEmptyValue(): void
    {
        $GLOBALS['test_enum'] = [
            '1' => ['key1', 'Value One'],
        ];
        
        $result = _enum('::test:0:1', '');
        $this->assertEquals('', $result);
    }

    public function testEnumWithMultipleMixedValues(): void
    {
        $GLOBALS['test_enum'] = [
            '1' => ['key1', 'Value One'],
            '2' => ['key2', 'Value Two'],
            '3' => ['key3', 'Value Three'],
        ];
        
        $result = _enum('::test:0:1', '1,999,2');
        $this->assertStringContainsString('Value One', $result);
        $this->assertStringContainsString('999', $result);
        $this->assertStringContainsString('Value Two', $result);
    }

    public function testKvWithLiteralValue(): void
    {
        $o = [];
        $p = [];
        $op = '';
        
        // Test literal value (starts with space)
        $result = _kv(' literal_value', $op, $o, $p);
        $this->assertEquals('literal_value', $result);
    }

    public function testKvWithConditionalOperator(): void
    {
        $o = ['field1' => 'value1', 'field2' => 'value2'];
        $p = [];
        $op = '';
        
        // Test conditional operator - when field1 is set, use field2
        $result = _kv(':::field1:default:field2', $op, $o, $p);
        // Result should be the value from conditional logic
        $this->assertIsString($result);
    }

    public function testValIdIncrementing(): void
    {
        $ids = [];
        for ($i = 0; $i < 10; $i++) {
            $ids[] = _val_id();
            usleep(100);
        }
        
        // Check all IDs are unique and incrementing
        $uniqueIds = array_unique($ids);
        $this->assertCount(10, $uniqueIds);
        
        for ($i = 1; $i < count($ids); $i++) {
            $this->assertGreaterThanOrEqual($ids[$i-1], $ids[$i]);
        }
    }

    public function testModelKIdWithCustomAlias(): void
    {
        $GLOBALS['RESOURCES'] = [
            'users' => ['auth', 'user', '3', '0', '0', 'User'],
        ];
        
        $a = [['id', 'user_id', '0', '2']];
        $result = model_k_id('users', '', $a);
        $this->assertEquals('user_id', $result);
    }

    public function testStr2tsWithAllPeriods(): void
    {
        $result = _str2ts('today');
        $this->assertIsNumeric($result);
        $this->assertGreaterThan(0, $result);
        
        $result = _str2ts('this_week');
        $this->assertStringContainsString(';', $result);
        
        $result = _str2ts('this_month');
        $this->assertStringContainsString(';', $result);
        
        $result = _str2ts('this_year');
        $this->assertStringContainsString(';', $result);
        
        $result = _str2ts('last_3_month');
        $this->assertStringContainsString(';', $result);
    }
}
