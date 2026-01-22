<?php

namespace Tests\Unit;

use Tests\TestCase;

class DatabaseOpsTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        require_once __DIR__ . '/../../lib/rest.php';
        
        $_SESSION['cc_user_id'] = '1';
        $_SESSION['cc_user_role'] = '1';
        $_SESSION['cc_user_usn'] = 'testuser';
        
        $GLOBALS['RESOURCES'] = [
            'contacts' => ['contact', '', '3', '0', '0', 'Contact', 'id DESC'],
            'cases' => ['kase', 'case', '3', '0', '0', 'Case', 'id DESC'],
        ];
        
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['created_on', '', '0', '3', '', '', '', '', '', 'Created On', ''],
            ['created_by', '', '0', '2', '', '', '', '', '', 'Created By', ''],
            ['created_by_id', '', '0', '2', '', 'f', '', '', '', 'Created By ID', ''],
            ['fullname', '', '3', '1', 'm', '', '', '', '', 'Full Name', ''],
            ['email', '', '3', '2', '', 'e', '', '', '', 'Email', ''],
            ['phone', '', '3', '1', '', 'p', '', '', '', 'Phone', ''],
            ['status', '', '3', '1', 'v', '', '', '1', '', 'Status', ''],
        ];
    }

    public function testTryFunctionValidatesFields(): void
    {
        $o = ['i_' => 0, 'fullname' => 'John Doe', 'email' => 'john@example.com'];
        $p = [];
        
        $result = _try('contacts', '', null, $o, $p);
        
        // Should succeed (return null for add or id for update)
        $this->assertNull($result);
    }

    public function testTryFunctionDetectsInvalidFields(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $o = ['i_' => 0, 'fullname' => '', 'email' => 'invalid-email'];
        $p = [];
        
        $result = _try('contacts', '', null, $o, $p);
        
        // Should fail validation
        $this->assertEquals(-2, $result);
        $this->assertGreaterThan(0, count($ERRORS));
    }

    public function testValFunctionSkipsUnsetFieldsDuringUpdate(): void
    {
        $a = ['fullname', '', '3', '1', 'm', '', '', '', '', 'Full Name', ''];
        $o = []; // Field not set
        $p = [];
        $v = null;
        
        $result = _val('contacts', '123', $o, $p, $a, $v); // Update mode (id is set)
        
        // Should skip validation
        $this->assertEquals(0, $result);
        $this->assertNull($v);
    }

    public function testValFunctionRequiresMandatoryFieldsOnAdd(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $a = ['fullname', '', '3', '1', 'm', '', '', '', '', 'Full Name', ''];
        $o = ['i_' => 0]; // Field not set
        $p = [];
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v); // Add mode
        
        // Should require the field
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
    }

    public function testValFunctionWithRegexValidation(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $a = ['code', '', '3', '1', '', 'r', '/^[A-Z]{3}$/', '', '', 'Code', ''];
        
        // Valid code
        $o = ['i_' => 0, 'code' => 'ABC'];
        $p = [];
        $v = null;
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        
        // Invalid code
        $ERRORS = [];
        $o = ['i_' => 0, 'code' => 'abc123'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
    }

    public function testValFunctionWithNumericLengthValidation(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $a = ['score', '', '3', '4', '', 'l', '0', '100', '', 'Score', ''];
        
        // Valid score
        $o = ['i_' => 0, 'score' => '50'];
        $p = [];
        $v = null;
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        
        // Score too low
        $ERRORS = [];
        $o = ['i_' => 0, 'score' => '-10'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertGreaterThan(0, $result);
        
        // Score too high
        $ERRORS = [];
        $o = ['i_' => 0, 'score' => '150'];
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertGreaterThan(0, $result);
    }

    public function testValFunctionWithForeignKey(): void
    {
        global $ERRORS;
        $ERRORS = [];
        
        $a = ['user_id', '', '3', '2', '', 'f', '', '', '', 'User ID', ''];
        
        // Foreign key not validated when p is set
        $o = ['i_' => 0, 'user_id' => '999'];
        $p = ['user_id' => '1']; // Validated from DB
        $v = null;
        
        $result = _val('contacts', null, $o, $p, $a, $v);
        $this->assertEquals(0, $result);
        
        // Foreign key fails when not in p
        $ERRORS = [];
        $o = ['i_' => 0, 'user_id' => '999'];
        $p = []; // Not validated
        $result = _val('contacts', null, $o, $p, $a, $v, 0);
        $this->assertEquals(1, $result);
        $this->assertCount(1, $ERRORS);
        $this->assertStringContainsString('INVALID_FOREIGN_KEY', $ERRORS[0][2]);
    }

    public function testValAddrFunction(): void
    {
        $GLOBALS['COUNTRY_CODE'] = '+256';
        $GLOBALS['src_enum'] = [
            '1' => ['whatsapp', 'WhatsApp', 'WhatsApp', '1'],
            '2' => ['email', 'Email', 'Email', '0'],
        ];
        
        // Phone address
        $o = ['src' => '1'];
        $v = '0701234567';
        $result = _val_addr($o, $v);
        $this->assertEquals(0, $result);
        $this->assertEquals('+256701234567', $v);
        
        // Invalid phone
        $v = 'invalid';
        $result = _val_addr($o, $v);
        $this->assertEquals(1, $result);
    }

    public function testSelectColsFunctionWithPrefix(): void
    {
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['fullname', '', '3', '1', '', '', '', '', '', 'Full Name', ''],
        ];
        
        $q = '';
        _select_cols('contacts', 'c.', $q);
        
        $this->assertStringContainsString('c.id', $q);
        $this->assertStringContainsString('c.fullname', $q);
    }

    public function testSelectColsFunctionWithComputedFields(): void
    {
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['age', '', '4', '2', '', '', 'users', 'YEAR(NOW())-YEAR(dob)', '', 'Age', ''],
        ];
        
        $q = '';
        _select_cols('contacts', '', $q);
        
        $this->assertStringContainsString('id', $q);
        // Computed field should include the expression
        $this->assertStringContainsString('YEAR(NOW())', $q);
    }

    public function testSelectColsFunctionExcludesHiddenFields(): void
    {
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['password', '', '0', '1', '', '', '', '', '', 'Password', ''], // Hidden (type 0)
            ['fullname', '', '3', '1', '', '', '', '', '', 'Full Name', ''],
        ];
        
        $q = '';
        _select_cols('contacts', '', $q);
        
        $this->assertStringContainsString('id', $q);
        $this->assertStringContainsString('fullname', $q);
        // Password should not be in select (hidden field)
    }

    public function testModelKIdWithMissingResources(): void
    {
        // When RESOURCES is not set, should fallback to singularized resource name
        unset($GLOBALS['RESOURCES']);
        
        $a = [['id', '', '0', '2']];
        $result = model_k_id('contacts', '', $a);
        
        // Should singularize 'contacts' to 'contact' and append '_id'
        $this->assertEquals('contact_id', $result);
    }

    public function testKvWithDefaultValue(): void
    {
        $o = [];
        $p = [];
        $op = '';
        
        // Test default value when key not found
        $result = _kv(':=:missing_key:default_value', $op, $o, $p);
        $this->assertEquals('default_value', $result);
    }

    public function testKvWithNullPlaceholder(): void
    {
        $o = [];
        $p = [];
        $op = '';
        
        // Test null placeholder
        $result = _kv(':: : null', $op, $o, $p);
        $this->assertStringContainsString('null', $result);
        $this->assertStringContainsString('-', $result);
    }
}
