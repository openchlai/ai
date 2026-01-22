<?php

namespace Tests\Unit;

use Tests\TestCase;

class FieldOperationsTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        require_once __DIR__ . '/../../lib/rest.php';
        
        $_SESSION['cc_user_id'] = '1';
        $_SESSION['cc_user_role'] = '1';
        
        $GLOBALS['COUNTRY_CODE'] = '+256';
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['fullname', '', '3', '1', 'm', '', '', '', '', 'Full Name', ''],
            ['email', '', '3', '2', '', 'e', '', '', '', 'Email', ''],
        ];
    }

    public function testSelectColsBasic(): void
    {
        $q = '';
        _select_cols('contacts', '', $q);
        
        $this->assertNotEmpty($q);
        $this->assertStringContainsString('id', $q);
        $this->assertStringContainsString('fullname', $q);
    }

    public function testSelectColsWithTablePrefix(): void
    {
        $q = '';
        _select_cols('contacts', 't1.', $q);
        
        $this->assertStringContainsString('t1.id', $q);
        $this->assertStringContainsString('t1.fullname', $q);
    }

    public function testSelectColsWithAlias(): void
    {
        $GLOBALS['users_def'] = [
            ['id', 'user_id', '0', '2', '', '', '', '', '', 'ID', ''],
            ['name', 'username', '3', '1', '', '', '', '', '', 'Name', ''],
        ];
        
        $q = '';
        _select_cols('users', '', $q);
        
        // Aliases are not used in SELECT, original field names are
        $this->assertStringContainsString('id', $q);
        $this->assertStringContainsString('name', $q);
    }

    public function testSelectColsWithComputedField(): void
    {
        $GLOBALS['reports_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['total', '', '4', '2', '', '', 'reports', 'SUM(amount)', '', 'Total', ''],
        ];
        
        $q = '';
        _select_cols('reports', '', $q);
        
        // Computed fields use field name, not expression in basic SELECT
        $this->assertStringContainsString('id', $q);
        $this->assertStringContainsString('total', $q);
    }

    public function testCsvColsKMapping(): void
    {
        $this->markTestSkipped('CSV functions not available in test context');
    }

    public function testCsvColsVMapping(): void
    {
        $this->markTestSkipped('CSV functions not available in test context');
    }

    public function testValWithEmptyStringVsNull(): void
    {
        $a = ['field', '', '3', '1', '', '', '', '', '', 'Field', ''];
        $p = [];
        $v = null;
        
        // Empty string in o
        $o = ['i_' => 0, 'field' => ''];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('', $v);
        
        // Null/missing in o
        $o = ['i_' => 0];
        $v = null;
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        $this->assertNull($v);
    }

    public function testValWithPOverridesO(): void
    {
        $a = ['field', '', '3', '1', '', '', '', '', '', 'Field', ''];
        $o = ['i_' => 0, 'field' => 'from_o'];
        $p = ['field' => 'from_p'];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(0, $result);
        $this->assertEquals('from_p', $v); // p takes precedence
    }

    public function testValWithDefaultValueWhenNull(): void
    {
        $a = ['status', '', '3', '1', 'v', '', '', 'active', '', 'Status', ''];
        $o = ['i_' => 0];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(0, $result);
        $this->assertEquals('active', $v);
    }

    public function testValWithDefaultValueNotAppliedWhenSet(): void
    {
        $a = ['status', '', '3', '1', 'v', '', '', 'active', '', 'Status', ''];
        $o = ['i_' => 0, 'status' => 'inactive'];
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        
        $this->assertEquals(0, $result);
        $this->assertEquals('inactive', $v);
    }

    public function testValStringLengthValidation(): void
    {
        global $ERRORS;
        
        // Min length validation
        $a = ['code', '', '3', '1', '', 'l', '3', '10', '', 'Code', ''];
        
        // Too short
        $ERRORS = [];
        $o = ['i_' => 0, 'code' => 'AB'];
        $p = [];
        $v = null;
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertGreaterThan(0, $result);
        $this->assertGreaterThan(0, count($ERRORS));
        
        // Valid length
        $ERRORS = [];
        $o = ['i_' => 0, 'code' => 'ABCD'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        
        // Too long
        $ERRORS = [];
        $o = ['i_' => 0, 'code' => '12345678901'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertGreaterThan(0, $result);
    }

    public function testValNumericRangeValidation(): void
    {
        global $ERRORS;
        
        $a = ['age', '', '3', '4', '', 'l', '0', '150', '', 'Age', ''];
        
        // Valid
        $ERRORS = [];
        $o = ['i_' => 0, 'age' => 25];
        $p = [];
        $v = null;
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        
        // Below minimum
        $ERRORS = [];
        $o = ['i_' => 0, 'age' => -5];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertGreaterThan(0, $result);
        
        // Above maximum
        $ERRORS = [];
        $o = ['i_' => 0, 'age' => 200];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertGreaterThan(0, $result);
    }

    public function testTryWithValidData(): void
    {
        $o = ['i_' => 0, 'fullname' => 'Test User', 'email' => 'test@example.com'];
        $p = [];
        
        $result = _try('contacts', '', null, $o, $p);
        
        $this->assertNull($result);
    }

    public function testTryWithInvalidData(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $o = ['i_' => 0, 'fullname' => '', 'email' => 'invalid'];
        $p = [];
        
        $result = _try('contacts', '', null, $o, $p);
        
        $this->assertEquals(-2, $result);
        $this->assertGreaterThan(0, count($ERRORS));
    }

    public function testPhoneFmtWithVariousInputs(): void
    {
        // Test with spaces
        $result = _phone_fmt(' 0701234567 ');
        $this->assertEquals('+256701234567', $result);
        
        // Test with plus and spaces
        $result = _phone_fmt(' +256701234567 ');
        $this->assertEquals('256701234567', $result);
        
        // Test already formatted
        $result = _phone_fmt('256701234567');
        $this->assertEquals('256701234567', $result);
    }

    public function testVESCWithComplexContent(): void
    {
        $complex = '<div class="test">Content & "quotes" with \'apostrophes\'</div>';
        $result = __VESC($complex);
        
        $this->assertStringContainsString('&lt;', $result);
        $this->assertStringContainsString('&gt;', $result);
        $this->assertStringContainsString('&amp;', $result);
    }

    public function testModelKIdWithPartialResources(): void
    {
        $GLOBALS['RESOURCES'] = [
            'contacts' => ['contact'],
        ];
        
        $a = [['id', '', '0']];
        $result = model_k_id('contacts', '', $a);
        
        $this->assertEquals('contact_id', $result);
    }

    public function testKvWithComplexOperators(): void
    {
        $o = ['field1' => 'value1', 'field2' => 'value2', 'field3' => ''];
        $p = ['field4' => 'value4'];
        $op = '';
        
        // Test with colon prefix for default
        $result = _kv(':>=:field1:default', $op, $o, $p);
        $this->assertEquals('value1', $result);
        $this->assertEquals('>=', $op);
        
        // Test with missing field and default
        $result = _kv(':=:missing:fallback', $op, $o, $p);
        $this->assertEquals('fallback', $result);
    }

    public function testValAddrWithDifferentSources(): void
    {
        $GLOBALS['src_enum'] = [
            '1' => ['phone', 'Phone', 'Phone', '1'],
            '2' => ['email', 'Email', 'Email', '0'],
        ];
        
        // Phone source
        $o = ['src' => '1'];
        $v = '0701234567';
        $result = _val_addr($o, $v);
        $this->assertEquals(0, $result);
        
        // Non-phone source
        $o = ['src' => '2'];
        $v = 'test@example.com';
        $result = _val_addr($o, $v);
        $this->assertEquals(0, $result);
    }
}
