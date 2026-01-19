<?php

namespace Tests\Unit;

use Tests\TestCase;

class ContextTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        require_once __DIR__ . '/../../lib/rest.php';
        
        // Setup test data
        $_SESSION['cc_user_id'] = '1';
        $_SESSION['cc_user_role'] = '1';
        $_SESSION['cc_user_usn'] = 'testuser';
        
        $GLOBALS['RESOURCES'] = [
            'contacts' => ['contact', '', '3', '0', '0', 'Contact', 'id DESC'],
        ];
        
        $GLOBALS['RIGHTS_1'] = [
            'contacts' => ['1', '1', '1', '0', '0', 'created_by_id=', 'auth_id'],
        ];
        
        $GLOBALS['contacts_def'] = [
            ['id', '', '0', '2', '', '', '', '', '', 'ID', ''],
            ['fullname', '', '3', '1', 'm', '', '', '', '', 'Full Name', ''],
            ['created_by_id', '', '0', '2', '', '', '', '', '', 'Created By', ''],
        ];
    }

    public function testCtxRightsWithoutContextFilter(): void
    {
        $aa = ['w' => '', 's' => '', 'ta' => ''];
        $av = [];
        $p = [];
        $rights = ['1', '1', '1', '0', '0']; // No context filter
        
        $result = ctx_rights('contacts', $aa, $av, $p, $rights);
        $this->assertEquals(0, $result);
    }

    public function testCtxRightsWithContextFilter(): void
    {
        $aa = ['w' => '', 's' => '', 'ta' => ''];
        $av = [];
        $p = [];
        $rights = ['1', '1', '1', '0', '0', 'created_by_id=', 'auth_id'];
        
        $result = ctx_rights('contacts', $aa, $av, $p, $rights);
        $this->assertEquals(0, $result);
        
        // Check that where clause was added
        $this->assertStringContainsString('created_by_id', $aa['w']);
        $this->assertStringContainsString('1', implode(',', $av));
    }

    public function testCtxFunctionBasic(): void
    {
        $aa = ['w' => '', 's' => '', 'lim' => '', 'ta' => '', 'f' => '', 'group' => ''];
        $av = [];
        $fo = ['_c' => 10, '_o' => 0];
        $join = [];
        
        ctx('contacts', '', $aa, $av, $fo, $join);
        
        // Should set limit
        $this->assertStringContainsString('LIMIT', $aa['lim']);
    }

    public function testCtxWithSearchFilter(): void
    {
        $aa = ['w' => '', 's' => '', 'lim' => '', 'ta' => '', 'f' => '', 'group' => ''];
        $av = [];
        $fo = ['_c' => 10, '_o' => 0, '_search' => 'john'];
        $join = [];
        
        ctx('contacts', '', $aa, $av, $fo, $join);
        
        // Should add WHERE clause for search
        $this->assertStringContainsString('WHERE', $aa['w']);
        $this->assertStringContainsString('%john%', implode(',', $av));
    }

    public function testCtxFvFunctionGeneratesKeyMap(): void
    {
        $aa = ['f' => ''];
        $av = [];
        $fo = ['id' => '123'];
        
        ctx_fv('contacts', $aa, $av, $fo);
        
        // Should generate key-value map JSON
        $this->assertStringContainsString('id', $aa['f']);
    }

    public function testCtxFFunctionGeneratesFullFieldInfo(): void
    {
        $aa = ['f' => ''];
        $av = [];
        $fo = ['id' => '123'];
        
        ctx_f('contacts', $aa, $av, $fo);
        
        // Should generate full field information
        $this->assertStringContainsString('id', $aa['f']);
        $this->assertStringContainsString('fullname', $aa['f']);
    }
}
